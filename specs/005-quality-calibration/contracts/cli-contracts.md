# CLI Interface Contract: Quality & Calibration

**Feature**: 005-quality-calibration
**Date**: 2026-01-27

## Overview

This document defines the CLI interface contract for quality metrics and calibration commands. These commands extend the existing `research-cli` tool from Phases 0-3.

---

## Command Structure

```
research-cli
├── persona                    # (Phase 0) Persona management
├── research
│   ├── single                 # (Phase 1) Single persona session
│   ├── panel                  # (Phase 2) Panel commands
│   ├── protocol               # (Phase 3) Protocol management
│   ├── survey                 # (Phase 3) Survey commands
│   ├── interview              # (Phase 3) Interview commands
│   ├── focus-group            # (Phase 3) Focus group commands
│   ├── quality                # (Phase 4) NEW - Quality commands
│   │   ├── analyze            # Run quality analysis on session
│   │   ├── dashboard          # View aggregated metrics
│   │   └── report             # Generate quality report
│   └── calibration            # (Phase 4) NEW - Calibration commands
│       ├── import             # Import real user baseline
│       ├── list               # List stored baselines
│       ├── show               # Show baseline details
│       ├── compare            # Compare synthetic vs baseline
│       └── delete             # Delete baseline
└── init                       # (Phase 0) Initialize project
```

---

## Quality Commands

### `research quality analyze`

Run quality analysis on a completed research session.

**Usage**:
```bash
research-cli research quality analyze --session=<session-id> [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--session`, `-s` | string | Yes | - | Session ID to analyze |
| `--format`, `-f` | choice | No | `text` | Output format: `text`, `json` |
| `--output`, `-o` | path | No | - | Export analysis to file |
| `--consistency-threshold` | float | No | `70.0` | Minimum consistency score (%) |
| `--sycophancy-threshold` | float | No | `30.0` | Maximum sycophancy rate (%) |
| `--drift-threshold` | float | No | `25.0` | Maximum drift score (%) |

**Output (text format)**:
```
╭─ Quality Analysis: session-abc123 ─────────────────────────────────────────╮
│ Session Type: panel | Panel: tech-adopters | Personas: 5                   │
│ Analysis Time: 2026-01-27 14:30:00                                         │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Overall Status: ⚠️ WARNING ───────────────────────────────────────────────╮
│ Quality Score: 72.5/100                                                    │
│ Issues Found: 1                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Consistency Analysis ─────────────────────────────────────────────────────╮
│ Overall Score: 78.0% ✅ (threshold: 70%)                                   │
│                                                                            │
│ Big Five Alignment: 82.0%                                                  │
│   ├─ Openness: 85% ✅                                                      │
│   ├─ Conscientiousness: 80% ✅                                             │
│   ├─ Extraversion: 78% ✅                                                  │
│   ├─ Agreeableness: 88% ✅                                                 │
│   └─ Neuroticism: 79% ✅                                                   │
│                                                                            │
│ Schwartz Alignment: 72.0%                                                  │
│   ├─ Self-Direction: 75% ✅                                                │
│   └─ Security: 69% ⚠️ (below optimal)                                      │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Bias Analysis ────────────────────────────────────────────────────────────╮
│ Sycophancy Rate: 35.0% ⚠️ (threshold: 30%)                                 │
│ Positive:Negative Ratio: 4.5:1 ⚠️ (threshold: 4:1)                         │
│                                                                            │
│ Flagged Responses (2):                                                     │
│ ▸ Response #3 (tech-early-adopter): Excessive positive phrases detected    │
│   "This is exactly what I need... I can't find any issues..."              │
│ ▸ Response #4 (power-user): Missing expected criticism                     │
│   Skeptical persona showed no concerns                                     │
│                                                                            │
│ Sentiment Clustering: Not detected ✅                                      │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Variance Analysis ────────────────────────────────────────────────────────╮
│ Rating Variance: 0.72 ✅ (threshold: 0.60)                                 │
│ Sentiment Distribution:                                                    │
│   Positive: 60% | Negative: 20% | Mixed: 15% | Neutral: 5%                 │
│                                                                            │
│ Clustering: Not detected ✅                                                │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Drift Analysis ───────────────────────────────────────────────────────────╮
│ Max Drift Score: 12.0% ✅ (threshold: 25%)                                 │
│                                                                            │
│ Per-Persona Drift:                                                         │
│   tech-early-adopter: 8% ✅                                                │
│   power-user: 12% ✅                                                       │
│   busy-professional: 5% ✅                                                 │
│   privacy-conscious-user: 10% ✅                                           │
│   skeptical-late-adopter: 7% ✅                                            │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Warnings ─────────────────────────────────────────────────────────────────╮
│ ⚠️ Sycophancy rate (35%) exceeds threshold (30%)                           │
│    Recommendation: Review flagged responses and consider adjusting         │
│    criticism_tendency for affected personas.                               │
╰────────────────────────────────────────────────────────────────────────────╯

⚠️  Synthetic Research Disclaimer: This analysis is based on synthetic user
    responses. Validate with real user research for critical decisions.
```

