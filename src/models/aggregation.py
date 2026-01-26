"""Aggregation models for panel research results.

Defines Theme, QuoteReference, SentimentDistribution, ConsensusPoint,
DivergencePoint, Position, AggregatedResults, and PanelQualityMetrics.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field

from models.session import QualityMetrics, Sentiment


class QuoteReference(BaseModel):
    """A quote from a specific persona response."""

    persona_id: str = Field(
        ...,
        description="Persona who said this",
    )
    persona_name: str = Field(
        ...,
        description="Display name",
    )
    quote: str = Field(
        ...,
        description="The quoted text",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "quote": self.quote,
        }


class Theme(BaseModel):
    """A recurring topic identified across multiple responses."""

    name: str = Field(
        ...,
        description="Theme title (3-7 words)",
    )
    description: str = Field(
        ...,
        description="Theme summary (1-2 sentences)",
    )
    frequency: int = Field(
        ...,
        ge=1,
        description="Number of personas mentioning theme",
    )
    percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Frequency as percentage of panel",
    )
    supporting_quotes: list[QuoteReference] = Field(
        default_factory=list,
        description="Quotes supporting this theme",
    )
    sentiment_tendency: Optional[Sentiment] = Field(
        default=None,
        description="Common sentiment for this theme",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "percentage": self.percentage,
            "supporting_quotes": [q.to_dict() for q in self.supporting_quotes],
            "sentiment_tendency": self.sentiment_tendency.value if self.sentiment_tendency else None,
        }


class SentimentDistribution(BaseModel):
    """Breakdown of sentiment across panel responses."""

    positive: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage positive (0-100)",
    )
    negative: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage negative (0-100)",
    )
    mixed: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage mixed (0-100)",
    )
    neutral: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage neutral (0-100)",
    )
    dominant: Sentiment = Field(
        ...,
        description="Most common sentiment",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "positive": self.positive,
            "negative": self.negative,
            "mixed": self.mixed,
            "neutral": self.neutral,
            "dominant": self.dominant.value,
        }


class Position(BaseModel):
    """A viewpoint on a divergent topic."""

    stance: str = Field(
        ...,
        description="The position (e.g., 'Support', 'Oppose')",
    )
    persona_ids: list[str] = Field(
        ...,
        description="Personas holding this position",
    )
    rationale: str = Field(
        ...,
        description="Why they hold this view",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "stance": self.stance,
            "persona_ids": self.persona_ids,
            "rationale": self.rationale,
        }


class ConsensusPoint(BaseModel):
    """A point where significant agreement exists."""

    statement: str = Field(
        ...,
        description="What personas agree on",
    )
    agreement_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage agreeing",
    )
    supporting_personas: list[str] = Field(
        default_factory=list,
        description="Persona IDs who agree",
    )
    key_quotes: Optional[list[QuoteReference]] = Field(
        default=None,
        description="Representative quotes",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "statement": self.statement,
            "agreement_rate": self.agreement_rate,
            "supporting_personas": self.supporting_personas,
            "key_quotes": [q.to_dict() for q in self.key_quotes] if self.key_quotes else [],
        }


class DivergencePoint(BaseModel):
    """A point of significant disagreement."""

    topic: str = Field(
        ...,
        description="The topic of disagreement",
    )
    positions: list[Position] = Field(
        ...,
        min_length=2,
        description="Different viewpoints (at least 2)",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "topic": self.topic,
            "positions": [p.to_dict() for p in self.positions],
        }


class AggregatedResults(BaseModel):
    """Synthesized findings from panel responses."""

    themes: list[Theme] = Field(
        default_factory=list,
        description="Top 3-5 recurring themes",
    )
    sentiment_distribution: SentimentDistribution = Field(
        ...,
        description="Sentiment breakdown",
    )
    consensus_points: list[ConsensusPoint] = Field(
        default_factory=list,
        description="Points of agreement (may be empty)",
    )
    divergence_points: list[DivergencePoint] = Field(
        default_factory=list,
        description="Points of disagreement (may be empty)",
    )
    executive_summary: str = Field(
        ...,
        description="2-3 sentence synthesis",
    )
    aggregation_confidence: float = Field(
        ...,
        ge=0,
        le=100,
        description="0-100% confidence in aggregation",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "themes": [t.to_dict() for t in self.themes],
            "sentiment_distribution": self.sentiment_distribution.to_dict(),
            "consensus_points": [c.to_dict() for c in self.consensus_points],
            "divergence_points": [d.to_dict() for d in self.divergence_points],
            "executive_summary": self.executive_summary,
            "aggregation_confidence": self.aggregation_confidence,
        }


class PanelQualityMetrics(BaseModel):
    """Panel-level quality measurements."""

    avg_consistency_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Mean consistency across personas (0-100%)",
    )
    completion_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Successful/total personas (0-100%)",
    )
    theme_confidence: float = Field(
        ...,
        ge=0,
        le=100,
        description="How well themes are supported (0-100%)",
    )
    divergence_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Degree of disagreement (0-100%)",
    )
    passed_gates: bool = Field(
        ...,
        description="True if all quality gates passed",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Quality warnings (may be empty)",
    )
    individual_metrics: list[QualityMetrics] = Field(
        default_factory=list,
        description="Phase 1 metrics per persona",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "avg_consistency_score": self.avg_consistency_score,
            "completion_rate": self.completion_rate,
            "theme_confidence": self.theme_confidence,
            "divergence_score": self.divergence_score,
            "passed_gates": self.passed_gates,
            "warnings": self.warnings,
            "individual_metrics": [
                {
                    "consistency_score": m.consistency_score,
                    "passed_gates": m.passed_gates,
                    "warnings": m.warnings,
                }
                for m in self.individual_metrics
            ],
        }
