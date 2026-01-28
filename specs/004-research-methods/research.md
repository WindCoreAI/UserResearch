# Research Findings: Research Methods

**Feature**: 004-research-methods
**Date**: 2026-01-26
**Status**: Complete

## Overview

This document consolidates research findings for implementing Survey, Interview, and Focus Group research methods in the Synthetic User Research Platform. All technical decisions are grounded in existing codebase patterns and best practices.

---

## 1. Survey Engine Design

### Decision: Sequential Question Execution per Persona

**Rationale**: Execute survey questions sequentially within a single persona session to maintain conversational context and reduce API calls.

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| One API call per question | Maximum isolation | 10x API overhead; breaks persona context | Performance impact unacceptable for SC-001 (5 min for 10 questions) |
| Batch all questions in single prompt | Minimum API calls | Risk of truncated responses; harder to parse | Parsing complexity; unreliable for rating validation |
| **Sequential within session** | Balance of context + parsability | Requires careful prompt design | **Selected**: Best trade-off |

**Implementation Pattern**:
```python
class SurveyEngine:
    def execute_survey(self, survey: Survey, persona_id: str) -> SurveyResult:
        """Execute all questions in sequence, maintaining conversation context."""
        session = self.session_runner.create_session(persona_id)
        responses = []
        for question in survey.questions:
            prompt = self.build_question_prompt(question, responses)
            response = self.session_runner.execute(session, prompt)
            parsed = self.parse_response(question.type, response)
            responses.append(parsed)
        return SurveyResult(responses=responses)
```

### Decision: Rating Validation with Re-prompt Strategy

**Rationale**: When a persona provides an out-of-range rating, re-prompt once with explicit bounds; if still invalid, use closest valid value with warning.

**Alternatives Considered**:
- Silent clamping (loses data integrity signal)
- Hard failure (disrupts research flow)
- **Re-prompt + fallback** (selected): Maintains flow while maximizing data quality

### Decision: Statistics Module for Aggregation

**Rationale**: Use Python's built-in `statistics` module for mean, median, stdev calculations. No external dependencies needed.

**Implementation**:
```python
from statistics import mean, median, stdev, StatisticsError

class SurveyAggregator:
    def aggregate_ratings(self, ratings: list[int]) -> RatingStatistics:
        return RatingStatistics(
            mean=mean(ratings),
            median=median(ratings),
            stdev=stdev(ratings) if len(ratings) > 1 else 0.0,
            distribution=self._calculate_distribution(ratings)
        )
```

---

## 2. Interview Engine Design

### Decision: Section-Based Conversation Flow

**Rationale**: Interviews execute as a sequence of sections, each containing ordered questions. The persona maintains context across the entire interview.

**Pattern from Existing Code**: Mirrors `SessionRunner.create_session()` pattern but extends conversation across multiple exchanges.

**Implementation Pattern**:
```python
class InterviewEngine:
    def conduct_interview(self, guide: InterviewGuide, persona_id: str) -> InterviewTranscript:
        transcript = InterviewTranscript(guide_id=guide.id, persona_id=persona_id)
        for section in guide.sections:
            section_transcript = self._execute_section(section, transcript.context)
            transcript.sections.append(section_transcript)
        return transcript
```

### Decision: Follow-up Question Generation Strategy

**Rationale**: Generate contextual follow-ups using the same LLM infrastructure, with a dedicated prompt template that includes the previous response.

**Constraints**:
- Maximum 3 follow-up levels (FR-013)
- Follow-ups only when permitted by guide configuration
- 80% relevance target (SC-003)

**Follow-up Trigger Logic**:
```python
def should_probe(self, response: str, config: ProbeConfig) -> bool:
    """Determine if probing question should be asked."""
    if len(response) < config.min_length_chars:  # Default: 50
        return True
    if config.always_probe_keywords and any(kw in response.lower() for kw in config.always_probe_keywords):
        return True
    return False
```

### Decision: Transcript Structure

