"""Tests for variance monitor service (T041-T044).

Validates rating variance calculation, sentiment distribution analysis,
clustering detection, and cross-session stability checking.
"""

import pytest

from services.variance_monitor import VarianceMonitor
from models.calibration import QualityThresholds


class TestCalculateRatingVariance:
    """T041: Test calculate_rating_variance with known rating distributions."""

    def test_basic_statistics(self):
        """Verify mean, stdev, variance for ratings [3, 5, 7, 8, 4]."""
        monitor = VarianceMonitor()
        result = monitor.calculate_rating_variance(
            ratings=[3.0, 5.0, 7.0, 8.0, 4.0],
            question_id="q1",
            scale_type="rating_1_10",
        )
        assert result.question_id == "q1"
        assert result.mean == pytest.approx(5.4, abs=0.01)
        assert result.stdev > 0
        assert result.variance > 0

    def test_expected_stdev_for_1_10_scale(self):
        """Expected stdev for rating_1_10 scale should be 2.5."""
        monitor = VarianceMonitor()
        result = monitor.calculate_rating_variance(
            ratings=[3.0, 5.0, 7.0, 8.0, 4.0],
            question_id="q1",
            scale_type="rating_1_10",
        )
        assert result.expected_stdev == 2.5

    def test_variance_ratio_calculation(self):
        """Variance ratio should be actual_stdev / expected_stdev."""
        monitor = VarianceMonitor()
        result = monitor.calculate_rating_variance(
            ratings=[3.0, 5.0, 7.0, 8.0, 4.0],
            question_id="q1",
            scale_type="rating_1_10",
        )
        expected_ratio = result.stdev / 2.5
        assert result.variance_ratio == pytest.approx(expected_ratio, abs=0.001)

    def test_clustering_detected_when_low_variance(self):
        """Clustering is detected when variance_ratio < 0.6."""
        monitor = VarianceMonitor()
        # Tightly clustered ratings -> low stdev -> low ratio
        result = monitor.calculate_rating_variance(
            ratings=[5.0, 5.0, 5.0, 5.0, 5.1],
            question_id="q1",
            scale_type="rating_1_10",
        )
        assert result.variance_ratio < 0.6
        assert result.clustering_detected is True

    def test_no_clustering_when_high_variance(self):
        """No clustering when variance_ratio >= 0.6."""
        monitor = VarianceMonitor()
        # Spread-out ratings -> high stdev
        result = monitor.calculate_rating_variance(
            ratings=[1.0, 3.0, 5.0, 7.0, 10.0],
            question_id="q1",
            scale_type="rating_1_10",
        )
        assert result.variance_ratio >= 0.6
        assert result.clustering_detected is False

    def test_single_rating_edge_case(self):
        """Single rating should have stdev=0 and detect clustering."""
        monitor = VarianceMonitor()
        result = monitor.calculate_rating_variance(
            ratings=[7.0],
            question_id="q1",
        )
        assert result.stdev == 0.0
        assert result.variance == 0.0
        assert result.clustering_detected is True

    def test_min_max_values(self):
        """Min and max values should match the data."""
        monitor = VarianceMonitor()
        result = monitor.calculate_rating_variance(
            ratings=[3.0, 5.0, 7.0, 8.0, 4.0],
            question_id="q1",
        )
        assert result.min_value == 3.0
        assert result.max_value == 8.0


class TestCalculateSentimentDistribution:
    """T042: Test calculate_sentiment_distribution with mixed panel sentiments."""

    def test_mixed_sentiments_percentages(self):
        """Percentages should sum to approximately 100."""
        monitor = VarianceMonitor()
        sentiments = ["positive", "positive", "negative", "mixed", "neutral"]
        result = monitor.calculate_sentiment_distribution(sentiments)
        total = result.positive + result.negative + result.mixed + result.neutral
        assert total == pytest.approx(100.0, abs=0.1)

    def test_individual_percentages(self):
        """Each sentiment percentage should be correct."""
        monitor = VarianceMonitor()
        sentiments = ["positive", "positive", "negative", "mixed", "neutral"]
        result = monitor.calculate_sentiment_distribution(sentiments)
        assert result.positive == pytest.approx(40.0, abs=0.1)
        assert result.negative == pytest.approx(20.0, abs=0.1)
        assert result.mixed == pytest.approx(20.0, abs=0.1)
        assert result.neutral == pytest.approx(20.0, abs=0.1)

    def test_diversity_score_positive_for_mixed(self):
        """Diversity score should be > 0 for mixed sentiments."""
        monitor = VarianceMonitor()
        sentiments = ["positive", "positive", "negative", "mixed", "neutral"]
        result = monitor.calculate_sentiment_distribution(sentiments)
        assert result.diversity_score > 0

    def test_diversity_score_zero_for_uniform(self):
        """Diversity score should be 0 when all sentiments are the same."""
        monitor = VarianceMonitor()
        sentiments = ["positive", "positive", "positive"]
        result = monitor.calculate_sentiment_distribution(sentiments)
        assert result.diversity_score == 0.0

    def test_empty_sentiments(self):
        """Empty sentiments list should return all zeros."""
        monitor = VarianceMonitor()
        result = monitor.calculate_sentiment_distribution([])
        assert result.positive == 0.0
        assert result.negative == 0.0
        assert result.mixed == 0.0
        assert result.neutral == 0.0
        assert result.diversity_score == 0.0


