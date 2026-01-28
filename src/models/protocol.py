"""Research protocol models.

Defines ResearchProtocol base class and typed protocol variants
for Survey, Interview, and Focus Group research methods.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Any

from pydantic import BaseModel, Field

from models.enums import ResearchMethodType


class ResearchProtocol(BaseModel):
    """Base class for all research protocols.

    Provides common fields for protocol identification, versioning,
    and metadata across all research method types.
    """

    id: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        min_length=1,
        max_length=100,
        description="Unique protocol identifier (kebab-case)",
    )
    version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version (e.g., 1.0.0)",
    )
    type: ResearchMethodType = Field(
        ...,
        description="Research method type",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable protocol name",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Protocol description",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Protocol tags for categorization",
    )


class SurveyProtocol(ResearchProtocol):
    """Protocol wrapper for Survey research.

    Contains a Survey definition with questions and configuration
    for executing structured surveys.
    """

    type: Literal[ResearchMethodType.SURVEY] = Field(
        default=ResearchMethodType.SURVEY,
        description="Survey research type",
    )
    survey: Any = Field(
        ...,
        description="Survey definition",
    )


class InterviewProtocol(ResearchProtocol):
    """Protocol wrapper for Interview research.

    Contains an InterviewGuide with sections and questions
    for conducting in-depth interviews.
    """

    type: Literal[ResearchMethodType.INTERVIEW] = Field(
        default=ResearchMethodType.INTERVIEW,
        description="Interview research type",
    )
    guide: Any = Field(
        ...,
        description="Interview guide definition",
    )


class FocusGroupProtocol(ResearchProtocol):
    """Protocol wrapper for Focus Group research.

    Contains a FocusGroup configuration with participants
    and discussion topics.
    """

    type: Literal[ResearchMethodType.FOCUS_GROUP] = Field(
        default=ResearchMethodType.FOCUS_GROUP,
        description="Focus group research type",
    )
    focus_group: Any = Field(
        ...,
        description="Focus group configuration",
    )