**Exit Codes**:
- `0`: Success, all quality gates passed
- `1`: Error (session not found, analysis failed)
- `2`: Warning (quality gates failed but analysis complete)

---

### `research quality dashboard`

View aggregated quality metrics across sessions.

**Usage**:
```bash
research-cli research quality dashboard [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--limit`, `-l` | int | No | `10` | Number of recent sessions to show |
| `--status`, `-s` | choice | No | `all` | Filter: `all`, `healthy`, `warning`, `critical` |
| `--format`, `-f` | choice | No | `text` | Output format: `text`, `json` |
| `--since` | date | No | - | Only show sessions after this date (YYYY-MM-DD) |

**Output (text format)**:
```
╭─────────────────────── Quality Dashboard ───────────────────────────────────╮
│                                                                              │
│  Overall Health: ⚠️ Warning (2 sessions need review)                         │
│  Period: Last 7 days | Sessions Analyzed: 12                                │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─ Aggregate Metrics ──────────────────────────────────────────────────────────╮
│                                                                              │
│  ┌─────────────────────┬─────────┬───────────┬─────────────────────────────┐ │
│  │ Metric              │ Current │ Threshold │ Status                      │ │
│  ├─────────────────────┼─────────┼───────────┼─────────────────────────────┤ │
│  │ Avg Consistency     │ 78.2%   │ 70%       │ ✅ Healthy                  │ │
│  │ Avg Sycophancy Rate │ 28.5%   │ 30%       │ ✅ Healthy                  │ │
│  │ Avg Variance Score  │ 0.72    │ 0.60      │ ✅ Healthy                  │ │
│  │ Max Drift Score     │ 18.0%   │ 25%       │ ✅ Healthy                  │ │
│  └─────────────────────┴─────────┴───────────┴─────────────────────────────┘ │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─ Session Health Distribution ────────────────────────────────────────────────╮
│                                                                              │
│  ✅ Healthy:  10 (83.3%)  ████████████████████████                          │
│  ⚠️ Warning:   2 (16.7%)  █████                                              │
│  ❌ Critical:  0 (0.0%)                                                      │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─ Recent Sessions ────────────────────────────────────────────────────────────╮
│                                                                              │
│  ┌────────────────┬─────────────┬──────────────┬────────┬──────┬──────────┐ │
│  │ Session        │ Type        │ Panel        │ Status │ Cons │ Syco     │ │
│  ├────────────────┼─────────────┼──────────────┼────────┼──────┼──────────┤ │
│  │ session-abc123 │ panel       │ tech-adopters│ ⚠️     │ 78%  │ 35%      │ │
│  │ session-def456 │ panel       │ skeptics     │ ✅     │ 82%  │ 22%      │ │
│  │ session-ghi789 │ interview   │ -            │ ✅     │ 85%  │ 18%      │ │
│  │ session-jkl012 │ survey      │ general-pop  │ ⚠️     │ 71%  │ 32%      │ │
│  │ session-mno345 │ focus-group │ power-users  │ ✅     │ 88%  │ 15%      │ │
│  └────────────────┴─────────────┴──────────────┴────────┴──────┴──────────┘ │
│                                                                              │
│  (Showing 5 of 12 sessions. Use --limit to show more.)                      │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─ Trends (7 days) ────────────────────────────────────────────────────────────╮
│                                                                              │
│  Consistency: Stable (78% → 78%)                                            │
│  Sycophancy:  Improving (32% → 28%)  ↓                                      │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

Tip: Use 'research quality analyze --session=<id>' for detailed analysis.
```

