# CLI Interface Contract: Single Persona MVP

**Feature**: 002-single-persona-mvp
**Date**: 2026-01-25
**CLI Version**: 0.2.0

## Overview

This document defines the CLI interface for single persona research sessions. The `research` command group extends the existing `research-cli` tool from Phase 0.

---

## Command Structure

```
research-cli
├── persona           # (Phase 0) Persona management
│   ├── validate
│   ├── list
│   ├── show
│   └── prompt
├── init              # (Phase 0) Project initialization
└── research          # (NEW) Research session execution
    └── single        # Single persona research
```

---

## New Commands

### `research single`

Execute a single-persona research session.

**Synopsis**:
```bash
research-cli research single --persona <ID> --question <TEXT> [OPTIONS]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--persona`, `-p` | string | Yes | Persona ID from the library |
| `--question`, `-q` | string | Yes | Question to ask the persona |

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--type`, `-t` | choice | `open` | Question type: `open`, `rating`, `choice` |
| `--options` | string | - | Comma-separated options for choice questions |
| `--scale` | string | `1-10` | Rating scale (e.g., `1-5`, `1-10`) |
| `--format`, `-f` | choice | `text` | Output format: `text`, `json` |
| `--output`, `-o` | path | - | Export session to file |
| `--timeout` | int | `30` | Timeout in seconds |
| `--no-quality` | flag | false | Skip quality metrics calculation |
| `--verbose`, `-v` | flag | false | Show detailed output including raw response |

**Exit Codes**:

| Code | Meaning |
|------|---------|
| 0 | Success - session completed |
| 1 | Error - session failed |
| 2 | Warning - session completed with quality warnings |

---

## Examples

### Basic Open-Ended Question

```bash
research-cli research single \
  --persona tech-early-adopter \
  --question "What do you think of this daily reflection feature for a productivity app?"
```

**Output** (text format):
```
╭─ Research Session ─────────────────────────────────────────────╮
│ Persona: Alex Chen (tech-early-adopter)                        │
│ Question: What do you think of this daily reflection feature?  │
╰────────────────────────────────────────────────────────────────╯

📊 Response Summary
┌────────────────────┬────────────────────────────────────────────┐
│ Sentiment          │ MIXED                                       │
│ Overall Impression │ Interesting concept but needs refinement    │
└────────────────────┴────────────────────────────────────────────┘

⚠️ Concerns:
  • Privacy of reflection data
  • Time commitment required

💡 Suggestions:
  • Add quick-entry mode for busy days
  • Integrate with existing calendar apps

📈 Quality Metrics
┌─────────────────────┬───────┐
│ Consistency Score   │ 87.5% │
│ Sycophancy Warning  │ No    │
│ Quality Gates       │ PASS  │
└─────────────────────┴───────┘

⚠️  SYNTHETIC DATA: Validate critical findings with real users.
```

### Rating Question

```bash
research-cli research single \
  --persona skeptical-late-adopter \
  --question "How likely are you to use this AI writing assistant?" \
  --type rating \
  --scale 1-10
```

**Output**:
```
╭─ Research Session ─────────────────────────────────────────────╮
│ Persona: Margaret Wilson (skeptical-late-adopter)              │
│ Question: How likely are you to use this AI writing assistant? │
│ Type: Rating (1-10)                                            │
╰────────────────────────────────────────────────────────────────╯

📊 Response Summary
┌────────────────────┬────────────────────────────────────────────┐
│ Rating             │ 3/10                                        │
│ Sentiment          │ NEGATIVE                                    │
│ Overall Impression │ Not for me, too much complexity for unclear │
│                    │ benefit                                     │
└────────────────────┴────────────────────────────────────────────┘

⚠️ Concerns:
  • Learning curve seems steep
  • Prefer writing in my own voice
  • Security concerns about what happens to my text

📈 Quality Metrics
┌─────────────────────┬───────┐
│ Consistency Score   │ 92.1% │
│ Sycophancy Warning  │ No    │
│ Quality Gates       │ PASS  │
└─────────────────────┴───────┘
```

### Multiple Choice Question

```bash
research-cli research single \
  --persona busy-professional \
  --question "Which pricing model would you prefer?" \
  --type choice \
  --options "Monthly subscription,Annual subscription,One-time purchase,Free with ads"
```

### JSON Output

```bash
research-cli research single \
  --persona tech-early-adopter \
  --question "What do you think of this feature?" \
  --format json
```

**Output**:
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
    "name": "Alex Chen"
  },
  "question": {
    "text": "What do you think of this feature?",
    "type": "OPEN_ENDED"
  },
  "response": {
    "sentiment": "MIXED",
    "overall_impression": "Interesting concept but needs refinement",
    "concerns": ["Privacy of reflection data"],
    "suggestions": ["Add quick-entry mode"],
    "quality": {
      "consistency_score": 87.5,
      "passed_gates": true
    }
  }
}
```

### Export to File

```bash
research-cli research single \
  --persona tech-early-adopter \
  --question "What do you think of this feature?" \
  --output ./sessions/session-2026-01-25.json
```

---

## Error Messages

### Persona Not Found

```bash
$ research-cli research single --persona unknown-persona --question "Test"

Error: Persona 'unknown-persona' not found.

Available personas:
  • tech-early-adopter
  • skeptical-late-adopter
  • busy-professional
  • privacy-conscious-user
  • power-user

Did you mean: skeptical-late-adopter?
```

### Empty Question

```bash
$ research-cli research single --persona tech-early-adopter --question ""

Error: Question cannot be empty.

Usage: research-cli research single --persona <ID> --question <TEXT>
```

### Question Too Long

```bash
$ research-cli research single --persona tech-early-adopter --question "[2500 chars]"

Warning: Question exceeds 2000 characters. Truncating.

[Session proceeds with truncated question]
```

### Session Timeout

```bash
$ research-cli research single --persona tech-early-adopter --question "Test" --timeout 5

Error: Session timed out after 5 seconds.

The persona subagent did not respond in time. Try:
  • Increasing timeout with --timeout 60
  • Using a simpler question
  • Retrying the session
```

### Quality Warning

```bash
$ research-cli research single --persona tech-early-adopter --question "Test"

[Session output...]

⚠️ Quality Warning:
  • Consistency score (65%) below threshold (70%)
  • Response may not fully reflect persona characteristics

Session completed with warnings (exit code 2).
```

---

## Shorthand Commands

For convenience, the `research single` command has a shorthand alias:

```bash
# Full form
research-cli research single --persona tech-early-adopter --question "Test"

# Shorthand
research-cli ask tech-early-adopter "Test"
```

---

## Integration with Phase 0 Commands

Phase 1 commands work with Phase 0 persona management:

```bash
# List available personas (Phase 0)
research-cli persona list

# Show persona details before research (Phase 0)
research-cli persona show tech-early-adopter

# Generate raw prompt for debugging (Phase 0)
research-cli persona prompt tech-early-adopter

# Run research session (Phase 1)
research-cli research single --persona tech-early-adopter --question "Test"
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RESEARCH_PERSONAS_DIR` | `./personas/definitions` | Persona definitions directory |
| `RESEARCH_DEFAULT_TIMEOUT` | `30` | Default session timeout (seconds) |
| `RESEARCH_DEFAULT_FORMAT` | `text` | Default output format |

---

## Configuration File

Optional `.research-cli.yaml` in project root:

```yaml
research:
  default_timeout: 45
  default_format: text
  quality:
    consistency_threshold: 70
    sycophancy_ratio_threshold: 4.0
  output:
    show_raw_response: false
    show_limitations_warning: true
```
