"""Panel models for multi-persona research sessions.

Defines ResearchPanel, PanelSessionStatus, and PanelSession models.
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from models.question import ResearchQuestion
from models.session import ResearchSession


class PanelSessionStatus(str, Enum):
    """Status of a panel research session."""

    PENDING = "pending"
    EXECUTING = "executing"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class ResearchPanel(BaseModel):
    """Defines a collection of personas for panel research.

    A panel groups multiple personas together for simultaneous research
    sessions, enabling comparison and aggregation of responses.
    """

    id: str = Field(
        ...,
        description="Unique panel identifier (slug format: lowercase, hyphens)",
    )
    name: str = Field(
        ...,
        description="Human-readable panel name",
    )
    description: str = Field(
        ...,
        description="Brief description of panel purpose",
    )
    purpose: Optional[str] = Field(
        default=None,
        description="Detailed use case description",
    )
    persona_ids: list[str] = Field(
        ...,
        min_length=2,
        max_length=50,
        description="IDs of personas in this panel (2-50 unique IDs)",
    )
    is_custom: bool = Field(
        ...,
        description="True if user-created, False if pre-built",
    )
    created_at: datetime = Field(
        ...,
        description="UTC timestamp of creation",
    )

    @field_validator("id")
    @classmethod
    def validate_id_slug_format(cls, v: str) -> str:
        """Validate that ID is in slug format (lowercase, hyphens, alphanumeric)."""
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", v):
            raise ValueError(
                "Panel ID must be in slug format (lowercase letters, numbers, and hyphens only, "
                "e.g., 'tech-adopters', 'my-panel-1')"
            )
        return v

    @field_validator("persona_ids")
    @classmethod
    def validate_unique_persona_ids(cls, v: list[str]) -> list[str]:
        """Validate that persona IDs are unique."""
        if len(v) != len(set(v)):
            duplicates = [pid for pid in v if v.count(pid) > 1]
            raise ValueError(f"Persona IDs must be unique. Duplicates found: {set(duplicates)}")
        return v

    def to_dict(self) -> dict[str, Any]:
        """Convert panel to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "purpose": self.purpose,
            "persona_ids": self.persona_ids,
            "is_custom": self.is_custom,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PanelSession(BaseModel):
    """Root entity representing a panel research interaction.

    Contains the question, all individual persona sessions,
    aggregated results, and quality metrics.
    """

    id: str = Field(
        ...,
        description="Unique session identifier (UUID)",
    )
    panel_id: str = Field(
        ...,
        description="ID of panel used",
    )
    panel_name: str = Field(
        ...,
        description="Display name of panel",
    )
    question: ResearchQuestion = Field(
        ...,
        description="The question asked",
    )
    individual_sessions: list[ResearchSession] = Field(
        default_factory=list,
        description="Phase 1 sessions per persona",
    )
    aggregation: Optional[AggregatedResults] = Field(
        default=None,
        description="Aggregated findings (null until complete)",
    )
    quality: Optional[PanelQualityMetrics] = Field(
        default=None,
        description="Panel-level metrics (null until computed)",
    )
    status: PanelSessionStatus = Field(
        ...,
        description="Current session state",
    )
    started_at: datetime = Field(
        ...,
        description="UTC timestamp of start",
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp of completion",
    )
    execution_time_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total execution time in milliseconds",
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional context (version, speedup_factor, etc.)",
    )

    model_config = {"arbitrary_types_allowed": True}

    def to_dict(self) -> dict[str, Any]:
        """Convert panel session to dictionary for serialization."""
        return {
            "id": self.id,
            "panel_id": self.panel_id,
            "panel_name": self.panel_name,
            "question": {
                "text": self.question.text,
                "type": self.question.type.value,
            },
            "individual_sessions": [
                {
                    "id": s.id,
                    "persona_id": s.persona_id,
                    "persona_name": s.persona_name,
                    "status": s.status.value,
                    "response": {
                        "parsed": {
                            "sentiment": s.response.parsed.sentiment.value,
                            "overall_impression": s.response.parsed.overall_impression,
                            "concerns": s.response.parsed.concerns,
                            "suggestions": s.response.parsed.suggestions,
                        }
                        if s.response and s.response.parsed
                        else None,
                        "quality": {
                            "consistency_score": s.response.quality.consistency_score,
                            "passed_gates": s.response.quality.passed_gates,
                        }
                        if s.response and s.response.quality
                        else None,
                    }
                    if s.response
                    else None,
                }
                for s in self.individual_sessions
            ],
            "aggregation": self.aggregation.to_dict() if self.aggregation else None,
            "quality": self.quality.to_dict() if self.quality else None,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }


# Import aggregation models for type resolution (after class definitions to avoid circular imports)
from models.aggregation import AggregatedResults, PanelQualityMetrics  # noqa: E402

# Update forward references
PanelSession.model_rebuild()
