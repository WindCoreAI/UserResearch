"""Session models for research sessions.

Defines session status, responses, and research session models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from models.question import ResearchQuestion


class SessionStatus(str, Enum):
    """Status of a research session."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Sentiment(str, Enum):
    """Sentiment classification for responses."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"
    NEUTRAL = "neutral"


class ParsedResponse(BaseModel):
    """Structured extraction from the raw persona response.

    Contains sentiment, concerns, suggestions, and other structured data
    extracted from the raw response text.
    """

    sentiment: Sentiment = Field(..., description="Overall sentiment classification")
    overall_impression: str = Field(
        ...,
        description="Brief summary (1-2 sentences)"
    )
    concerns: list[str] = Field(
        default_factory=list,
        description="Extracted concerns (may be empty)"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Extracted suggestions (may be empty)"
    )
    key_quotes: Optional[list[str]] = Field(
        default=None,
        description="Notable direct quotes from response"
    )
    rating: Optional[int] = Field(
        default=None,
        description="Numeric rating (for RATING questions)"
    )
    selected_option: Optional[str] = Field(
        default=None,
        description="Selected choice (for MULTIPLE_CHOICE)"
    )


class QualityMetrics(BaseModel):
    """Quality measurements for a persona response.

    Assesses whether the response is consistent with the persona's
    psychological profile and detects sycophancy patterns.
    """

    consistency_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="How well response matches persona traits (0-100%)"
    )
    sycophancy_indicators: dict[str, Any] = Field(
        default_factory=dict,
        description="Detected sycophancy patterns"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Quality warnings for review"
    )
    passed_gates: bool = Field(
        ...,
        description="Whether response passes quality thresholds"
    )
    matched_traits: Optional[list[str]] = Field(
        default=None,
        description="Traits that matched in response"
    )
    missing_traits: Optional[list[str]] = Field(
        default=None,
        description="Expected traits not found"
    )


class SessionResponse(BaseModel):
    """The response from a persona subagent.

    Contains the raw response text and timing information.
    Parsed and quality fields are populated by later processing steps.
    """

    raw_text: str = Field(..., description="Unprocessed response from subagent")
    response_time_ms: int = Field(
        ...,
        ge=0,
        description="Time from request to response (milliseconds)"
    )
    parsed: Optional[ParsedResponse] = Field(
        default=None,
        description="Structured extraction (populated by ResponseParser)"
    )
    quality: Optional[QualityMetrics] = Field(
        default=None,
        description="Quality measurements (populated by QualityMetricsCalculator)"
    )
    parse_errors: Optional[list[str]] = Field(
        default=None,
        description="Errors encountered during parsing"
    )


class ResearchSession(BaseModel):
    """A complete research session with a persona.

    Represents the full lifecycle of asking a question to a persona
    and receiving a response.
    """

    id: str = Field(..., description="Unique session identifier (UUID)")
    persona_id: str = Field(..., description="ID of persona used")
    persona_name: str = Field(..., description="Display name of persona")
    question: ResearchQuestion = Field(..., description="The question asked")
    response: Optional[SessionResponse] = Field(
        default=None,
        description="Response (null until completed)"
    )
    status: SessionStatus = Field(..., description="Current session state")
    started_at: datetime = Field(..., description="UTC timestamp of session start")
    completed_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp of completion"
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional context (version, etc.)"
    )
