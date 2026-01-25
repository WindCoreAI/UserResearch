# Data Model: Single Persona MVP

**Feature**: 002-single-persona-mvp
**Date**: 2026-01-25

## Overview

This document defines the data models for single persona research sessions. These models extend the Phase 0 Persona model to support research execution, response parsing, and quality metrics.

---

## Entity Relationship Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ ResearchSession │────▶│ ResearchQuestion │────▶│  QuestionType   │
│                 │     │                  │     │    (enum)       │
│ - id            │     │ - text           │     │                 │
│ - persona_id    │     │ - type           │     │ - OPEN_ENDED    │
│ - started_at    │     │ - options        │     │ - RATING        │
│ - completed_at  │     │ - scale          │     │ - MULTIPLE_CHOICE│
│ - status        │     └──────────────────┘     └─────────────────┘
└────────┬────────┘
         │
         │ 1:1
         ▼
┌─────────────────┐
│ SessionResponse │
│                 │
│ - raw_text      │
│ - parsed        │──────▶ ParsedResponse
│ - quality       │──────▶ QualityMetrics
│ - response_time │
└─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ ParsedResponse  │     │  QualityMetrics │
│                 │     │                 │
│ - sentiment     │     │ - consistency   │
│ - concerns      │     │ - sycophancy    │
│ - suggestions   │     │ - warnings      │
│ - key_quotes    │     │ - passed_gates  │
│ - impression    │     └─────────────────┘
└─────────────────┘
```

---

## Model Definitions

### QuestionType (Enum)

Defines the type of research question being asked.

| Value | Description | Response Format |
|-------|-------------|-----------------|
| `OPEN_ENDED` | Free-form question expecting narrative response | Unstructured text |
| `RATING` | Question expecting numeric rating with justification | Number (1-10) + explanation |
| `MULTIPLE_CHOICE` | Question with predefined options | Selected option + explanation |

### ResearchQuestion

Represents the question posed to a persona.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The question text (max 2000 chars) |
| `type` | QuestionType | Yes | Type of question (default: OPEN_ENDED) |
| `options` | list[string] | No | Options for MULTIPLE_CHOICE (2-10 items) |
| `scale_min` | int | No | Minimum for RATING (default: 1) |
| `scale_max` | int | No | Maximum for RATING (default: 10) |

**Validation Rules**:
- `text` must be non-empty and ≤2000 characters
- `options` required when `type` is MULTIPLE_CHOICE
- `options` must have 2-10 items when provided
- `scale_min` < `scale_max` when both provided

### Sentiment (Enum)

Classifies the overall sentiment of a response.

| Value | Description |
|-------|-------------|
| `POSITIVE` | Predominantly favorable response |
| `NEGATIVE` | Predominantly unfavorable response |
| `MIXED` | Contains both positive and negative elements |
| `NEUTRAL` | Factual, objective, neither positive nor negative |

### ParsedResponse

Structured extraction from the raw persona response.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sentiment` | Sentiment | Yes | Overall sentiment classification |
| `overall_impression` | string | Yes | Brief summary (1-2 sentences) |
| `concerns` | list[string] | Yes | Extracted concerns (may be empty) |
| `suggestions` | list[string] | Yes | Extracted suggestions (may be empty) |
| `key_quotes` | list[string] | No | Notable direct quotes from response |
| `rating` | int | No | Numeric rating (for RATING questions) |
| `selected_option` | string | No | Selected choice (for MULTIPLE_CHOICE) |

**Validation Rules**:
- `rating` must be within question's scale range when present
- `selected_option` must match one of the question's options when present

### QualityMetrics

Measurements of response quality and persona consistency.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `consistency_score` | float | Yes | 0-100%, how well response matches persona |
| `sycophancy_indicators` | dict | Yes | Flags for excessive positivity |
| `warnings` | list[string] | Yes | Quality warnings (may be empty) |
| `passed_gates` | bool | Yes | True if all quality gates passed |
| `matched_traits` | list[string] | No | Persona traits detected in response |
| `missing_traits` | list[string] | No | Expected traits not detected |

**Sycophancy Indicators**:
```json
{
  "excessive_praise": false,
  "no_concerns_raised": false,
  "unrealistic_enthusiasm": false,
  "positive_negative_ratio": 2.5
}
```

