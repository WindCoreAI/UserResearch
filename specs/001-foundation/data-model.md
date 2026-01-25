# Data Model: Phase 0 Foundation

**Date**: 2026-01-24
**Feature**: Phase 0 Foundation

## Entity Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          Persona                                 │
│  ┌───────────────┐  ┌────────────────────┐  ┌────────────────┐  │
│  │  Demographics │  │ PsychologicalProfile│  │   Background   │  │
│  └───────────────┘  └────────────────────┘  └────────────────┘  │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    │                   │                        │
│              ┌─────┴─────┐    ┌───────┴───────┐                │
│              │  BigFive  │    │ SchwartzValues │                │
│              └───────────┘    └───────────────┘                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  ResponseCalibration                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ generates
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SubagentPrompt                              │
└─────────────────────────────────────────────────────────────────┘
```

## Entities

### Persona (Root Entity)

The top-level entity representing a synthetic user.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier (kebab-case, e.g., "tech-early-adopter") |
| version | string | Yes | Semantic version (e.g., "1.0.0") |
| name | string | Yes | Human-readable display name |
| demographics | Demographics | Yes | Demographic information |
| psychological_profile | PsychologicalProfile | Yes | Personality and values |
| background | Background | Yes | Life context and experiences |
| response_calibration | ResponseCalibration | Yes | Behavior tuning settings |
| metadata | Metadata | No | Optional tracking information |

**Validation Rules**:
- `id` must be unique within the persona library
- `id` must match pattern: `^[a-z0-9]+(-[a-z0-9]+)*$` (kebab-case)
- `version` must follow semver: `^\\d+\\.\\d+\\.\\d+$`
- `name` must be 1-100 characters

### Demographics

Demographic characteristics of the persona.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| age | integer | Yes | Age in years (18-100) |
| gender | string | Yes | Gender identity |
| location | string | Yes | Geographic location (city, region, country) |
| occupation | Occupation | Yes | Job details |
| education | string | No | Highest education level |
| income_bracket | string | No | Relative income level |
| family_status | string | No | Family/relationship status |

**Validation Rules**:
- `age` must be between 18 and 100 (adult users only)
- `location` must be non-empty

### Occupation

Employment details for the persona.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Job title |
| industry | string | No | Industry sector |
| organization | string | No | Company/organization name |
| years_experience | integer | No | Years in current field |

**Validation Rules**:
- `title` must be non-empty
- `years_experience` must be >= 0 if provided

### PsychologicalProfile

Core psychological characteristics.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| big_five | BigFive | Yes | Big Five personality traits |
| schwartz_values | SchwartzValues | Yes | Value priorities |
| tech_adoption | TechAdoptionCategory | Yes | Technology adoption category |

### BigFive

The Five Factor Model personality traits.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| openness | integer | Yes | Openness to experience (1-10) |
| conscientiousness | integer | Yes | Organization and dependability (1-10) |
| extraversion | integer | Yes | Social energy and assertiveness (1-10) |
| agreeableness | integer | Yes | Cooperation and trust (1-10) |
| neuroticism | integer | Yes | Emotional reactivity (1-10) |

**Validation Rules**:
- All fields must be integers between 1 and 10 inclusive
- All five fields are required (no partial Big Five profiles)

**Behavioral Implications** (for prompt generation):

| Score Range | Openness | Conscientiousness | Extraversion | Agreeableness | Neuroticism |
|-------------|----------|-------------------|--------------|---------------|-------------|
| 1-3 (Low) | Conventional, practical | Flexible, spontaneous | Reserved, reflective | Skeptical, competitive | Calm, stable |
| 4-6 (Medium) | Balanced | Moderate | Ambiverted | Diplomatic | Moderate reactivity |
| 7-10 (High) | Creative, curious | Disciplined, organized | Outgoing, energetic | Trusting, cooperative | Anxious, reactive |

### SchwartzValues

Value priorities from Schwartz's Theory of Basic Values.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| primary | list[SchwartzValue] | Yes | Primary value priorities (min 2) |
| secondary | list[SchwartzValue] | No | Secondary values |
| conflicts | list[string] | No | Described value tensions |

**Validation Rules**:
- `primary` must contain at least 2 values
- Values in `primary` and `secondary` must not overlap
- `conflicts` entries should describe tensions between values

### SchwartzValue (Enum)

The ten universal values:

| Value | Description | Opposite |
|-------|-------------|----------|
| `self_direction` | Independence, creativity, curiosity | conformity |
| `stimulation` | Excitement, novelty, challenge | security |
| `hedonism` | Pleasure, enjoyment | (between openness and self-enhancement) |
| `achievement` | Personal success, competence | benevolence |
| `power` | Dominance, control, wealth | universalism |
| `security` | Safety, stability, order | stimulation |
| `conformity` | Restraint, obedience to norms | self_direction |
| `tradition` | Respect for customs, culture | self_direction |
| `benevolence` | Welfare of close others | achievement |
| `universalism` | Tolerance, equality for all | power |

### TechAdoptionCategory (Enum)

Rogers' Diffusion of Innovations categories:

| Value | Population % | Characteristics |
|-------|--------------|-----------------|
| `innovator` | 2.5% | Risk-tolerant, first to try, tech-savvy |
| `early_adopter` | 13.5% | Opinion leader, strategic adoption |
| `early_majority` | 34% | Pragmatic, waits for proof |
| `late_majority` | 34% | Skeptical, adopts due to peer pressure |
| `laggard` | 16% | Traditional, resists change |

### Background

Life context and narrative elements.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| life_stage | string | Yes | Current life phase description |
| key_experiences | list[string] | No | Formative experiences |
| pain_points | list[string] | Yes | Current frustrations/challenges |
| goals | list[string] | Yes | Aspirations and objectives |

**Validation Rules**:
- `life_stage` must be non-empty
- `pain_points` must contain at least 1 item
- `goals` must contain at least 1 item

### DomainContext

Domain-specific knowledge and experience (optional section within Background).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| relevant_experience | list[string] | No | Prior experience with domain |
| knowledge_level | dict[string, string] | No | Expertise levels by topic |

### ResponseCalibration

Settings that tune how the persona responds.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| verbosity | VerbosityLevel | Yes | Response length tendency |
| emotional_expressiveness | ExpressivenessLevel | Yes | Emotional display level |
| criticism_tendency | CriticismLevel | Yes | Positive vs critical lean |
| certainty_level | CertaintyLevel | No | Confidence in opinions |

### VerbosityLevel (Enum)

| Value | Description |
|-------|-------------|
| `concise` | Brief, to-the-point responses |
| `moderate` | Balanced detail level |
| `detailed` | Thorough, elaborate responses |

### ExpressivenessLevel (Enum)

| Value | Description |
|-------|-------------|
| `reserved` | Minimal emotional display |
| `moderate` | Natural emotional expression |
| `expressive` | Strong emotional display |

### CriticismLevel (Enum)

| Value | Description |
|-------|-------------|
| `positive` | Tends toward optimistic feedback |
| `balanced` | Mix of positive and negative |
| `critical` | Tends toward skeptical feedback |

### CertaintyLevel (Enum)

| Value | Description |
|-------|-------------|
| `certain` | Strong, definitive opinions |
| `questioning` | Exploratory, considers alternatives |
| `uncertain` | Hesitant, acknowledges limitations |

### Metadata (Optional)

Tracking and organizational information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| created_date | string (ISO date) | No | Creation date |
| created_by | string | No | Creator identifier |
| panel_memberships | list[string] | No | Panels this persona belongs to |
| tags | list[string] | No | Searchable tags |

## SubagentPrompt (Output Entity)

Generated prompt for Claude Code Task tool invocation.

| Field | Type | Description |
|-------|------|-------------|
| persona_id | string | Source persona identifier |
| prompt_text | string | Complete prompt content |
| generated_at | string (ISO datetime) | Generation timestamp |

**Prompt Structure** (sections in generated text):
1. Identity (name, demographics)
2. Personality (Big Five with behavioral guidance)
3. Values (Schwartz values with conflict notes)
4. Background (life stage, experiences, pain points, goals)
5. Response Guidelines (calibration settings)
6. Anti-Sycophancy Instructions (critical response requirements)

## State Transitions

Personas in Phase 0 have simple state:

```
[Draft] ──validate──▶ [Valid] ──generate──▶ [Prompt Ready]
    │                    │
    └──errors────────────┘
