"""Tests for BiasDetector service (T025-T029).

Validates sycophancy phrase detection, sentiment ratio calculation,
clustering detection, skeptical persona validation, and sycophancy
rate calculation with threshold warnings.
"""

import pytest

from services.bias_detector import BiasDetector
from models.calibration import QualityThresholds


class TestDetectSycophancyPhrases:
    """T025: Test detect_sycophancy_phrases() with known sycophantic text."""

    def test_detects_single_sycophancy_phrase(self):
        """A single sycophancy phrase in text is detected."""
        detector = BiasDetector()
        text = "I think this is absolutely amazing and I really enjoyed it."
        phrases = detector.detect_sycophancy_phrases(text)
        assert "absolutely amazing" in phrases
        assert len(phrases) == 1

    def test_detects_multiple_sycophancy_phrases(self):
        """Multiple sycophancy phrases in text are all detected."""
        detector = BiasDetector()
        text = (
            "This is absolutely amazing! It's perfect in every way. "
            "I have no concerns at all and this is exactly what I need."
        )
        phrases = detector.detect_sycophancy_phrases(text)
        assert "absolutely amazing" in phrases
        assert "perfect in every way" in phrases
        assert "no concerns at all" in phrases
        assert "this is exactly what i need" in phrases
        assert len(phrases) == 4

    def test_case_insensitive_detection(self):
        """Phrase detection works regardless of case."""
        detector = BiasDetector()
        text = "This is ABSOLUTELY AMAZING and PERFECT IN EVERY WAY!"
        phrases = detector.detect_sycophancy_phrases(text)
        assert "absolutely amazing" in phrases
        assert "perfect in every way" in phrases

    def test_no_sycophancy_phrases(self):
        """Clean text returns no phrases."""
        detector = BiasDetector()
        text = "I have some concerns about the usability. The interface could be improved."
        phrases = detector.detect_sycophancy_phrases(text)
        assert phrases == []

    def test_detects_all_known_phrases(self):
        """All 15 sycophancy phrases are detected when present."""
        detector = BiasDetector()
        text = (
            "This is absolutely amazing! I love everything about it. "
            "It's perfect in every way with no concerns at all. "
            "It's the best thing ever and couldn't be better. "
            "There's nothing to improve and I wouldn't change anything. "
            "This is exactly what I need and I can't find any issues. "
            "This is perfect. I would definitely recommend it. "
            "This exceeds expectations. I have no complaints. "
            "I'm completely satisfied."
        )
        phrases = detector.detect_sycophancy_phrases(text)
        assert len(phrases) == 15


class TestCalculateSentimentRatio:
    """T026: Test calculate_sentiment_ratio() with positive-skewed responses."""

    def test_positive_skewed_ratio_exceeds_four(self):
        """Responses heavy on positive keywords produce ratio > 4."""
        detector = BiasDetector()
        responses = [
            "I love this product, it's great and amazing!",
            "This is excellent and fantastic, really wonderful!",
            "It's perfect, brilliant, and outstanding work!",
            "I love the great design, it's amazing and excellent!",
            "This is fantastic and wonderful, truly brilliant!",
        ]
        ratio = detector.calculate_sentiment_ratio(responses)
        assert ratio > 4.0

    def test_balanced_responses_ratio_near_one(self):
        """Balanced responses produce a ratio near 1."""
        detector = BiasDetector()
        responses = [
            "I love the design but I have a concern about the interface.",
            "It's great overall, though there's a problem with loading.",
            "Amazing features, but some issues with performance.",
        ]
        ratio = detector.calculate_sentiment_ratio(responses)
        assert 0.5 <= ratio <= 5.0

    def test_no_negative_keywords_caps_at_ten(self):
        """When no negative keywords exist, ratio is capped at 10.0."""
        detector = BiasDetector()
        responses = [
            "I love this great and amazing product!",
            "It's excellent and fantastic!",
        ]
        ratio = detector.calculate_sentiment_ratio(responses)
        assert ratio == 10.0

    def test_empty_responses(self):
        """Empty responses produce capped ratio (no keywords at all)."""
        detector = BiasDetector()
        responses = ["", ""]
        ratio = detector.calculate_sentiment_ratio(responses)
        assert ratio == 10.0

    def test_only_negative_keywords(self):
        """Only negative keywords produce ratio of 0."""
        detector = BiasDetector()
        responses = [
            "I have a concern and an issue with this.",
            "There is a problem and it's frustrating and confusing.",
        ]
        ratio = detector.calculate_sentiment_ratio(responses)
        assert ratio == 0.0


