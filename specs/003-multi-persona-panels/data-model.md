# Data Model: Multi-Persona Panels

**Feature**: 003-multi-persona-panels
**Date**: 2026-01-25

## Overview

This document defines the data models for multi-persona panel research sessions. These models extend the Phase 1 session models to support panel management, parallel execution, response aggregation, and report generation.

---

## Entity Relationship Diagram

```
┌─────────────────────┐
│   ResearchPanel     │
│                     │
│ - id                │
│ - name              │
│ - description       │
│ - purpose           │
│ - persona_ids       │
│ - is_custom         │
│ - created_at        │
└──────────┬──────────┘
           │
           │ 1:N (used by)
           ▼
┌─────────────────────┐     ┌──────────────────────┐
│   PanelSession      │────▶│  ResearchQuestion    │
│                     │     │     (Phase 1)        │
│ - id                │     └──────────────────────┘
│ - panel_id          │
│ - question          │
│ - status            │     ┌──────────────────────┐
│ - started_at        │────▶│  ResearchSession[]   │
│ - completed_at      │     │     (Phase 1)        │
│ - individual_sessions│     └──────────────────────┘
│ - aggregation       │
│ - quality           │
│ - metadata          │
└──────────┬──────────┘
           │
           │ 1:1
           ▼
┌─────────────────────┐     ┌──────────────────────┐
│  AggregatedResults  │────▶│      Theme[]         │
│                     │     └──────────────────────┘
│ - themes            │
│ - sentiment_dist    │
│ - consensus_points  │
│ - divergence_points │
│ - executive_summary │
└─────────────────────┘

┌─────────────────────┐
│ PanelQualityMetrics │
│                     │
│ - avg_consistency   │
│ - completion_rate   │
│ - theme_confidence  │
│ - divergence_score  │
│ - passed_gates      │
│ - warnings          │
└─────────────────────┘
```

---

## Model Definitions

### ResearchPanel

Defines a collection of personas for panel research.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique panel identifier (slug format) |
| `name` | string | Yes | Human-readable panel name |
| `description` | string | Yes | Brief description of panel purpose |
| `purpose` | string | No | Detailed use case description |
| `persona_ids` | list[string] | Yes | IDs of personas in this panel (2-50) |
| `is_custom` | bool | Yes | True if user-created, False if pre-built |
| `created_at` | datetime | Yes | UTC timestamp of creation |

**Validation Rules**:
- `id` must be unique across pre-built and custom panels
- `id` must be slug format (lowercase, hyphens, no spaces)
- `persona_ids` must have 2-50 unique, valid persona IDs
- Pre-built panel IDs cannot be overwritten by custom panels

### PanelSessionStatus (Enum)

Tracks the state of a panel research session.

| Value | Description |
|-------|-------------|
| `PENDING` | Session created but not started |
| `EXECUTING` | Personas being queried in parallel |
| `AGGREGATING` | Responses collected, aggregating |
| `COMPLETED` | All processing finished |
| `PARTIAL` | Completed with some failures |
| `FAILED` | Critical failure, no results |

### PanelSession

Root entity representing a panel research interaction.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique session identifier (UUID) |
| `panel_id` | string | Yes | ID of panel used |
| `panel_name` | string | Yes | Display name of panel |
| `question` | ResearchQuestion | Yes | The question asked |
| `individual_sessions` | list[ResearchSession] | Yes | Phase 1 sessions per persona |
| `aggregation` | AggregatedResults | No | Aggregated findings (null until complete) |
| `quality` | PanelQualityMetrics | No | Panel-level metrics (null until computed) |
| `status` | PanelSessionStatus | Yes | Current session state |
| `started_at` | datetime | Yes | UTC timestamp of start |
| `completed_at` | datetime | No | UTC timestamp of completion |
| `execution_time_ms` | int | No | Total execution time |
| `metadata` | dict | No | Additional context |

