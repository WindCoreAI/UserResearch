# Quickstart Guide: Single Persona Research Sessions

**Feature**: 002-single-persona-mvp
**Prerequisites**: Phase 0 Foundation installed and working

## Overview

This guide covers running single-persona research sessions using synthetic users. You'll learn to ask questions to AI-powered personas and interpret the quality-validated responses.

---

## Prerequisites

Ensure Phase 0 is working:

```bash
# Verify CLI is installed
research-cli --version
# Expected: research-cli, version 0.2.0

# List available personas
research-cli persona list
# Expected: 5 personas (tech-early-adopter, skeptical-late-adopter, etc.)
```

---

## Your First Research Session

### Step 1: Choose a Persona

View available personas:

```bash
research-cli persona list
```

Output:
```
ID                        NAME                 ADOPTION        AGE
------------------------------------------------------------------------
tech-early-adopter        Alex Chen            early_adopter    32
skeptical-late-adopter    Margaret Wilson      late_majority    58
busy-professional         David Park           early_majority   42
privacy-conscious-user    Sarah Martinez       late_majority    35
power-user                Jamie Thompson       innovator        27

5 personas found
```

### Step 2: Review Persona Details

Before asking questions, understand who you're talking to:

```bash
research-cli persona show tech-early-adopter
```

This shows demographics, personality traits (Big Five), values, and response style.

### Step 3: Run a Research Session

Ask an open-ended question:

```bash
research-cli research single \
  --persona tech-early-adopter \
  --question "What would make you excited about a new daily journaling app?"
```

The persona subagent will process your question and respond in character.

### Step 4: Interpret the Results

The output includes:
- **Sentiment**: Overall tone (positive/negative/mixed/neutral)
- **Concerns**: Issues the persona raised
- **Suggestions**: Ideas for improvement
- **Quality Metrics**: How well the response matches persona traits

---

## Question Types

### Open-Ended Questions (Default)

Best for exploratory research:

```bash
research-cli research single \
  --persona skeptical-late-adopter \
  --question "What concerns would you have about using AI to help write emails?"
```

### Rating Questions

Get numeric feedback with justification:

```bash
research-cli research single \
  --persona busy-professional \
  --question "How likely would you be to pay for this premium feature?" \
  --type rating \
  --scale 1-10
```

### Multiple Choice Questions

Test specific options:

```bash
research-cli research single \
  --persona privacy-conscious-user \
  --question "Which data sharing option would you prefer?" \
  --type choice \
  --options "Share anonymized data,Share with explicit consent only,Never share any data,Depends on the benefit"
```

---

## Understanding Quality Metrics

Every session includes quality validation:

```
📈 Quality Metrics
┌─────────────────────┬───────┐
│ Consistency Score   │ 87.5% │
│ Sycophancy Warning  │ No    │
│ Quality Gates       │ PASS  │
└─────────────────────┴───────┘
```

### Consistency Score

Measures how well the response matches the persona's defined traits:
- **>85%**: High confidence - response strongly aligns with persona
- **70-85%**: Acceptable - response generally matches persona
- **<70%**: Warning - response may not reflect persona accurately

### Sycophancy Warning

Flags when responses are unrealistically positive:
- **No**: Response includes genuine criticism and nuance
- **Yes**: Response may be overly agreeable - interpret with caution

### Quality Gates

- **PASS**: Response meets all quality thresholds
- **WARN**: One or more metrics below threshold - interpret carefully

---

## Saving Research Sessions

Export sessions for later analysis:

```bash
# Save to JSON file
research-cli research single \
  --persona tech-early-adopter \
  --question "What's your first impression of this design?" \
  --output ./research/session-001.json

# View saved session
cat ./research/session-001.json | jq .
```

---

## Comparing Personas

Run the same question across different personas to see varied perspectives:

```bash
# Early adopter perspective
research-cli research single \
  --persona tech-early-adopter \
  --question "Would you try a new AI-powered calendar assistant?" \
  --output ./research/calendar-early-adopter.json

# Skeptic perspective
research-cli research single \
  --persona skeptical-late-adopter \
  --question "Would you try a new AI-powered calendar assistant?" \
  --output ./research/calendar-skeptic.json

# Privacy-conscious perspective
research-cli research single \
  --persona privacy-conscious-user \
  --question "Would you try a new AI-powered calendar assistant?" \
  --output ./research/calendar-privacy.json
```

---

## Best Practices

### Do:
- **Be specific** in your questions - vague questions get vague answers
- **Review persona traits** before interpreting responses
- **Save sessions** for important research you'll reference later
- **Compare personas** to understand different user perspectives
- **Check quality metrics** before drawing conclusions

### Don't:
- **Lead the persona** with biased questions ("Don't you love this feature?")
- **Ignore quality warnings** - they indicate potential issues
- **Present as real research** - always disclose synthetic nature
- **Skip validation** for important decisions - test with real users too

---

## Troubleshooting

### "Persona not found"

Check the persona ID matches exactly:
```bash
research-cli persona list  # See available IDs
```

### Session timeout

Increase timeout for complex questions:
```bash
research-cli research single --timeout 60 ...
```

### Quality warnings

If consistency score is low:
1. Check if the question is relevant to the persona's expertise
2. Try rephrasing the question
3. Consider if the persona is appropriate for this topic

---

## Next Steps

- **Explore all 5 personas** - understand their different perspectives
- **Test your product concepts** - get early synthetic feedback
- **Document your findings** - save sessions and compare results
- **Wait for Phase 2** - panel research with multiple personas simultaneously

---

## Limitations

Remember that synthetic user research has inherent limitations:
- Responses may trend toward being overly positive (sycophancy)
- Variance is narrower than real human populations
- Cannot capture authentic lived experiences

**Always validate critical findings with real users before making major product decisions.**
