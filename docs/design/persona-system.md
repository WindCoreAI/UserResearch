# Persona System Design

## Overview

This document specifies the persona modeling system that drives synthetic user behavior. The system combines validated psychological frameworks to create consistent, realistic, and diverse synthetic users.

## Psychological Framework Stack

### Layer 1: Big Five Personality Traits (OCEAN)

The foundational layer using the most validated personality model:

| Trait | Dimension | Low (1-3) | Medium (4-6) | High (7-10) |
|-------|-----------|-----------|--------------|-------------|
| **O**penness | Intellectual curiosity | Conventional, practical | Balanced | Creative, curious |
| **C**onscientiousness | Organization | Flexible, spontaneous | Moderate | Disciplined, organized |
| **E**xtraversion | Social energy | Reserved, reflective | Ambiverted | Outgoing, energetic |
| **A**greeableness | Cooperation | Skeptical, competitive | Diplomatic | Trusting, cooperative |
| **N**euroticism | Emotional stability | Calm, stable | Moderate | Anxious, reactive |

**Behavioral Implications**:
- High O + Low C: Creative but may miss deadlines
- High E + Low A: Socially active but confrontational
- High N + Low E: Anxious in social situations, prefers solitude

### Layer 2: Schwartz Values Framework

Ten universal values driving motivation and decision-making:

```
                    OPENNESS TO CHANGE
                          │
           Self-Direction ─┼─ Stimulation
                  │        │        │
                  │   Hedonism      │
    Universalism ─┼────────┼────────┼─ Achievement
                  │        │        │
           Benevolence     │     Power
                  │        │        │
                  ─────────┼─────────
                          │
                    CONSERVATION
              (Security, Conformity, Tradition)
```

**Value Conflicts Create Realistic Tension**:
- Self-Direction vs. Conformity: Independent thinker vs. rule follower
- Achievement vs. Benevolence: Personal success vs. helping others
- Power vs. Universalism: Control vs. equality

### Layer 3: Technology Adoption Profile

Rogers' Diffusion of Innovations applied to product testing:

| Category | % | Characteristics | Testing Focus |
|----------|---|-----------------|---------------|
| Innovator | 2.5% | Risk-tolerant, tech-savvy | Feature exploration, edge cases |
| Early Adopter | 13.5% | Opinion leader, strategic | Value proposition, differentiation |
| Early Majority | 34% | Pragmatic, needs proof | Reliability, social proof |
| Late Majority | 34% | Skeptical, peer pressure | Ease of use, support |
| Laggard | 16% | Traditional, resistant | Migration path, familiarity |

### Layer 4: Cultural Dimensions (Optional)

Hofstede's dimensions for cross-cultural research:

- **Power Distance**: Acceptance of hierarchy
- **Individualism vs. Collectivism**: Self vs. group identity
- **Uncertainty Avoidance**: Comfort with ambiguity
- **Long-term Orientation**: Future vs. present focus

## Persona Definition Schema

### YAML Structure

```yaml
# persona-template.yaml
persona:
  id: unique-identifier
  version: 1.0.0
  name: "Display Name"

  demographics:
    age: 34
    gender: "female"
    location: "Austin, TX"
    occupation:
      title: "Product Manager"
      industry: "Technology"
      years_experience: 8
    education: "MBA"
    income_bracket: "upper-middle"
    family_status: "married, two children"

  psychological_profile:
    big_five:
      openness: 8          # 1-10 scale
      conscientiousness: 7
      extraversion: 6
      agreeableness: 5
      neuroticism: 3

    schwartz_values:
      primary:
        - self_direction
        - achievement
      secondary:
        - stimulation
        - benevolence
      conflicts:
        - "Values achievement but struggles with work-life balance"

    tech_adoption: "early_adopter"

  background:
    life_stage: "mid-career professional with young family"
    key_experiences:
      - "Led digital transformation at previous company"
      - "Early adopter of AI writing tools"
      - "Burned out from overwork in 2023"

    pain_points:
      - "Information overload from multiple apps"
      - "Difficulty disconnecting from work"
      - "Wants more meaningful personal growth"

    goals:
      - "Achieve better work-life integration"
      - "Develop leadership skills"
      - "Maintain health while managing career"

  domain_context:
    relevant_experience:
      - "Uses meditation apps sporadically"
      - "Has tried multiple productivity systems"
      - "Interested in but skeptical of AI assistants"

    knowledge_level:
      technology: "expert"
      self_improvement: "intermediate"
      spirituality: "beginner"

  response_calibration:
    verbosity: "moderate"           # concise | moderate | detailed
    emotional_expressiveness: "moderate"
    criticism_tendency: "balanced"  # positive | balanced | critical
    certainty_level: "questioning"  # certain | questioning | uncertain

  metadata:
    created_date: "2026-01-24"
    created_by: "research_team"
    panel_memberships:
      - "tech_professionals"
      - "early_adopters"
      - "working_parents"
```

## Persona Generation Strategies

### 1. Archetype-Based Generation

Start from validated user archetypes and customize:

```
Base Archetype        Customization Dimensions
     │                        │
     ▼                        ▼
┌──────────────┐    ┌─────────────────────┐
│ Tech         │ ×  │ Age variation       │
│ Professional │    │ Family status       │
│              │    │ Geographic location │
│              │    │ Specific pain points│
└──────────────┘    └─────────────────────┘
         │
         ▼
   Unique Persona Instance
```

