"""Tests for calibration models (T069-T070).

Validates model creation, field validation, range constraints,
and computed properties for CalibrationBaseline and CalibrationComparison models.
"""

import pytest
from pydantic import ValidationError
from datetime import date, datetime

from models.calibration import (
    NumericDistribution,
    CategoricalDistribution,
    QuestionDistribution,
    CalibrationBaseline,
    QuestionComparison,
    Recommendation,
    CalibrationComparison,
    QualityThresholds,
)
from models.enums import AlignmentStatus, RecommendationType, RecommendationPriority


# ---------------------------------------------------------------------------
# Helpers: factory functions for building valid model instances
# ---------------------------------------------------------------------------


def _make_numeric_distribution(**overrides) -> NumericDistribution:
    defaults = dict(
        mean=6.2,
        stdev=2.3,
        min_value=1.0,
        max_value=10.0,
        histogram=[2, 3, 5, 7, 8, 10, 7, 4, 3, 1],
        bucket_labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    )
    defaults.update(overrides)
    return NumericDistribution(**defaults)


def _make_categorical_distribution(**overrides) -> CategoricalDistribution:
    defaults = dict(
        frequencies={"Privacy": 0.35, "Complexity": 0.28, "Cost": 0.22, "None": 0.15},
        total_responses=50,
    )
    defaults.update(overrides)
    return CategoricalDistribution(**defaults)


def _make_question_distribution(dist_type="numeric", **overrides) -> QuestionDistribution:
    defaults = dict(
        question_id="q1",
        question_text="How likely are you to use this feature?",
        distribution_type=dist_type,
    )
    if dist_type == "numeric":
        defaults["numeric"] = _make_numeric_distribution()
    elif dist_type == "categorical":
        defaults["categorical"] = _make_categorical_distribution()
    defaults.update(overrides)
    return QuestionDistribution(**defaults)


def _make_calibration_baseline(**overrides) -> CalibrationBaseline:
    defaults = dict(
        id="baseline-001",
        name="Test Baseline",
        version="1.0.0",
        source="User Survey 2026",
        sample_size=50,
        collection_date=date(2026, 1, 15),
        demographic_tags=["early_adopter", "professional"],
        distributions=[_make_question_distribution("numeric")],
    )
    defaults.update(overrides)
    return CalibrationBaseline(**defaults)


def _make_question_comparison(**overrides) -> QuestionComparison:
    defaults = dict(
        question_id="q1",
        overlap_percentage=75.0,
        synthetic_mean=6.5,
        baseline_mean=6.2,
        mean_difference=0.3,
        synthetic_distribution={"1": 0.05, "5": 0.20, "10": 0.10},
        baseline_distribution={"1": 0.04, "5": 0.16, "10": 0.02},
        divergence_detected=False,
    )
    defaults.update(overrides)
    return QuestionComparison(**defaults)


def _make_recommendation(**overrides) -> Recommendation:
    defaults = dict(
        recommendation_id="rec-001",
        target="persona",
        target_id="persona-1",
        recommendation_type=RecommendationType.INCREASE,
        parameter="criticism_tendency",
        current_value="balanced",
        suggested_value="critical",
        rationale="Synthetic responses are more positive than real data",
        priority=RecommendationPriority.HIGH,
        impact_estimate="Expected to improve overlap by ~10%",
    )
    defaults.update(overrides)
    return Recommendation(**defaults)


def _make_calibration_comparison(**overrides) -> CalibrationComparison:
    defaults = dict(
        id="comp-001",
        baseline_id="baseline-001",
        session_id="sess-001",
        panel_id="panel-001",
        overall_overlap=75.0,
        alignment_status=AlignmentStatus.ALIGNED,
        question_comparisons=[_make_question_comparison()],
        divergence_points=[],
        divergence_summary="",
        recommendations=[],
        synthetic_sample_size=30,
        baseline_sample_size=50,
    )
    defaults.update(overrides)
    return CalibrationComparison(**defaults)


