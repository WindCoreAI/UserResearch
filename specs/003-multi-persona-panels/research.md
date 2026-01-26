# Research Document: Multi-Persona Panels

**Feature**: 003-multi-persona-panels
**Date**: 2026-01-25
**Status**: Complete

## Overview

This document captures technical decisions made during the planning phase for implementing multi-persona panel research. Each section addresses a key technical question with decision, rationale, and alternatives considered.

---

## 1. Parallel Execution Strategy

### Decision
**Execute panel personas in parallel using multiple concurrent Claude Code Task tool invocations with asyncio coordination.**

The panel executor will:
1. Load all personas in the panel
2. Build prompts for each persona using the existing PromptBuilder
3. Launch all Task tool invocations concurrently
4. Collect responses as they complete
5. Handle partial failures gracefully

### Rationale
- Claude Code Task tool supports parallel execution natively
- asyncio provides clean concurrent execution in Python without threading complexity
- Aligns with Constitution Principle V (Parallel Execution MUST maximize efficiency)
- Achieves the 3x speedup target for 10 personas vs sequential execution
- Existing SessionRunner can be reused for individual persona execution

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Sequential execution with batching | Doesn't achieve speedup requirements; no efficiency gain over single-persona sessions |
| ThreadPoolExecutor | Adds threading complexity; asyncio is more Pythonic for I/O-bound work |
| Background tasks with polling | More complex to coordinate; harder to aggregate results |
| External job queue (Celery) | Over-engineering; adds infrastructure requirements |

### Implementation Notes
- PanelExecutor class wraps SessionRunner with concurrent execution
- asyncio.gather() with return_exceptions=True for partial failure handling
- Progress tracking via callback or async iterator
- Timeout per persona + overall panel timeout

---

## 2. Response Aggregation Approach

### Decision
**Use LLM-based aggregation via a dedicated Claude Task tool invocation to identify themes, consensus, and divergence.**

After collecting individual responses:
1. Format all responses with persona metadata
2. Send to a dedicated "aggregator" Task subagent with structured prompt
3. Request theme extraction, sentiment distribution, and divergence analysis
4. Parse aggregator response into structured AggregatedResults

### Rationale
- LLM excels at cross-document synthesis and theme extraction
- No external NLP dependencies required (aligns with Phase 1 approach)
- Can identify subtle patterns humans might miss
- Single aggregation call is efficient vs per-response analysis
- Produces natural language summaries alongside structured data

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Rule-based keyword clustering | Misses semantic themes; fragile; requires extensive tuning |
| Embedding-based clustering (scikit-learn) | Adds heavy dependencies; over-engineering for initial panel sizes |
| Human-only analysis | Doesn't scale; defeats purpose of automation |
| Per-response micro-aggregation | Higher latency; loses holistic view |

### Aggregation Prompt Structure
```
You are a research analyst. Analyze these {N} persona responses to the question: "{question}"

For each response, I'll provide:
- Persona name and key traits
- Their parsed response (sentiment, concerns, suggestions)

Please provide:
1. THEMES: Top 3-5 recurring themes with frequency counts and supporting quotes
2. SENTIMENT_DISTRIBUTION: Percentage breakdown (positive/negative/mixed/neutral)
3. CONSENSUS_POINTS: Issues where >60% of personas agree
4. DIVERGENCE_POINTS: Issues where personas disagree, grouped by position
5. EXECUTIVE_SUMMARY: 2-3 sentence synthesis for stakeholders
```

### Implementation Notes
- ResponseAggregator service class
- Configurable theme extraction depth (3-5 themes)
- Consensus threshold configurable (default 60%)
- Fallback: If aggregation fails, return individual responses with warning

---

## 3. Panel Definition Format

### Decision
**Use YAML files for panel definitions stored in `panels/definitions/` directory, mirroring the persona structure.**

Panel definition structure:
```yaml
id: tech-adopters
name: Technology Adopters Panel
description: Full spectrum of technology adoption attitudes
purpose: Product feature testing with diverse tech comfort levels
created: 2026-01-25
personas:
  - tech-early-adopter
  - power-user
  - busy-professional
  - privacy-conscious-user
  - skeptical-late-adopter
```

### Rationale
- Consistent with persona YAML format (familiar pattern)
- Human-readable and editable
- Version controllable alongside code
- Pydantic validation ensures panel integrity
- Supports both pre-built and custom panels

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| JSON files | Less readable; harder to hand-edit |
| SQLite database | Over-engineering; not needed until Phase 5 |
| Python code defining panels | Less accessible to non-developers |
| Environment variables | Can't handle complex panel structures |

### Directory Structure
```
panels/
├── definitions/
│   ├── tech-adopters.yaml
│   ├── skeptics-critics.yaml
│   ├── power-users.yaml
│   └── general-population.yaml
└── custom/
    └── (user-created panels)
```

### Implementation Notes
- PanelLoader service (mirrors PersonaLoader pattern)
- Panel Pydantic model with validation
- Custom panels saved to panels/custom/
- Panel names must be unique across pre-built and custom

---

## 4. Panel-Level Quality Metrics

### Decision
**Aggregate individual session quality metrics and add panel-specific metrics for theme confidence and response divergence.**

Panel quality metrics:
1. **Average Consistency**: Mean of individual persona consistency scores
2. **Theme Confidence**: How strongly themes are supported (quotes/mentions ratio)
3. **Divergence Score**: Degree of disagreement across personas (0-100%)
4. **Completion Rate**: Successful responses / total personas
5. **Overall Quality Gate**: Pass if avg consistency >70% AND completion >80%

