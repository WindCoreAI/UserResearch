# Data Model: Quality & Calibration

**Feature**: Quality & Calibration (Phase 4)
**Date**: 2026-01-27
**Status**: Complete

## Overview

This document defines the data models for quality metrics, bias analysis, variance monitoring, drift detection, and calibration systems. All models extend existing Phase 1-3 structures while maintaining backward compatibility.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Quality Analysis Flow                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     analyzes      ┌──────────────────────┐
│ ResearchSession  │◄──────────────────│   QualityAnalyzer    │
│ (Phase 1-3)      │                   │   (orchestrator)     │
└────────┬─────────┘                   └──────────┬───────────┘
         │                                        │
         │ contains                               │ produces
         ▼                                        ▼
┌──────────────────┐                   ┌──────────────────────┐
│ SessionResponse  │                   │ ExtendedQualityMetrics│
│ (Phase 1)        │                   │                      │
└──────────────────┘                   └──────────┬───────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
         ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
         │ ConsistencyScore │         │   BiasAnalysis   │         │  DriftAnalysis   │
         │                  │         │                  │         │                  │
         │ - overall        │         │ - sycophancy_rate│         │ - drift_score    │
         │ - big_five       │         │ - clustering     │         │ - drift_point    │
         │ - schwartz       │         │ - flagged_items  │         │ - affected_traits│
         │ - per_response   │         │                  │         │                  │
         └──────────────────┘         └──────────────────┘         └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          Panel Analysis Flow                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     analyzes      ┌──────────────────────┐
│  PanelSession    │◄──────────────────│   VarianceMonitor    │
│  (Phase 2)       │                   │                      │
└────────┬─────────┘                   └──────────┬───────────┘
         │                                        │
         │ contains                               │ produces
         ▼                                        ▼
┌──────────────────┐                   ┌──────────────────────┐
│ Multiple         │                   │   VarianceReport     │
│ SessionResponse  │                   │                      │
│                  │                   │ - rating_variance    │
└──────────────────┘                   │ - sentiment_dist     │
                                       │ - clustering_detected│
                                       │ - stability_score    │
                                       └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          Calibration Flow                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐                   ┌──────────────────────┐
│ CalibrationBase- │     compared      │ Synthetic Session    │
│ line (real data) │◄─────────────────▶│ Results              │
└────────┬─────────┘                   └──────────┬───────────┘
         │                                        │
         └──────────────────┬─────────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │CalibrationComparison │
                 │                      │
                 │ - overlap_percentage │
                 │ - divergence_points  │
                 │ - recommendations    │
                 └──────────────────────┘
```

---

## Core Entities

### QualityThresholds

Configurable limits for quality warnings. Used globally or per-session.

```python
class QualityThresholds(BaseModel):
    """Configurable thresholds for quality gates."""

    # Consistency thresholds
    consistency_minimum: float = 70.0          # Minimum acceptable consistency score (%)
    consistency_warning: float = 80.0          # Warning threshold (%)

    # Sycophancy thresholds
    sycophancy_maximum: float = 30.0           # Maximum acceptable sycophancy rate (%)
    positive_negative_ratio: float = 4.0       # Max ratio before warning

    # Variance thresholds
    variance_minimum_ratio: float = 0.6        # Min ratio vs expected variance
    clustering_threshold: float = 0.8          # Max single-sentiment percentage

    # Drift thresholds
    drift_warning: float = 15.0                # Warning threshold (%)
    drift_critical: float = 25.0               # Critical threshold (%)

    # Validation
    @field_validator("*")
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Threshold must be non-negative")
        return v
```

**Validation Rules:**
- All thresholds must be non-negative
- Percentage thresholds must be 0-100

---

### ConsistencyScore

Measures alignment between persona responses and defined traits.

```python
class TraitAlignment(BaseModel):
    """Alignment score for a single trait."""

    trait_name: str                            # e.g., "openness", "self_direction"
    trait_value: float                         # Defined value (1-10 for Big Five)
    alignment_score: float                     # 0-100%
    matched_keywords: list[str]                # Keywords found in response
    expected_keywords: list[str]               # Keywords expected for trait
    weight: float                              # Trait weight based on extremity