**Metadata Fields**:
```json
{
  "platform_version": "0.3.0",
  "panel_version": "1.0.0",
  "parallel_execution": true,
  "persona_count": 5,
  "success_count": 5,
  "failure_count": 0,
  "estimated_sequential_time_ms": 75000,
  "speedup_factor": 3.2,
  "limitations_acknowledged": true
}
```

### Theme

A recurring topic identified across multiple responses.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Theme title (3-7 words) |
| `description` | string | Yes | Theme summary (1-2 sentences) |
| `frequency` | int | Yes | Number of personas mentioning theme |
| `percentage` | float | Yes | Frequency as percentage of panel |
| `supporting_quotes` | list[QuoteReference] | Yes | Quotes supporting this theme |
| `sentiment_tendency` | Sentiment | No | Common sentiment for this theme |

### QuoteReference

A quote from a specific persona response.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `persona_id` | string | Yes | Persona who said this |
| `persona_name` | string | Yes | Display name |
| `quote` | string | Yes | The quoted text |

### SentimentDistribution

Breakdown of sentiment across panel responses.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `positive` | float | Yes | Percentage positive (0-100) |
| `negative` | float | Yes | Percentage negative (0-100) |
| `mixed` | float | Yes | Percentage mixed (0-100) |
| `neutral` | float | Yes | Percentage neutral (0-100) |
| `dominant` | Sentiment | Yes | Most common sentiment |

### ConsensusPoint

A point where significant agreement exists.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `statement` | string | Yes | What personas agree on |
| `agreement_rate` | float | Yes | Percentage agreeing (>60%) |
| `supporting_personas` | list[string] | Yes | Persona IDs who agree |
| `key_quotes` | list[QuoteReference] | No | Representative quotes |

### DivergencePoint

A point of significant disagreement.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | Yes | The topic of disagreement |
| `positions` | list[Position] | Yes | Different viewpoints |

### Position

A viewpoint on a divergent topic.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stance` | string | Yes | The position (e.g., "Support", "Oppose") |
| `persona_ids` | list[string] | Yes | Personas holding this position |
| `rationale` | string | Yes | Why they hold this view |

### AggregatedResults

Synthesized findings from panel responses.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `themes` | list[Theme] | Yes | Top 3-5 recurring themes |
| `sentiment_distribution` | SentimentDistribution | Yes | Sentiment breakdown |
| `consensus_points` | list[ConsensusPoint] | Yes | Points of agreement (may be empty) |
| `divergence_points` | list[DivergencePoint] | Yes | Points of disagreement (may be empty) |
| `executive_summary` | string | Yes | 2-3 sentence synthesis |
| `aggregation_confidence` | float | Yes | 0-100% confidence in aggregation |

### PanelQualityMetrics

Panel-level quality measurements.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `avg_consistency_score` | float | Yes | Mean consistency across personas |
| `completion_rate` | float | Yes | Successful/total personas (0-100%) |
| `theme_confidence` | float | Yes | How well themes are supported (0-100%) |
| `divergence_score` | float | Yes | Degree of disagreement (0-100%) |
| `passed_gates` | bool | Yes | True if all quality gates passed |
| `warnings` | list[string] | Yes | Quality warnings (may be empty) |
| `individual_metrics` | list[QualityMetrics] | Yes | Phase 1 metrics per persona |

**Quality Gates**:
- `avg_consistency_score` >= 70%: PASS
- `completion_rate` >= 80%: PASS
- Both gates pass: `passed_gates` = True

---

## State Transitions

### PanelSession States

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
            ┌────│   EXECUTING     │────┐
            │    │                 │    │
            │    └────────┬────────┘    │
            │             │             │
            │   all_done()│             │ critical_error()
            │             │             │
            │             ▼             │
            │    ┌─────────────────┐    │
            │    │                 │    │
            │    │  AGGREGATING    │    │
            │    │                 │    │
            │    └────────┬────────┘    │
            │             │             │
            │             ├─────────────┼─────────┐
            │             │             │         │
            │   success() │    partial()│         │ aggregate_fail()
            │             │             │         │
            ▼             ▼             ▼         ▼
   ┌────────────┐ ┌─────────────┐ ┌────────────┐
   │            │ │             │ │            │
   │   FAILED   │ │  COMPLETED  │ │  PARTIAL   │
   │            │ │             │ │            │
   └────────────┘ └─────────────┘ └────────────┘
```