**Exit Codes**:
- `0`: Success
- `1`: Error (no sessions found, storage access failed)
- `2`: Warning (some sessions have quality issues)

---

### `research quality report`

Generate a quality report for a session or time period.

**Usage**:
```bash
research-cli research quality report [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--session`, `-s` | string | No* | - | Single session ID |
| `--since` | date | No* | - | Start date for period report |
| `--until` | date | No | today | End date for period report |
| `--output`, `-o` | path | Yes | - | Output file path (.md or .json) |
| `--format`, `-f` | choice | No | `markdown` | Output format: `markdown`, `json` |

*Either `--session` or `--since` is required.

**Output (Markdown report)**:
```markdown
# Quality Report: session-abc123

**Generated**: 2026-01-27 14:30:00
**Session Type**: Panel Research
**Panel**: tech-adopters (5 personas)

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| Overall Quality Score | 72.5/100 | ⚠️ Warning |
| Consistency Score | 78.0% | ✅ Pass |
| Sycophancy Rate | 35.0% | ⚠️ Fail |
| Variance Score | 0.72 | ✅ Pass |
| Max Drift Score | 12.0% | ✅ Pass |

**Issues Found**: 1 warning

## Detailed Analysis

### Consistency Analysis
...

### Bias Analysis
...

## Recommendations

1. Review responses from tech-early-adopter and power-user for excessive positivity
2. Consider increasing criticism_tendency setting for affected personas
3. Re-run session with adjusted personas to validate improvement

---

*Synthetic Research Disclaimer: This analysis is based on AI-generated responses.
Validate findings with real user research for critical decisions.*
```

**Exit Codes**:
- `0`: Success
- `1`: Error (session not found, output path invalid)

---

## Calibration Commands

### `research calibration import`

Import real user data as a calibration baseline.

**Usage**:
```bash
research-cli research calibration import --file=<path> --name=<name> [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--file`, `-f` | path | Yes | - | Path to data file (CSV or JSON) |
| `--name`, `-n` | string | Yes | - | Baseline identifier (slug format) |
| `--source` | string | No | - | Description of data source |
| `--tags` | string | No | - | Comma-separated demographic tags |
| `--collection-date` | date | No | today | When data was collected |

**Input Format (CSV)**:
```csv
question_id,response_type,response_value,demographic_tag
q1,rating,7,early_adopter
q1,rating,5,late_majority
q2,multiple_choice,A,early_adopter
q2,multiple_choice,B,late_majority
```

**Input Format (JSON)**:
```json
{
  "responses": [
    {"question_id": "q1", "type": "rating", "value": 7, "tag": "early_adopter"},
    {"question_id": "q1", "type": "rating", "value": 5, "tag": "late_majority"}
  ]
}
```

**Output**:
```
Importing baseline from: survey-results.csv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

✓ Baseline imported successfully

  Name: feature-survey-q1-2026
  Source: Real User Survey Q1 2026
  Sample Size: 150 responses
  Questions: 5
  Tags: early_adopter, late_majority, privacy_conscious

  Distributions calculated:
  • q1_likelihood: rating (mean: 6.2, stdev: 2.3)
  • q2_concern: categorical (4 options)
  • q3_satisfaction: rating (mean: 7.1, stdev: 1.8)
  • q4_recommendation: rating (mean: 6.8, stdev: 2.1)
  • q5_feedback: open_ended (skipped - not comparable)

  Saved to: calibration/baselines/feature-survey-q1-2026.yaml

Use 'research calibration compare' to compare with synthetic data.
```

**Exit Codes**:
- `0`: Success
- `1`: Error (file not found, invalid format, parse error)

**Validation**:
- Minimum 10 responses required
- Question IDs must be valid identifiers
- Response types must be: rating, multiple_choice, or open_ended
- Duplicate baseline names are rejected

---

### `research calibration list`

List stored calibration baselines.

**Usage**:
```bash
research-cli research calibration list [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--format`, `-f` | choice | No | `text` | Output format: `text`, `json` |
| `--tags` | string | No | - | Filter by demographic tags |

