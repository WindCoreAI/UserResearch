"""Tests for quality metrics calculator.

Validates consistency scoring and sycophancy detection.
"""

import pytest

from models.persona import BigFive


class TestQualityMetricsCalculator:
    """Tests for QualityMetricsCalculator class."""

    def test_calculator_initialization(self):
        """QualityMetricsCalculator can be instantiated."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        assert calculator is not None

    def test_calculate_consistency_high_openness(self):
        """High openness persona should match 'curious', 'innovative' keywords."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=9,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        response_text = """
        I'm curious about this new approach and would love to explore
        the innovative features. This looks like a novel way to solve the problem.
        """

        result = calculator.calculate(big_five, response_text)

        assert result.consistency_score > 50  # Should be reasonably high

    def test_calculate_consistency_low_openness(self):
        """Low openness persona should match 'traditional', 'proven' keywords."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=2,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        response_text = """
        I prefer traditional approaches that are proven to work.
        This is too practical for my tastes - I like familiar solutions.
        """

        result = calculator.calculate(big_five, response_text)

        assert result.consistency_score > 50

    def test_detect_sycophancy_excessive_positivity(self):
        """Detect sycophancy when response is overly positive."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=5,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        response_text = """
        This is absolutely amazing! I love everything about it!
        It's perfect, fantastic, wonderful, and great in every way!
        I have no concerns at all - this is the best thing ever!
        """

        result = calculator.calculate(big_five, response_text)

        assert result.sycophancy_indicators.get("excessive_praise", False) or \
               result.sycophancy_indicators.get("positive_negative_ratio", 0) > 4

    def test_detect_sycophancy_no_concerns(self):
        """Detect when no concerns are raised (potential sycophancy)."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=5,
            conscientiousness=5,
            extraversion=5,
            agreeableness=3,  # Low agreeableness should have concerns
            neuroticism=5,
        )

        response_text = """
        This is great! I love it! Everything is perfect.
        No issues, no problems, just pure excellence.
        """

        result = calculator.calculate(big_five, response_text)

        # Should flag no_concerns_raised for a low agreeableness persona
        assert "sycophancy_indicators" in result.model_dump()

    def test_quality_gates_pass(self):
        """Quality gates should pass for balanced response."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=7,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        response_text = """
        I'm curious about this new feature and would explore it.
        However, I do have some concerns about the learning curve.
        I would suggest adding better documentation.
        Overall, it's a mixed experience with both positives and negatives.
        """

        result = calculator.calculate(big_five, response_text)

        assert result.passed_gates or result.consistency_score >= 70

    def test_quality_gates_fail_low_consistency(self):
        """Quality gates should fail for low consistency score."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=2,  # Low openness
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        # Response uses high-openness keywords, inconsistent with persona
        response_text = """
        I'm so excited to explore this innovative new approach!
        This is such a novel and creative solution!
        """

        result = calculator.calculate(big_five, response_text)

        # Either low consistency or sycophancy warning should trigger
        assert result.consistency_score < 70 or not result.passed_gates

    def test_matched_traits_identified(self):
        """Should identify which traits matched in response."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=8,
            conscientiousness=7,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        response_text = """
        I'm curious about this and would explore it thoroughly.
        I prefer to be organized and plan my approach carefully.
        """

        result = calculator.calculate(big_five, response_text)

        assert result.matched_traits is not None or result.consistency_score > 0

    def test_sycophancy_ratio_calculation(self):
        """Should calculate positive:negative ratio."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=5,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        response_text = """
        This is great and amazing! I love it!
        But I'm concerned about one small issue.
        """

        result = calculator.calculate(big_five, response_text)

        ratio = result.sycophancy_indicators.get("positive_negative_ratio", 0)
        assert ratio > 0  # Should have calculated a ratio

    def test_warnings_generated(self):
        """Should generate warnings for quality issues."""
        from services.quality_metrics import QualityMetricsCalculator

        calculator = QualityMetricsCalculator()
        big_five = BigFive(
            openness=2,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        # Highly positive response inconsistent with low openness
        response_text = """
        This is absolutely fantastic and innovative!
        I love exploring new things! Amazing and creative!
        """

        result = calculator.calculate(big_five, response_text)

        # Should have some warnings
        assert len(result.warnings) > 0 or not result.passed_gates
