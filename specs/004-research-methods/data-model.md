# Data Model: Research Methods

**Feature**: 004-research-methods
**Date**: 2026-01-26
**Status**: Complete

## Overview

This document defines the data models for Survey, Interview, and Focus Group research methods. All models follow existing Pydantic patterns from Phase 0/1/2.

---

## 1. Enums (Extend `src/models/enums.py`)

### ResearchMethodType

```python
class ResearchMethodType(str, Enum):
    """Type of research method being conducted."""
    SURVEY = "survey"
    INTERVIEW = "interview"
    FOCUS_GROUP = "focus_group"
    SINGLE = "single"  # Existing single-question method
    PANEL = "panel"    # Existing panel method
```

### SurveyQuestionType

```python
class SurveyQuestionType(str, Enum):
    """Types of survey questions."""
    RATING = "rating"
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"
```

### InterviewProbeType

```python
class InterviewProbeType(str, Enum):
    """Types of interview probing strategies."""
    ELABORATION = "elaboration"     # "Can you tell me more about that?"
    CLARIFICATION = "clarification" # "What do you mean by...?"
    EXAMPLE = "example"             # "Can you give me an example?"
    FEELING = "feeling"             # "How did that make you feel?"
```

### DiscussionInteractionType

```python
class DiscussionInteractionType(str, Enum):
    """Types of interactions in focus group discussions."""
    AGREEMENT = "agreement"
    DISAGREEMENT = "disagreement"
    BUILDING_ON = "building_on"
    QUESTION = "question"
    NEW_POINT = "new_point"
```

---

## 2. Survey Models (`src/models/survey.py`)

### SurveyQuestion

```python
class SurveyQuestion(BaseModel):
    """A single question within a survey."""
    id: str = Field(..., pattern=r"^[a-z0-9-]+$", description="Question identifier")
    text: str = Field(..., min_length=1, max_length=500, description="Question text")
    type: SurveyQuestionType
    required: bool = Field(default=True)

    # Type-specific fields
    scale_min: int | None = Field(default=None, ge=1, le=10)
    scale_max: int | None = Field(default=None, ge=1, le=10)
    scale_labels: dict[int, str] | None = Field(default=None, description="Optional labels for scale points")
    options: list[str] | None = Field(default=None, min_length=2, max_length=10)

    @model_validator(mode='after')
    def validate_type_fields(self) -> 'SurveyQuestion':
        if self.type == SurveyQuestionType.RATING:
            if self.scale_min is None or self.scale_max is None:
                raise ValueError("Rating questions require scale_min and scale_max")
            if self.scale_min >= self.scale_max:
                raise ValueError("scale_min must be less than scale_max")
        elif self.type == SurveyQuestionType.MULTIPLE_CHOICE:
            if not self.options:
                raise ValueError("Multiple choice questions require options")
        return self
```

### Survey

```python
class Survey(BaseModel):
    """A complete survey protocol definition."""
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    questions: list[SurveyQuestion] = Field(..., min_length=1, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('questions')
    @classmethod
    def validate_unique_question_ids(cls, v: list[SurveyQuestion]) -> list[SurveyQuestion]:
        ids = [q.id for q in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Question IDs must be unique within a survey")
        return v
```

### SurveyResponse

```python
class SurveyResponse(BaseModel):
    """Response to a single survey question."""
    question_id: str
    question_type: SurveyQuestionType
    raw_response: str

    # Parsed values (one will be populated based on type)
    rating_value: int | None = None
    selected_option: str | None = None
    text_response: str | None = None

    # Metadata
    response_time_ms: int | None = None
    validation_warnings: list[str] = Field(default_factory=list)
    is_valid: bool = True
```

### SurveyResult

```python
class SurveyResult(BaseModel):
    """Complete result from a survey execution."""
    survey_id: str
    survey_version: str
    persona_id: str
    responses: list[SurveyResponse]

    started_at: datetime
    completed_at: datetime
    total_time_ms: int

    completion_rate: float = Field(ge=0.0, le=1.0, description="Fraction of questions answered")
    quality_metrics: QualityMetrics | None = None
```

