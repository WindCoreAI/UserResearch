"""Quality models for Phase 4 quality calibration and analysis.

Defines models for consistency scoring, bias analysis, variance reporting,
drift detection, and quality dashboard metrics. These models support the
full quality pipeline from individual trait alignment through aggregate
dashboard views.
"""

from datetime import date as _date
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models.calibration import QualityThresholds
from models.enums import DriftWarningLevel, QualityStatus

# --- T005: Trait Alignment ---


class TraitAlignment(BaseModel):
    """Alignment measurement for a single personality trait.

    Compares detected trait expression in a response against expected
    values from the persona definition, tracking keyword matches and
    computing a weighted alignment score.
    """

    trait_name: str = Field(..., description="Name of the personality trait")
    trait_value: float = Field(..., description="Expected trait value from persona")
    alignment_score: float = Field(
        ..., ge=0, le=100,
        description="How well the response aligns with this trait (0-100%)"
    )
    matched_keywords: list[str] = Field(
        ..., description="Keywords from response matching this trait"
    )
    expected_keywords: list[str] = Field(
        ..., description="Keywords expected for this trait"
    )
    weight: float = Field(
        ..., description="Weight of this trait in overall consistency"
    )


# --- T017: Consistency Score ---


class ConsistencyScore(BaseModel):
    """Detailed consistency analysis across personality frameworks.

    Evaluates response consistency against both Big Five and Schwartz
    value frameworks, producing per-response and aggregate scores with
    configurable weighting.
    """

    overall_score: float = Field(
        ..., ge=0, le=100,
        description="Weighted overall consistency score (0-100%)"
    )
    big_five_score: float = Field(
        ..., ge=0, le=100,
        description="Consistency score for Big Five traits (0-100%)"
    )
    schwartz_score: float = Field(
        ..., ge=0, le=100,
        description="Consistency score for Schwartz values (0-100%)"
    )
    big_five_alignment: list[TraitAlignment] = Field(
        ..., description="Per-trait alignment for Big Five"
    )
    schwartz_alignment: list[TraitAlignment] = Field(
        ..., description="Per-trait alignment for Schwartz values"
    )
    per_response_scores: list[float] = Field(
        ..., description="Consistency score for each individual response"
    )
    response_variance: float = Field(
        ..., ge=0,
        description="Variance across per-response scores"
    )
    passed_threshold: bool = Field(
        ..., description="Whether overall score meets minimum threshold"
    )
    warning_flags: list[str] = Field(
        default_factory=list,
        description="Quality warnings raised during analysis"
    )
    threshold_used: float = Field(
        ..., description="Threshold value used for pass/fail determination"
    )
    calculation_method: str = Field(
        default="weighted",
        description="Method used for score calculation"
    )


# --- T030: Flagged Response ---


class FlaggedResponse(BaseModel):
    """A response flagged for potential quality issues.

    Identifies specific responses that exhibit sycophancy, bias,
    or other quality concerns with a confidence level.
    """

    response_index: int = Field(
        ..., ge=0,
        description="Index of the flagged response in the session"
    )
    response_text: str = Field(
        ..., description="Text of the flagged response"
    )
    flag_type: str = Field(
        ..., description="Category of the flag (e.g., 'sycophancy', 'bias')"
    )
    flag_reason: str = Field(
        ..., description="Explanation of why the response was flagged"
    )
    confidence: float = Field(
        ..., ge=0, le=1,
        description="Confidence in the flag (0-1)"
    )


# --- T031: Sentiment Clustering ---


class SentimentClustering(BaseModel):
    """Detection of unhealthy sentiment clustering across responses.

    Identifies when responses cluster around a single sentiment rather
    than reflecting natural diversity expected from varied personas.
    """

    detected: bool = Field(
        ..., description="Whether sentiment clustering was detected"
    )
    dominant_sentiment: Optional[str] = Field(
        default=None,
        description="The dominant sentiment if clustering detected"
    )
    dominant_percentage: float = Field(
        ..., ge=0, le=100,
        description="Percentage of responses with dominant sentiment (0-100%)"
    )
    expected_diversity: float = Field(
        ..., description="Expected sentiment diversity score"
    )
    personas_affected: list[str] = Field(
        default_factory=list,
        description="Persona IDs exhibiting clustering"
    )


# --- T032: Bias Analysis ---


