# Research Document: Single Persona MVP

**Feature**: 002-single-persona-mvp
**Date**: 2026-01-25
**Status**: Complete

## Overview

This document captures technical decisions made during the planning phase for implementing single persona research sessions. Each section addresses a key technical question with decision, rationale, and alternatives considered.

---

## 1. Subagent Execution Strategy

### Decision
**Use Claude Code Task tool directly via generated Python code that outputs the Task tool invocation format.**

The session runner will not directly call the Claude API. Instead, it will:
1. Generate the complete subagent prompt (persona + question)
2. Output a structured format that instructs Claude Code to spawn a Task subagent
3. Capture the subagent's response for parsing

### Rationale
- This platform runs within Claude Code environment, where the Task tool is the native mechanism for subagent execution
- Direct API calls would require API keys and bypass the subagent isolation guarantees
- Task tool provides model selection, timeout handling, and background execution built-in
- Aligns with Constitution Principle I (Subagent-First Architecture)

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Direct Claude API calls via anthropic SDK | Requires API keys, loses subagent isolation, doesn't work in Claude Code context |
| Shell subprocess calling claude CLI | Brittle, hard to capture structured output, security concerns |
| Mock subagent for MVP | Doesn't validate the real execution path, defeats purpose of MVP |

### Implementation Notes
- SessionRunner will build the prompt and return a Task invocation specification
- The CLI command will use this specification to spawn the actual subagent
- Response capture happens through Task tool's standard output mechanism

---

## 2. Response Parsing Approach

### Decision
**Use structured prompt instructions to request JSON-formatted responses from the persona subagent.**

The research prompt template will include explicit instructions for the persona to structure their response with labeled sections:
```
## Response Format
Please structure your response as follows:
1. OVERALL_IMPRESSION: [Your gut reaction in 1-2 sentences]
2. SENTIMENT: [positive/negative/mixed/neutral]
3. CONCERNS: [List your concerns, if any]
4. SUGGESTIONS: [List any suggestions for improvement]
5. DETAILED_RESPONSE: [Your full, detailed thoughts]
```

### Rationale
- LLM-native approach: Claude excels at following structured output instructions
- No external dependencies: Avoids NLP libraries (spaCy, NLTK) that add complexity
- Reliable extraction: Labeled sections are easier to parse than free-form text
- Maintains persona voice: The structured format doesn't prevent natural expression

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| NLP-based sentiment analysis | Adds heavy dependencies, less accurate than LLM self-reporting |
| Post-processing with second LLM call | Adds latency, cost, and complexity |
| Regex pattern matching on free text | Fragile, misses nuance, requires extensive rules |
| JSON-only output from persona | Too rigid, loses natural conversational quality |

### Implementation Notes
- ResponseParser will extract labeled sections using simple string parsing
- Fallback: If sections are missing, extract from free-form text using heuristics
- Sentiment mapping: positive/negative/mixed/neutral to enum values

---

## 3. Quality Metrics Implementation

### Decision
**Implement keyword-based consistency scoring with configurable trait-keyword mappings.**

Each Big Five trait and tech adoption category has associated keywords:
- High Openness: "curious", "innovative", "explore", "novel"
- Low Openness: "traditional", "proven", "familiar", "practical"
- Early Adopter: "excited", "first", "try", "cutting-edge"
- Late Majority: "skeptical", "proven", "wait", "cautious"

Consistency score = (matched trait keywords / expected trait keywords) * 100

### Rationale
- Transparent: Researchers can understand why scores are assigned
- Tunable: Keyword lists can be refined based on calibration data
- Fast: O(n) string matching, no model calls required
- Baseline: Establishes foundation for more sophisticated calibration in Phase 4

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Embedding similarity comparison | Requires embedding model, adds latency and complexity |
| Second LLM evaluating consistency | Expensive, adds another failure point |
| Human evaluation only | Doesn't scale, no automated feedback loop |
| Statistical variance analysis | Requires multiple sessions, not applicable to single session |

### Sycophancy Detection
- Count positive sentiment markers vs. critical markers
- Flag if positive:critical ratio exceeds 4:1
- Check for specific sycophancy phrases: "great idea", "love it", "perfect"

