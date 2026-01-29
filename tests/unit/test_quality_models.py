"""Tests for quality and calibration models.

Validates model creation, field validation, range constraints,
and computed properties for all Phase 4 quality models.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime, date

from models.quality import (
    TraitAlignment, ConsistencyScore, FlaggedResponse, SentimentClustering,
    BiasAnalysis, RatingVariance, QualitySentimentDistribution, VarianceReport,
    SegmentScore, AffectedTrait, DriftAnalysis, ExtendedQualityMetrics,
    SessionSummary, TrendDataPoint, QualityDashboardMetrics,
)
from models.calibration import QualityThresholds
from models.enums import QualityStatus, DriftWarningLevel


# ---------------------------------------------------------------------------
# Helpers: factory functions for building valid model instances
# ---------------------------------------------------------------------------

def _make_trait_alignment(**overrides) -> TraitAlignment:
    defaults = dict(
        trait_name="openness",
        trait_value=7.0,
        alignment_score=85.0,
        matched_keywords=["curious", "explore"],
        expected_keywords=["curious", "explore", "novel"],
        weight=1.0,
    )
    defaults.update(overrides)
    return TraitAlignment(**defaults)


def _make_consistency_score(**overrides) -> ConsistencyScore:
    defaults = dict(
        overall_score=80.0,
        big_five_score=82.0,
        schwartz_score=78.0,
        big_five_alignment=[_make_trait_alignment()],
        schwartz_alignment=[_make_trait_alignment(trait_name="self_direction")],
        per_response_scores=[75.0, 80.0, 85.0],
        response_variance=12.5,
        passed_threshold=True,
        threshold_used=70.0,
    )
    defaults.update(overrides)
    return ConsistencyScore(**defaults)


def _make_flagged_response(**overrides) -> FlaggedResponse:
    defaults = dict(
        response_index=0,
        response_text="This is absolutely amazing!",
        flag_type="sycophancy",
        flag_reason="Excessive positive language",
        confidence=0.85,
    )
    defaults.update(overrides)
    return FlaggedResponse(**defaults)


def _make_sentiment_clustering(**overrides) -> SentimentClustering:
    defaults = dict(
        detected=True,
        dominant_sentiment="positive",
        dominant_percentage=75.0,
        expected_diversity=0.6,
        personas_affected=["persona_1"],
    )
    defaults.update(overrides)
    return SentimentClustering(**defaults)


def _make_bias_analysis(**overrides) -> BiasAnalysis:
    defaults = dict(
        sycophancy_rate=15.0,
        sycophancy_phrases_found=["absolutely amazing"],
        positive_negative_ratio=3.0,
        sentiment_clustering=_make_sentiment_clustering(),
        flagged_responses=[_make_flagged_response()],
        passed_threshold=True,
        threshold_used=30.0,
    )
    defaults.update(overrides)
    return BiasAnalysis(**defaults)


def _make_rating_variance(**overrides) -> RatingVariance:
    defaults = dict(
        question_id="q1",
        mean=3.5,
        stdev=1.2,
        variance=1.44,
        min_value=1.0,
        max_value=5.0,
        expected_stdev=1.0,
        variance_ratio=1.2,
        clustering_detected=False,
    )
    defaults.update(overrides)
    return RatingVariance(**defaults)


def _make_quality_sentiment_distribution(**overrides) -> QualitySentimentDistribution:
    defaults = dict(
        positive=40.0,
        negative=20.0,
        mixed=25.0,
        neutral=15.0,
        diversity_score=0.8,
    )
    defaults.update(overrides)
    return QualitySentimentDistribution(**defaults)


def _make_variance_report(**overrides) -> VarianceReport:
    defaults = dict(
        rating_variances=[_make_rating_variance()],
        overall_rating_variance=1.44,
        sentiment_distribution=_make_quality_sentiment_distribution(),
        clustering_detected=False,
        passed_threshold=True,
        panel_size=5,
        expected_variance_baseline="default_baseline",
    )
    defaults.update(overrides)
    return VarianceReport(**defaults)


def _make_segment_score(**overrides) -> SegmentScore:
    defaults = dict(
        segment_index=0,
        start_response=0,
        end_response=4,
        consistency_score=85.0,
        response_count=5,
    )
    defaults.update(overrides)
    return SegmentScore(**defaults)


def _make_affected_trait(**overrides) -> AffectedTrait:
    defaults = dict(
        trait_name="openness",
        trait_type="big_five",
        initial_alignment=90.0,
        final_alignment=60.0,
        drift_amount=30.0,
        drift_direction="decreased",
    )
    defaults.update(overrides)
    return AffectedTrait(**defaults)


def _make_drift_analysis(**overrides) -> DriftAnalysis:
    defaults = dict(
        drift_score=20.0,
        drift_detected=True,
        segment_scores=[
            _make_segment_score(segment_index=0, consistency_score=90.0),
            _make_segment_score(segment_index=1, start_response=5, end_response=9, consistency_score=70.0),
        ],
        drift_point_index=1,
        drift_point_response=5,
        affected_traits=[_make_affected_trait()],
        stable_traits=["conscientiousness"],
        passed_threshold=False,
        warning_level=DriftWarningLevel.WARNING,
        persona_id="persona_1",
        session_length=10,
        segment_count=2,
    )
    defaults.update(overrides)
    return DriftAnalysis(**defaults)


def _make_extended_quality_metrics(**overrides) -> ExtendedQualityMetrics:
    defaults = dict(
        consistency_score=80.0,
        passed_gates=True,
        consistency_details=_make_consistency_score(),
        bias_analysis=_make_bias_analysis(),
        quality_status=QualityStatus.HEALTHY,
        quality_score=85.0,
        thresholds_used=QualityThresholds(),
        session_type="survey",
    )
    defaults.update(overrides)
    return ExtendedQualityMetrics(**defaults)


def _make_session_summary(**overrides) -> SessionSummary:
    defaults = dict(
        session_id="sess_001",
        session_type="survey",
        quality_status=QualityStatus.HEALTHY,
        consistency_score=85.0,
        sycophancy_rate=10.0,
        timestamp=datetime(2026, 1, 15, 10, 0, 0),
        warning_count=0,
    )
    defaults.update(overrides)
    return SessionSummary(**defaults)


def _make_trend_data_point(**overrides) -> TrendDataPoint:
    defaults = dict(
        date=date(2026, 1, 15),
        metric_value=82.5,
        session_count=3,
    )
    defaults.update(overrides)
    return TrendDataPoint(**defaults)


def _make_quality_dashboard_metrics(**overrides) -> QualityDashboardMetrics:
    defaults = dict(
        overall_status=QualityStatus.HEALTHY,
        sessions_analyzed=10,
        sessions_healthy=8,
        sessions_warning=1,
        sessions_critical=1,
        avg_consistency_score=82.0,
        avg_sycophancy_rate=12.0,
        avg_variance_score=1.3,
        max_drift_score=18.0,
        thresholds=QualityThresholds(),
        analysis_start=datetime(2026, 1, 1),
        analysis_end=datetime(2026, 1, 28),
    )
    defaults.update(overrides)
    return QualityDashboardMetrics(**defaults)


# ---------------------------------------------------------------------------
# T007: QualityThresholds
# ---------------------------------------------------------------------------


class TestQualityThresholds:
    """Tests for QualityThresholds model validation (T007)."""

    def test_default_values(self):
        """Default thresholds match specification."""
        thresholds = QualityThresholds()
        assert thresholds.consistency_minimum == 70.0
        assert thresholds.sycophancy_maximum == 30.0
        assert thresholds.drift_warning == 15.0
        assert thresholds.drift_critical == 25.0
        assert thresholds.variance_minimum_ratio == 0.6

    def test_non_negative_consistency_minimum(self):
        """consistency_minimum must be >= 0."""
        with pytest.raises(ValidationError):
            QualityThresholds(consistency_minimum=-1)

    def test_non_negative_sycophancy_maximum(self):
        """sycophancy_maximum must be >= 0."""
        with pytest.raises(ValidationError):
            QualityThresholds(sycophancy_maximum=-5)

    def test_non_negative_drift_warning(self):
        """drift_warning must be >= 0."""
        with pytest.raises(ValidationError):
            QualityThresholds(drift_warning=-1)

    def test_non_negative_drift_critical(self):
        """drift_critical must be >= 0."""
        with pytest.raises(ValidationError):
            QualityThresholds(drift_critical=-1)

    def test_non_negative_variance_minimum_ratio(self):
        """variance_minimum_ratio must be >= 0."""
        with pytest.raises(ValidationError):
            QualityThresholds(variance_minimum_ratio=-0.1)

    def test_percentage_consistency_minimum_max(self):
        """consistency_minimum must be <= 100."""
        with pytest.raises(ValidationError):
            QualityThresholds(consistency_minimum=101)

    def test_percentage_sycophancy_maximum_max(self):
        """sycophancy_maximum must be <= 100."""
        with pytest.raises(ValidationError):
            QualityThresholds(sycophancy_maximum=101)

    def test_percentage_drift_warning_max(self):
        """drift_warning must be <= 100."""
        with pytest.raises(ValidationError):
            QualityThresholds(drift_warning=101)

    def test_percentage_drift_critical_max(self):
        """drift_critical must be <= 100."""
        with pytest.raises(ValidationError):
            QualityThresholds(drift_critical=101)

    def test_custom_threshold_values(self):
        """Custom threshold values are accepted and stored."""
        thresholds = QualityThresholds(
            consistency_minimum=60.0,
            sycophancy_maximum=20.0,
            drift_warning=10.0,
            drift_critical=20.0,
            variance_minimum_ratio=0.5,
        )
        assert thresholds.consistency_minimum == 60.0
        assert thresholds.sycophancy_maximum == 20.0
        assert thresholds.drift_warning == 10.0
        assert thresholds.drift_critical == 20.0
        assert thresholds.variance_minimum_ratio == 0.5


# ---------------------------------------------------------------------------
# T008: TraitAlignment & ExtendedQualityMetrics
# ---------------------------------------------------------------------------


class TestTraitAlignment:
    """Tests for TraitAlignment model (T008)."""

    def test_creation_with_valid_data(self):
        """TraitAlignment can be created with valid fields."""
        ta = _make_trait_alignment()
        assert ta.trait_name == "openness"
        assert ta.alignment_score == 85.0
        assert ta.matched_keywords == ["curious", "explore"]

    def test_alignment_score_lower_bound(self):
        """alignment_score must be >= 0."""
        with pytest.raises(ValidationError):
            _make_trait_alignment(alignment_score=-1)

    def test_alignment_score_upper_bound(self):
        """alignment_score must be <= 100."""
        with pytest.raises(ValidationError):
            _make_trait_alignment(alignment_score=101)

    def test_alignment_score_boundary_zero(self):
        """alignment_score of 0 is valid."""
        ta = _make_trait_alignment(alignment_score=0)
        assert ta.alignment_score == 0

    def test_alignment_score_boundary_hundred(self):
        """alignment_score of 100 is valid."""
        ta = _make_trait_alignment(alignment_score=100)
        assert ta.alignment_score == 100


class TestExtendedQualityMetrics:
    """Tests for ExtendedQualityMetrics model (T008)."""

    def test_creation_with_required_fields(self):
        """ExtendedQualityMetrics can be created with all required fields."""
        eqm = _make_extended_quality_metrics()
        assert eqm.consistency_score == 80.0
        assert eqm.quality_status == QualityStatus.HEALTHY
        assert eqm.quality_score == 85.0
        assert eqm.session_type == "survey"

    def test_has_issues_false_when_healthy(self):
        """has_issues returns False when status is HEALTHY."""
        eqm = _make_extended_quality_metrics(quality_status=QualityStatus.HEALTHY)
        assert eqm.has_issues is False

    def test_has_issues_true_when_warning(self):
        """has_issues returns True when status is WARNING."""
        eqm = _make_extended_quality_metrics(quality_status=QualityStatus.WARNING)
        assert eqm.has_issues is True

    def test_has_issues_true_when_critical(self):
        """has_issues returns True when status is CRITICAL."""
        eqm = _make_extended_quality_metrics(quality_status=QualityStatus.CRITICAL)
        assert eqm.has_issues is True

    def test_optional_fields_default_none(self):
        """Optional fields default to None."""
        eqm = _make_extended_quality_metrics()
        assert eqm.variance_report is None
        assert eqm.drift_analysis is None
        assert eqm.matched_traits is None
        assert eqm.missing_traits is None

    def test_analysis_timestamp_auto_set(self):
        """analysis_timestamp is automatically populated."""
        eqm = _make_extended_quality_metrics()
        assert isinstance(eqm.analysis_timestamp, datetime)


# ---------------------------------------------------------------------------
# T011: ConsistencyScore
# ---------------------------------------------------------------------------


class TestConsistencyScore:
    """Tests for ConsistencyScore model (T011)."""

    def test_overall_score_lower_bound(self):
        """overall_score must be >= 0."""
        with pytest.raises(ValidationError):
            _make_consistency_score(overall_score=-1)

    def test_overall_score_upper_bound(self):
        """overall_score must be <= 100."""
        with pytest.raises(ValidationError):
            _make_consistency_score(overall_score=101)

    def test_overall_score_valid_boundaries(self):
        """overall_score of 0 and 100 are valid."""
        cs_zero = _make_consistency_score(overall_score=0, passed_threshold=False)
        assert cs_zero.overall_score == 0
        cs_hundred = _make_consistency_score(overall_score=100)
        assert cs_hundred.overall_score == 100

    def test_big_five_alignment_list(self):
        """big_five_alignment contains TraitAlignment instances."""
        cs = _make_consistency_score()
        assert len(cs.big_five_alignment) == 1
        assert isinstance(cs.big_five_alignment[0], TraitAlignment)
        assert cs.big_five_alignment[0].trait_name == "openness"

    def test_per_response_scores(self):
        """per_response_scores stores list of floats."""
        scores = [60.0, 70.0, 80.0, 90.0]
        cs = _make_consistency_score(per_response_scores=scores)
        assert cs.per_response_scores == scores
        assert len(cs.per_response_scores) == 4

    def test_passed_threshold_true_when_above(self):
        """passed_threshold is True when score exceeds threshold."""
        cs = _make_consistency_score(
            overall_score=85.0, passed_threshold=True, threshold_used=70.0
        )
        assert cs.passed_threshold is True

    def test_passed_threshold_false_when_below(self):
        """passed_threshold is False when score is below threshold."""
        cs = _make_consistency_score(
            overall_score=50.0, passed_threshold=False, threshold_used=70.0
        )
        assert cs.passed_threshold is False

    def test_response_variance_non_negative(self):
        """response_variance must be >= 0."""
        with pytest.raises(ValidationError):
            _make_consistency_score(response_variance=-1.0)

    def test_warning_flags_default_empty(self):
        """warning_flags defaults to empty list."""
        cs = _make_consistency_score()
        assert cs.warning_flags == []


# ---------------------------------------------------------------------------
# T024: FlaggedResponse, SentimentClustering, BiasAnalysis
# ---------------------------------------------------------------------------


class TestFlaggedResponse:
    """Tests for FlaggedResponse model (T024)."""

    def test_creation(self):
        """FlaggedResponse can be created with valid data."""
        fr = _make_flagged_response()
        assert fr.response_index == 0
        assert fr.flag_type == "sycophancy"
        assert fr.confidence == 0.85

    def test_confidence_lower_bound(self):
        """confidence must be >= 0."""
        with pytest.raises(ValidationError):
            _make_flagged_response(confidence=-0.1)

    def test_confidence_upper_bound(self):
        """confidence must be <= 1."""
        with pytest.raises(ValidationError):
            _make_flagged_response(confidence=1.1)

    def test_confidence_boundary_zero(self):
        """confidence of 0 is valid."""
        fr = _make_flagged_response(confidence=0)
        assert fr.confidence == 0

    def test_confidence_boundary_one(self):
        """confidence of 1 is valid."""
        fr = _make_flagged_response(confidence=1)
        assert fr.confidence == 1

    def test_response_index_non_negative(self):
        """response_index must be >= 0."""
        with pytest.raises(ValidationError):
            _make_flagged_response(response_index=-1)


class TestSentimentClustering:
    """Tests for SentimentClustering model (T024)."""

    def test_creation(self):
        """SentimentClustering can be created with valid data."""
        sc = _make_sentiment_clustering()
        assert sc.detected is True
        assert sc.dominant_sentiment == "positive"
        assert sc.dominant_percentage == 75.0

    def test_dominant_percentage_lower_bound(self):
        """dominant_percentage must be >= 0."""
        with pytest.raises(ValidationError):
            _make_sentiment_clustering(dominant_percentage=-1)

    def test_dominant_percentage_upper_bound(self):
        """dominant_percentage must be <= 100."""
        with pytest.raises(ValidationError):
            _make_sentiment_clustering(dominant_percentage=101)

    def test_dominant_percentage_boundary_values(self):
        """dominant_percentage of 0 and 100 are valid."""
        sc_zero = _make_sentiment_clustering(dominant_percentage=0, detected=False)
        assert sc_zero.dominant_percentage == 0
        sc_full = _make_sentiment_clustering(dominant_percentage=100)
        assert sc_full.dominant_percentage == 100

    def test_dominant_sentiment_optional(self):
        """dominant_sentiment defaults to None."""
        sc = _make_sentiment_clustering(
            detected=False, dominant_sentiment=None, dominant_percentage=30.0
        )
        assert sc.dominant_sentiment is None


class TestBiasAnalysis:
    """Tests for BiasAnalysis model (T024)."""

    def test_creation_with_all_fields(self):
        """BiasAnalysis can be created with all required fields."""
        ba = _make_bias_analysis()
        assert ba.sycophancy_rate == 15.0
        assert ba.positive_negative_ratio == 3.0
        assert ba.passed_threshold is True
        assert isinstance(ba.sentiment_clustering, SentimentClustering)
        assert len(ba.flagged_responses) == 1

    def test_sycophancy_rate_range(self):
        """sycophancy_rate must be 0-100."""
        with pytest.raises(ValidationError):
            _make_bias_analysis(sycophancy_rate=-1)
        with pytest.raises(ValidationError):
            _make_bias_analysis(sycophancy_rate=101)

    def test_positive_negative_ratio_non_negative(self):
        """positive_negative_ratio must be >= 0."""
        with pytest.raises(ValidationError):
            _make_bias_analysis(positive_negative_ratio=-1)

    def test_warning_flags_default_empty(self):
        """warning_flags defaults to empty list."""
        ba = _make_bias_analysis()
        assert ba.warning_flags == []


# ---------------------------------------------------------------------------
# T040: RatingVariance, QualitySentimentDistribution, VarianceReport
# ---------------------------------------------------------------------------


class TestRatingVariance:
    """Tests for RatingVariance model (T040)."""

    def test_creation(self):
        """RatingVariance can be created with valid data."""
        rv = _make_rating_variance()
        assert rv.question_id == "q1"
        assert rv.mean == 3.5
        assert rv.stdev == 1.2
        assert rv.clustering_detected is False

    def test_stdev_non_negative(self):
        """stdev must be >= 0."""
        with pytest.raises(ValidationError):
            _make_rating_variance(stdev=-0.1)

    def test_stdev_zero_valid(self):
        """stdev of 0 is valid (all ratings identical)."""
        rv = _make_rating_variance(stdev=0)
        assert rv.stdev == 0

    def test_variance_non_negative(self):
        """variance must be >= 0."""
        with pytest.raises(ValidationError):
            _make_rating_variance(variance=-1)

    def test_variance_ratio_non_negative(self):
        """variance_ratio must be >= 0."""
        with pytest.raises(ValidationError):
            _make_rating_variance(variance_ratio=-0.5)


class TestQualitySentimentDistribution:
    """Tests for QualitySentimentDistribution model (T040)."""

    def test_creation_with_valid_percentages(self):
        """QualitySentimentDistribution accepts valid percentage values."""
        qsd = _make_quality_sentiment_distribution()
        assert qsd.positive == 40.0
        assert qsd.negative == 20.0
        assert qsd.mixed == 25.0
        assert qsd.neutral == 15.0
        assert qsd.diversity_score == 0.8

    def test_percentage_lower_bound(self):
        """Percentage fields must be >= 0."""
        with pytest.raises(ValidationError):
            _make_quality_sentiment_distribution(positive=-1)
        with pytest.raises(ValidationError):
            _make_quality_sentiment_distribution(negative=-1)

    def test_percentage_upper_bound(self):
        """Percentage fields must be <= 100."""
        with pytest.raises(ValidationError):
            _make_quality_sentiment_distribution(positive=101)
        with pytest.raises(ValidationError):
            _make_quality_sentiment_distribution(neutral=101)

    def test_diversity_score_range(self):
        """diversity_score must be 0-1."""
        with pytest.raises(ValidationError):
            _make_quality_sentiment_distribution(diversity_score=-0.1)
        with pytest.raises(ValidationError):
            _make_quality_sentiment_distribution(diversity_score=1.1)


class TestVarianceReport:
    """Tests for VarianceReport model (T040)."""

    def test_creation_with_full_data(self):
        """VarianceReport can be created with complete data."""
        vr = _make_variance_report()
        assert vr.overall_rating_variance == 1.44
        assert len(vr.rating_variances) == 1
        assert isinstance(vr.sentiment_distribution, QualitySentimentDistribution)
        assert vr.clustering_detected is False
        assert vr.passed_threshold is True
        assert vr.panel_size == 5
        assert vr.expected_variance_baseline == "default_baseline"

    def test_overall_rating_variance_non_negative(self):
        """overall_rating_variance must be >= 0."""
        with pytest.raises(ValidationError):
            _make_variance_report(overall_rating_variance=-1)

    def test_panel_size_minimum(self):
        """panel_size must be >= 1."""
        with pytest.raises(ValidationError):
            _make_variance_report(panel_size=0)

    def test_session_count_default(self):
        """session_count defaults to 1."""
        vr = _make_variance_report()
        assert vr.session_count == 1

    def test_stability_score_optional(self):
        """stability_score defaults to None."""
        vr = _make_variance_report()
        assert vr.stability_score is None

    def test_clustering_details_default_empty(self):
        """clustering_details defaults to empty list."""
        vr = _make_variance_report()
        assert vr.clustering_details == []


# ---------------------------------------------------------------------------
# T054: SegmentScore, AffectedTrait, DriftAnalysis
# ---------------------------------------------------------------------------


class TestSegmentScore:
    """Tests for SegmentScore model (T054)."""

    def test_creation_with_valid_data(self):
        """SegmentScore can be created with valid segment data."""
        ss = _make_segment_score()
        assert ss.segment_index == 0
        assert ss.start_response == 0
        assert ss.end_response == 4
        assert ss.consistency_score == 85.0
        assert ss.response_count == 5

    def test_segment_index_non_negative(self):
        """segment_index must be >= 0."""
        with pytest.raises(ValidationError):
            _make_segment_score(segment_index=-1)

    def test_consistency_score_range(self):
        """consistency_score must be 0-100."""
        with pytest.raises(ValidationError):
            _make_segment_score(consistency_score=-1)
        with pytest.raises(ValidationError):
            _make_segment_score(consistency_score=101)

    def test_response_count_minimum(self):
        """response_count must be >= 1."""
        with pytest.raises(ValidationError):
            _make_segment_score(response_count=0)


class TestAffectedTrait:
    """Tests for AffectedTrait model (T054)."""

    def test_creation_valid(self):
        """AffectedTrait can be created with valid data."""
        at = _make_affected_trait()
        assert at.trait_name == "openness"
        assert at.trait_type == "big_five"
        assert at.drift_direction == "decreased"

    def test_trait_type_big_five(self):
        """trait_type accepts 'big_five'."""
        at = _make_affected_trait(trait_type="big_five")
        assert at.trait_type == "big_five"

    def test_trait_type_schwartz(self):
        """trait_type accepts 'schwartz'."""
        at = _make_affected_trait(trait_type="schwartz")
        assert at.trait_type == "schwartz"

    def test_trait_type_invalid(self):
        """trait_type rejects values other than 'big_five' or 'schwartz'."""
        with pytest.raises(ValidationError):
            _make_affected_trait(trait_type="other")

    def test_drift_direction_increased(self):
        """drift_direction accepts 'increased'."""
        at = _make_affected_trait(drift_direction="increased")
        assert at.drift_direction == "increased"

    def test_drift_direction_decreased(self):
        """drift_direction accepts 'decreased'."""
        at = _make_affected_trait(drift_direction="decreased")
        assert at.drift_direction == "decreased"

    def test_drift_direction_invalid(self):
        """drift_direction rejects values other than 'increased'/'decreased'."""
        with pytest.raises(ValidationError):
            _make_affected_trait(drift_direction="stable")

    def test_alignment_range(self):
        """initial_alignment and final_alignment must be 0-100."""
        with pytest.raises(ValidationError):
            _make_affected_trait(initial_alignment=-1)
        with pytest.raises(ValidationError):
            _make_affected_trait(final_alignment=101)

    def test_drift_amount_non_negative(self):
        """drift_amount must be >= 0."""
        with pytest.raises(ValidationError):
            _make_affected_trait(drift_amount=-5)


class TestDriftAnalysis:
    """Tests for DriftAnalysis model (T054)."""

    def test_creation(self):
        """DriftAnalysis can be created with valid data."""
        da = _make_drift_analysis()
        assert da.drift_score == 20.0
        assert da.drift_detected is True
        assert da.persona_id == "persona_1"
        assert len(da.segment_scores) == 2
        assert len(da.affected_traits) == 1

    def test_drift_score_range(self):
        """drift_score must be 0-100."""
        with pytest.raises(ValidationError):
            _make_drift_analysis(drift_score=-1)
        with pytest.raises(ValidationError):
            _make_drift_analysis(drift_score=101)

    def test_warning_level_none(self):
        """warning_level accepts NONE."""
        da = _make_drift_analysis(
            warning_level=DriftWarningLevel.NONE,
            drift_detected=False,
            passed_threshold=True,
        )
        assert da.warning_level == DriftWarningLevel.NONE

    def test_warning_level_warning(self):
        """warning_level accepts WARNING."""
        da = _make_drift_analysis(warning_level=DriftWarningLevel.WARNING)
        assert da.warning_level == DriftWarningLevel.WARNING

    def test_warning_level_critical(self):
        """warning_level accepts CRITICAL."""
        da = _make_drift_analysis(warning_level=DriftWarningLevel.CRITICAL)
        assert da.warning_level == DriftWarningLevel.CRITICAL

    def test_session_length_minimum(self):
        """session_length must be >= 1."""
        with pytest.raises(ValidationError):
            _make_drift_analysis(session_length=0)

    def test_segment_count_minimum(self):
        """segment_count must be >= 1."""
        with pytest.raises(ValidationError):
            _make_drift_analysis(segment_count=0)

    def test_passed_threshold(self):
        """passed_threshold reflects drift vs threshold relationship."""
        da_pass = _make_drift_analysis(
            drift_score=5.0, passed_threshold=True,
            warning_level=DriftWarningLevel.NONE, drift_detected=False,
        )
        assert da_pass.passed_threshold is True

        da_fail = _make_drift_analysis(drift_score=30.0, passed_threshold=False)
        assert da_fail.passed_threshold is False


# ---------------------------------------------------------------------------
# T096: SessionSummary, TrendDataPoint, QualityDashboardMetrics
# ---------------------------------------------------------------------------


class TestSessionSummary:
    """Tests for SessionSummary model (T096)."""

    def test_creation(self):
        """SessionSummary can be created with valid data."""
        ss = _make_session_summary()
        assert ss.session_id == "sess_001"
        assert ss.session_type == "survey"
        assert ss.quality_status == QualityStatus.HEALTHY
        assert ss.consistency_score == 85.0
        assert ss.sycophancy_rate == 10.0
        assert ss.warning_count == 0

    def test_optional_scores_default_none(self):
        """variance_score and drift_score default to None."""
        ss = _make_session_summary()
        assert ss.variance_score is None
        assert ss.drift_score is None

    def test_consistency_score_range(self):
        """consistency_score must be 0-100."""
        with pytest.raises(ValidationError):
            _make_session_summary(consistency_score=-1)
        with pytest.raises(ValidationError):
            _make_session_summary(consistency_score=101)

    def test_sycophancy_rate_range(self):
        """sycophancy_rate must be 0-100."""
        with pytest.raises(ValidationError):
            _make_session_summary(sycophancy_rate=-1)
        with pytest.raises(ValidationError):
            _make_session_summary(sycophancy_rate=101)

    def test_warning_count_non_negative(self):
        """warning_count must be >= 0."""
        with pytest.raises(ValidationError):
            _make_session_summary(warning_count=-1)


class TestTrendDataPoint:
    """Tests for TrendDataPoint model (T096)."""

    def test_creation_with_date(self):
        """TrendDataPoint can be created with a date."""
        tdp = _make_trend_data_point()
        assert tdp.date == date(2026, 1, 15)
        assert tdp.metric_value == 82.5
        assert tdp.session_count == 3

    def test_session_count_minimum(self):
        """session_count must be >= 1."""
        with pytest.raises(ValidationError):
            _make_trend_data_point(session_count=0)

    def test_different_dates(self):
        """TrendDataPoint accepts various date values."""
        tdp = _make_trend_data_point(date=date(2025, 12, 31))
        assert tdp.date == date(2025, 12, 31)


class TestQualityDashboardMetrics:
    """Tests for QualityDashboardMetrics model (T096)."""

    def test_creation(self):
        """QualityDashboardMetrics can be created with valid data."""
        qdm = _make_quality_dashboard_metrics()
        assert qdm.overall_status == QualityStatus.HEALTHY
        assert qdm.sessions_analyzed == 10
        assert qdm.sessions_healthy == 8
        assert qdm.sessions_warning == 1
        assert qdm.sessions_critical == 1

    def test_health_percentage_property(self):
        """health_percentage returns correct percentage of healthy sessions."""
        qdm = _make_quality_dashboard_metrics(
            sessions_analyzed=10, sessions_healthy=8
        )
        assert qdm.health_percentage == 80.0

    def test_health_percentage_all_healthy(self):
        """health_percentage returns 100 when all sessions are healthy."""
        qdm = _make_quality_dashboard_metrics(
            sessions_analyzed=5, sessions_healthy=5,
            sessions_warning=0, sessions_critical=0,
        )
        assert qdm.health_percentage == 100.0

    def test_health_percentage_none_healthy(self):
        """health_percentage returns 0 when no sessions are healthy."""
        qdm = _make_quality_dashboard_metrics(
            sessions_analyzed=5, sessions_healthy=0,
            sessions_warning=3, sessions_critical=2,
        )
        assert qdm.health_percentage == 0.0

    def test_health_percentage_zero_sessions(self):
        """health_percentage returns 100 when no sessions analyzed."""
        qdm = _make_quality_dashboard_metrics(
            sessions_analyzed=0, sessions_healthy=0,
            sessions_warning=0, sessions_critical=0,
        )
        assert qdm.health_percentage == 100.0

    def test_avg_consistency_score_range(self):
        """avg_consistency_score must be 0-100."""
        with pytest.raises(ValidationError):
            _make_quality_dashboard_metrics(avg_consistency_score=-1)
        with pytest.raises(ValidationError):
            _make_quality_dashboard_metrics(avg_consistency_score=101)

    def test_max_drift_score_range(self):
        """max_drift_score must be 0-100."""
        with pytest.raises(ValidationError):
            _make_quality_dashboard_metrics(max_drift_score=-1)
        with pytest.raises(ValidationError):
            _make_quality_dashboard_metrics(max_drift_score=101)

    def test_recent_sessions_default_empty(self):
        """recent_sessions defaults to empty list."""
        qdm = _make_quality_dashboard_metrics()
        assert qdm.recent_sessions == []

    def test_trends_default_none(self):
        """Trend fields default to None."""
        qdm = _make_quality_dashboard_metrics()
        assert qdm.consistency_trend is None
        assert qdm.sycophancy_trend is None