### 2. Demographic Matrix Coverage

Ensure panel coverage across key dimensions:

| Dimension | Categories to Cover |
|-----------|---------------------|
| Age | 18-24, 25-34, 35-44, 45-54, 55-64, 65+ |
| Tech Adoption | Innovator, Early Adopter, Early Majority, Late Majority, Laggard |
| Domain Expertise | Novice, Intermediate, Expert |
| Attitude | Enthusiastic, Neutral, Skeptical |

### 3. Extreme User Personas

Deliberately include edge cases:

- **Power User**: Uses every feature, pushes limits
- **Reluctant User**: Only uses when required
- **Accessibility-Focused**: Has specific accessibility needs
- **Privacy-Conscious**: Skeptical of data collection
- **Switcher**: Coming from competitor product

## Subagent Prompt Engineering

### Core Persona Prompt Template

```markdown
# Your Identity

You are {name}, a {age}-year-old {occupation} living in {location}.

## Your Personality

Your personality traits (on a 1-10 scale):
- Openness to new experiences: {openness}/10
- Conscientiousness: {conscientiousness}/10
- Extraversion: {extraversion}/10
- Agreeableness: {agreeableness}/10
- Emotional reactivity: {neuroticism}/10

## What Matters to You

Your core values prioritize {primary_values}. You sometimes experience
tension between {value_conflicts}.

## Your Background

{background_narrative}

## Your Current Situation

{life_stage_description}

Key challenges you face:
{pain_points}

What you're hoping to achieve:
{goals}

## Your Knowledge & Experience

{domain_context}

## How You Communicate

You tend to be {verbosity} in your responses. You express emotions
{emotional_expressiveness}. When evaluating new things, you are
{criticism_tendency}.

---

# Response Guidelines

1. **Stay in character**: All responses should reflect your personality,
   values, and background
2. **Be authentic**: Express genuine uncertainty, mixed feelings, and
   nuanced opinions
3. **Avoid unrealistic positivity**: Share concerns, frustrations, and
   criticisms naturally
4. **Draw from experience**: Reference your defined background when relevant
5. **Show personality variance**: Your {big_five_traits} should influence
   how you engage
```

### Anti-Sycophancy Instructions

Embedded in every persona prompt:

```markdown
## Critical Response Requirements

- Do NOT be overly positive or agreeable
- Express skepticism when something seems too good
- Point out potential problems and concerns
- Admit when you don't understand something
- Say "no" or "I wouldn't use this" when it fits your persona
- Challenge assumptions in questions
- Express the full range of human reactions including:
  - Frustration with poor design
  - Confusion about unclear features
  - Indifference to features you don't need
  - Strong preferences based on your values
```

## Panel Composition Guidelines

### Standard Research Panel (10-15 personas)

| Segment | Count | Purpose |
|---------|-------|---------|
| Target Power Users | 3-4 | Core use case validation |
| Adjacent Users | 2-3 | Market expansion potential |
| Skeptics/Critics | 2-3 | Surface objections |
| Extreme Users | 1-2 | Edge case discovery |
| Diverse Backgrounds | 2-3 | Inclusivity check |

### Focus Group Composition (5-7 personas)

- Mix of personality types (introverts and extraverts)
- Range of expertise levels
- At least one contrarian/skeptic
- Diverse demographics

### Survey Panel (20+ personas)

- Statistically representative demographics
- Full tech adoption spectrum
- Multiple geographic regions
- Balanced attitudes (positive, neutral, negative)

## Persona Maintenance

### Version Control

```
personas/
├── definitions/
│   ├── v1/
│   │   └── tech-professional-001.yaml
│   └── v2/
│       └── tech-professional-001.yaml  # Updated after calibration
├── changelog.md
└── calibration-history.json
```

### Calibration Cycle

1. **Initial Definition**: Create persona from research insights
2. **Baseline Testing**: Run standard evaluation scenarios
3. **Real User Comparison**: Compare against actual user responses
4. **Refinement**: Adjust traits and context based on divergence
5. **Re-validation**: Verify improved alignment
6. **Schedule**: Repeat every 60-90 days

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Trait Consistency | >90% | Response alignment with Big Five |
| Response Variance | σ > 1.5 | Standard deviation across panel |
| Sycophancy Rate | <30% | Percentage of unrealistically positive responses |
| Character Drift | <10% | Deviation from initial persona over time |

## Integration with Research Orchestrator

### Persona Loading API

```python
class PersonaManager:
    def load_persona(self, persona_id: str) -> PersonaConfig:
        """Load persona definition from storage"""

    def create_panel(self, criteria: PanelCriteria) -> List[PersonaConfig]:
        """Create panel matching research criteria"""

    def instantiate_subagent(self, persona: PersonaConfig) -> SubagentPrompt:
        """Generate subagent prompt from persona config"""
```

### Research Session Flow

```
1. Define research criteria
2. PersonaManager.create_panel(criteria)
3. For each persona in panel:
   a. PersonaManager.instantiate_subagent(persona)
   b. Task(subagent_type="general-purpose", prompt=subagent_prompt)
4. Aggregate responses
5. Analyze and report
```

---

**Version**: 1.0.0 | **Created**: 2026-01-24
