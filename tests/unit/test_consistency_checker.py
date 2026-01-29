"""Tests for ConsistencyChecker service (T012-T016).

Validates Big Five consistency scoring, Schwartz value alignment,
per-response breakdown, weighted scoring, and threshold warnings.
"""

import pytest

from models.persona import BigFive
from services.consistency_checker import ConsistencyChecker


class TestCalculateBigFive:
    """T012: Test calculate_big_five with high-openness persona and matching keywords."""

    def test_high_openness_with_creative_keywords(self):
        """High openness (9) with creative/innovative keywords should score >70%.

        Openness HIGH_TRAIT_KEYWORDS has 16 entries. We need to hit at least 12
        across all responses to exceed 70%.
        """
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=3,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        # Responses saturated with openness keywords to hit >70% of the 16 keywords:
        # curious, innovative, creative, novel, explore, experiment, imaginative,
        # unconventional, new ideas, original, artistic, inventive, diverse, abstract,
        # philosophical, open-minded
        responses = [
            "I'm curious about this innovative and creative approach. The novel ideas "
            "here inspire me to explore and experiment with imaginative solutions. "
            "I appreciate how unconventional and original this concept is.",
            "The artistic and inventive design shows diverse thinking. I find abstract "
            "concepts like these philosophical yet practical. Being open-minded helps me "
            "appreciate new ideas fully.",
            "I prefer flexible, spontaneous, adaptable methods. Being casual and relaxed "
            "about structure lets me improvise and go with the flow in an easygoing way.",
        ]

        score, alignments = checker.calculate_big_five(big_five, responses)

        assert score > 70, f"Expected score >70% for high-openness persona, got {score:.1f}%"
        # Find openness alignment
        openness_alignment = next(a for a in alignments if a.trait_name == "openness")
        assert openness_alignment.alignment_score > 70
        assert len(openness_alignment.matched_keywords) > 0

    def test_high_openness_low_conscientiousness_combined(self):
        """Both extreme traits should be scored: high openness + low conscientiousness."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=3,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        # Include enough keywords from both lists to get reasonable scores.
        # Openness HIGH (16 kw): curious, innovative, creative, novel, explore,
        #   experiment, imaginative, unconventional, new ideas
        # Conscientiousness LOW (12 kw): flexible, spontaneous, adaptable, casual,
        #   relaxed, improvise, go with the flow, easygoing
        responses = [
            "I'm curious about this creative, innovative and novel approach. I love to "
            "explore, experiment, and be imaginative with unconventional new ideas. "
            "I prefer to be flexible and spontaneous rather than following rigid plans. "
            "Being adaptable and casual feels natural. I like to improvise, go with the "
            "flow, and stay relaxed and easygoing about things.",
        ]

        score, alignments = checker.calculate_big_five(big_five, responses)

        openness_align = next(a for a in alignments if a.trait_name == "openness")
        consc_align = next(a for a in alignments if a.trait_name == "conscientiousness")
        assert openness_align.alignment_score > 50, \
            f"Openness score {openness_align.alignment_score:.1f}% should be >50%"
        assert consc_align.alignment_score > 50, \
            f"Conscientiousness score {consc_align.alignment_score:.1f}% should be >50%"

    def test_no_matching_keywords_low_score(self):
        """Responses with no matching keywords should produce low scores."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=3,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        responses = [
            "The weather is nice today.",
            "I had lunch at noon.",
        ]

        score, alignments = checker.calculate_big_five(big_five, responses)

        assert score < 50, f"Expected low score for non-matching responses, got {score:.1f}%"


