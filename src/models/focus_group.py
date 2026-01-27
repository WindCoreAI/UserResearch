"""Focus group models for group discussion research.

Defines FocusGroup, DiscussionTurn, DiscussionLog,
and related models for simulating focus group discussions.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from models.enums import DiscussionInteractionType
from models.session import QualityMetrics, Sentiment
from models.aggregation import ConsensusPoint, DivergencePoint


class FocusGroupConfig(BaseModel):
    """Configuration for focus group dynamics.

    Controls the structure and behavior of focus group discussions.
    """

    max_rounds: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of discussion rounds",
    )
    turns_per_round: int = Field(
        default=6,
        ge=4,
        le=10,
        description="Turns per round (usually = num personas)",
    )
    moderator_prompts_enabled: bool = Field(
        default=True,
        description="Whether moderator prompts are enabled",
    )
    allow_cross_references: bool = Field(
        default=True,
        description="Allow personas to reference each other",
    )


class FocusGroup(BaseModel):
    """Focus group protocol definition.

    Contains participant personas, discussion topics, and configuration.
    """

    id: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        min_length=1,
        max_length=100,
        description="Focus group identifier (kebab-case)",
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
        description="Focus group name",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Focus group description",
    )

    persona_ids: list[str] = Field(
        ...,
        min_length=4,
        max_length=6,
        description="Participant persona IDs (4-6 required)",
    )
    discussion_topics: list[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Topics for discussion",
    )

    config: FocusGroupConfig = Field(
        default_factory=FocusGroupConfig,
        description="Discussion configuration",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )

    @field_validator("persona_ids")
    @classmethod
    def validate_unique_personas(cls, v: list[str]) -> list[str]:
        """Ensure all persona IDs are unique."""
        if len(v) != len(set(v)):
            raise ValueError("Focus group must have unique persona IDs")
        return v


class DiscussionReference(BaseModel):
    """A reference to another participant's statement.

    Tracks when personas acknowledge or respond to each other.
    """

    referenced_persona_id: str = Field(
        ...,
        description="Persona being referenced",
    )
    referenced_turn_index: int = Field(
        ...,
        ge=0,
        description="Turn index being referenced",
    )
    reference_type: DiscussionInteractionType = Field(
        ...,
        description="Type of reference (agreement, disagreement, etc.)",
    )
    quote_fragment: str | None = Field(
        default=None,
        max_length=200,
        description="Fragment of referenced statement",
    )


class DiscussionTurn(BaseModel):
    """A single turn in a focus group discussion.

    Represents one persona's contribution to the conversation.
    """

    turn_index: int = Field(..., ge=0, description="Sequential turn number")
    round_number: int = Field(..., ge=1, description="Discussion round")
    persona_id: str = Field(..., description="Speaking persona ID")
    persona_name: str = Field(..., description="Speaking persona name")

    statement: str = Field(..., description="Persona's statement")
    timestamp: datetime = Field(..., description="Turn timestamp")

    # Interaction analysis
    references: list[DiscussionReference] = Field(
        default_factory=list,
        description="References to other participants",
    )
    interaction_type: DiscussionInteractionType = Field(
        default=DiscussionInteractionType.NEW_POINT,
        description="Type of interaction",
    )

    # Sentiment on current topic
    sentiment: Sentiment | None = Field(
        default=None,
        description="Sentiment toward topic",
    )


class OpinionShift(BaseModel):
    """Record of a persona changing their position during discussion.

    Tracks evolution of opinions throughout the focus group.
    """

    persona_id: str = Field(..., description="Persona who shifted")
    persona_name: str = Field(..., description="Persona name")
    topic: str = Field(..., description="Topic of the shift")

    from_turn_index: int = Field(..., ge=0, description="Original position turn")
    to_turn_index: int = Field(..., ge=0, description="New position turn")

    original_position: str = Field(..., description="Original stance")
    new_position: str = Field(..., description="New stance")

    trigger_reference: DiscussionReference | None = Field(
        default=None,
        description="What caused the shift",
    )


class DiscussionLog(BaseModel):
    """Complete log of a focus group discussion.

    Contains all turns, analysis, and quality metrics.
    """

    group_id: str = Field(..., description="Focus group identifier")
    group_version: str = Field(..., description="Focus group version")
    topic: str = Field(..., description="Discussion topic")

    participants: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Participant info (persona_id, name, etc.)",
    )
    turns: list[DiscussionTurn] = Field(
        default_factory=list,
        description="All discussion turns",
    )

    started_at: datetime = Field(..., description="Discussion start time")
    completed_at: datetime = Field(..., description="Discussion completion time")
    total_time_ms: int = Field(..., ge=0, description="Total time in milliseconds")
    total_rounds: int = Field(..., ge=0, description="Number of rounds completed")

    # Analysis
    consensus_points: list[ConsensusPoint] = Field(
        default_factory=list,
        description="Points of agreement",
    )
    divergence_points: list[DivergencePoint] = Field(
        default_factory=list,
        description="Points of disagreement",
    )
    opinion_shifts: list[OpinionShift] = Field(
        default_factory=list,
        description="Tracked opinion changes",
    )
    interaction_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Interaction type counts",
    )

    quality_metrics: QualityMetrics | None = Field(
        default=None,
        description="Quality metrics for this discussion",
    )
