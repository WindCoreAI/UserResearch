# CLI Contracts: Research Methods

**Feature**: 004-research-methods
**Date**: 2026-01-26
**Status**: Complete

## Overview

This document defines the CLI contract specifications for Survey, Interview, Focus Group, and Protocol commands. All commands follow existing patterns from `panel_commands.py`.

---

## 1. Survey Commands

### `research survey run`

Execute a survey protocol against a persona or panel.

```
research-cli research survey run [OPTIONS]

Options:
  --protocol, -p TEXT    Survey protocol ID (required)
  --persona TEXT         Single persona ID (mutually exclusive with --panel)
  --panel TEXT           Panel ID for multi-persona survey
  --output, -o PATH      Export results to JSON file
  --report, -r PATH      Generate Markdown report
  --format [text|json]   Output format (default: text)
  --timeout INTEGER      Per-question timeout in seconds (default: 60)
  --verbose, -v          Show detailed progress
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (protocol not found, persona not found, execution failure)
  2  Warning (partial completion, quality gate warnings)

Examples:
  research-cli research survey run -p feature-concept-test --persona tech-early-adopter
  research-cli research survey run -p nps-survey --panel tech-adopters -o results.json
  research-cli research survey run -p feature-concept-test --panel general-population -r report.md
```

**Output Contract (JSON)**:
```json
{
  "survey_id": "feature-concept-test",
  "survey_version": "1.0.0",
  "method": "survey",
  "execution_type": "single|panel",
  "results": [
    {
      "persona_id": "tech-early-adopter",
      "responses": [
        {
          "question_id": "likelihood-to-use",
          "question_type": "rating",
          "raw_response": "I would rate this an 8 out of 10...",
          "rating_value": 8,
          "is_valid": true
        }
      ],
      "completion_rate": 1.0,
      "total_time_ms": 15000
    }
  ],
  "aggregation": {
    "rating_statistics": [...],
    "multiple_choice_statistics": [...],
    "open_ended_themes": [...]
  },
  "quality_metrics": {
    "avg_consistency_score": 0.85,
    "completion_rate": 1.0
  },
  "metadata": {
    "started_at": "2026-01-26T10:00:00Z",
    "completed_at": "2026-01-26T10:05:00Z",
    "total_time_ms": 300000
  }
}
```

### `research survey create`

Create a new survey protocol.

```
research-cli research survey create [OPTIONS]

Options:
  --from-yaml, -f PATH   Create from YAML file
  --interactive, -i      Interactive creation wizard
  --output, -o PATH      Output path for created protocol
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (validation failure, file write error)

Examples:
  research-cli research survey create -f my-survey.yaml
  research-cli research survey create -i
```

---

## 2. Interview Commands

### `research interview run`

Execute an interview guide with a persona.

```
research-cli research interview run [OPTIONS]

Options:
  --guide, -g TEXT       Interview guide ID (required)
  --persona, -p TEXT     Persona ID (required)
  --output, -o PATH      Export transcript to JSON file
  --report, -r PATH      Generate Markdown transcript report
  --format [text|json]   Output format (default: text)
  --timeout INTEGER      Per-section timeout in seconds (default: 180)
  --verbose, -v          Show detailed progress
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (guide not found, persona not found, execution failure)
  2  Warning (partial completion, quality gate warnings)

Examples:
  research-cli research interview run -g onboarding-experience -p tech-early-adopter
  research-cli research interview run -g pain-point-exploration -p skeptical-late-adopter -o transcript.json
  research-cli research interview run -g onboarding-experience -p power-user -r report.md
```