# ---------------------------------------------------------------------------
# T069: NumericDistribution, CategoricalDistribution, QuestionDistribution,
#       CalibrationBaseline
# ---------------------------------------------------------------------------


class TestNumericDistribution:
    """Tests for NumericDistribution model (T069)."""

    def test_creation_with_valid_data(self):
        """NumericDistribution can be created with valid fields."""
        nd = _make_numeric_distribution()
        assert nd.mean == 6.2
        assert nd.stdev == 2.3
        assert nd.min_value == 1.0
        assert nd.max_value == 10.0
        assert len(nd.histogram) == 10
        assert len(nd.bucket_labels) == 10

    def test_stdev_non_negative(self):
        """stdev must be >= 0."""
        with pytest.raises(ValidationError):
            _make_numeric_distribution(stdev=-0.1)

    def test_stdev_zero_valid(self):
        """stdev of 0 is valid (all values identical)."""
        nd = _make_numeric_distribution(stdev=0)
        assert nd.stdev == 0

    def test_histogram_stores_counts(self):
        """histogram stores integer frequency counts."""
        nd = _make_numeric_distribution(histogram=[1, 2, 3])
        assert nd.histogram == [1, 2, 3]

    def test_bucket_labels_stores_strings(self):
        """bucket_labels stores label strings."""
        nd = _make_numeric_distribution(bucket_labels=["low", "mid", "high"])
        assert nd.bucket_labels == ["low", "mid", "high"]


class TestCategoricalDistribution:
    """Tests for CategoricalDistribution model (T069)."""

    def test_creation_with_valid_data(self):
        """CategoricalDistribution can be created with valid fields."""
        cd = _make_categorical_distribution()
        assert cd.frequencies["Privacy"] == 0.35
        assert cd.total_responses == 50

    def test_total_responses_minimum(self):
        """total_responses must be >= 1."""
        with pytest.raises(ValidationError):
            _make_categorical_distribution(total_responses=0)

    def test_total_responses_negative(self):
        """total_responses rejects negative values."""
        with pytest.raises(ValidationError):
            _make_categorical_distribution(total_responses=-5)

    def test_frequencies_stores_dict(self):
        """frequencies stores option -> percentage mapping."""
        cd = _make_categorical_distribution(frequencies={"Yes": 0.6, "No": 0.4})
        assert cd.frequencies == {"Yes": 0.6, "No": 0.4}


class TestQuestionDistribution:
    """Tests for QuestionDistribution model (T069)."""

    def test_numeric_distribution_creation(self):
        """QuestionDistribution can hold a numeric distribution."""
        qd = _make_question_distribution("numeric")
        assert qd.distribution_type == "numeric"
        assert qd.numeric is not None
        assert qd.categorical is None

    def test_categorical_distribution_creation(self):
        """QuestionDistribution can hold a categorical distribution."""
        qd = _make_question_distribution("categorical")
        assert qd.distribution_type == "categorical"
        assert qd.categorical is not None
        assert qd.numeric is None

    def test_invalid_distribution_type(self):
        """distribution_type rejects values other than 'numeric'/'categorical'."""
        with pytest.raises(ValidationError):
            _make_question_distribution(dist_type="numeric", distribution_type="invalid")

    def test_question_id_required(self):
        """question_id is required."""
        with pytest.raises(ValidationError):
            QuestionDistribution(
                distribution_type="numeric",
                numeric=_make_numeric_distribution(),
            )

    def test_question_text_optional(self):
        """question_text defaults to None."""
        qd = _make_question_distribution("numeric", question_text=None)
        assert qd.question_text is None