### SurveyAggregation

```python
class RatingStatistics(BaseModel):
    """Statistical summary of rating responses."""
    question_id: str
    count: int
    mean: float
    median: float
    stdev: float
    min_value: int
    max_value: int
    distribution: dict[int, int]  # value -> count

class MultipleChoiceStatistics(BaseModel):
    """Statistical summary of multiple choice responses."""
    question_id: str
    count: int
    selection_counts: dict[str, int]  # option -> count
    selection_percentages: dict[str, float]  # option -> percentage

class SurveyAggregation(BaseModel):
    """Aggregated results from panel survey execution."""
    survey_id: str
    panel_id: str
    total_respondents: int

    rating_statistics: list[RatingStatistics]
    multiple_choice_statistics: list[MultipleChoiceStatistics]
    open_ended_themes: list[Theme]  # Reuse from aggregation.py

    segment_analysis: dict[str, Any] | None = None  # Optional breakdown by persona attributes
```

---

## 3. Interview Models (`src/models/interview.py`)

### InterviewProbe

```python
class InterviewProbe(BaseModel):
    """A probing question configuration."""
    type: InterviewProbeType
    trigger: str | None = Field(default=None, description="Keyword or condition that triggers this probe")
    question_template: str = Field(..., description="Template for the probe question")
```

### InterviewQuestion

```python
class InterviewQuestion(BaseModel):
    """A single question within an interview section."""
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    text: str = Field(..., min_length=1, max_length=1000)
    probes: list[InterviewProbe] = Field(default_factory=list, max_length=3)
    allow_followups: bool = Field(default=True)
    max_followup_depth: int = Field(default=3, ge=1, le=5)
```

### InterviewSection

```python
class InterviewSection(BaseModel):
    """A thematic section within an interview guide."""
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    questions: list[InterviewQuestion] = Field(..., min_length=1, max_length=10)
    transition_prompt: str | None = Field(default=None, description="Prompt to use when transitioning to this section")
```

### InterviewGuide

```python
class InterviewGuide(BaseModel):
    """Complete interview protocol definition."""
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(..., min_length=1, max_length=200)
    topic: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=1000)

    sections: list[InterviewSection] = Field(..., min_length=1, max_length=10)

    # Configuration
    min_response_length: int = Field(default=50, ge=10, description="Minimum chars before probing")
    default_max_followups: int = Field(default=3, ge=1, le=5)

    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### InterviewExchange

```python
class InterviewExchange(BaseModel):
    """A single question-response exchange in an interview."""
    question_id: str
    question_text: str
    response: str
    timestamp: datetime

    # Follow-up chain
    followups: list['InterviewExchange'] = Field(default_factory=list)
    probe_used: InterviewProbeType | None = None

    # Quality
    response_length: int
    response_time_ms: int | None = None
```

### SectionTranscript

```python
class SectionTranscript(BaseModel):
    """Transcript of a single interview section."""
    section_id: str
    section_name: str
    exchanges: list[InterviewExchange]

    started_at: datetime
    completed_at: datetime
    total_exchanges: int  # Including follow-ups
```

### InterviewTranscript

```python
class InterviewTranscript(BaseModel):
    """Complete transcript from an interview session."""
    guide_id: str
    guide_version: str
    persona_id: str
    persona_name: str

    sections: list[SectionTranscript]

    started_at: datetime
    completed_at: datetime
    total_time_ms: int

    # Analysis
    identified_themes: list[Theme] = Field(default_factory=list)
    key_quotes: list[str] = Field(default_factory=list)
    followup_relevance_score: float | None = Field(default=None, ge=0.0, le=1.0)

    quality_metrics: QualityMetrics | None = None
```

---

## 4. Focus Group Models (`src/models/focus_group.py`)

### FocusGroupConfig

```python
class FocusGroupConfig(BaseModel):
    """Configuration for focus group dynamics."""
    max_rounds: int = Field(default=3, ge=1, le=10, description="Number of discussion rounds")
    turns_per_round: int = Field(default=6, ge=4, le=10, description="Turns per round (usually = num personas)")
    moderator_prompts_enabled: bool = Field(default=True)
    allow_cross_references: bool = Field(default=True, description="Allow personas to reference each other")