```

| State | Description | Transitions |
|-------|-------------|-------------|
| Draft | File exists but not validated | → Valid (on successful validation) |
| Valid | Passes all schema validations | → Prompt Ready (on prompt generation) |
| Prompt Ready | Subagent prompt has been generated | (terminal for Phase 0) |

## Sample YAML Structure

```yaml
persona:
  id: tech-early-adopter
  version: "1.0.0"
  name: "Alex Chen"

  demographics:
    age: 32
    gender: "non-binary"
    location: "San Francisco, CA"
    occupation:
      title: "Senior Software Engineer"
      industry: "Technology"
      organization: "Startup"
      years_experience: 8
    education: "MS Computer Science"
    income_bracket: "upper-middle"
    family_status: "single"

  psychological_profile:
    big_five:
      openness: 9
      conscientiousness: 7
      extraversion: 6
      agreeableness: 5
      neuroticism: 4
    schwartz_values:
      primary:
        - self_direction
        - achievement
      secondary:
        - stimulation
      conflicts:
        - "Values independence but works on team-dependent projects"
    tech_adoption: early_adopter

  background:
    life_stage: "Established professional exploring entrepreneurship"
    key_experiences:
      - "Built and sold a side project"
      - "Early adopter of AI coding assistants"
      - "Burned out at previous FAANG job"
    pain_points:
      - "Too many productivity tools that don't integrate"
      - "Skeptical of AI hype after seeing failures"
      - "Wants depth over surface-level features"
    goals:
      - "Find tools that genuinely save time"
      - "Build a personal knowledge system"
      - "Eventually start own company"

  response_calibration:
    verbosity: moderate
    emotional_expressiveness: moderate
    criticism_tendency: balanced
    certainty_level: questioning

  metadata:
    created_date: "2026-01-24"
    created_by: "foundation-team"
    panel_memberships:
      - tech_professionals
      - early_adopters
    tags:
      - engineer
      - startup
      - ai-aware
```