class BiasAnalysis(BaseModel):
    """Comprehensive bias and sycophancy analysis for a session.

    Evaluates sycophancy rate, sentiment balance, and identifies
    specific flagged responses that may indicate AI bias patterns.
    """

    sycophancy_rate: float = Field(
        ..., ge=0, le=100,
        description="Percentage of responses showing sycophancy (0-100%)"
    )
    sycophancy_phrases_found: list[str] = Field(
        default_factory=list,
        description="Specific sycophantic phrases detected"
    )
    positive_negative_ratio: float = Field(
        ..., ge=0,
        description="Ratio of positive to negative responses"
    )
    sentiment_clustering: SentimentClustering = Field(
        ..., description="Sentiment clustering analysis"
    )
    flagged_responses: list[FlaggedResponse] = Field(
        default_factory=list,
        description="Responses flagged for quality issues"
    )
    passed_threshold: bool = Field(
        ..., description="Whether bias metrics are within acceptable range"
    )
    warning_flags: list[str] = Field(
        default_factory=list,
        description="Bias-related warnings"
    )
    threshold_used: float = Field(
        ..., description="Sycophancy threshold used for pass/fail"
    )


# --- T045: Rating Variance ---


class RatingVariance(BaseModel):
    """Variance analysis for a single rated question.

    Compares observed rating variance against expected baselines
    to detect suspiciously uniform or divergent response patterns.
    """

    question_id: str = Field(..., description="ID of the rated question")
    mean: float = Field(..., description="Mean rating value")
    stdev: float = Field(
        ..., ge=0,
        description="Standard deviation of ratings"
    )
    variance: float = Field(
        ..., ge=0,
        description="Statistical variance of ratings"
    )
    min_value: float = Field(..., description="Minimum rating observed")
    max_value: float = Field(..., description="Maximum rating observed")
    expected_stdev: float = Field(
        ..., description="Expected standard deviation from baseline"
    )
    variance_ratio: float = Field(
        ..., ge=0,
        description="Ratio of observed to expected variance"
    )
    clustering_detected: bool = Field(
        ..., description="Whether rating clustering was detected"
    )


# --- T046: Quality Sentiment Distribution ---


class QualitySentimentDistribution(BaseModel):
    """Sentiment distribution across responses for quality analysis.

    Named QualitySentimentDistribution to avoid conflict with the
    existing SentimentDistribution in aggregation models.
    """

    positive: float = Field(
        ..., ge=0, le=100,
        description="Percentage of positive responses (0-100%)"
    )
    negative: float = Field(
        ..., ge=0, le=100,
        description="Percentage of negative responses (0-100%)"
    )
    mixed: float = Field(
        ..., ge=0, le=100,
        description="Percentage of mixed responses (0-100%)"
    )
    neutral: float = Field(
        ..., ge=0, le=100,
        description="Percentage of neutral responses (0-100%)"
    )
    diversity_score: float = Field(
        ..., ge=0, le=1,
        description="Diversity of sentiment distribution (0-1)"
    )


# --- T047: Variance Report ---


class VarianceReport(BaseModel):
    """Comprehensive variance analysis across a panel or session.

    Aggregates per-question rating variance, sentiment distribution,
    and clustering detection into an overall variance assessment.
    """

    rating_variances: list[RatingVariance] = Field(
        default_factory=list,
        description="Per-question rating variance analysis"
    )
    overall_rating_variance: float = Field(
        ..., ge=0,
        description="Aggregate rating variance across all questions"
    )
    sentiment_distribution: QualitySentimentDistribution = Field(
        ..., description="Sentiment distribution across responses"
    )
    clustering_detected: bool = Field(
        ..., description="Whether clustering was detected in any metric"
    )
    clustering_details: list[str] = Field(
        default_factory=list,
        description="Details of detected clustering patterns"
    )
    stability_score: Optional[float] = Field(
        default=None,
        description="Cross-session stability score if multiple sessions"
    )
    session_count: int = Field(
        default=1,
        description="Number of sessions included in analysis"
    )
    passed_threshold: bool = Field(
        ..., description="Whether variance meets minimum threshold"
    )
    warning_flags: list[str] = Field(
        default_factory=list,
        description="Variance-related warnings"
    )
    panel_size: int = Field(
        ..., ge=1,
        description="Number of personas in the panel"
    )
    expected_variance_baseline: str = Field(
        ..., description="Baseline identifier used for expected variance"
    )


# --- T060: Segment Score ---


class SegmentScore(BaseModel):
    """Consistency score for a segment of a session.

    Sessions are divided into segments to detect consistency drift
    over the course of a conversation.
    """

    segment_index: int = Field(
        ..., ge=0,
        description="Zero-based index of this segment"
    )
    start_response: int = Field(
        ..., ge=0,
        description="Index of the first response in this segment"
    )
    end_response: int = Field(
        ..., ge=0,
        description="Index of the last response in this segment"
    )
    consistency_score: float = Field(
        ..., ge=0, le=100,
        description="Consistency score for this segment (0-100%)"
    )
    response_count: int = Field(
        ..., ge=1,
        description="Number of responses in this segment"
    )