class ConsistencyScore(BaseModel):
    """Comprehensive consistency assessment."""

    # Overall scores
    overall_score: float                       # Combined score (0-100%)
    big_five_score: float                      # Big Five alignment (0-100%)
    schwartz_score: float                      # Schwartz values alignment (0-100%)

    # Per-trait breakdown
    big_five_alignment: list[TraitAlignment]   # 5 items (O, C, E, A, N)
    schwartz_alignment: list[TraitAlignment]   # Variable (priority values only)

    # Per-response scores
    per_response_scores: list[float]           # Score for each response
    response_variance: float                   # Variance across responses

    # Quality flags
    passed_threshold: bool                     # Meets minimum threshold
    warning_flags: list[str]                   # Specific warnings

    # Metadata
    threshold_used: float                      # Threshold applied
    calculation_method: str = "weighted"       # Algorithm used
```

**Validation Rules:**
- All scores must be 0-100
- big_five_alignment must have exactly 5 items
- per_response_scores length must match session response count

**State Transitions:**
- N/A (immutable result object)

---

### BiasAnalysis

Assessment of response bias patterns.

```python
class FlaggedResponse(BaseModel):
    """A response flagged for potential bias."""

    response_index: int                        # Position in session
    response_text: str                         # The flagged text
    flag_type: str                             # "sycophancy", "clustering", "missing_criticism"
    flag_reason: str                           # Human-readable explanation
    confidence: float                          # 0-1 confidence in flag


class SentimentClustering(BaseModel):
    """Detection of unusual sentiment clustering."""

    detected: bool                             # Clustering detected?
    dominant_sentiment: Optional[str]          # "positive", "negative", "mixed", "neutral"
    dominant_percentage: float                 # Percentage of dominant sentiment
    expected_diversity: float                  # Expected diversity based on panel composition
    personas_affected: list[str]               # Persona IDs showing clustering


class BiasAnalysis(BaseModel):
    """Comprehensive bias assessment."""

    # Sycophancy metrics
    sycophancy_rate: float                     # Percentage of sycophantic responses
    sycophancy_phrases_found: list[str]        # Specific phrases detected
    positive_negative_ratio: float             # Ratio of positive to negative keywords

    # Clustering analysis
    sentiment_clustering: SentimentClustering  # Panel sentiment clustering
    response_similarity_score: float           # How similar responses are (0-100)

    # Skeptical persona validation
    skeptical_validation_passed: bool          # Skeptical personas showed criticism?
    missing_criticism_count: int               # Number of skeptical responses without criticism

    # Flagged items
    flagged_responses: list[FlaggedResponse]   # Responses needing review

    # Quality flags
    passed_threshold: bool                     # Meets sycophancy threshold
    warning_flags: list[str]                   # Specific warnings

    # Metadata
    threshold_used: float                      # Sycophancy threshold applied
```

**Validation Rules:**
- sycophancy_rate must be 0-100
- positive_negative_ratio must be non-negative
- response_similarity_score must be 0-100

---

### VarianceReport

Statistical analysis of response diversity across a panel.

```python
class RatingVariance(BaseModel):
    """Variance analysis for rating-type responses."""

    question_id: str                           # Question identifier
    mean: float                                # Mean rating
    stdev: float                               # Standard deviation
    variance: float                            # Statistical variance
    min_value: float                           # Minimum rating
    max_value: float                           # Maximum rating
    expected_stdev: float                      # Expected human baseline stdev
    variance_ratio: float                      # Actual/expected ratio
    clustering_detected: bool                  # Below variance threshold?


class SentimentDistribution(BaseModel):
    """Distribution of sentiment across responses."""

    positive: float                            # Percentage positive
    negative: float                            # Percentage negative
    mixed: float                               # Percentage mixed
    neutral: float                             # Percentage neutral
    diversity_score: float                     # Entropy-based diversity (0-1)


class VarianceReport(BaseModel):
    """Panel variance analysis report."""

    # Quantitative variance
    rating_variances: list[RatingVariance]     # Per-question rating variance
    overall_rating_variance: float             # Aggregated variance ratio

    # Qualitative variance
    sentiment_distribution: SentimentDistribution  # Overall sentiment spread
    theme_diversity: float                     # Number of unique themes / expected

    # Clustering detection
    clustering_detected: bool                  # Any clustering flags?
    clustering_details: list[str]              # Specific clustering issues

    # Stability (multi-session)
    stability_score: Optional[float]           # Variance consistency across sessions
    session_count: int = 1                     # Sessions analyzed

    # Quality flags
    passed_threshold: bool                     # Meets variance threshold
    warning_flags: list[str]                   # Specific warnings

    # Metadata
    panel_size: int                            # Number of personas
    expected_variance_baseline: str            # Baseline source