class TestDetectClustering:
    """T027: Test detect_clustering() with identical sentiments from diverse panel."""

    def test_all_positive_sentiments_detected_as_clustering(self):
        """5 responses all positive (100%) triggers clustering detection."""
        detector = BiasDetector()
        sentiments = ["positive", "positive", "positive", "positive", "positive"]
        result = detector.detect_clustering(sentiments)
        assert result.detected is True
        assert result.dominant_sentiment == "positive"
        assert result.dominant_percentage == 100.0

    def test_high_clustering_above_eighty_percent(self):
        """90% same sentiment triggers clustering."""
        detector = BiasDetector()
        sentiments = [
            "positive", "positive", "positive", "positive", "positive",
            "positive", "positive", "positive", "positive", "negative",
        ]
        result = detector.detect_clustering(sentiments)
        assert result.detected is True
        assert result.dominant_sentiment == "positive"
        assert result.dominant_percentage == 90.0

    def test_exactly_eighty_percent_no_clustering(self):
        """Exactly 80% does not trigger clustering (must be >80%)."""
        detector = BiasDetector()
        sentiments = [
            "positive", "positive", "positive", "positive", "negative",
        ]
        result = detector.detect_clustering(sentiments)
        assert result.detected is False
        assert result.dominant_sentiment is None

    def test_diverse_sentiments_no_clustering(self):
        """Well-distributed sentiments do not trigger clustering."""
        detector = BiasDetector()
        sentiments = ["positive", "negative", "mixed", "neutral", "positive"]
        result = detector.detect_clustering(sentiments)
        assert result.detected is False

    def test_empty_sentiments(self):
        """Empty sentiment list returns no clustering."""
        detector = BiasDetector()
        result = detector.detect_clustering([])
        assert result.detected is False
        assert result.dominant_percentage == 0.0


class TestValidateSkepticalPersonas:
    """T028: Test validate_skeptical_personas() checking that skeptical personas include criticism."""

    def test_skeptical_persona_missing_criticism(self):
        """Persona with agreeableness=2 and no criticism keywords is flagged."""
        detector = BiasDetector()
        persona_traits = [
            {"agreeableness": 2, "criticism_tendency": "balanced"},
        ]
        responses = [
            "This is wonderful! I love everything about it. Amazing product!",
        ]
        all_passed, missing_count = detector.validate_skeptical_personas(
            persona_traits, responses
        )
        assert all_passed is False
        assert missing_count == 1

    def test_skeptical_persona_with_criticism_passes(self):
        """Skeptical persona expressing concern passes validation."""
        detector = BiasDetector()
        persona_traits = [
            {"agreeableness": 2, "criticism_tendency": "balanced"},
        ]
        responses = [
            "I have a concern about this feature. There are some issues that need addressing.",
        ]
        all_passed, missing_count = detector.validate_skeptical_personas(
            persona_traits, responses
        )
        assert all_passed is True
        assert missing_count == 0

    def test_critical_tendency_treated_as_skeptical(self):
        """Persona with criticism_tendency='critical' is treated as skeptical."""
        detector = BiasDetector()
        persona_traits = [
            {"agreeableness": 7, "criticism_tendency": "critical"},
        ]
        responses = [
            "This is great! Everything looks fine to me!",
        ]
        all_passed, missing_count = detector.validate_skeptical_personas(
            persona_traits, responses
        )
        assert all_passed is False
        assert missing_count == 1

    def test_non_skeptical_persona_always_passes(self):
        """Persona with agreeableness=7 and balanced tendency always passes."""
        detector = BiasDetector()
        persona_traits = [
            {"agreeableness": 7, "criticism_tendency": "balanced"},
        ]
        responses = [
            "This is absolutely wonderful! I love everything!",
        ]
        all_passed, missing_count = detector.validate_skeptical_personas(
            persona_traits, responses
        )
        assert all_passed is True
        assert missing_count == 0

    def test_mixed_panel_partial_failure(self):
        """Panel with mix of skeptical and agreeable personas flags only skeptical ones."""
        detector = BiasDetector()
        persona_traits = [
            {"agreeableness": 2, "criticism_tendency": "balanced"},  # skeptical, no criticism
            {"agreeableness": 8, "criticism_tendency": "balanced"},  # not skeptical
            {"agreeableness": 3, "criticism_tendency": "critical"},  # skeptical, has criticism
        ]
        responses = [
            "This is amazing! Everything is perfect!",
            "This is amazing! Everything is perfect!",
            "I have a concern about the security risk involved here.",
        ]
        all_passed, missing_count = detector.validate_skeptical_personas(
            persona_traits, responses
        )
        assert all_passed is False
        assert missing_count == 1