# --- T061: Affected Trait ---


class AffectedTrait(BaseModel):
    """A trait that drifted during a session.

    Tracks the initial and final alignment for a specific trait,
    quantifying the drift amount and direction.
    """

    trait_name: str = Field(..., description="Name of the affected trait")
    trait_type: str = Field(
        ..., description="Framework type ('big_five' or 'schwartz')"
    )
    initial_alignment: float = Field(
        ..., ge=0, le=100,
        description="Alignment score at session start (0-100%)"
    )
    final_alignment: float = Field(
        ..., ge=0, le=100,
        description="Alignment score at session end (0-100%)"
    )
    drift_amount: float = Field(
        ..., ge=0,
        description="Absolute change in alignment"
    )
    drift_direction: str = Field(
        ..., description="Direction of drift ('increased' or 'decreased')"
    )

    @field_validator("trait_type")
    @classmethod
    def validate_trait_type(cls, v: str) -> str:
        if v not in ("big_five", "schwartz"):
            raise ValueError("trait_type must be 'big_five' or 'schwartz'")
        return v

    @field_validator("drift_direction")
    @classmethod
    def validate_drift_direction(cls, v: str) -> str:
        if v not in ("increased", "decreased"):
            raise ValueError("drift_direction must be 'increased' or 'decreased'")
        return v


# --- T062: Drift Analysis ---


class DriftAnalysis(BaseModel):
    """Full drift detection analysis for a session.

    Identifies when a persona's behavior drifts from its defined
    profile over the course of a session, pinpointing the drift
    point and affected traits.
    """

    drift_score: float = Field(
        ..., ge=0, le=100,
        description="Overall drift severity score (0-100%)"
    )
    drift_detected: bool = Field(
        ..., description="Whether significant drift was detected"
    )
    segment_scores: list[SegmentScore] = Field(
        ..., description="Per-segment consistency scores"
    )
    drift_point_index: int = Field(
        ..., ge=0,
        description="Segment index where drift began"
    )
    drift_point_response: int = Field(
        ..., ge=0,
        description="Response index where drift began"
    )
    affected_traits: list[AffectedTrait] = Field(
        default_factory=list,
        description="Traits that experienced drift"
    )
    stable_traits: list[str] = Field(
        default_factory=list,
        description="Traits that remained stable"
    )
    passed_threshold: bool = Field(
        ..., description="Whether drift is within acceptable range"
    )
    warning_level: DriftWarningLevel = Field(
        ..., description="Severity level of the drift warning"
    )
    warning_flags: list[str] = Field(
        default_factory=list,
        description="Drift-related warnings"
    )
    persona_id: str = Field(
        ..., description="ID of the persona being analyzed"
    )
    session_length: int = Field(
        ..., ge=1,
        description="Total number of responses in the session"
    )
    segment_count: int = Field(
        ..., ge=1,
        description="Number of segments the session was divided into"
    )


# --- T006: Extended Quality Metrics ---


class ExtendedQualityMetrics(BaseModel):
    """Extended quality metrics aggregating all quality dimensions.

    Combines consistency, bias, variance, and drift analyses into
    a unified quality assessment with an overall status and score.
    """

    consistency_score: float = Field(
        ..., ge=0, le=100,
        description="Overall consistency score (0-100%)"
    )
    sycophancy_indicators: dict = Field(
        default_factory=dict,
        description="Detected sycophancy patterns"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Quality warnings for review"
    )
    passed_gates: bool = Field(
        ..., description="Whether response passes all quality gates"
    )
    matched_traits: Optional[list[str]] = Field(
        default=None,
        description="Traits that matched in response"
    )
    missing_traits: Optional[list[str]] = Field(
        default=None,
        description="Expected traits not found"
    )
    consistency_details: ConsistencyScore = Field(
        ..., description="Detailed consistency analysis"
    )
    bias_analysis: BiasAnalysis = Field(
        ..., description="Bias and sycophancy analysis"
    )
    variance_report: Optional[VarianceReport] = Field(
        default=None,
        description="Variance analysis (populated for panels)"
    )
    drift_analysis: Optional[DriftAnalysis] = Field(
        default=None,
        description="Drift detection analysis (populated for long sessions)"
    )
    quality_status: QualityStatus = Field(
        ..., description="Overall quality status"
    )
    quality_score: float = Field(
        ..., ge=0, le=100,
        description="Composite quality score (0-100%)"
    )
    analysis_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="When the analysis was performed"
    )
    thresholds_used: QualityThresholds = Field(
        ..., description="Threshold configuration used for this analysis"
    )
    session_type: str = Field(
        ..., description="Type of session analyzed"
    )

    @property
    def has_issues(self) -> bool:
        """Return True if quality status is not healthy."""
        return self.quality_status != QualityStatus.HEALTHY


