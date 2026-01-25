"""Question type models for research sessions.

Defines question types and validation for research questions.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class QuestionType(str, Enum):
    """Type of research question being asked."""

    OPEN_ENDED = "open_ended"
    RATING = "rating"
    MULTIPLE_CHOICE = "multiple_choice"


class ResearchQuestion(BaseModel):
    """A research question to ask a persona.

    Supports three question types:
    - OPEN_ENDED: Free-form response expected
    - RATING: Numeric response with justification
    - MULTIPLE_CHOICE: Selection from provided options
    """

    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The question text (max 2000 chars)"
    )
    type: QuestionType = Field(
        default=QuestionType.OPEN_ENDED,
        description="Type of question"
    )
    options: Optional[list[str]] = Field(
        default=None,
        description="Options for MULTIPLE_CHOICE (2-10 items)"
    )
    scale_min: int = Field(
        default=1,
        ge=1,
        description="Minimum for RATING scale"
    )
    scale_max: int = Field(
        default=10,
        le=100,
        description="Maximum for RATING scale"
    )

    @model_validator(mode="after")
    def validate_question_type_requirements(self) -> "ResearchQuestion":
        """Validate requirements based on question type."""
        if self.type == QuestionType.MULTIPLE_CHOICE:
            if not self.options:
                raise ValueError("options are required for MULTIPLE_CHOICE questions")
            if len(self.options) < 2:
                raise ValueError("MULTIPLE_CHOICE requires at least 2 options")
            if len(self.options) > 10:
                raise ValueError("MULTIPLE_CHOICE allows maximum 10 options")

        if self.type == QuestionType.RATING:
            if self.scale_min >= self.scale_max:
                raise ValueError("scale_min must be less than scale_max")

        return self