**Output Contract (JSON)**:
```json
{
  "guide_id": "onboarding-experience",
  "guide_version": "1.0.0",
  "method": "interview",
  "persona_id": "tech-early-adopter",
  "persona_name": "Alex Chen",
  "sections": [
    {
      "section_id": "background",
      "section_name": "Background",
      "exchanges": [
        {
          "question_id": "similar-products",
          "question_text": "Tell me about similar products you've tried",
          "response": "...",
          "timestamp": "2026-01-26T10:01:00Z",
          "response_length": 250,
          "followups": [
            {
              "question_text": "Can you describe what made those memorable?",
              "response": "...",
              "probe_used": "elaboration"
            }
          ]
        }
      ]
    }
  ],
  "analysis": {
    "identified_themes": [...],
    "key_quotes": [...],
    "followup_relevance_score": 0.85
  },
  "quality_metrics": {
    "consistency_score": 0.88,
    "total_exchanges": 12
  },
  "metadata": {
    "started_at": "2026-01-26T10:00:00Z",
    "completed_at": "2026-01-26T10:15:00Z",
    "total_time_ms": 900000
  }
}
```

### `research interview create`

Create a new interview guide.

```
research-cli research interview create [OPTIONS]

Options:
  --from-yaml, -f PATH   Create from YAML file
  --interactive, -i      Interactive creation wizard
  --output, -o PATH      Output path for created guide
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (validation failure, file write error)

Examples:
  research-cli research interview create -f my-interview.yaml
  research-cli research interview create -i
```

---

## 3. Focus Group Commands

### `research focus-group run`

Execute a focus group discussion.

```
research-cli research focus-group run [OPTIONS]

Options:
  --config, -c TEXT      Focus group config ID (required)
  --topic, -t TEXT       Discussion topic (overrides config default)
  --output, -o PATH      Export discussion log to JSON file
  --report, -r PATH      Generate Markdown discussion report
  --format [text|json]   Output format (default: text)
  --rounds INTEGER       Number of discussion rounds (default: from config)
  --timeout INTEGER      Per-turn timeout in seconds (default: 60)
  --verbose, -v          Show turn-by-turn progress
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (config not found, persona not found, execution failure)
  2  Warning (partial completion, quality gate warnings)

Examples:
  research-cli research focus-group run -c pricing-feedback -t "Initial reactions to proposed pricing"
  research-cli research focus-group run -c feature-prioritization --rounds 4 -o discussion.json
  research-cli research focus-group run -c pricing-feedback -r report.md
```

**Output Contract (JSON)**:
```json
{
  "group_id": "pricing-feedback",
  "group_version": "1.0.0",
  "method": "focus_group",
  "topic": "Initial reactions to proposed pricing",
  "participants": [
    {"persona_id": "tech-early-adopter", "persona_name": "Alex Chen"},
    {"persona_id": "skeptical-late-adopter", "persona_name": "Margaret Wilson"}
  ],
  "turns": [
    {
      "turn_index": 0,
      "round_number": 1,
      "persona_id": "tech-early-adopter",
      "persona_name": "Alex Chen",
      "statement": "...",
      "timestamp": "2026-01-26T10:01:00Z",
      "interaction_type": "new_point",
      "references": [],
      "sentiment": "positive"
    },
    {
      "turn_index": 1,
      "round_number": 1,
      "persona_id": "skeptical-late-adopter",
      "persona_name": "Margaret Wilson",
      "statement": "I disagree with Alex...",
      "timestamp": "2026-01-26T10:02:00Z",
      "interaction_type": "disagreement",
      "references": [
        {
          "referenced_persona_id": "tech-early-adopter",
          "referenced_turn_index": 0,
          "reference_type": "disagreement",
          "quote_fragment": "..."
        }
      ],
      "sentiment": "negative"
    }
  ],
  "analysis": {
    "consensus_points": [...],
    "divergence_points": [...],
    "opinion_shifts": [...],
    "interaction_summary": {
      "agreement": 3,
      "disagreement": 4,
      "building_on": 2,
      "new_point": 5
    }
  },
  "quality_metrics": {
    "avg_consistency_score": 0.82,
    "interaction_diversity_score": 0.75
  },
  "metadata": {
    "started_at": "2026-01-26T10:00:00Z",
    "completed_at": "2026-01-26T10:12:00Z",
    "total_time_ms": 720000,
    "total_rounds": 3,
    "total_turns": 12
  }
}
```

### `research focus-group create`

