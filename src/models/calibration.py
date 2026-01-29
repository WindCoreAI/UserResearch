"""Calibration models for quality thresholds and baseline comparisons.

Defines configurable quality thresholds, calibration baselines for real user data,
and comparison models for synthetic vs real data analysis.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models.enums import AlignmentStatus, RecommendationPriority, RecommendationType


class QualityThresholds(BaseModel):
    """Configurable thresholds for quality gates."""

    # Consistency thresholds
    consistency_minimum: float = Field(
        default=70.0, ge=0, le=100,
        description="Minimum acceptable consistency score (%)"
    )
    consistency_warning: float = Field(
        default=80.0, ge=0, le=100,
        description="Warning threshold (%)"
    )

    # Sycophancy thresholds
    sycophancy_maximum: float = Field(
        default=30.0, ge=0, le=100,
        description="Maximum acceptable sycophancy rate (%)"
    )
    positive_negative_ratio: float = Field(
        default=4.0, ge=0,
        description="Max positive:negative ratio before warning"
    )

    # Variance thresholds
    variance_minimum_ratio: float = Field(
        default=0.6, ge=0,
        description="Min ratio vs expected variance"
    )
    clustering_threshold: float = Field(
        default=0.8, ge=0, le=1.0,
        description="Max single-sentiment percentage"
    )

    # Drift thresholds
    drift_warning: float = Field(
        default=15.0, ge=0, le=100,
        description="Warning threshold (%)"
    )
    drift_critical: float = Field(
        default=25.0, ge=0, le=100,
        description="Critical threshold (%)"
    )


class NumericDistribution(BaseModel):
    """Distribution data for numeric responses."""

    mean: float
    stdev: float = Field(ge=0)
    min_value: float
    max_value: float
    histogram: list[int] = Field(description="Frequency buckets")
    bucket_labels: list[str] = Field(description="Bucket range labels")


class CategoricalDistribution(BaseModel):
    """Distribution data for categorical responses."""

    frequencies: dict[str, float] = Field(description="Option -> percentage")
    total_responses: int = Field(ge=1)


class QuestionDistribution(BaseModel):
    """Distribution for a single question."""

    question_id: str
    question_text: Optional[str] = None
    distribution_type: str = Field(description="'numeric' or 'categorical'")
    numeric: Optional[NumericDistribution] = None
    categorical: Optional[CategoricalDistribution] = None

    @field_validator("distribution_type")
    @classmethod
    def validate_distribution_type(cls, v: str) -> str:
        if v not in ("numeric", "categorical"):
            raise ValueError("distribution_type must be 'numeric' or 'categorical'")
        return v


class CalibrationBaseline(BaseModel):
    """Real user data baseline for calibration."""

    id: str
    name: str
    version: str = "1.0.0"

    # Source metadata
    source: str = Field(description="Data source description")
    sample_size: int = Field(ge=10, description="Number of real responses")
    collection_date: date
    collection_method: Optional[str] = None

    # Demographic tags
    demographic_tags: list[str] = Field(default_factory=list)
    demographic_description: Optional[str] = None

    # Distribution data
    distributions: list[QuestionDistribution] = Field(min_length=1)

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    notes: Optional[str] = None


class QuestionComparison(BaseModel):
    """Comparison result for a single question."""

    question_id: str
    overlap_percentage: float = Field(ge=0, le=100)
    synthetic_mean: Optional[float] = None
    baseline_mean: Optional[float] = None
    mean_difference: Optional[float] = None
    synthetic_distribution: dict = Field(default_factory=dict)
    baseline_distribution: dict = Field(default_factory=dict)
    divergence_detected: bool = False


class Recommendation(BaseModel):
    """Persona adjustment recommendation."""

    recommendation_id: str
    target: str = Field(description="'persona', 'panel', or 'protocol'")
    target_id: Optional[str] = None
    recommendation_type: RecommendationType
    parameter: str
    current_value: Optional[str] = None
    suggested_value: Optional[str] = None
    rationale: str
    priority: RecommendationPriority
    impact_estimate: str


class CalibrationComparison(BaseModel):
    """Full calibration comparison result."""

    id: str
    baseline_id: str
    session_id: Optional[str] = None
    panel_id: Optional[str] = None

    # Overall results
    overall_overlap: float = Field(ge=0, le=100)
    alignment_status: AlignmentStatus

    # Per-question comparison
    question_comparisons: list[QuestionComparison] = Field(default_factory=list)

    # Divergence analysis
    divergence_points: list[str] = Field(default_factory=list)
    divergence_summary: str = ""

    # Recommendations
    recommendations: list[Recommendation] = Field(default_factory=list)

    # Metadata
    comparison_timestamp: datetime = Field(default_factory=lambda: datetime.now())
    synthetic_sample_size: int = Field(ge=1)
    baseline_sample_size: int = Field(ge=1)

    @property
    def needs_calibration(self) -> bool:
        return self.overall_overlap < 60.0
