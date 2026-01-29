# Quickstart: Quality & Calibration

**Feature**: Quality & Calibration (Phase 4)
**Date**: 2026-01-27

## Overview

Phase 4 adds comprehensive quality metrics and calibration capabilities to the Synthetic User Research Platform. This guide shows you how to:

1. Analyze research session quality
2. View aggregated quality metrics
3. Import real user baselines for calibration
4. Compare synthetic vs real data

## Prerequisites

- Phase 0-3 installed and working
- At least one completed research session (single, panel, survey, interview, or focus group)
- For calibration: Real user survey data in CSV or JSON format

## Quick Start

### 1. Analyze Session Quality

After running any research session, analyze its quality:

```bash
# Run a panel session (Phase 2)
research-cli research panel run --panel=tech-adopters --question="What do you think of this AI feature?"

# Analyze the session quality
research-cli research quality analyze --session=<session-id>
```

**Output includes:**
- Consistency score (trait alignment)
- Sycophancy rate (bias detection)
- Variance analysis (panel diversity)
- Drift analysis (for multi-turn sessions)

### 2. View Quality Dashboard

See aggregated metrics across all sessions:

```bash
# View dashboard with last 10 sessions
research-cli research quality dashboard

# Filter by status
research-cli research quality dashboard --status=warning

# Export as JSON
research-cli research quality dashboard --format=json
```

### 3. Generate Quality Report

Export a detailed quality report:

```bash
# Single session report
research-cli research quality report --session=<session-id> --output=quality-report.md

# Period report (last 7 days)
research-cli research quality report --since=2026-01-20 --output=weekly-report.md
```

### 4. Import Calibration Baseline

Import real user data for comparison:

```bash
# Prepare your CSV file
cat survey-results.csv
# question_id,response_type,response_value,demographic_tag
# q1,rating,7,early_adopter
# q1,rating,5,late_majority
# ...

# Import the baseline
research-cli research calibration import \
  --file=survey-results.csv \
  --name=feature-survey-q1 \
  --source="Real User Survey Jan 2026" \
  --tags=early_adopter,late_majority
```

### 5. Compare Synthetic vs Real Data

Run calibration comparison:

```bash
# First, run a synthetic survey with the same questions
research-cli research survey run --protocol=feature-survey --panel=tech-adopters

# Compare with real baseline
research-cli research calibration compare \
  --baseline=feature-survey-q1 \
  --session=<session-id> \
  --recommendations
```

**Output includes:**
- Distribution overlap percentage
- Per-question alignment
- Recommendations for persona adjustments

## Common Workflows

### Validate Research Quality

```bash
# 1. Run research
research-cli research panel run --panel=skeptics-critics --question="What concerns do you have?"

# 2. Check quality immediately
research-cli research quality analyze --session=<session-id>

# 3. If warnings appear, review and adjust
# - Check flagged responses
# - Adjust persona calibration settings
# - Re-run if needed
```

### Calibrate Against Real Data

```bash
# 1. Import baseline (once)
research-cli research calibration import --file=real-data.csv --name=baseline-q1

# 2. Run synthetic research
research-cli research survey run --protocol=user-feedback --panel=general-population

# 3. Compare
research-cli research calibration compare --baseline=baseline-q1 --session=<session-id>

# 4. Apply recommendations
# - Adjust persona criticism_tendency
# - Modify panel composition
# - Re-run and compare again
```

### Monitor Research Quality Over Time

```bash
# Daily check
research-cli research quality dashboard --since=$(date -d "7 days ago" +%Y-%m-%d)

# Export weekly report
research-cli research quality report \
  --since=$(date -d "7 days ago" +%Y-%m-%d) \
  --output=reports/weekly-$(date +%Y-%m-%d).md
```

## Quality Thresholds

Default thresholds (configurable per command):

| Metric | Default | Flag |
|--------|---------|------|
| Consistency minimum | 70% | `--consistency-threshold` |
| Sycophancy maximum | 30% | `--sycophancy-threshold` |
| Drift maximum | 25% | `--drift-threshold` |
| Variance minimum | 0.6 | (baseline comparison) |

## Understanding Results

### Quality Status

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ Healthy | All gates passed | Results usable |
| ⚠️ Warning | Some gates failed | Review before using |
| ❌ Critical | Multiple failures | Do not use without review |

### Consistency Score

- **>80%**: Excellent trait alignment
- **70-80%**: Acceptable alignment
- **<70%**: Poor alignment, review persona definitions

### Sycophancy Rate

- **<20%**: Natural response distribution
- **20-30%**: Acceptable, monitor trends
- **>30%**: Bias detected, adjust personas

### Calibration Overlap

- **>70%**: Aligned with real data
- **60-70%**: Partial alignment, consider adjustments
- **<60%**: Divergent, calibration needed

## Troubleshooting

### "Sycophancy rate exceeds threshold"

1. Check flagged responses
2. Increase `criticism_tendency` for affected personas
3. Add more skeptical personas to panel
4. Re-run and compare

### "Low variance detected"

1. Review panel composition
2. Ensure personas have diverse traits
3. Check for unintentionally similar personas
4. Consider adding contrarian personas

### "Character drift detected"

1. Review session length
2. Check drift point in analysis
3. Consider shorter sessions
4. Reinforce persona traits in protocol

### "Calibration shows divergence"

1. Review comparison details
2. Apply persona adjustment recommendations
3. Re-run synthetic research
4. Iterate until alignment improves

## Next Steps

- Run `/speckit.tasks` to generate implementation tasks
- Review [data-model.md](data-model.md) for entity details
- Check [cli-contracts.md](contracts/cli-contracts.md) for full CLI reference
- Explore [research.md](research.md) for technical decisions

## Version

CLI Version: 0.4.0 (Phase 4)