---

## JSON Export Schema

Complete panel session export format:

```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "COMPLETED",
    "started_at": "2026-01-25T11:00:00Z",
    "completed_at": "2026-01-25T11:00:45Z",
    "execution_time_ms": 45000
  },
  "panel": {
    "id": "tech-adopters",
    "name": "Technology Adopters Panel",
    "persona_count": 5,
    "is_custom": false
  },
  "question": {
    "text": "What do you think of this AI assistant feature?",
    "type": "OPEN_ENDED"
  },
  "individual_responses": [
    {
      "persona_id": "tech-early-adopter",
      "persona_name": "Alex Chen",
      "status": "COMPLETED",
      "parsed": {
        "sentiment": "POSITIVE",
        "overall_impression": "Excited to try it",
        "concerns": ["Learning curve"],
        "suggestions": ["Add tutorials"]
      },
      "quality": {
        "consistency_score": 92.0,
        "passed_gates": true
      }
    }
  ],
  "aggregation": {
    "executive_summary": "Panel shows generally positive reception with concerns about complexity.",
    "themes": [
      {
        "name": "Enthusiasm for Innovation",
        "frequency": 3,
        "percentage": 60.0,
        "supporting_quotes": [
          {"persona_id": "tech-early-adopter", "quote": "This is exactly what I've been waiting for"}
        ]
      }
    ],
    "sentiment_distribution": {
      "positive": 60.0,
      "negative": 20.0,
      "mixed": 20.0,
      "neutral": 0.0,
      "dominant": "POSITIVE"
    },
    "consensus_points": [
      {
        "statement": "Feature has potential value",
        "agreement_rate": 80.0,
        "supporting_personas": ["tech-early-adopter", "power-user", "busy-professional", "privacy-conscious-user"]
      }
    ],
    "divergence_points": [
      {
        "topic": "Data privacy implications",
        "positions": [
          {"stance": "Concerned", "persona_ids": ["privacy-conscious-user", "skeptical-late-adopter"], "rationale": "Want to understand data handling"},
          {"stance": "Not concerned", "persona_ids": ["tech-early-adopter", "power-user"], "rationale": "Trust the platform"}
        ]
      }
    ]
  },
  "quality": {
    "avg_consistency_score": 85.0,
    "completion_rate": 100.0,
    "theme_confidence": 80.0,
    "divergence_score": 40.0,
    "passed_gates": true,
    "warnings": []
  },
  "metadata": {
    "platform_version": "0.3.0",
    "parallel_execution": true,
    "speedup_factor": 3.2,
    "generated_by": "synthetic-user-research",
    "limitations": "This is synthetic research data. Validate critical findings with real users."
  }
}
```

---

## Relationship to Phase 1 Models

| Phase 1 Model | Phase 2 Usage |
|---------------|---------------|
| `ResearchSession` | Individual persona sessions within PanelSession |
| `SessionResponse` | Individual responses aggregated into AggregatedResults |
| `ParsedResponse` | Source data for theme extraction and sentiment distribution |
| `QualityMetrics` | Individual metrics aggregated into PanelQualityMetrics |
| `ResearchQuestion` | Shared across all personas in panel |
| `Sentiment` | Reused for theme sentiment and distribution |

Phase 2 models **extend but do not modify** Phase 1 models. PanelSession contains a list of ResearchSessions, enabling full reuse of Phase 1 execution and parsing logic.