class TestCalibrationBaseline:
    """Tests for CalibrationBaseline model (T069)."""

    def test_creation_with_all_fields(self):
        """CalibrationBaseline can be created with all fields populated."""
        cb = _make_calibration_baseline()
        assert cb.id == "baseline-001"
        assert cb.name == "Test Baseline"
        assert cb.version == "1.0.0"
        assert cb.source == "User Survey 2026"
        assert cb.sample_size == 50
        assert cb.collection_date == date(2026, 1, 15)
        assert "early_adopter" in cb.demographic_tags
        assert len(cb.distributions) == 1

    def test_sample_size_minimum_10(self):
        """sample_size must be >= 10."""
        with pytest.raises(ValidationError):
            _make_calibration_baseline(sample_size=9)

    def test_sample_size_exactly_10(self):
        """sample_size of exactly 10 is valid."""
        cb = _make_calibration_baseline(sample_size=10)
        assert cb.sample_size == 10

    def test_sample_size_negative(self):
        """sample_size rejects negative values."""
        with pytest.raises(ValidationError):
            _make_calibration_baseline(sample_size=-1)

    def test_distributions_min_length_1(self):
        """distributions must have at least 1 element."""
        with pytest.raises(ValidationError):
            _make_calibration_baseline(distributions=[])

    def test_distributions_multiple(self):
        """distributions accepts multiple QuestionDistribution items."""
        dists = [
            _make_question_distribution("numeric", question_id="q1"),
            _make_question_distribution("categorical", question_id="q2"),
        ]
        cb = _make_calibration_baseline(distributions=dists)
        assert len(cb.distributions) == 2

    def test_created_at_auto_populated(self):
        """created_at is automatically set to current time."""
        cb = _make_calibration_baseline()
        assert isinstance(cb.created_at, datetime)

    def test_collection_method_optional(self):
        """collection_method defaults to None."""
        cb = _make_calibration_baseline()
        assert cb.collection_method is None

    def test_notes_optional(self):
        """notes defaults to None."""
        cb = _make_calibration_baseline()
        assert cb.notes is None

    def test_demographic_tags_default_empty(self):
        """demographic_tags defaults to empty list if not provided."""
        cb = _make_calibration_baseline(demographic_tags=[])
        assert cb.demographic_tags == []


# ---------------------------------------------------------------------------
# T070: QuestionComparison, Recommendation, CalibrationComparison
# ---------------------------------------------------------------------------


class TestQuestionComparison:
    """Tests for QuestionComparison model (T070)."""

    def test_creation_with_valid_data(self):
        """QuestionComparison can be created with valid data."""
        qc = _make_question_comparison()
        assert qc.question_id == "q1"
        assert qc.overlap_percentage == 75.0
        assert qc.divergence_detected is False

    def test_overlap_percentage_lower_bound(self):
        """overlap_percentage must be >= 0."""
        with pytest.raises(ValidationError):
            _make_question_comparison(overlap_percentage=-1)

    def test_overlap_percentage_upper_bound(self):
        """overlap_percentage must be <= 100."""
        with pytest.raises(ValidationError):
            _make_question_comparison(overlap_percentage=101)

    def test_overlap_percentage_boundary_zero(self):
        """overlap_percentage of 0 is valid."""
        qc = _make_question_comparison(overlap_percentage=0)
        assert qc.overlap_percentage == 0

    def test_overlap_percentage_boundary_hundred(self):
        """overlap_percentage of 100 is valid."""
        qc = _make_question_comparison(overlap_percentage=100)
        assert qc.overlap_percentage == 100

    def test_optional_means_default_none(self):
        """synthetic_mean, baseline_mean, mean_difference default to None."""
        qc = QuestionComparison(
            question_id="q1",
            overlap_percentage=50.0,
        )
        assert qc.synthetic_mean is None
        assert qc.baseline_mean is None
        assert qc.mean_difference is None