**Rationale**: Store transcripts as nested structure mirroring the interview guide, with timestamps for each exchange.

**Structure**:
```yaml
transcript:
  guide_id: "onboarding-interview"
  persona_id: "tech-early-adopter"
  started_at: "2026-01-26T10:00:00Z"
  completed_at: "2026-01-26T10:15:00Z"
  sections:
    - section_name: "Background"
      exchanges:
        - question: "Tell me about similar products you've tried"
          response: "..."
          timestamp: "2026-01-26T10:01:00Z"
          follow_ups:
            - question: "What made you choose those products?"
              response: "..."
              timestamp: "2026-01-26T10:02:30Z"
```

---

## 3. Focus Group Engine Design

### Decision: Turn-Based Simulation (Not Real-Time)

**Rationale**: Simulate focus group discussions using turn-based approach where each persona responds sequentially, with context of previous statements visible.

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| True parallel (all respond simultaneously) | Realistic | Personas can't react to each other | Defeats purpose of group dynamics |
| Real-time streaming | Most realistic | Extreme complexity; token race conditions | Over-engineered for MVP |
| **Turn-based sequential** | Personas can reference others | Less spontaneous | **Selected**: Captures key dynamics without complexity |

**Implementation Pattern**:
```python
class FocusGroupEngine:
    def run_discussion(self, group: FocusGroup, topic: str) -> DiscussionLog:
        log = DiscussionLog(group_id=group.id, topic=topic)
        discussion_context = []

        for round_num in range(group.max_rounds):
            for persona_id in group.persona_order:
                prompt = self._build_turn_prompt(persona_id, topic, discussion_context)
                response = self._execute_turn(persona_id, prompt)
                turn = DiscussionTurn(
                    persona_id=persona_id,
                    statement=response,
                    references=self._extract_references(response, discussion_context)
                )
                log.turns.append(turn)
                discussion_context.append(turn)

        return log
```

### Decision: Opinion Shift Detection

**Rationale**: Track opinion evolution by comparing each persona's sentiment/position on key topics across their turns.

**Implementation**:
```python
class OpinionTracker:
    def detect_shifts(self, log: DiscussionLog) -> list[OpinionShift]:
        shifts = []
        for persona_id in log.unique_personas:
            persona_turns = [t for t in log.turns if t.persona_id == persona_id]
            for i in range(1, len(persona_turns)):
                if self._positions_differ(persona_turns[i-1], persona_turns[i]):
                    shifts.append(OpinionShift(
                        persona_id=persona_id,
                        from_turn=i-1,
                        to_turn=i,
                        topic=self._extract_topic(persona_turns[i])
                    ))
        return shifts
```

### Decision: Group Size Limits (4-6 personas)

**Rationale**: Per spec assumption, limit to 4-6 personas for readable transcripts and manageable computation.

**Validation**:
```python
class FocusGroup(BaseModel):
    persona_ids: list[str] = Field(..., min_length=4, max_length=6)
```

---

## 4. Protocol Management Design

### Decision: YAML-Based Protocol Definitions with Type Discrimination

**Rationale**: Store protocols as YAML files with a `type` field that determines the schema variant (survey, interview, focus-group). Consistent with existing persona/panel patterns.

**Protocol Directory Structure**:
```
protocols/
├── surveys/
│   ├── feature-concept-test.yaml
│   └── nps-survey.yaml
├── interviews/
│   ├── onboarding-experience.yaml
│   └── pain-point-exploration.yaml
└── focus-groups/
    ├── pricing-feedback.yaml
    └── feature-prioritization.yaml
```

**Protocol Base Schema**:
```yaml
protocol:
  id: "feature-concept-test"      # Required: kebab-case identifier
  version: "1.0.0"                # Required: semver
  type: "survey"                  # Required: survey|interview|focus-group
  name: "Feature Concept Test"    # Required: display name
  description: "..."              # Optional
  created_at: "2026-01-26"        # Auto-generated
  # Type-specific fields follow...
```

