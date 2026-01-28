"""Survey models for structured survey research.

Defines Survey, SurveyQuestion, SurveyResponse, SurveyResult,
and aggregation models for survey-based research.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from models.enums import SurveyQuestionType
from models.session import QualityMetrics


class SurveyQuestion(BaseModel):
    """A single question within a survey.

    Supports three question types: rating, multiple choice, and open-ended.
    Type-specific fields are validated based on the question type.
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
        max_length=500,
        description="Question text",
    )
    type: SurveyQuestionType = Field(
        ...,
        description="Question type",
    )
    required: bool = Field(
        default=True,
        description="Whether the question requires an answer",
    )

    # Rating-specific fields
    scale_min: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Minimum rating value (for rating questions)",
    )
    scale_max: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Maximum rating value (for rating questions)",
    )
    scale_labels: dict[int, str] | None = Field(
        default=None,
        description="Optional labels for scale points",
    )

    # Multiple choice fields
    options: list[str] | None = Field(
        default=None,
        min_length=2,
        max_length=10,
        description="Answer options (for multiple choice questions)",
    )

    @model_validator(mode="after")
    def validate_type_fields(self) -> "SurveyQuestion":
        """Validate type-specific fields based on question type."""
        if self.type == SurveyQuestionType.RATING:
            if self.scale_min is None or self.scale_max is None:
                raise ValueError("Rating questions require scale_min and scale_max")
            if self.scale_min >= self.scale_max:
                raise ValueError("scale_min must be less than scale_max")
        elif self.type == SurveyQuestionType.MULTIPLE_CHOICE:
            if not self.options:
                raise ValueError("Multiple choice questions require options")
        return self


class Survey(BaseModel):
    """A complete survey protocol definition.

    Contains a list of questions with unique IDs and metadata.
    """

    id: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        min_length=1,
        max_length=100,
        description="Survey identifier (kebab-case)",
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
        description="Survey name",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Survey description",
    )
    questions: list[SurveyQuestion] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Survey questions",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )

    @field_validator("questions")
    @classmethod
    def validate_unique_question_ids(
        cls, v: list[SurveyQuestion]
    ) -> list[SurveyQuestion]:
        """Ensure all question IDs are unique within the survey."""
        ids = [q.id for q in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Question IDs must be unique within a survey")
        return v


class SurveyResponse(BaseModel):
    """Response to a single survey question.

    Contains the raw response and parsed values based on question type.
    """

    question_id: str = Field(
        ...,
        description="ID of the question being answered",
    )
    question_type: SurveyQuestionType = Field(
        ...,
        description="Type of the question",
    )
    raw_response: str = Field(
        ...,
        description="Raw text response from persona",
    )

    # Parsed values (one populated based on type)
    rating_value: int | None = Field(
        default=None,
        description="Parsed rating value (for rating questions)",
    )
    selected_option: str | None = Field(
        default=None,
        description="Selected option (for multiple choice)",
    )
    text_response: str | None = Field(
        default=None,
        description="Text response (for open-ended)",
    )

    # Metadata
    response_time_ms: int | None = Field(
        default=None,
        ge=0,
        description="Time to respond in milliseconds",
    )
    validation_warnings: list[str] = Field(
        default_factory=list,
        description="Validation warnings for this response",
    )
    is_valid: bool = Field(
        default=True,
        description="Whether the response passed validation",
    )


class SurveyResult(BaseModel):
    """Complete result from a survey execution for a single persona."""

    survey_id: str = Field(..., description="Survey identifier")
    survey_version: str = Field(..., description="Survey version")
    persona_id: str = Field(..., description="Persona who completed the survey")
    responses: list[SurveyResponse] = Field(..., description="All responses")

    started_at: datetime = Field(..., description="Survey start time")
    completed_at: datetime = Field(..., description="Survey completion time")
    total_time_ms: int = Field(..., ge=0, description="Total time in milliseconds")

    completion_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of questions answered",
    )
    quality_metrics: QualityMetrics | None = Field(
        default=None,
        description="Quality metrics for this result",
    )


# Aggregation models for panel surveys


class RatingStatistics(BaseModel):
    """Statistical summary of rating responses across a panel."""

    question_id: str = Field(..., description="Question identifier")
    count: int = Field(..., ge=0, description="Number of responses")
    mean: float = Field(..., description="Mean rating value")
    median: float = Field(..., description="Median rating value")
    stdev: float = Field(..., ge=0, description="Standard deviation")
    min_value: int = Field(..., description="Minimum rating given")
    max_value: int = Field(..., description="Maximum rating given")
    distribution: dict[int, int] = Field(
        default_factory=dict,
        description="Value to count mapping",
    )


class MultipleChoiceStatistics(BaseModel):
    """Statistical summary of multiple choice responses across a panel."""

    question_id: str = Field(..., description="Question identifier")
    count: int = Field(..., ge=0, description="Number of responses")
    selection_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Option to count mapping",
    )
    selection_percentages: dict[str, float] = Field(
        default_factory=dict,
        description="Option to percentage mapping",
    )


class SurveyAggregation(BaseModel):
    """Aggregated results from panel survey execution."""

    survey_id: str = Field(..., description="Survey identifier")
    panel_id: str = Field(..., description="Panel identifier")
    total_respondents: int = Field(..., ge=0, description="Total respondents")

    rating_statistics: list[RatingStatistics] = Field(
        default_factory=list,
        description="Statistics for rating questions",
    )
    multiple_choice_statistics: list[MultipleChoiceStatistics] = Field(
        default_factory=list,
        description="Statistics for multiple choice questions",
    )
    open_ended_themes: list[Any] = Field(
        default_factory=list,
        description="Themes from open-ended responses (uses Theme from aggregation.py)",
    )

    segment_analysis: dict[str, Any] | None = Field(
        default=None,
        description="Optional breakdown by persona attributes",
    )