### Implementation Notes
- QualityMetrics class with configurable keyword mappings
- Persona-specific expected traits derived from Big Five scores
- Threshold configuration: warning at <70%, flag at <50%

---

## 4. Question Type Handling

### Decision
**Use a Question model with type enum and format-specific prompt templates.**

Three question types for MVP:
1. **Open-ended**: Free-form response expected
2. **Rating**: Numeric 1-10 response with justification
3. **Multiple-choice**: Selection from provided options with explanation

Each type has a prompt template that instructs the persona how to respond.

### Rationale
- Clear expectations: Personas know the expected response format
- Structured output: Rating/MC questions produce consistent parseable data
- Extensible: Easy to add new question types in future phases

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Single free-form question type only | Loses structure for quantitative research |
| Complex survey DSL | Over-engineering for MVP; Phase 3 handles surveys |
| Auto-detect question type | Unreliable, adds complexity |

### Implementation Notes
- QuestionType enum: OPEN_ENDED, RATING, MULTIPLE_CHOICE
- Question model includes: text, type, options (for MC), scale (for rating)
- Template injection based on question type

---

## 5. CLI Output Formatting

### Decision
**Use Rich library for human-readable output with JSON export option.**

Default output shows:
- Persona summary (name, key traits)
- Question asked
- Parsed response (sentiment, concerns, suggestions)
- Quality metrics (consistency score, warnings)
- Raw response (collapsible/optional)

JSON format exports complete session data for programmatic use.

### Rationale
- Rich provides beautiful terminal output with minimal code
- Familiar UX: Similar to other Python CLI tools (pytest, poetry)
- Progressive disclosure: Show summary first, details on demand
- Export compatibility: JSON for integration with other tools

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Plain print statements | Poor readability, no color/formatting |
| Tabulate only | Limited formatting options |
| Custom formatting | More code, less polished |
| HTML output | Overkill for CLI tool |

### Implementation Notes
- Rich Console for colored output
- Rich Table for structured data (metrics, parsed response)
- Rich Panel for persona summary
- --format json flag for JSON output

---

## 6. Session Persistence

### Decision
**Optional JSON export with --output flag; no persistent session database for MVP.**

Sessions are ephemeral by default. Researchers explicitly save sessions they want to keep.

### Rationale
- Simplicity: No database setup required
- User control: Researchers decide what to save
- Sufficient for MVP: Session database comes in Phase 2/5
- Export format: JSON is human-readable and machine-parseable

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| SQLite session database | Over-engineering for MVP |
| Automatic session logging | Storage concerns, privacy implications |
| YAML export | Less standard for data interchange |

### Implementation Notes
- Session model has to_json() method
- Export includes: metadata, question, response (raw + parsed), quality metrics
- Filename includes timestamp and persona ID for uniqueness

---

## 7. Error Handling Strategy

### Decision
**Graceful degradation with clear error messages and partial result preservation.**

Error categories:
1. **Persona not found**: List available personas, suggest closest match
2. **Subagent timeout**: Return timeout error, suggest retry
3. **Parse failure**: Return raw response with parsing warning
4. **Quality threshold breach**: Return results with quality warning

### Rationale
- Usability: Researchers get actionable feedback on errors
- Resilience: Partial results are often still valuable
- Debuggability: Clear error messages aid troubleshooting

### Implementation Notes
- Custom exception hierarchy: SessionError, ParseError, QualityWarning
- CLI catches exceptions and formats user-friendly messages
- Exit codes: 0 (success), 1 (error), 2 (warning)

---

## Summary of Technical Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| Language | Python 3.11+ | Continuation from Phase 0 |
| CLI Framework | Click | Continuation from Phase 0 |
| Output Formatting | Rich | Beautiful terminal output |
| Data Validation | Pydantic | Continuation from Phase 0 |
| Templating | Jinja2 | Continuation from Phase 0 |
| Subagent Execution | Claude Code Task tool | Native subagent mechanism |
| Response Parsing | Structured prompts + string parsing | LLM-native, no dependencies |
| Quality Metrics | Keyword matching | Transparent, tunable baseline |
| Session Export | JSON files | Standard, portable format |

---

**Research Complete**: All technical decisions documented. Proceed to Phase 1 design artifacts.