### Decision: Protocol Versioning via Copy-on-Write

**Rationale**: When a protocol is modified, create a new file with incremented version rather than modifying in place. Original remains unchanged for reproducibility.

**Alternatives Considered**:
- Git-based versioning (adds git dependency)
- Database versioning (requires new storage layer)
- **File-based copy-on-write** (selected): Simple, consistent with existing patterns

**Implementation**:
```python
class ProtocolLoader:
    def save_protocol(self, protocol: ResearchProtocol) -> Path:
        if self.protocol_exists(protocol.id):
            existing = self.load_protocol(protocol.id)
            if existing.version != protocol.version:
                # Save as new version
                return self._save_versioned(protocol)
            else:
                raise ProtocolVersionConflictError(...)
        return self._save_new(protocol)
```

---

## 5. Response Parsing Extensions

### Decision: Method-Specific Parsers with Common Interface

**Rationale**: Extend existing `ResponseParser` with method-specific parsing logic while maintaining common interface.

**Pattern**:
```python
class ResponseParser:
    def parse(self, raw: str, method: ResearchMethodType, context: dict) -> ParsedResponse:
        if method == ResearchMethodType.SURVEY:
            return self._parse_survey_response(raw, context)
        elif method == ResearchMethodType.INTERVIEW:
            return self._parse_interview_response(raw, context)
        elif method == ResearchMethodType.FOCUS_GROUP:
            return self._parse_focus_group_response(raw, context)
        else:
            return self._parse_generic(raw)  # Fallback to existing logic
```

### Decision: Survey Rating Extraction

**Rationale**: Use regex pattern matching for rating extraction with explicit bounds validation.

**Pattern**:
```python
def _extract_rating(self, response: str, scale_min: int, scale_max: int) -> int | None:
    # Look for numeric patterns like "7", "7/10", "Rating: 7"
    patterns = [
        r"(?:rating[:\s]*)?(\d+)(?:/\d+)?",
        r"(?:score[:\s]*)(\d+)",
        r"^(\d+)$"
    ]
    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            if scale_min <= value <= scale_max:
                return value
    return None
```

---

## 6. CLI Design Patterns

### Decision: Command Group Structure

**Rationale**: Mirror existing `panel` command group pattern. Each method gets its own command group with `run` and `create` subcommands.

**CLI Structure**:
```
research-cli
├── persona (existing)
├── research
│   ├── single (existing)
│   ├── panel (existing)
│   ├── survey
│   │   ├── run --protocol <id> --persona <id> [--panel <id>] [--output <file>] [--report <file>]
│   │   └── create [--from-yaml <file>] [--interactive]
│   ├── interview
│   │   ├── run --guide <id> --persona <id> [--output <file>] [--report <file>]
│   │   └── create [--from-yaml <file>] [--interactive]
│   ├── focus-group
│   │   ├── run --config <id> --topic <text> [--output <file>] [--report <file>]
│   │   └── create [--from-yaml <file>] [--interactive]
│   └── protocol
│       ├── list [--type <survey|interview|focus-group>]
│       ├── show <protocol-id>
│       └── delete <protocol-id> [--force]
```

### Decision: Rich Progress Display

**Rationale**: Reuse existing Rich progress patterns from panel execution for survey and focus group progress.

**Pattern** (from existing `panel_commands.py`):
```python
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    console=console
) as progress:
    task = progress.add_task(f"Running survey...", total=len(survey.questions))
    for response in engine.execute_streaming(survey, persona_id):
        progress.update(task, advance=1)
```

---

## 7. Template Design

### Decision: Separate Prompt Templates per Method

**Rationale**: Each method has distinct prompt requirements. Separate templates improve maintainability and allow method-specific optimization.

**Templates to Create**:

