"""Service for monitoring response variance and detecting clustering patterns.

Analyzes rating distributions and sentiment patterns to detect suspiciously
uniform responses that may indicate AI bias or insufficient persona differentiation.
"""

import math
from statistics import mean, stdev, variance

from models.calibration import QualityThresholds
from models.quality import (
    QualitySentimentDistribution,
    RatingVariance,
    VarianceReport,
)


class VarianceMonitor:
    """Monitor response variance across panel sessions.

    Detects clustering patterns in ratings and sentiments that indicate
    insufficient diversity in synthetic persona responses.
    """

    EXPECTED_VARIANCE: dict[str, float] = {
        "rating_1_10": 2.5,
        "rating_1_5": 1.2,
        "nps_0_10": 2.8,
    }

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        self.thresholds = thresholds or QualityThresholds()

    def calculate_rating_variance(
        self,
        ratings: list[float],
        question_id: str,
        scale_type: str = "rating_1_10",
    ) -> RatingVariance:
        """Calculate variance metrics for a set of ratings.

        Args:
            ratings: List of numeric rating values.
            question_id: Identifier for the rated question.
            scale_type: Type of rating scale used.

        Returns:
            RatingVariance with computed statistics and clustering flag.
        """
        if len(ratings) == 0:
            raise ValueError("ratings list must not be empty")

        if len(ratings) == 1:
            rating_mean = ratings[0]
            rating_stdev = 0.0
            rating_variance = 0.0
        else:
            rating_mean = mean(ratings)
            rating_stdev = stdev(ratings)
            rating_variance = variance(ratings)

        expected_stdev = self.EXPECTED_VARIANCE.get(scale_type, 2.5)
        variance_ratio = rating_stdev / expected_stdev if expected_stdev > 0 else 0.0
        clustering_detected = variance_ratio < self.thresholds.variance_minimum_ratio

        return RatingVariance(
            question_id=question_id,
            mean=rating_mean,
            stdev=rating_stdev,
            variance=rating_variance,
            min_value=min(ratings),
            max_value=max(ratings),
            expected_stdev=expected_stdev,
            variance_ratio=variance_ratio,
            clustering_detected=clustering_detected,
        )

    def calculate_sentiment_distribution(
        self,
        sentiments: list[str],
    ) -> QualitySentimentDistribution:
        """Calculate sentiment distribution and diversity score.

        Args:
            sentiments: List of sentiment labels.

        Returns:
            QualitySentimentDistribution with percentages and diversity score.
        """
        total = len(sentiments)

        if total == 0:
            return QualitySentimentDistribution(
                positive=0.0,
                negative=0.0,
                mixed=0.0,
                neutral=0.0,
                diversity_score=0.0,
            )

        counts = {
            "positive": 0,
            "negative": 0,
            "mixed": 0,
            "neutral": 0,
        }
        for s in sentiments:
            key = s.lower()
            if key in counts:
                counts[key] += 1

        percentages = {k: (v / total) * 100.0 for k, v in counts.items()}

        # Entropy-based diversity score normalized to 0-1
        probabilities = [v / total for v in counts.values()]
        non_zero = [p for p in probabilities if p > 0]
        if len(non_zero) <= 1:
            diversity_score = 0.0
        else:
            entropy = -sum(p * math.log2(p) for p in non_zero)
            max_entropy = math.log2(4)  # 4 categories
            diversity_score = entropy / max_entropy

        return QualitySentimentDistribution(
            positive=percentages["positive"],
            negative=percentages["negative"],
            mixed=percentages["mixed"],
            neutral=percentages["neutral"],
            diversity_score=diversity_score,
        )

    def detect_clustering(
        self,
        rating_variances: list[RatingVariance],
        sentiment_dist: QualitySentimentDistribution,
    ) -> tuple[bool, list[str]]:
        """Detect clustering in ratings and sentiments.

        Args:
            rating_variances: Per-question rating variance results.
            sentiment_dist: Sentiment distribution across responses.

        Returns:
            Tuple of (clustering_detected, details list).
        """
        detected = False
        details: list[str] = []

        # Check rating clustering
        for rv in rating_variances:
            if rv.clustering_detected:
                detected = True
                details.append(
                    f"Rating clustering detected for '{rv.question_id}': "
                    f"variance_ratio={rv.variance_ratio:.2f} "
                    f"(threshold={self.thresholds.variance_minimum_ratio})"
                )

        # Check sentiment clustering
        threshold_pct = self.thresholds.clustering_threshold * 100
        for sentiment_name in ("positive", "negative", "mixed", "neutral"):
            pct = getattr(sentiment_dist, sentiment_name)
            if pct > threshold_pct:
                detected = True
                details.append(
                    f"Sentiment clustering: '{sentiment_name}' at {pct:.1f}% "
                    f"exceeds threshold {threshold_pct:.1f}%"
                )

        return detected, details

    def check_stability(
        self,
        current_variances: list[float],
        previous_variances: list[float],
    ) -> float | None:
        """Check variance stability across sessions.

        Args:
            current_variances: Variance ratios from current session.
            previous_variances: Variance ratios from previous session.

        Returns:
            Average relative difference as a percentage (0-100),
            or None if lists are different lengths.
        """
        if len(current_variances) != len(previous_variances):
            return None

        if len(current_variances) == 0:
            return 0.0

        relative_diffs: list[float] = []
        for curr, prev in zip(current_variances, previous_variances, strict=False):
            denom = max(abs(prev), abs(curr), 1e-10)
            relative_diffs.append(abs(curr - prev) / denom * 100.0)

        return mean(relative_diffs)

    def analyze(
        self,
        ratings_by_question: dict[str, list[float]],
        sentiments: list[str],
        scale_type: str = "rating_1_10",
        previous_variances: list[float] | None = None,
    ) -> VarianceReport:
        """Run full variance analysis.

        Args:
            ratings_by_question: Mapping of question_id -> list of ratings.
            sentiments: List of sentiment labels across panel.
            scale_type: Rating scale type.
            previous_variances: Optional previous session variance ratios.

        Returns:
            Complete VarianceReport.
        """
        # Calculate per-question rating variances
        rating_variances: list[RatingVariance] = []
        for qid, ratings in ratings_by_question.items():
            rv = self.calculate_rating_variance(ratings, qid, scale_type)
            rating_variances.append(rv)

        # Calculate sentiment distribution
        sentiment_dist = self.calculate_sentiment_distribution(sentiments)

        # Detect clustering
        clustering_detected, clustering_details = self.detect_clustering(
            rating_variances, sentiment_dist
        )

        # Overall rating variance as mean of variance ratios
        if rating_variances:
            overall_rating_variance = mean(
                rv.variance_ratio for rv in rating_variances
            )
        else:
            overall_rating_variance = 0.0

        # Stability check
        stability_score: float | None = None
        session_count = 1
        if previous_variances is not None:
            current_ratios = [rv.variance_ratio for rv in rating_variances]
            stability_score = self.check_stability(current_ratios, previous_variances)
            if stability_score is not None:
                session_count = 2

        # Determine pass/fail
        passed = not clustering_detected
        if stability_score is not None and stability_score > 20.0:
            passed = False

        # Warning flags
        warning_flags: list[str] = []
        if clustering_detected:
            warning_flags.append("Response clustering detected")
        if stability_score is not None and stability_score > 20.0:
            warning_flags.append(
                f"Variance instability: {stability_score:.1f}% relative difference"
            )

        # Panel size from sentiments count (at least 1)
        panel_size = max(len(sentiments), 1)

        return VarianceReport(
            rating_variances=rating_variances,
            overall_rating_variance=overall_rating_variance,
            sentiment_distribution=sentiment_dist,
            clustering_detected=clustering_detected,
            clustering_details=clustering_details,
            stability_score=stability_score,
            session_count=session_count,
            passed_threshold=passed,
            warning_flags=warning_flags,
            panel_size=panel_size,
            expected_variance_baseline=scale_type,
        )