```

### FocusGroup

```python
class FocusGroup(BaseModel):
    """Focus group protocol definition."""
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

    persona_ids: list[str] = Field(..., min_length=4, max_length=6)
    discussion_topics: list[str] = Field(..., min_length=1, max_length=5)

    config: FocusGroupConfig = Field(default_factory=FocusGroupConfig)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('persona_ids')
    @classmethod
    def validate_unique_personas(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("Focus group must have unique persona IDs")
        return v
```

### DiscussionReference

```python
class DiscussionReference(BaseModel):
    """A reference to another participant's statement."""
    referenced_persona_id: str
    referenced_turn_index: int
    reference_type: DiscussionInteractionType
    quote_fragment: str | None = Field(default=None, max_length=200)
```

### DiscussionTurn

```python
class DiscussionTurn(BaseModel):
    """A single turn in a focus group discussion."""
    turn_index: int
    round_number: int
    persona_id: str
    persona_name: str

    statement: str
    timestamp: datetime

    # Interaction analysis
    references: list[DiscussionReference] = Field(default_factory=list)
    interaction_type: DiscussionInteractionType = Field(default=DiscussionInteractionType.NEW_POINT)

    # Sentiment on current topic
    sentiment: Sentiment | None = None
```

### OpinionShift

```python
class OpinionShift(BaseModel):
    """Record of a persona changing their position during discussion."""
    persona_id: str
    persona_name: str
    topic: str

    from_turn_index: int
    to_turn_index: int

    original_position: str
    new_position: str

    trigger_reference: DiscussionReference | None = None  # What caused the shift
```

### DiscussionLog

```python
class DiscussionLog(BaseModel):
    """Complete log of a focus group discussion."""
    group_id: str
    group_version: str
    topic: str

    participants: list[dict]  # [{persona_id, persona_name, tech_adoption}]
    turns: list[DiscussionTurn]

    started_at: datetime
    completed_at: datetime
    total_time_ms: int
    total_rounds: int

    # Analysis
    consensus_points: list[ConsensusPoint] = Field(default_factory=list)
    divergence_points: list[DivergencePoint] = Field(default_factory=list)
    opinion_shifts: list[OpinionShift] = Field(default_factory=list)
    interaction_summary: dict[str, int] = Field(default_factory=dict)  # interaction_type -> count

    quality_metrics: QualityMetrics | None = None
```

---

## 5. Protocol Models (`src/models/protocol.py`)

### ResearchProtocol (Base)

```python
class ResearchProtocol(BaseModel):
    """Base class for all research protocols."""
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    type: ResearchMethodType
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list, max_length=10)

class SurveyProtocol(ResearchProtocol):
    """Protocol wrapper for Survey."""
    type: Literal[ResearchMethodType.SURVEY] = ResearchMethodType.SURVEY
    survey: Survey

class InterviewProtocol(ResearchProtocol):
    """Protocol wrapper for Interview Guide."""
    type: Literal[ResearchMethodType.INTERVIEW] = ResearchMethodType.INTERVIEW
    guide: InterviewGuide

class FocusGroupProtocol(ResearchProtocol):
    """Protocol wrapper for Focus Group."""
    type: Literal[ResearchMethodType.FOCUS_GROUP] = ResearchMethodType.FOCUS_GROUP
    focus_group: FocusGroup