```

**Validation Rules:**
- All percentages must sum to approximately 100
- variance_ratio must be non-negative
- panel_size must be >= 3 for meaningful variance

---

### DriftAnalysis

Measurement of persona characterization stability over a session.

```python
class SegmentScore(BaseModel):
    """Consistency score for a session segment."""

    segment_index: int                         # 0=beginning, 1=middle, 2=end
    start_response: int                        # First response index in segment
    end_response: int                          # Last response index in segment
    consistency_score: float                   # Segment consistency (0-100)
    response_count: int                        # Responses in segment


class AffectedTrait(BaseModel):
    """A trait showing significant drift."""

    trait_name: str                            # e.g., "conscientiousness"
    trait_type: str                            # "big_five" or "schwartz"
    initial_alignment: float                   # Alignment in first segment
    final_alignment: float                     # Alignment in last segment
    drift_amount: float                        # Absolute difference
    drift_direction: str                       # "increased" or "decreased"


class DriftAnalysis(BaseModel):
    """Session character drift assessment."""

    # Overall drift
    drift_score: float                         # Overall drift (0-100)
    drift_detected: bool                       # Exceeds warning threshold?

    # Segment analysis
    segment_scores: list[SegmentScore]         # Per-segment consistency
    drift_point_index: int                     # Segment where drift began
    drift_point_response: int                  # Approximate response index

    # Trait-level analysis
    affected_traits: list[AffectedTrait]       # Traits showing drift
    stable_traits: list[str]                   # Traits without drift

    # Quality flags
    passed_threshold: bool                     # Below critical threshold?
    warning_level: str                         # "none", "warning", "critical"
    warning_flags: list[str]                   # Specific warnings

    # Metadata
    persona_id: str                            # Persona analyzed
    session_length: int                        # Total responses
    segment_count: int                         # Segments used (typically 3)
```

**Validation Rules:**
- drift_score must be 0-100
- segment_scores must have segment_count items
- warning_level must be one of "none", "warning", "critical"

---

### ExtendedQualityMetrics

Combined quality assessment extending Phase 1 QualityMetrics.

```python
class ExtendedQualityMetrics(BaseModel):
    """Comprehensive quality metrics (Phase 4 extension)."""

    # Phase 1 compatibility fields
    consistency_score: float                   # Overall consistency (0-100)
    sycophancy_indicators: dict                # Legacy format for compatibility
    warnings: list[str]                        # All warnings
    passed_gates: bool                         # All gates passed?
    matched_traits: list[str]                  # Traits matched in responses
    missing_traits: list[str]                  # Expected traits not found

    # Phase 4 extended fields
    consistency_details: ConsistencyScore      # Detailed consistency breakdown
    bias_analysis: BiasAnalysis                # Comprehensive bias assessment
    variance_report: Optional[VarianceReport]  # Panel sessions only
    drift_analysis: Optional[DriftAnalysis]    # Multi-turn sessions only

    # Aggregated status
    quality_status: str                        # "healthy", "warning", "critical"
    quality_score: float                       # Weighted overall score (0-100)

    # Metadata
    analysis_timestamp: datetime               # When analysis was performed
    thresholds_used: QualityThresholds         # Thresholds applied
    session_type: str                          # "single", "panel", "interview", "focus_group"

    @property
    def has_issues(self) -> bool:
        return self.quality_status != "healthy"
```

**Validation Rules:**
- quality_status must be one of "healthy", "warning", "critical"
- variance_report required for panel sessions
- drift_analysis required for interview/focus_group sessions

---

## Calibration Entities

### CalibrationBaseline

Stored real user research data for comparison.

```python
class NumericDistribution(BaseModel):
    """Distribution data for numeric responses."""

    mean: float
    stdev: float
    min_value: float
    max_value: float
    histogram: list[int]                       # Frequency buckets
    bucket_labels: list[str]                   # Bucket range labels


class CategoricalDistribution(BaseModel):
    """Distribution data for categorical responses."""

    frequencies: dict[str, float]              # Option -> percentage
    total_responses: int