| Template | Purpose | Key Sections |
|----------|---------|--------------|
| `survey_prompt.j2` | Single survey question execution | Persona context, question text, response format, scale constraints |
| `interview_prompt.j2` | Interview section execution | Persona context, section context, question, follow-up rules |
| `focus_group_prompt.j2` | Focus group turn execution | Persona context, topic, discussion history, turn instructions |
| `survey_report.j2` | Survey results report | Questions, per-persona responses, aggregate statistics |
| `interview_report.j2` | Interview transcript report | Sections, exchanges, themes identified |
| `focus_group_report.j2` | Discussion report | Topic, turns, consensus/divergence, opinion shifts |

### Decision: Report Template Structure

**Rationale**: Follow existing `panel_report.j2` pattern with method-specific sections.

**Common Report Sections**:
1. Executive Summary
2. Methodology (method type, protocol version, timing)
3. Participants (personas involved)
4. Findings (method-specific)
5. Quality Metrics
6. Limitations Disclaimer

---

## 8. Quality Metrics Integration

### Decision: Reuse Existing Quality Infrastructure

**Rationale**: The existing `QualityMetricsCalculator` already provides trait consistency and sycophancy detection. Apply these to all research methods.

**Per-Method Quality Extensions**:

| Method | Additional Quality Checks |
|--------|--------------------------|
| Survey | Rating distribution variance; response completeness |
| Interview | Follow-up relevance scoring; probe effectiveness |
| Focus Group | Interaction frequency; opinion diversity score |

**Implementation**:
```python
class MethodQualityMetrics:
    def calculate(self, method: ResearchMethodType, result: Any) -> QualityMetrics:
        base_metrics = self.quality_calculator.calculate(result.parsed_responses)

        if method == ResearchMethodType.SURVEY:
            base_metrics.custom["rating_variance"] = self._calculate_rating_variance(result)
        elif method == ResearchMethodType.INTERVIEW:
            base_metrics.custom["followup_relevance"] = self._calculate_followup_relevance(result)
        elif method == ResearchMethodType.FOCUS_GROUP:
            base_metrics.custom["interaction_score"] = self._calculate_interaction_score(result)

        return base_metrics
```

---

## 9. Testing Strategy

### Decision: Test Pyramid with Method-Specific Coverage

**Rationale**: Follow existing test patterns with unit tests for models/services, integration tests for CLI, contract tests for schemas.

**Test Distribution Target**:
- Unit tests: 70% (models, engines, parsers, aggregators)
- Integration tests: 20% (CLI workflows, end-to-end scenarios)
- Contract tests: 10% (protocol schema validation)

**Key Test Scenarios per Method**:

| Method | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| Survey | Question type handling, rating validation, aggregation math | Full survey execution, panel survey, export |
| Interview | Section flow, follow-up generation, transcript building | Full interview execution, report generation |
| Focus Group | Turn-taking logic, reference detection, opinion tracking | Full discussion simulation, interaction analysis |
| Protocol | Schema validation, versioning, CRUD operations | Protocol lifecycle via CLI |

---

## 10. Risk Mitigation

### Risk: Focus Group Complexity

**Mitigation**: Implement Focus Group as P3 (lowest priority). Survey and Interview can ship independently if Focus Group requires more iteration.

### Risk: Follow-up Relevance Below Target

**Mitigation**: Implement relevance scoring early in Interview engine development. If <80% threshold not met, tune prompt templates before proceeding.

### Risk: Survey Performance (SC-001)

**Mitigation**: Profile early with 10-question surveys. If sequential execution too slow, consider batching 2-3 questions per API call.

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Survey Execution | Sequential per persona | Balance context + parsability |
| Rating Validation | Re-prompt + fallback | Maximizes data quality |
| Interview Flow | Section-based | Natural conversation structure |
| Follow-ups | LLM-generated with depth limit | Maintains relevance |
| Focus Group | Turn-based simulation | Captures dynamics without complexity |
| Protocols | YAML with copy-on-write versioning | Simple, reproducible |
| CLI | Command groups per method | Consistent with existing patterns |
| Quality | Extend existing infrastructure | Maintains platform consistency |