```

---

## 6. Entity Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                     ResearchProtocol                             │
│  (id, version, type, name, description, created_at, tags)       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ type discriminator
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  SurveyProtocol  │ │InterviewProtocol │ │FocusGroupProtocol│
│    contains:     │ │    contains:     │ │    contains:     │
│     Survey       │ │  InterviewGuide  │ │   FocusGroup     │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     Survey       │ │  InterviewGuide  │ │   FocusGroup     │
│ questions: [...] │ │ sections: [...]  │ │ persona_ids: [...│
│                  │ │                  │ │ topics: [...]    │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         │ execution          │ execution          │ execution
         ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  SurveyResult    │ │InterviewTranscript│ │  DiscussionLog  │
│ responses: [...] │ │ sections: [...]  │ │ turns: [...]    │
│ aggregation:     │ │ themes: [...]    │ │ consensus: [...] │
│   (for panels)   │ │                  │ │ shifts: [...]   │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## 7. YAML Schema Examples

### Survey Protocol YAML

```yaml
protocol:
  id: feature-concept-test
  version: "1.0.0"
  type: survey
  name: "Feature Concept Test"
  description: "Evaluate user reactions to proposed feature"
  tags: [concept-testing, product-research]

survey:
  id: feature-concept-test
  version: "1.0.0"
  name: "Feature Concept Test Survey"
  questions:
    - id: likelihood-to-use
      text: "How likely are you to use this feature?"
      type: rating
      scale_min: 1
      scale_max: 10
      scale_labels:
        1: "Not at all likely"
        5: "Neutral"
        10: "Extremely likely"

    - id: primary-concern
      text: "What is your primary concern about this feature?"
      type: multiple_choice
      options:
        - "Privacy"
        - "Complexity"
        - "Cost"
        - "No concerns"

    - id: value-addition
      text: "What would make this feature more valuable to you?"
      type: open_ended
```

### Interview Guide YAML

```yaml
protocol:
  id: onboarding-experience
  version: "1.0.0"
  type: interview
  name: "Onboarding Experience Interview"
  description: "Deep-dive into user onboarding journey"
  tags: [onboarding, user-experience]

guide:
  id: onboarding-experience
  version: "1.0.0"
  name: "Onboarding Experience"
  topic: "New user onboarding flow"
  min_response_length: 50
  default_max_followups: 3

  sections:
    - id: background
      name: "Background"
      description: "Understand user's prior experience"
      questions:
        - id: similar-products
          text: "Tell me about similar products you've tried"
          probes:
            - type: elaboration
              question_template: "Can you describe what made those products memorable?"
          allow_followups: true
          max_followup_depth: 2

        - id: first-impression
          text: "What was your first impression of our product?"

    - id: experience
      name: "Onboarding Experience"
      transition_prompt: "Now let's focus on your actual experience with our onboarding..."
      questions:
        - id: first-session
          text: "Walk me through your first session"
          probes:
            - type: example
              trigger: "confused"
              question_template: "Can you give me a specific example of what confused you?"
```

### Focus Group YAML

```yaml
protocol:
  id: pricing-feedback
  version: "1.0.0"
  type: focus_group
  name: "Pricing Model Feedback"
  description: "Group discussion on proposed pricing tiers"
  tags: [pricing, market-research]

focus_group:
  id: pricing-feedback
  version: "1.0.0"
  name: "Pricing Feedback Session"
  description: "Gather diverse perspectives on pricing"

  persona_ids:
    - tech-early-adopter
    - skeptical-late-adopter
    - busy-professional
    - privacy-conscious-user

  discussion_topics:
    - "Initial reactions to proposed pricing"
    - "Value perception at each tier"
    - "Comparison to alternatives"

  config:
    max_rounds: 3
    turns_per_round: 4
    moderator_prompts_enabled: true
    allow_cross_references: true
```

---

## 8. Validation Rules Summary

| Model | Validation | Error Message |
|-------|------------|---------------|
| SurveyQuestion (rating) | scale_min < scale_max | "scale_min must be less than scale_max" |
| SurveyQuestion (mc) | options provided | "Multiple choice questions require options" |
| Survey | unique question IDs | "Question IDs must be unique within a survey" |
| InterviewGuide | 1-10 sections | "Interview must have 1-10 sections" |
| FocusGroup | 4-6 unique personas | "Focus group must have 4-6 unique personas" |
| ResearchProtocol | kebab-case ID | "Protocol ID must be kebab-case" |
| ResearchProtocol | semver version | "Version must follow semver format" |