class TestDetectClustering:
    """T043: Test detect_clustering with below-threshold variance ratio."""

    def test_clustering_from_low_variance_ratio(self):
        """Clustering detected when variance_ratio < 0.6."""
        monitor = VarianceMonitor()
        # Create a RatingVariance with clustering
        rv = monitor.calculate_rating_variance(
            ratings=[5.0, 5.0, 5.0, 5.0, 5.1],
            question_id="q1",
        )
        sentiment_dist = monitor.calculate_sentiment_distribution(
            ["positive", "negative", "mixed", "neutral"]
        )
        detected, details = monitor.detect_clustering([rv], sentiment_dist)
        assert detected is True
        assert len(details) > 0

    def test_clustering_from_dominant_sentiment(self):
        """Clustering detected when single sentiment > 80%."""
        monitor = VarianceMonitor()
        # No rating clustering
        rv = monitor.calculate_rating_variance(
            ratings=[1.0, 3.0, 5.0, 7.0, 10.0],
            question_id="q1",
        )
        # Dominant sentiment: 9/10 = 90% positive > 80% threshold
        sentiments = ["positive"] * 9 + ["negative"]
        sentiment_dist = monitor.calculate_sentiment_distribution(sentiments)
        detected, details = monitor.detect_clustering([rv], sentiment_dist)
        assert detected is True
        assert any("Sentiment clustering" in d for d in details)

    def test_no_clustering_balanced(self):
        """No clustering when variance and sentiments are balanced."""
        monitor = VarianceMonitor()
        rv = monitor.calculate_rating_variance(
            ratings=[1.0, 3.0, 5.0, 7.0, 10.0],
            question_id="q1",
        )
        sentiment_dist = monitor.calculate_sentiment_distribution(
            ["positive", "negative", "mixed", "neutral"]
        )
        detected, details = monitor.detect_clustering([rv], sentiment_dist)
        assert detected is False
        assert len(details) == 0


class TestCheckStability:
    """T044: Test variance stability across multiple sessions."""

    def test_stable_variances(self):
        """Relative difference < 20% should be considered stable."""
        monitor = VarianceMonitor()
        current = [0.8, 0.9, 0.7]
        previous = [0.82, 0.88, 0.72]
        result = monitor.check_stability(current, previous)
        assert result is not None
        assert result < 20.0

    def test_unstable_variances(self):
        """Large relative difference indicates instability."""
        monitor = VarianceMonitor()
        current = [0.8, 0.9, 0.7]
        previous = [0.2, 0.3, 0.1]
        result = monitor.check_stability(current, previous)
        assert result is not None
        assert result > 20.0

    def test_different_lengths_returns_none(self):
        """Different length lists should return None."""
        monitor = VarianceMonitor()
        result = monitor.check_stability([0.8, 0.9], [0.8])
        assert result is None


class TestAnalyze:
    """Test the full analyze orchestration method."""

    def test_full_analysis(self):
        """Full analysis should return a complete VarianceReport."""
        monitor = VarianceMonitor()
        report = monitor.analyze(
            ratings_by_question={
                "q1": [3.0, 5.0, 7.0, 8.0, 4.0],
                "q2": [2.0, 4.0, 6.0, 8.0, 10.0],
            },
            sentiments=["positive", "negative", "mixed", "neutral", "positive"],
            scale_type="rating_1_10",
        )
        assert len(report.rating_variances) == 2
        assert report.overall_rating_variance > 0
        assert report.panel_size == 5
        assert report.expected_variance_baseline == "rating_1_10"

    def test_analysis_with_previous_variances(self):
        """Analysis with previous variances should compute stability."""
        monitor = VarianceMonitor()
        report = monitor.analyze(
            ratings_by_question={
                "q1": [3.0, 5.0, 7.0, 8.0, 4.0],
                "q2": [2.0, 4.0, 6.0, 8.0, 10.0],
            },
            sentiments=["positive", "negative", "mixed", "neutral", "positive"],
            previous_variances=[0.75, 1.1],
        )
        assert report.stability_score is not None
        assert report.session_count == 2

    def test_analysis_clustering_flagged(self):
        """Analysis should flag clustering when ratings are uniform."""
        monitor = VarianceMonitor()
        report = monitor.analyze(
            ratings_by_question={
                "q1": [5.0, 5.0, 5.0, 5.0, 5.0],
            },
            sentiments=["positive", "positive", "positive", "positive", "positive"],
        )
        assert report.clustering_detected is True
        assert report.passed_threshold is False
        assert len(report.warning_flags) > 0