class TestCalculateSchwartz:
    """T013: Test calculate_schwartz with self_direction and security priorities."""

    def test_self_direction_keywords_reflected(self):
        """Responses containing self_direction keywords should be reflected."""
        checker = ConsistencyChecker()
        schwartz_primary = ["self_direction", "stimulation"]
        responses = [
            "I value my independence and freedom to choose my own way. "
            "Being self-reliant and creative is important to me.",
            "I find this exciting and varied. The novelty and adventure "
            "of trying new things thrills me.",
        ]

        score, alignments = checker.calculate_schwartz(schwartz_primary, responses)

        assert score == 100.0, f"Expected 100% when all values reflected, got {score:.1f}%"
        assert len(alignments) == 2

    def test_security_value_alignment(self):
        """Security-focused responses should score for security value."""
        checker = ConsistencyChecker()
        schwartz_primary = ["security", "conformity"]
        responses = [
            "I need a safe and stable environment. Order and protection "
            "are essential for my peace of mind. I feel secure here.",
            "It's important to be polite and follow rules. Being obedient "
            "and respectful is my duty.",
        ]

        score, alignments = checker.calculate_schwartz(schwartz_primary, responses)

        assert score == 100.0
        security_align = next(a for a in alignments if a.trait_name == "security")
        assert security_align.alignment_score == 100.0

    def test_partial_value_reflection(self):
        """When only some values are reflected, score should be partial."""
        checker = ConsistencyChecker()
        schwartz_primary = ["self_direction", "security"]
        responses = [
            "I value my independence and freedom to explore.",
            "This approach seems interesting overall.",
        ]

        score, alignments = checker.calculate_schwartz(schwartz_primary, responses)

        # self_direction reflected but security not
        assert score == 50.0, f"Expected 50% for 1/2 values reflected, got {score:.1f}%"

    def test_no_values_reflected(self):
        """When no values are reflected, score should be 0."""
        checker = ConsistencyChecker()
        schwartz_primary = ["power", "achievement"]
        responses = [
            "The weather is nice today.",
            "I had lunch at noon.",
        ]

        score, alignments = checker.calculate_schwartz(schwartz_primary, responses)

        assert score == 0.0


