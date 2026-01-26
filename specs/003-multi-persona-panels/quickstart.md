# Quickstart Guide: Multi-Persona Panels

**Feature**: 003-multi-persona-panels
**Date**: 2026-01-25

## Overview

This guide helps you get started with multi-persona panel research. Panels allow you to gather feedback from multiple synthetic personas simultaneously, with automatic aggregation of themes, sentiment, and consensus/divergence analysis.

---

## Prerequisites

- Completed Phase 0 (Foundation) and Phase 1 (Single Persona MVP) installation
- Python 3.11+ with research-cli installed
- Familiarity with single persona research sessions

---

## Quick Start

### 1. List Available Panels

```bash
# See all pre-built panels
research-cli research panel list
```

You'll see 4 pre-built panels:
- **tech-adopters** (5 personas): Full technology adoption spectrum
- **skeptics-critics** (5 personas): Privacy-conscious and skeptical users
- **power-users** (5 personas): High-engagement expert users
- **general-population** (10 personas): Diverse general audience

### 2. Run Your First Panel Research

```bash
# Run a panel research session
research-cli research panel run \
  --panel=tech-adopters \
  --question="What do you think of a daily reflection feature that helps track productivity?"
```

The system will:
1. Query all 5 personas in parallel
2. Collect and parse their responses
3. Aggregate findings into themes and insights
4. Display results with quality metrics

### 3. Export Results

```bash
# Export to JSON for analysis
research-cli research panel run \
  --panel=tech-adopters \
  --question="Your question here" \
  --output results.json

# Generate a Markdown report
research-cli research panel run \
  --panel=tech-adopters \
  --question="Your question here" \
  --report research-report.md
```

---

## Understanding Panel Results

### Executive Summary
A 2-3 sentence synthesis of the most important findings across all personas.

### Themes
Recurring topics identified across multiple responses:
- **Frequency**: How many personas mentioned this theme
- **Supporting quotes**: Direct quotes from personas

### Sentiment Distribution
Breakdown of how personas feel about the topic:
- Positive / Negative / Mixed / Neutral percentages

### Consensus Points
Issues where significant agreement exists (>60% of personas agree):
- What they agree on
- Which personas share this view

### Divergence Points
Issues where personas disagree:
- The topic of disagreement
- Different positions and who holds them
- Rationale for each position

### Quality Metrics
- **Avg Consistency**: How well responses match persona traits
- **Completion Rate**: Successful responses / total personas
- **Theme Confidence**: How strongly themes are supported

---

## Creating Custom Panels

### Create a Panel

```bash
# Create a custom panel with specific personas
research-cli research panel create \
  --name="my-focus-group" \
  --personas="tech-early-adopter,skeptical-late-adopter,privacy-conscious-user" \
  --description="Custom panel for privacy feature testing"
```

### Use Your Custom Panel

```bash
research-cli research panel run \
  --panel=my-focus-group \
  --question="How do you feel about end-to-end encryption?"
```

### Delete a Custom Panel

```bash
research-cli research panel delete my-focus-group
```

---

## Best Practices

### Choosing the Right Panel

| Research Goal | Recommended Panel |
|--------------|-------------------|
| General product feedback | `general-population` |
| New feature testing | `tech-adopters` |
| Identifying concerns/risks | `skeptics-critics` |
| Advanced feature validation | `power-users` |
| Specific audience testing | Create custom panel |

### Writing Effective Questions

**Good questions**:
- "What do you think of this feature?" (open-ended)
- "What concerns would you have about using this?" (targeted)
- "How would this fit into your daily routine?" (context-rich)

**Questions to avoid**:
- "Isn't this a great feature?" (leading)
- "Feature A or B?" (too narrow for panel research)
- Very long, multi-part questions (split into separate sessions)

### Interpreting Results

1. **High consensus + positive sentiment**: Strong signal to proceed
2. **High divergence**: Different user types have different needs
3. **Low consistency scores**: Responses may not reflect persona traits
4. **Strong negative themes**: Important concerns to address

---

## Troubleshooting

### Panel execution is slow
- This is normal for larger panels (10+ personas)
- Use `--quiet` flag for non-interactive scripts
- Consider using smaller panels for iterative testing

### Some personas failed
- System continues with successful personas
- Check warnings for failure reasons
- Retry with `--timeout` increased

### Quality warnings
- Consistency below 70%: Response may not reflect persona
- High divergence: Consider if aggregation is appropriate
- Low theme confidence: Responses may be too varied to aggregate

---

## Example Workflow

```bash
# 1. Quick exploratory research with tech adopters
research-cli research panel run -p tech-adopters \
  -q "First impressions of AI-powered meeting notes?"

# 2. Deep dive with skeptics to find concerns
research-cli research panel run -p skeptics-critics \
  -q "What concerns would you have about AI listening to your meetings?" \
  --report concerns-report.md

# 3. Full panel research with export
research-cli research panel run -p general-population \
  -q "Would you use an AI assistant for meeting notes? Why or why not?" \
  --output full-research.json \
  --report final-report.md
```

---

## Next Steps

- Review the [CLI Interface Contract](contracts/cli-interface.md) for complete command reference
- See [Data Model](data-model.md) for understanding the data structures
- Check the [Research Document](research.md) for technical decision rationale