**Quality Gates**:
- `consistency_score` ≥ 70% (warning if below)
- `sycophancy.positive_negative_ratio` ≤ 4.0 (warning if above)

### SessionStatus (Enum)

Tracks the state of a research session.

| Value | Description |
|-------|-------------|
| `PENDING` | Session created but not started |
| `RUNNING` | Subagent executing |
| `COMPLETED` | Response received and parsed |
| `FAILED` | Error during execution |
| `TIMEOUT` | Subagent did not respond in time |

### SessionResponse

The complete response from a persona subagent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `raw_text` | string | Yes | Unprocessed response from subagent |
| `parsed` | ParsedResponse | No | Structured extraction (null if parse failed) |
| `quality` | QualityMetrics | No | Quality measurements (null if not computed) |
| `response_time_ms` | int | Yes | Time from request to response (milliseconds) |
| `parse_errors` | list[string] | No | Errors encountered during parsing |

### ResearchSession

Root entity representing a complete research interaction.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique session identifier (UUID) |
| `persona_id` | string | Yes | ID of persona used |
| `persona_name` | string | Yes | Display name of persona |
| `question` | ResearchQuestion | Yes | The question asked |
| `response` | SessionResponse | No | Response (null until completed) |
| `status` | SessionStatus | Yes | Current session state |
| `started_at` | datetime | Yes | UTC timestamp of session start |
| `completed_at` | datetime | No | UTC timestamp of completion |
| `metadata` | dict | No | Additional context (version, etc.) |

**Metadata Fields**:
```json
{
  "platform_version": "0.2.0",
  "persona_version": "1.0.0",
  "model_used": "sonnet",
  "limitations_acknowledged": true
}
```

---

## State Transitions

```
                 ┌─────────────────┐
                 │                 │
                 │     PENDING     │
                 │                 │
                 └────────┬────────┘
                          │ start()
                          ▼
                 ┌─────────────────┐
                 │                 │
            ┌────│     RUNNING     │────┐
            │    │                 │    │
            │    └────────┬────────┘    │
            │             │             │
    timeout │   complete()│             │ error()
            │             │             │
            ▼             ▼             ▼
   ┌────────────┐ ┌─────────────┐ ┌────────────┐
   │            │ │             │ │            │
   │  TIMEOUT   │ │  COMPLETED  │ │   FAILED   │
   │            │ │             │ │            │
   └────────────┘ └─────────────┘ └────────────┘
```

---

## JSON Export Schema

Complete session export format:

```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "COMPLETED",
    "started_at": "2026-01-25T10:30:00Z",
    "completed_at": "2026-01-25T10:30:15Z"
  },
  "persona": {
    "id": "tech-early-adopter",
    "name": "Alex Chen",
    "version": "1.0.0"
  },
  "question": {
    "text": "What do you think of this daily reflection feature?",
    "type": "OPEN_ENDED"
  },
  "response": {
    "raw_text": "As someone who's always looking for new productivity tools...",
    "parsed": {
      "sentiment": "MIXED",
      "overall_impression": "Interesting concept but needs refinement",
      "concerns": ["Privacy of reflection data", "Time commitment"],
      "suggestions": ["Add quick-entry mode", "Integrate with calendar"],
      "key_quotes": ["I'd want to control who sees my reflections"]
    },
    "quality": {
      "consistency_score": 87.5,
      "sycophancy_indicators": {
        "excessive_praise": false,
        "no_concerns_raised": false,
        "positive_negative_ratio": 1.5
      },
      "warnings": [],
      "passed_gates": true
    },
    "response_time_ms": 12450
  },
  "metadata": {
    "platform_version": "0.2.0",
    "generated_by": "synthetic-user-research",
    "limitations": "This is synthetic research data. Validate critical findings with real users."
  }
}
```

---

## Relationship to Phase 0 Models

| Phase 0 Model | Phase 1 Usage |
|---------------|---------------|
| `Persona` | Referenced by `persona_id` in ResearchSession |
| `BigFive` | Used by QualityMetrics for trait matching |
| `TechAdoptionCategory` | Used by QualityMetrics for consistency scoring |
| `SchwartzValue` | Used by QualityMetrics for value alignment |

Phase 1 models **do not modify** Phase 0 models. They reference them via ID and extract trait information for quality calculations.