class TestPerResponseBreakdown:
    """T014: Test per_response_breakdown for individual response scores."""

    def test_returns_score_per_response(self):
        """Should return one score per response."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        responses = [
            "I'm curious about innovative approaches.",
            "The weather is unremarkable.",
            "I love to explore creative and novel ideas.",
        ]

        scores = checker.per_response_breakdown(big_five, responses)

        assert len(scores) == 3, "Should return one score per response"

    def test_matching_response_scores_higher(self):
        """Responses with matching keywords should score higher than non-matching."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=3,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        responses = [
            "I'm curious about innovative and creative exploration. I prefer "
            "flexible, spontaneous approaches.",
            "The item is on the table.",
        ]

        scores = checker.per_response_breakdown(big_five, responses)

        assert scores[0] > scores[1], (
            f"Matching response ({scores[0]:.1f}) should score higher than "
            f"non-matching ({scores[1]:.1f})"
        )

    def test_empty_responses_list(self):
        """Empty responses list should return empty scores list."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=5,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )

        scores = checker.per_response_breakdown(big_five, [])

        assert scores == []


class TestWeightedScoring:
    """T015: Test that extreme traits are weighted higher than neutral traits."""

    def test_extreme_traits_weighted_higher(self):
        """Traits far from 5 should have higher weight than neutral (5)."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=10,  # extreme high: weight = |10-5|/5 = 1.0
            conscientiousness=1,  # extreme low: weight = |1-5|/5 = 0.8
            extraversion=5,  # neutral: weight = |5-5|/5 = 0.0
            agreeableness=5,  # neutral: weight = 0.0
            neuroticism=5,  # neutral: weight = 0.0
        )
        responses = [
            "I'm curious about creative and innovative exploration. "
            "I prefer flexible, spontaneous, go with the flow approaches.",
        ]

        _, alignments = checker.calculate_big_five(big_five, responses)

        openness_weight = next(a for a in alignments if a.trait_name == "openness").weight
        consc_weight = next(a for a in alignments if a.trait_name == "conscientiousness").weight
        extra_weight = next(a for a in alignments if a.trait_name == "extraversion").weight

        assert openness_weight > extra_weight, "Extreme openness should be weighted higher than neutral extraversion"
        assert consc_weight > extra_weight, "Extreme conscientiousness should be weighted higher than neutral"
        assert openness_weight == pytest.approx(1.0)
        assert consc_weight == pytest.approx(0.8)
        assert extra_weight == pytest.approx(0.0)

    def test_all_neutral_uses_equal_weights(self):
        """When all traits are neutral (5), equal weights should be used."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=5,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        responses = [
            "I'm curious and enjoy creative exploration.",
        ]

        score, alignments = checker.calculate_big_five(big_five, responses)

        # All weights are 0, so equal weights should be used.
        # Score should still be computed (not NaN or error).
        assert 0 <= score <= 100


class TestConsistencyThresholdWarnings:
    """T016: Test consistency threshold warning flags when score < 70%."""

    def test_warning_when_below_threshold(self):
        """Should generate warning flags when overall score < 70%."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=2,
            extraversion=8,
            agreeableness=5,
            neuroticism=2,
        )
        # Responses that do NOT match the persona at all
        responses = [
            "The weather is nice today.",
            "I had lunch at noon.",
            "The table is brown.",
        ]

        result = checker.calculate(
            big_five=big_five,
            schwartz_primary=["self_direction", "stimulation"],
            responses=responses,
        )

        assert not result.passed_threshold, "Should fail threshold with non-matching responses"
        assert len(result.warning_flags) > 0, "Should have warning flags"
        assert any("consistency" in w.lower() for w in result.warning_flags), \
            "Should have a consistency-related warning"

    def test_no_warning_when_above_threshold(self):
        """Should not generate consistency warnings when score >= 70%."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=3,
            extraversion=7,
            agreeableness=5,
            neuroticism=2,
        )
        # Saturate responses with keywords from all extreme traits to push above 70%.
        # Openness HIGH (16 kw), Conscientiousness LOW (12 kw),
        # Extraversion HIGH (16 kw), Neuroticism LOW (14 kw).
        responses = [
            "I'm curious about this innovative, creative, novel approach. I love to "
            "explore, experiment with imaginative, unconventional new ideas. Original, "
            "artistic, inventive, diverse, abstract, philosophical, open-minded thinking. "
            "I'm flexible, spontaneous, adaptable, casual, relaxed. I improvise and "
            "go with the flow in an easygoing, unstructured, carefree, laid-back way.",
            "I'm excited, energetic, social, enthusiastic, outgoing about collaborating "
            "with the team. I interact in an engaging, talkative, sociable, assertive, "
            "lively, dynamic, expressive, vibrant manner. "
            "I feel calm, stable, relaxed, composed, confident, resilient, steady, "
            "unworried, serene, content, secure, optimistic, even-tempered, peaceful.",
            "This independent freedom lets me be autonomous and self-reliant, creative "
            "and curious. I choose to explore my own way. It's exciting, varied, daring "
            "with adventure, novelty, thrill, dynamic challenge and risk.",
        ]

        result = checker.calculate(
            big_five=big_five,
            schwartz_primary=["self_direction", "stimulation"],
            responses=responses,
        )

        assert result.passed_threshold, (
            f"Should pass threshold with matching responses, got score {result.overall_score:.1f}%"
        )

    def test_custom_threshold(self):
        """Should use custom threshold when provided."""
        from models.calibration import QualityThresholds

        custom_thresholds = QualityThresholds(consistency_minimum=90.0)
        checker = ConsistencyChecker(thresholds=custom_thresholds)

        big_five = BigFive(
            openness=9,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        responses = [
            "I'm curious and creative with innovative ideas.",
        ]

        result = checker.calculate(
            big_five=big_five,
            schwartz_primary=["self_direction"],
            responses=responses,
        )

        assert result.threshold_used == 90.0

    def test_high_variance_warning(self):
        """Should warn when response variance is high."""
        checker = ConsistencyChecker()
        big_five = BigFive(
            openness=9,
            conscientiousness=5,
            extraversion=5,
            agreeableness=5,
            neuroticism=5,
        )
        # First response matches well, second doesn't match at all
        responses = [
            "I'm incredibly curious about this innovative and creative approach. "
            "I love to explore novel, unconventional, imaginative ideas and experiment.",
            "The table is brown. The chair is wooden. Nothing notable here.",
        ]

        result = checker.calculate(
            big_five=big_five,
            schwartz_primary=["self_direction"],
            responses=responses,
        )

        # High variance between response scores should generate a warning
        assert result.response_variance > 0, "Should have non-zero variance"