Create a new focus group configuration.

```
research-cli research focus-group create [OPTIONS]

Options:
  --from-yaml, -f PATH   Create from YAML file
  --interactive, -i      Interactive creation wizard
  --output, -o PATH      Output path for created config
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (validation failure, persona validation failure, file write error)

Examples:
  research-cli research focus-group create -f my-focus-group.yaml
  research-cli research focus-group create -i
```

---

## 4. Protocol Commands

### `research protocol list`

List available research protocols.

```
research-cli research protocol list [OPTIONS]

Options:
  --type [survey|interview|focus-group]  Filter by method type
  --format [table|json|yaml]             Output format (default: table)
  --help                                  Show this message and exit

Exit Codes:
  0  Success

Examples:
  research-cli research protocol list
  research-cli research protocol list --type survey
  research-cli research protocol list --type interview --format json
```

**Output Contract (table)**:
```
╭──────────────────────────────────────────────────────────────────────────╮
│ Available Research Protocols                                              │
├───────────────────────┬─────────┬──────────────┬─────────────────────────┤
│ ID                    │ Type    │ Version      │ Name                    │
├───────────────────────┼─────────┼──────────────┼─────────────────────────┤
│ feature-concept-test  │ survey  │ 1.0.0        │ Feature Concept Test    │
│ nps-survey            │ survey  │ 1.0.0        │ NPS Survey              │
│ onboarding-experience │ interview│ 1.0.0       │ Onboarding Experience   │
│ pricing-feedback      │ focus   │ 1.0.0        │ Pricing Model Feedback  │
╰───────────────────────┴─────────┴──────────────┴─────────────────────────╯
```

### `research protocol show`

Show details of a specific protocol.

```
research-cli research protocol show [OPTIONS] PROTOCOL_ID

Arguments:
  PROTOCOL_ID            Protocol ID to show (required)

Options:
  --format [yaml|json]   Output format (default: yaml)
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (protocol not found)

Examples:
  research-cli research protocol show feature-concept-test
  research-cli research protocol show onboarding-experience --format json
```

### `research protocol delete`

Delete a research protocol.

```
research-cli research protocol delete [OPTIONS] PROTOCOL_ID

Arguments:
  PROTOCOL_ID            Protocol ID to delete (required)

Options:
  --force, -f            Skip confirmation prompt
  --help                 Show this message and exit

Exit Codes:
  0  Success
  1  Error (protocol not found, permission denied)

Examples:
  research-cli research protocol delete my-custom-survey
  research-cli research protocol delete my-custom-survey --force
```

---

## 5. Error Codes

| Code | Constant | Description |
|------|----------|-------------|
| `PROTOCOL_NOT_FOUND` | Protocol ID does not exist | Check protocol list |
| `PERSONA_NOT_FOUND` | Persona ID does not exist | Check persona list |
| `PANEL_NOT_FOUND` | Panel ID does not exist | Check panel list |
| `VALIDATION_ERROR` | Protocol/input validation failed | Check error details |
| `EXECUTION_TIMEOUT` | Research execution timed out | Increase timeout or simplify protocol |
| `QUALITY_GATE_FAILED` | Response quality below threshold | Review persona definition or protocol |
| `PARTIAL_COMPLETION` | Some responses failed | Check individual results |

---

## 6. Common Options

All research commands support these common options inherited from the CLI framework:

```
Global Options:
  --verbose, -v          Enable verbose output
  --quiet, -q            Suppress non-essential output
  --help                 Show command help
```

---

## 7. Output Format Specifications

### Text Format
- Uses Rich library for formatted terminal output
- Progress bars for multi-step operations
- Colored status indicators (green=success, yellow=warning, red=error)
- Synthetic data disclaimer at start of output

### JSON Format
- Valid JSON with consistent schema per command
- Timestamps in ISO 8601 format
- All numeric IDs as strings for consistency
- Includes `metadata` object with execution details

### YAML Format (protocol show only)
- Human-readable protocol definition
- Mirrors the storage format
- Includes all protocol fields