class TestSycophancyRateAndThresholds:
    """T029: Test sycophancy rate calculation and threshold warnings."""

    def test_sycophancy_rate_calculation(self):
        """Sycophancy rate = (flagged / total) * 100."""
        detector = BiasDetector()
        responses = [
            "This is absolutely amazing and perfect in every way!",
            "I have some concerns about the user interface design.",
            "This is the best thing ever and couldn't be better!",
            "The feature needs improvement in several areas.",
        ]
        analysis = detector.full_analysis(responses)
        # 2 out of 4 responses flagged = 50%
        assert analysis.sycophancy_rate == 50.0

    def test_zero_sycophancy_rate(self):
        """No flagged responses produces 0% rate."""
        detector = BiasDetector()
        responses = [
            "I have some concerns about the feature.",
            "The interface could be more intuitive.",
            "There are both strengths and weaknesses here.",
        ]
        analysis = detector.full_analysis(responses)
        assert analysis.sycophancy_rate == 0.0

    def test_hundred_percent_sycophancy_rate(self):
        """All responses flagged produces 100% rate."""
        detector = BiasDetector()
        responses = [
            "This is absolutely amazing!",
            "I love everything about this!",
            "This is perfect in every way!",
        ]
        analysis = detector.full_analysis(responses)
        assert analysis.sycophancy_rate == 100.0

    def test_threshold_pass_when_below_maximum(self):
        """Analysis passes when sycophancy rate is below threshold."""
        thresholds = QualityThresholds(sycophancy_maximum=60.0)
        detector = BiasDetector(thresholds=thresholds)
        responses = [
            "This is absolutely amazing!",
            "I have concerns about performance.",
            "The design could be improved.",
        ]
        analysis = detector.full_analysis(responses)
        # 1 out of 3 = 33.3%, below 60% threshold
        assert analysis.passed_threshold is True

    def test_threshold_fail_when_above_maximum(self):
        """Analysis fails when sycophancy rate exceeds threshold."""
        thresholds = QualityThresholds(sycophancy_maximum=20.0)
        detector = BiasDetector(thresholds=thresholds)
        responses = [
            "This is absolutely amazing!",
            "I love everything about this!",
            "This is perfect in every way!",
            "I have one small concern about timing.",
        ]
        analysis = detector.full_analysis(responses)
        # 3 out of 4 = 75%, above 20% threshold
        assert analysis.passed_threshold is False
        assert analysis.threshold_used == 20.0

    def test_warning_flags_include_high_ratio(self):
        """Warning flags are generated for high positive:negative ratio."""
        detector = BiasDetector()
        responses = [
            "I love this great and amazing product! It's excellent and fantastic!",
        ]
        analysis = detector.full_analysis(responses)
        ratio_warnings = [w for w in analysis.warning_flags if "ratio" in w.lower()]
        assert len(ratio_warnings) > 0

    def test_warning_flags_include_clustering(self):
        """Warning flags generated when clustering is detected."""
        detector = BiasDetector()
        responses = [
            "Positive response here.",
            "Another positive response.",
            "Yet another positive one.",
            "Still positive response.",
            "More positivity here.",
        ]
        sentiments = ["positive"] * 5
        analysis = detector.full_analysis(responses, sentiments=sentiments)
        clustering_warnings = [w for w in analysis.warning_flags if "clustering" in w.lower()]
        assert len(clustering_warnings) > 0

    def test_warning_flags_include_missing_criticism(self):
        """Warning flags generated when skeptical personas lack criticism."""
        detector = BiasDetector()
        persona_traits = [
            {"agreeableness": 2, "criticism_tendency": "balanced"},
        ]
        responses = [
            "This is absolutely amazing! I love everything!",
        ]
        analysis = detector.full_analysis(
            responses, persona_traits=persona_traits
        )
        criticism_warnings = [
            w for w in analysis.warning_flags if "criticism" in w.lower()
        ]
        assert len(criticism_warnings) > 0

    def test_full_analysis_populates_all_fields(self):
        """Full analysis returns a BiasAnalysis with all required fields."""
        detector = BiasDetector()
        responses = [
            "This is absolutely amazing and perfect in every way!",
            "I have concerns about the interface being confusing.",
        ]
        sentiments = ["positive", "negative"]
        persona_traits = [
            {"agreeableness": 2, "criticism_tendency": "balanced"},
            {"agreeableness": 7, "criticism_tendency": "balanced"},
        ]
        analysis = detector.full_analysis(
            responses, persona_traits=persona_traits, sentiments=sentiments
        )
        assert analysis.sycophancy_rate >= 0.0
        assert analysis.positive_negative_ratio >= 0.0
        assert analysis.sentiment_clustering is not None
        assert isinstance(analysis.flagged_responses, list)
        assert isinstance(analysis.warning_flags, list)
        assert analysis.threshold_used == detector.thresholds.sycophancy_maximum

    def test_empty_responses_returns_clean_analysis(self):
        """Empty response list returns a clean BiasAnalysis."""
        detector = BiasDetector()
        analysis = detector.full_analysis([])
        assert analysis.sycophancy_rate == 0.0
        assert analysis.passed_threshold is True
        assert analysis.flagged_responses == []