# --- T100: Session Summary ---


class SessionSummary(BaseModel):
    """Compact summary of a session's quality metrics.

    Provides a lightweight view of key quality indicators for
    use in dashboard listings and trend analysis.
    """

    session_id: str = Field(..., description="Unique session identifier")
    session_type: str = Field(
        ..., description="Type of session (e.g., 'survey', 'interview')"
    )
    quality_status: QualityStatus = Field(
        ..., description="Quality status of the session"
    )
    consistency_score: float = Field(
        ..., ge=0, le=100,
        description="Consistency score (0-100%)"
    )
    sycophancy_rate: float = Field(
        ..., ge=0, le=100,
        description="Sycophancy rate (0-100%)"
    )
    variance_score: Optional[float] = Field(
        default=None,
        description="Variance score if applicable"
    )
    drift_score: Optional[float] = Field(
        default=None,
        description="Drift score if applicable"
    )
    timestamp: datetime = Field(
        ..., description="When the session was conducted"
    )
    warning_count: int = Field(
        ..., ge=0,
        description="Number of quality warnings"
    )


# --- T101: Trend Data Point ---


class TrendDataPoint(BaseModel):
    """A single data point in a quality trend time series.

    Represents an aggregated metric value for a specific date,
    potentially spanning multiple sessions.
    """

    date: _date = Field(..., description="Date of the data point")
    metric_value: float = Field(
        ..., description="Aggregated metric value for this date"
    )
    session_count: int = Field(
        ..., ge=1,
        description="Number of sessions contributing to this data point"
    )


# --- T102: Quality Dashboard Metrics ---


class QualityDashboardMetrics(BaseModel):
    """Aggregate quality metrics for the dashboard view.

    Provides a comprehensive overview of quality across all analyzed
    sessions, including status breakdowns, averages, trends, and
    threshold comparisons.
    """

    overall_status: QualityStatus = Field(
        ..., description="Overall quality status across all sessions"
    )
    sessions_analyzed: int = Field(
        ..., ge=0,
        description="Total number of sessions analyzed"
    )
    sessions_healthy: int = Field(
        ..., ge=0,
        description="Number of sessions with healthy status"
    )
    sessions_warning: int = Field(
        ..., ge=0,
        description="Number of sessions with warning status"
    )
    sessions_critical: int = Field(
        ..., ge=0,
        description="Number of sessions with critical status"
    )
    avg_consistency_score: float = Field(
        ..., ge=0, le=100,
        description="Average consistency score across sessions (0-100%)"
    )
    avg_sycophancy_rate: float = Field(
        ..., ge=0, le=100,
        description="Average sycophancy rate across sessions (0-100%)"
    )
    avg_variance_score: float = Field(
        ..., ge=0,
        description="Average variance score across sessions"
    )
    max_drift_score: float = Field(
        ..., ge=0, le=100,
        description="Maximum drift score observed (0-100%)"
    )
    thresholds: QualityThresholds = Field(
        ..., description="Threshold configuration used"
    )
    metrics_above_threshold: list[str] = Field(
        default_factory=list,
        description="Metrics exceeding their thresholds"
    )
    metrics_below_threshold: list[str] = Field(
        default_factory=list,
        description="Metrics below their thresholds"
    )
    recent_sessions: list[SessionSummary] = Field(
        default_factory=list,
        description="Most recent session summaries"
    )
    consistency_trend: Optional[list[TrendDataPoint]] = Field(
        default=None,
        description="Consistency score trend over time"
    )
    sycophancy_trend: Optional[list[TrendDataPoint]] = Field(
        default=None,
        description="Sycophancy rate trend over time"
    )
    analysis_start: datetime = Field(
        ..., description="Start of the analysis period"
    )
    analysis_end: datetime = Field(
        ..., description="End of the analysis period"
    )

    @property
    def health_percentage(self) -> float:
        """Calculate percentage of sessions with healthy status."""
        if self.sessions_analyzed > 0:
            return self.sessions_healthy / self.sessions_analyzed * 100
        return 100.0