class QuestionDistribution(BaseModel):
    """Distribution for a single question."""

    question_id: str
    question_text: Optional[str]
    distribution_type: str                     # "numeric" or "categorical"
    numeric: Optional[NumericDistribution]
    categorical: Optional[CategoricalDistribution]


class CalibrationBaseline(BaseModel):
    """Real user data baseline for calibration."""

    # Identity
    id: str                                    # Unique identifier
    name: str                                  # Human-readable name
    version: str = "1.0.0"                     # Baseline version

    # Source metadata
    source: str                                # Data source description
    sample_size: int                           # Number of real responses
    collection_date: date                      # When data was collected
    collection_method: Optional[str]           # Survey, interview, etc.

    # Demographic tags
    demographic_tags: list[str]                # e.g., ["early_adopter", "us_based"]
    demographic_description: Optional[str]     # Free-text description

    # Distribution data
    distributions: list[QuestionDistribution]  # Per-question distributions

    # Metadata
    created_at: datetime
    notes: Optional[str]

    # Validation
    @field_validator("sample_size")
    def validate_sample_size(cls, v):
        if v < 10:
            raise ValueError("Sample size must be at least 10")
        return v
```

**Validation Rules:**
- sample_size must be >= 10
- distributions must have at least one item
- Each distribution must have either numeric or categorical data

---

### CalibrationComparison

Analysis comparing synthetic responses against real baselines.

```python
class QuestionComparison(BaseModel):
    """Comparison result for a single question."""

    question_id: str
    overlap_percentage: float                  # 0-100%
    synthetic_mean: Optional[float]            # For numeric questions
    baseline_mean: Optional[float]
    mean_difference: Optional[float]
    synthetic_distribution: dict               # Synthetic results
    baseline_distribution: dict                # Baseline data
    divergence_detected: bool                  # Below 60% overlap?


class Recommendation(BaseModel):
    """Persona adjustment recommendation."""

    recommendation_id: str
    target: str                                # "persona", "panel", "protocol"
    target_id: Optional[str]                   # Specific persona/panel ID
    recommendation_type: str                   # "increase", "decrease", "add", "remove"
    parameter: str                             # e.g., "criticism_tendency"
    current_value: Optional[str]
    suggested_value: Optional[str]
    rationale: str                             # Why this recommendation
    priority: str                              # "high", "medium", "low"
    impact_estimate: str                       # Expected improvement


class CalibrationComparison(BaseModel):
    """Full calibration comparison result."""

    # Identity
    id: str                                    # Comparison identifier
    baseline_id: str                           # Baseline used
    session_id: Optional[str]                  # Session compared (if single)
    panel_id: Optional[str]                    # Panel compared

    # Overall results
    overall_overlap: float                     # Average overlap percentage
    alignment_status: str                      # "aligned", "divergent", "partial"

    # Per-question comparison
    question_comparisons: list[QuestionComparison]

    # Divergence analysis
    divergence_points: list[str]               # Questions with significant divergence
    divergence_summary: str                    # Human-readable summary

    # Recommendations
    recommendations: list[Recommendation]       # Adjustment suggestions

    # Metadata
    comparison_timestamp: datetime
    synthetic_sample_size: int
    baseline_sample_size: int

    @property
    def needs_calibration(self) -> bool:
        return self.overall_overlap < 60.0
```

**Validation Rules:**
- overall_overlap must be 0-100
- alignment_status must be one of "aligned", "divergent", "partial"
- Either session_id or panel_id must be provided

---

## Dashboard Entities

### QualityDashboardMetrics

Aggregated metrics for dashboard display.

```python
class SessionSummary(BaseModel):
    """Summary of a single session's quality."""

    session_id: str
    session_type: str                          # "single", "panel", etc.
    panel_id: Optional[str]
    persona_ids: list[str]
    quality_status: str                        # "healthy", "warning", "critical"
    consistency_score: float
    sycophancy_rate: float
    variance_score: Optional[float]
    drift_score: Optional[float]
    timestamp: datetime
    warning_count: int


class TrendDataPoint(BaseModel):
    """Single point in trend data."""

    date: date
    metric_value: float
    session_count: int