### Rationale
- Builds on Phase 1 QualityMetrics (reuse, don't replace)
- Theme confidence helps assess aggregation reliability
- Divergence score indicates when artificial consensus shouldn't be forced
- Completion rate shows panel execution health

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Only individual metrics | Misses panel-level patterns |
| Statistical variance analysis | More complex; requires larger panels |
| External quality model | Adds dependencies; harder to tune |

### Quality Gates
- Average consistency < 70%: Warning - panel results may not reflect personas
- Completion rate < 80%: Warning - missing perspectives may bias results
- Divergence > 80%: Note - high disagreement, individual responses may be more useful than aggregation

### Implementation Notes
- Extend QualityMetrics class or create PanelQualityMetrics
- Calculate after aggregation completes
- Include in report and JSON export

---

## 5. Report Generation Format

### Decision
**Generate Markdown reports using Jinja2 templates with optional Rich terminal output.**

Report structure:
1. **Executive Summary**: Key findings in 2-3 sentences
2. **Methodology**: Panel composition, question asked, session metadata
3. **Aggregated Findings**: Themes, sentiment distribution, consensus/divergence
4. **Individual Responses**: Per-persona summaries with key quotes
5. **Quality Assessment**: Panel metrics, warnings, limitations disclaimer

### Rationale
- Markdown is universal: readable in GitHub, IDEs, converts to HTML/PDF
- Jinja2 already in tech stack (Phase 0)
- Template-based allows customization
- Rich output provides immediate terminal feedback

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| PDF generation | Adds dependencies (WeasyPrint, etc.); overkill for MVP |
| HTML only | Less portable; requires browser |
| Plain text | Poor formatting; hard to scan |
| JSON only | Not human-readable for stakeholders |

### Template Variables
- `panel`: Panel definition with persona list
- `question`: Research question
- `responses`: List of individual SessionResponses
- `aggregation`: AggregatedResults object
- `quality`: PanelQualityMetrics
- `metadata`: Timestamps, versions, limitations

### Implementation Notes
- ReportGenerator service class
- Template at src/templates/panel_report.j2
- CLI option: --report <path.md>
- Include synthetic data disclaimer per Constitution Principle III

---

## 6. Pre-Built Panel Composition

### Decision
**Create 4 pre-built panels using the existing 5 personas, with general-population requiring additional personas to be created.**

| Panel | Required Size | Composition Strategy |
|-------|---------------|---------------------|
| tech-adopters | 5 | All 5 existing personas (full adoption spectrum) |
| skeptics-critics | 5 | skeptical-late-adopter, privacy-conscious-user + 3 new skeptic variants |
| power-users | 5 | power-user + 4 new expert/enthusiast personas |
| general-population | 10 | Mix of all types representing demographic diversity |

### Rationale
- Spec requires 4 pre-built panels with specific sizes (FR-003)
- Existing 5 personas cover tech-adopters well
- Other panels need new personas to meet composition requirements
- New personas should complement existing coverage

### New Personas Needed (minimum)
- 3 skeptic variants for skeptics-critics
- 4 power-user variants for power-users
- 5 additional for general-population (overlapping with above is acceptable)

### Implementation Notes
- Create new personas before panel definitions
- Each new persona needs full Big Five, Schwartz values, anti-sycophancy calibration
- New personas can be in scope for Phase 2 implementation or deferred to task breakdown

---

## 7. Custom Panel Persistence

### Decision
**Save custom panels as YAML files in `panels/custom/` with user-specified names.**

Custom panel workflow:
1. User runs `research panel create --name="my-panel" --personas="id1,id2,id3"`
2. System validates all persona IDs exist
3. System saves panel definition to `panels/custom/my-panel.yaml`
4. Panel is immediately available for research

### Rationale
- Consistent with pre-built panel format
- No database required
- User can hand-edit custom panels
- Version controllable if user chooses

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| SQLite storage | Over-engineering; file-based simpler |
| JSON format | Inconsistent with pre-built panels |
| In-memory only | Panels lost between sessions |

### Implementation Notes
- Validate persona IDs before saving
- Prevent overwriting pre-built panels
- CLI commands: create, list, show, delete (for custom)

---

## 8. Progress Display Strategy

### Decision
**Use Rich library progress bars and live updates for panel execution progress.**

Display shows:
- Overall progress bar (personas completed / total)
- Per-persona status (pending/running/completed/failed)
- Elapsed time and estimated remaining
- Live updates as responses arrive

### Rationale
- Rich is already in tech stack (Phase 1)
- Provides clear visibility into long-running operations
- Matches user expectations from modern CLI tools
- Progress is especially important for panels (vs instant single-session)

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Print statements | No progress indication during execution |
| Spinner only | No granular progress info |
| Quiet mode only | Poor user experience for interactive use |

### Implementation Notes
- Rich Progress with multiple tasks
- Callback from PanelExecutor on persona completion
- Option: --quiet flag for non-interactive use

---

## Summary of Technical Stack Additions

| Component | Technology | Justification |
|-----------|------------|---------------|
| Parallel Execution | asyncio + Task tool | Native Python concurrency |
| Panel Storage | YAML files | Consistent with persona storage |
| Response Aggregation | LLM via Task tool | No external NLP dependencies |
| Report Generation | Jinja2 + Markdown | Existing stack, universal format |
| Progress Display | Rich Progress | Already in stack, great UX |
| Panel Validation | Pydantic | Consistent with persona validation |

---

**Research Complete**: All technical decisions documented. Proceed to Phase 1 design artifacts.