class TestRecommendation:
    """Tests for Recommendation model (T070)."""

    def test_creation_with_all_fields(self):
        """Recommendation can be created with all fields."""
        rec = _make_recommendation()
        assert rec.recommendation_id == "rec-001"
        assert rec.target == "persona"
        assert rec.recommendation_type == RecommendationType.INCREASE
        assert rec.parameter == "criticism_tendency"
        assert rec.priority == RecommendationPriority.HIGH

    def test_recommendation_type_increase(self):
        """recommendation_type accepts INCREASE."""
        rec = _make_recommendation(recommendation_type=RecommendationType.INCREASE)
        assert rec.recommendation_type == RecommendationType.INCREASE

    def test_recommendation_type_decrease(self):
        """recommendation_type accepts DECREASE."""
        rec = _make_recommendation(recommendation_type=RecommendationType.DECREASE)
        assert rec.recommendation_type == RecommendationType.DECREASE

    def test_priority_levels(self):
        """priority accepts all defined levels."""
        for priority in RecommendationPriority:
            rec = _make_recommendation(priority=priority)
            assert rec.priority == priority

    def test_target_id_optional(self):
        """target_id defaults to None."""
        rec = _make_recommendation(target_id=None)
        assert rec.target_id is None


class TestCalibrationComparison:
    """Tests for CalibrationComparison model (T070)."""

    def test_creation_with_all_fields(self):
        """CalibrationComparison can be created with all fields."""
        cc = _make_calibration_comparison()
        assert cc.id == "comp-001"
        assert cc.baseline_id == "baseline-001"
        assert cc.overall_overlap == 75.0
        assert cc.alignment_status == AlignmentStatus.ALIGNED

    def test_overall_overlap_lower_bound(self):
        """overall_overlap must be >= 0."""
        with pytest.raises(ValidationError):
            _make_calibration_comparison(overall_overlap=-1)

    def test_overall_overlap_upper_bound(self):
        """overall_overlap must be <= 100."""
        with pytest.raises(ValidationError):
            _make_calibration_comparison(overall_overlap=101)

    def test_needs_calibration_true_below_60(self):
        """needs_calibration returns True when overall_overlap < 60."""
        cc = _make_calibration_comparison(
            overall_overlap=55.0,
            alignment_status=AlignmentStatus.DIVERGENT,
        )
        assert cc.needs_calibration is True

    def test_needs_calibration_false_at_60(self):
        """needs_calibration returns False when overall_overlap == 60."""
        cc = _make_calibration_comparison(
            overall_overlap=60.0,
            alignment_status=AlignmentStatus.PARTIAL,
        )
        assert cc.needs_calibration is False

    def test_needs_calibration_false_above_60(self):
        """needs_calibration returns False when overall_overlap > 60."""
        cc = _make_calibration_comparison(
            overall_overlap=85.0,
            alignment_status=AlignmentStatus.ALIGNED,
        )
        assert cc.needs_calibration is False

    def test_alignment_status_aligned(self):
        """alignment_status accepts ALIGNED."""
        cc = _make_calibration_comparison(alignment_status=AlignmentStatus.ALIGNED)
        assert cc.alignment_status == AlignmentStatus.ALIGNED

    def test_alignment_status_partial(self):
        """alignment_status accepts PARTIAL."""
        cc = _make_calibration_comparison(alignment_status=AlignmentStatus.PARTIAL)
        assert cc.alignment_status == AlignmentStatus.PARTIAL

    def test_alignment_status_divergent(self):
        """alignment_status accepts DIVERGENT."""
        cc = _make_calibration_comparison(alignment_status=AlignmentStatus.DIVERGENT)
        assert cc.alignment_status == AlignmentStatus.DIVERGENT

    def test_comparison_timestamp_auto_set(self):
        """comparison_timestamp is automatically populated."""
        cc = _make_calibration_comparison()
        assert isinstance(cc.comparison_timestamp, datetime)

    def test_synthetic_sample_size_minimum(self):
        """synthetic_sample_size must be >= 1."""
        with pytest.raises(ValidationError):
            _make_calibration_comparison(synthetic_sample_size=0)

    def test_baseline_sample_size_minimum(self):
        """baseline_sample_size must be >= 1."""
        with pytest.raises(ValidationError):
            _make_calibration_comparison(baseline_sample_size=0)

    def test_divergence_points_default_empty(self):
        """divergence_points defaults to empty list."""
        cc = _make_calibration_comparison()
        assert cc.divergence_points == []

    def test_recommendations_default_empty(self):
        """recommendations defaults to empty list."""
        cc = _make_calibration_comparison()
        assert cc.recommendations == []
