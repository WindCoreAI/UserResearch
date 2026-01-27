"""Interview models for in-depth interview research.

Defines InterviewGuide, InterviewSection, InterviewQuestion,
InterviewTranscript, and related models for conducting interviews.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from models.enums import InterviewProbeType
from models.session import QualityMetrics


class InterviewProbe(BaseModel):
    """A probing question configuration.

    Defines when and how to probe for more information during an interview.
    """

    type: InterviewProbeType = Field(
        ...,
        description="Type of probing strategy",
    )
    trigger: str | None = Field(
        default=None,
        description="Keyword or condition that triggers this probe",
    )
    question_template: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Template for the probe question",
    )


class InterviewQuestion(BaseModel):
    """A single question within an interview section.

    Supports configurable follow-up depth and probing strategies.
    """

    id: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        min_length=1,
        max_length=50,
        description="Question identifier (kebab-case)",
    )
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Question text",
    )
    probes: list[InterviewProbe] = Field(
        default_factory=list,
        max_length=3,
        description="Probing question configurations",
    )
    allow_followups: bool = Field(
        default=True,
        description="Whether follow-up questions are allowed",
    )
    max_followup_depth: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum depth of follow-up questions",
    )


class InterviewSection(BaseModel):
    """A thematic section within an interview guide.

    Groups related questions together with optional transitions.
    """

    id: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        min_length=1,
        max_length=50,
        description="Section identifier (kebab-case)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Section display name",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Section description",
    )
    questions: list[InterviewQuestion] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Questions in this section",
    )
    transition_prompt: str | None = Field(
        default=None,
        max_length=500,
        description="Prompt for transitioning to this section",
    )


class InterviewGuide(BaseModel):
    """Complete interview protocol definition.

    Contains sections with questions, configuration for probing,
    and metadata for the interview.
    """

    id: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        min_length=1,
        max_length=100,
        description="Guide identifier (kebab-case)",
    )
    version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Interview guide name",
    )
    topic: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Main topic of the interview",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Guide description",
    )
    sections: list[InterviewSection] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Interview sections",
    )

    # Configuration
    min_response_length: int = Field(
        default=50,
        ge=10,
        le=500,
        description="Minimum characters before probing",
    )
    default_max_followups: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Default maximum follow-up depth",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )


# Transcript models


class InterviewExchange(BaseModel):
    """A single question-response exchange in an interview.

    Represents one turn in the interview conversation,
    including any follow-up exchanges.
    """

    question_id: str = Field(..., description="Question identifier")
    question_text: str = Field(..., description="Question as asked")
    response: str = Field(..., description="Persona's response")
    timestamp: datetime = Field(..., description="Exchange timestamp")

    # Follow-up chain
    followups: list["InterviewExchange"] = Field(
        default_factory=list,
        description="Nested follow-up exchanges",
    )
    probe_used: InterviewProbeType | None = Field(
        default=None,
        description="Type of probe that triggered this exchange",
    )

    # Quality metrics
    response_length: int = Field(..., ge=0, description="Response character count")
    response_time_ms: int | None = Field(
        default=None,
        ge=0,
        description="Response time in milliseconds",
    )


class SectionTranscript(BaseModel):
    """Transcript of a single interview section.

    Contains all exchanges within one thematic section.
    """

    section_id: str = Field(..., description="Section identifier")
    section_name: str = Field(..., description="Section name")
    exchanges: list[InterviewExchange] = Field(
        default_factory=list,
        description="Question-response exchanges",
    )

    started_at: datetime = Field(..., description="Section start time")
    completed_at: datetime = Field(..., description="Section completion time")
    total_exchanges: int = Field(
        ...,
        ge=0,
        description="Total exchanges including follow-ups",
    )


class InterviewTranscript(BaseModel):
    """Complete transcript from an interview session.

    Contains all sections, identified themes, and quality metrics.
    """

    guide_id: str = Field(..., description="Interview guide identifier")
    guide_version: str = Field(..., description="Guide version")
    persona_id: str = Field(..., description="Persona identifier")
    persona_name: str = Field(..., description="Persona display name")

    sections: list[SectionTranscript] = Field(
        default_factory=list,
        description="Section transcripts",
    )

    started_at: datetime = Field(..., description="Interview start time")
    completed_at: datetime = Field(..., description="Interview completion time")
    total_time_ms: int = Field(..., ge=0, description="Total time in milliseconds")

    # Analysis
    identified_themes: list[Any] = Field(
        default_factory=list,
        description="Themes identified from responses",
    )
    key_quotes: list[str] = Field(
        default_factory=list,
        description="Notable quotes from the interview",
    )
    followup_relevance_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relevance score for follow-up questions",
    )

    quality_metrics: QualityMetrics | None = Field(
        default=None,
        description="Quality metrics for this transcript",
    )


# Update forward references
InterviewExchange.model_rebuild()