class QualityDashboardMetrics(BaseModel):
    """Aggregated dashboard metrics."""

    # Overall health
    overall_status: str                        # "healthy", "warning", "critical"
    sessions_analyzed: int
    sessions_healthy: int
    sessions_warning: int
    sessions_critical: int

    # Aggregated metrics
    avg_consistency_score: float
    avg_sycophancy_rate: float
    avg_variance_score: float
    max_drift_score: float

    # Threshold comparison
    thresholds: QualityThresholds
    metrics_above_threshold: list[str]         # Which metrics pass
    metrics_below_threshold: list[str]         # Which metrics fail

    # Recent sessions
    recent_sessions: list[SessionSummary]      # Last N sessions

    # Trends (optional)
    consistency_trend: Optional[list[TrendDataPoint]]
    sycophancy_trend: Optional[list[TrendDataPoint]]

    # Time range
    analysis_start: datetime
    analysis_end: datetime

    @property
    def health_percentage(self) -> float:
        if self.sessions_analyzed == 0:
            return 100.0
        return (self.sessions_healthy / self.sessions_analyzed) * 100
```

**Validation Rules:**
- sessions_analyzed = sessions_healthy + sessions_warning + sessions_critical
- All averages must be 0-100

---

## Enumerations

```python
class QualityStatus(str, Enum):
    """Quality assessment status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


class DriftWarningLevel(str, Enum):
    """Drift severity levels."""

    NONE = "none"
    WARNING = "warning"
    CRITICAL = "critical"


class AlignmentStatus(str, Enum):
    """Calibration alignment status."""

    ALIGNED = "aligned"
    PARTIAL = "partial"
    DIVERGENT = "divergent"


class RecommendationType(str, Enum):
    """Types of calibration recommendations."""

    INCREASE = "increase"
    DECREASE = "decrease"
    ADD = "add"
    REMOVE = "remove"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

---

## Storage Formats

### Calibration Baseline (YAML)

```yaml
# calibration/baselines/feature-feedback-2026q1.yaml
id: feature-feedback-2026q1
name: "Feature Feedback Survey Q1 2026"
version: "1.0.0"
source: "Real User Survey conducted via Typeform"
sample_size: 150
collection_date: 2026-01-15
collection_method: survey
demographic_tags:
  - early_adopter
  - us_based
  - professional
demographic_description: "US-based professionals, tech industry, ages 25-45"

distributions:
  - question_id: q1_likelihood
    question_text: "How likely are you to use this feature?"
    distribution_type: numeric
    numeric:
      mean: 6.2
      stdev: 2.3
      min_value: 1
      max_value: 10
      histogram: [2, 5, 12, 18, 25, 35, 28, 15, 7, 3]
      bucket_labels: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

  - question_id: q2_concern
    question_text: "What is your primary concern?"
    distribution_type: categorical
    categorical:
      frequencies:
        Privacy: 0.35
        Complexity: 0.28
        Cost: 0.22
        None: 0.15
      total_responses: 150

created_at: 2026-01-20T10:30:00Z
notes: "Baseline for Phase 4 calibration testing"
```

### Quality Report Export (JSON)

```json
{
  "session_id": "session-abc123",
  "analysis_timestamp": "2026-01-27T14:30:00Z",
  "quality_status": "warning",
  "quality_score": 72.5,
  "consistency_details": {
    "overall_score": 78.0,
    "big_five_score": 82.0,
    "schwartz_score": 72.0
  },
  "bias_analysis": {
    "sycophancy_rate": 35.0,
    "passed_threshold": false
  },
  "warnings": [
    "Sycophancy rate (35%) exceeds threshold (30%)"
  ],
  "synthetic_data_disclaimer": "This analysis is based on synthetic user responses generated by AI personas. Results should be validated with real user research for high-stakes decisions."
}
```

---

## Migration Notes

### Phase 1 Compatibility

The existing `QualityMetrics` model from Phase 1 remains unchanged. `ExtendedQualityMetrics` provides:
- All Phase 1 fields at the top level
- New detailed analysis in nested objects
- Backward-compatible serialization

```python
# Convert ExtendedQualityMetrics to Phase 1 format
def to_legacy_format(extended: ExtendedQualityMetrics) -> dict:
    return {
        "consistency_score": extended.consistency_score,
        "sycophancy_indicators": extended.sycophancy_indicators,
        "warnings": extended.warnings,
        "passed_gates": extended.passed_gates,
        "matched_traits": extended.matched_traits,
        "missing_traits": extended.missing_traits,
    }
```

---

**Data Model Status**: Complete
**Ready for**: CLI Contracts