**Output (text format)**:
```
╭─ Calibration Baselines ────────────────────────────────────────────────────╮
│                                                                            │
│  ┌───────────────────────┬────────┬────────────┬─────────────────────────┐ │
│  │ Name                  │ Size   │ Date       │ Tags                    │ │
│  ├───────────────────────┼────────┼────────────┼─────────────────────────┤ │
│  │ feature-survey-q1-2026│ 150    │ 2026-01-15 │ early_adopter, late_... │ │
│  │ usability-test-dec    │ 45     │ 2025-12-20 │ professional, us_based  │ │
│  │ beta-feedback         │ 230    │ 2025-11-01 │ beta_user, power_user   │ │
│  └───────────────────────┴────────┴────────────┴─────────────────────────┘ │
│                                                                            │
│  Total: 3 baselines                                                        │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯
```

---

### `research calibration show`

Show details of a calibration baseline.

**Usage**:
```bash
research-cli research calibration show <baseline-id> [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `baseline-id` | string | Yes | - | Baseline identifier |
| `--format`, `-f` | choice | No | `text` | Output format: `text`, `json`, `yaml` |

**Output (text format)**:
```
╭─ Baseline: feature-survey-q1-2026 ─────────────────────────────────────────╮
│                                                                            │
│  Source: Real User Survey Q1 2026                                          │
│  Sample Size: 150 responses                                                │
│  Collection Date: 2026-01-15                                               │
│  Tags: early_adopter, late_majority, privacy_conscious                     │
│                                                                            │
│  Questions (5):                                                            │
│  ┌─────────────────┬──────────────┬────────┬─────────┬──────────────────┐ │
│  │ ID              │ Type         │ Mean   │ Stdev   │ Distribution     │ │
│  ├─────────────────┼──────────────┼────────┼─────────┼──────────────────┤ │
│  │ q1_likelihood   │ rating       │ 6.2    │ 2.3     │ ▁▂▄▆█▇▅▃▂▁      │ │
│  │ q2_concern      │ categorical  │ -      │ -       │ Privacy:35%...   │ │
│  │ q3_satisfaction │ rating       │ 7.1    │ 1.8     │ ▁▁▂▄▆█▇▅▃▂      │ │
│  │ q4_recommend    │ rating       │ 6.8    │ 2.1     │ ▁▂▃▅▇█▆▄▂▁      │ │
│  │ q5_feedback     │ open_ended   │ -      │ -       │ (not comparable) │ │
│  └─────────────────┴──────────────┴────────┴─────────┴──────────────────┘ │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯
```

---

### `research calibration compare`

Compare synthetic session results against a baseline.

**Usage**:
```bash
research-cli research calibration compare --baseline=<id> --session=<id> [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--baseline`, `-b` | string | Yes | - | Baseline ID to compare against |
| `--session`, `-s` | string | Yes | - | Session ID with synthetic data |
| `--format`, `-f` | choice | No | `text` | Output format: `text`, `json` |
| `--output`, `-o` | path | No | - | Export comparison to file |
| `--recommendations` | flag | No | - | Include adjustment recommendations |

**Output (text format)**:
```
╭─ Calibration Comparison ───────────────────────────────────────────────────╮
│                                                                            │
│  Baseline: feature-survey-q1-2026 (150 responses)                          │
│  Session: session-abc123 (5 personas)                                      │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Overall Alignment: ⚠️ PARTIAL (68% overlap) ──────────────────────────────╮
│                                                                            │
│  Status: Synthetic responses show partial alignment with real user data.   │
│  Some calibration adjustments recommended.                                 │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Question-Level Comparison ────────────────────────────────────────────────╮
│                                                                            │
│  ┌─────────────────┬───────────┬───────────┬─────────┬────────────────────┐│
│  │ Question        │ Real Mean │ Synth Mean│ Overlap │ Status             ││
│  ├─────────────────┼───────────┼───────────┼─────────┼────────────────────┤│
│  │ q1_likelihood   │ 6.2       │ 7.4       │ 62%     │ ⚠️ Skews positive  ││
│  │ q2_concern      │ Privacy   │ Privacy   │ 85%     │ ✅ Aligned         ││
│  │ q3_satisfaction │ 7.1       │ 7.8       │ 71%     │ ✅ Acceptable      ││
│  │ q4_recommend    │ 6.8       │ 7.9       │ 55%     │ ⚠️ Skews positive  ││
│  └─────────────────┴───────────┴───────────┴─────────┴────────────────────┘│
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Distribution Visualization ───────────────────────────────────────────────╮
│                                                                            │
│  q1_likelihood (1-10 scale):                                               │
│                                                                            │
│  Real:      ▁▂▄▆█▇▅▃▂▁  (mean: 6.2, stdev: 2.3)                           │
│  Synthetic: ▁▁▂▃▅▇█▆▄▂  (mean: 7.4, stdev: 1.9)                           │
│                                                                            │
│  q4_recommend (1-10 scale):                                                │
│                                                                            │
│  Real:      ▁▂▃▅▇█▆▄▂▁  (mean: 6.8, stdev: 2.1)                           │
│  Synthetic: ▁▁▁▂▄▆█▇▅▃  (mean: 7.9, stdev: 1.6)                           │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ Recommendations ──────────────────────────────────────────────────────────╮
│                                                                            │
│  1. [HIGH] Increase criticism_tendency for tech-early-adopter              │
│     Current: balanced → Suggested: critical                                │
│     Rationale: Synthetic responses skew 1.2 points more positive           │
│                                                                            │
│  2. [MEDIUM] Adjust certainty_level for power-user                         │
│     Current: certain → Suggested: questioning                              │
│     Rationale: Reduce overly confident positive responses                  │
│                                                                            │
│  3. [LOW] Consider adding a "cautious optimist" persona                    │
│     Rationale: Real data shows more hedged positive responses              │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

Comparison saved to: calibration/comparisons/comparison-abc123.json
```

**Exit Codes**:
- `0`: Success, synthetic data aligned (>70% overlap)
- `1`: Error (baseline/session not found)
- `2`: Warning (synthetic data divergent, calibration recommended)

---

### `research calibration delete`

Delete a calibration baseline.

**Usage**:
```bash
research-cli research calibration delete <baseline-id> [options]
```

**Arguments**:

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `baseline-id` | string | Yes | - | Baseline ID to delete |
| `--force`, `-f` | flag | No | - | Skip confirmation prompt |

**Output**:
```
Are you sure you want to delete baseline 'feature-survey-q1-2026'? [y/N]: y
✓ Deleted baseline: feature-survey-q1-2026
```

**Exit Codes**:
- `0`: Success
- `1`: Error (baseline not found, in use by comparisons)

---

## Error Messages

| Error Code | Message | Resolution |
|------------|---------|------------|
| `SESSION_NOT_FOUND` | Session '{id}' not found | Verify session ID or run a research session first |
| `BASELINE_NOT_FOUND` | Baseline '{id}' not found | Use `calibration list` to see available baselines |
| `IMPORT_PARSE_ERROR` | Failed to parse file: {reason} | Check file format matches expected CSV/JSON structure |
| `INSUFFICIENT_DATA` | Baseline requires at least 10 responses | Provide more data or combine datasets |
| `DUPLICATE_BASELINE` | Baseline '{id}' already exists | Use different name or delete existing baseline |
| `INVALID_DATE_FORMAT` | Date must be YYYY-MM-DD format | Correct the date format |
| `MISSING_QUESTION_ID` | Row {n} missing question_id | Ensure all rows have question_id column |
| `BASELINE_IN_USE` | Baseline has {n} comparisons | Delete comparisons first or use --force |

---

## Integration with Previous Phases

Quality and calibration commands integrate with all research methods:

```bash
# Phase 1: Single persona → quality analysis
research-cli research single --persona=tech-early-adopter --question="..."
research-cli research quality analyze --session=<session-id>

# Phase 2: Panel → quality analysis
research-cli research panel run --panel=tech-adopters --question="..."
research-cli research quality analyze --session=<session-id>

# Phase 3: Survey → quality analysis + calibration
research-cli research survey run --protocol=feature-survey --persona=tech-early-adopter
research-cli research quality analyze --session=<session-id>
research-cli research calibration compare --baseline=real-survey --session=<session-id>

# Phase 3: Interview → quality analysis (with drift)
research-cli research interview run --protocol=user-interview --persona=power-user
research-cli research quality analyze --session=<session-id>
# Drift analysis automatically included for multi-turn sessions

# Phase 3: Focus group → quality analysis (with drift per persona)
research-cli research focus-group run --protocol=product-discussion --personas=tech-early-adopter,power-user,skeptical-late-adopter
research-cli research quality analyze --session=<session-id>
# Individual drift tracked for each participant
```

---

## Version

CLI Version: 0.4.0 (Phase 4 additions)
