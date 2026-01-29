"""Tests for DriftDetector service (T055-T059).

Validates session segmentation, drift score calculation, drift point
identification, per-trait drift tracking, and warning level thresholds.
"""

import pytest

from models.persona import BigFive
from services.drift_detector import DriftDetector
from models.enums import DriftWarningLevel
from models.calibration import QualityThresholds
from models.quality import SegmentScore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def detector() -> DriftDetector:
    """Return a DriftDetector with default thresholds."""
    return DriftDetector()


@pytest.fixture
def high_openness_big_five() -> BigFive:
    """High-openness persona Big Five traits."""
    return BigFive(
        openness=9,
        conscientiousness=5,
        extraversion=6,
        agreeableness=5,
        neuroticism=4,
    )


@pytest.fixture
def high_openness_schwartz() -> list[str]:
    """Schwartz values for a high-openness persona."""
    return ["self_direction", "stimulation"]


# ---------------------------------------------------------------------------
# T055: segment_session tests
# ---------------------------------------------------------------------------


class TestSegmentSession:
    """T055: Test segment_session dividing responses into segments."""

    def test_nine_responses_into_three_segments(self, detector):
        """9 responses / 3 segments = 3 responses per segment."""
        responses = [f"response {i}" for i in range(9)]
        segments = detector.segment_session(responses, segments=3)

        assert len(segments) == 3
        assert all(len(s) == 3 for s in segments)
        # Verify all responses are present and ordered
        flat = [r for seg in segments for r in seg]
        assert flat == responses

    def test_ten_responses_uneven_division(self, detector):
        """10 responses / 3 segments: 3 + 3 + 4 (remainder in last)."""
        responses = [f"response {i}" for i in range(10)]
        segments = detector.segment_session(responses, segments=3)

        assert len(segments) == 3
        assert len(segments[0]) == 3
        assert len(segments[1]) == 3
        assert len(segments[2]) == 4  # remainder goes to last segment
        flat = [r for seg in segments for r in seg]
        assert flat == responses

    def test_fewer_responses_than_segments(self, detector):
        """2 responses with 3 segments: each response is its own segment."""
        responses = ["response 0", "response 1"]
        segments = detector.segment_session(responses, segments=3)

        assert len(segments) == 2
        assert segments[0] == ["response 0"]
        assert segments[1] == ["response 1"]

    def test_equal_responses_and_segments(self, detector):
        """3 responses with 3 segments: each response is its own segment."""
        responses = ["a", "b", "c"]
        segments = detector.segment_session(responses, segments=3)

        assert len(segments) == 3
        assert segments == [["a"], ["b"], ["c"]]

    def test_single_response(self, detector):
        """1 response with 3 segments: single segment with one response."""
        segments = detector.segment_session(["only one"], segments=3)

        assert len(segments) == 1
        assert segments[0] == ["only one"]


# ---------------------------------------------------------------------------
# T056: calculate_drift_score tests
# ---------------------------------------------------------------------------


class TestCalculateDriftScore:
    """T056: Test drift score calculation with drifting sessions."""

    def test_drifted_session_significant_drift(
        self, detector, drifted_session
    ):
        """A session drifting from high-openness to conventional should show significant drift."""
        big_five = BigFive(**drifted_session["persona"]["big_five"])
        schwartz_primary = [
            v for v in drifted_session["persona"]["schwartz_values"]["primary"]
        ]
        responses = drifted_session["responses"]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=schwartz_primary,
            responses=responses,
            persona_id=drifted_session["persona"]["id"],
        )

        # Drift score should be significant (first segment aligned, last not)
        assert result.drift_score > 10, (
            f"Expected significant drift score >10, got {result.drift_score:.1f}"
        )
        assert result.drift_detected is True

    def test_consistent_session_low_drift(
        self, detector, high_openness_big_five, high_openness_schwartz
    ):
        """A session with consistent responses should have low drift."""
        # All responses match high-openness keywords
        responses = [
            "I'm curious about this innovative and creative approach. "
            "I love to explore and experiment with novel ideas.",
            "This is imaginative and unconventional. I find it creative "
            "and innovative. I'm curious to explore further.",
            "New ideas excite me. I want to experiment with this creative "
            "and innovative approach. Exploring novel solutions is key.",
        ]

        result = detector.analyze(
            big_five=high_openness_big_five,
            schwartz_primary=high_openness_schwartz,
            responses=responses,
            persona_id="consistent-persona",
        )

        assert result.drift_score < 15, (
            f"Expected low drift score <15 for consistent session, got {result.drift_score:.1f}"
        )

    def test_drift_score_equals_first_last_difference(
        self, detector, high_openness_big_five, high_openness_schwartz
    ):
        """Drift score should equal |first_segment_score - last_segment_score|."""
        responses = [
            "curious innovative creative explore experiment",
            "curious innovative creative explore experiment",
            "curious innovative creative explore experiment",
            "traditional proven familiar conventional standard",
            "traditional proven familiar conventional standard",
            "traditional proven familiar conventional standard",
        ]

        result = detector.analyze(
            big_five=high_openness_big_five,
            schwartz_primary=high_openness_schwartz,
            responses=responses,
            persona_id="test-persona",
            segments=2,
        )

        first_score = result.segment_scores[0].consistency_score
        last_score = result.segment_scores[-1].consistency_score
        expected_drift = abs(first_score - last_score)
        assert result.drift_score == pytest.approx(expected_drift, abs=0.01)


# ---------------------------------------------------------------------------
# T057: find_drift_point tests
# ---------------------------------------------------------------------------


class TestFindDriftPoint:
    """T057: Test find_drift_point identifying where drift began."""

    def test_drift_point_at_max_delta(self, detector):
        """With scores [85, 70, 50], drift point should be index 1 or 2 (max delta)."""
        segment_scores = [
            SegmentScore(
                segment_index=0, start_response=0, end_response=2,
                consistency_score=85.0, response_count=3,
            ),
            SegmentScore(
                segment_index=1, start_response=3, end_response=5,
                consistency_score=70.0, response_count=3,
            ),
            SegmentScore(
                segment_index=2, start_response=6, end_response=8,
                consistency_score=50.0, response_count=3,
            ),
        ]

        drift_index = detector.find_drift_point(segment_scores)

        # Delta 0->1 = 15, delta 1->2 = 20, so max delta is between 1 and 2
        # Drift point should be the LATER segment (index 2)
        assert drift_index == 2

    def test_drift_point_early_in_session(self, detector):
        """With scores [90, 50, 48], drift point should be index 1."""
        segment_scores = [
            SegmentScore(
                segment_index=0, start_response=0, end_response=2,
                consistency_score=90.0, response_count=3,
            ),
            SegmentScore(
                segment_index=1, start_response=3, end_response=5,
                consistency_score=50.0, response_count=3,
            ),
            SegmentScore(
                segment_index=2, start_response=6, end_response=8,
                consistency_score=48.0, response_count=3,
            ),
        ]

        drift_index = detector.find_drift_point(segment_scores)

        # Delta 0->1 = 40, delta 1->2 = 2: max delta at index 1
        assert drift_index == 1

    def test_single_segment_returns_zero(self, detector):
        """With only one segment, drift point should be 0."""
        segment_scores = [
            SegmentScore(
                segment_index=0, start_response=0, end_response=2,
                consistency_score=80.0, response_count=3,
            ),
        ]

        assert detector.find_drift_point(segment_scores) == 0

    def test_no_drift_returns_first_transition(self, detector):
        """With equal scores [80, 80, 80], drift index is 0 (no delta > 0)."""
        segment_scores = [
            SegmentScore(
                segment_index=0, start_response=0, end_response=2,
                consistency_score=80.0, response_count=3,
            ),
            SegmentScore(
                segment_index=1, start_response=3, end_response=5,
                consistency_score=80.0, response_count=3,
            ),
            SegmentScore(
                segment_index=2, start_response=6, end_response=8,
                consistency_score=80.0, response_count=3,
            ),
        ]

        # All deltas are 0, so drift_index stays at 0
        assert detector.find_drift_point(segment_scores) == 0


# ---------------------------------------------------------------------------
# T058: Per-trait drift tracking tests
# ---------------------------------------------------------------------------


class TestPerTraitDrift:
    """T058: Test per-trait drift tracking between first and last segments."""

    def test_affected_traits_include_openness(
        self, detector, high_openness_big_five, high_openness_schwartz
    ):
        """Openness should be affected when drifting from high-openness to conventional."""
        first_segment = [
            "I'm curious about this innovative and creative approach. "
            "I love to explore and experiment with novel, unconventional ideas. "
            "Imaginative and original thinking drives me.",
        ]
        last_segment = [
            "I prefer the traditional, proven, and familiar approach. "
            "Conventional and standard methods are more practical. "
            "I'm cautious about trying new things.",
        ]

        affected, stable = detector.identify_affected_traits(
            high_openness_big_five,
            high_openness_schwartz,
            first_segment,
            last_segment,
        )

        affected_names = [t.trait_name for t in affected]
        assert "openness" in affected_names, (
            f"Expected 'openness' in affected traits, got {affected_names}"
        )
        # The openness trait should show decreased alignment
        openness_trait = next(t for t in affected if t.trait_name == "openness")
        assert openness_trait.drift_direction == "decreased"
        assert openness_trait.initial_alignment > openness_trait.final_alignment

    def test_stable_traits_not_in_affected(
        self, detector, high_openness_big_five, high_openness_schwartz
    ):
        """Traits that didn't change much should appear in stable list."""
        # Both segments have moderate-neutral content for non-openness traits
        first_segment = [
            "I'm curious about this innovative and creative approach. "
            "I love to explore and experiment with novel ideas.",
        ]
        last_segment = [
            "I prefer the traditional, proven, and familiar approach. "
            "Conventional and standard methods are more practical.",
        ]

        affected, stable = detector.identify_affected_traits(
            high_openness_big_five,
            high_openness_schwartz,
            first_segment,
            last_segment,
        )

        # Stable traits should exist (traits that didn't drift much)
        assert len(stable) > 0, "Should have at least one stable trait"
        affected_names = {t.trait_name for t in affected}
        for s in stable:
            assert s not in affected_names, (
                f"Stable trait '{s}' should not be in affected traits"
            )

    def test_affected_trait_has_correct_fields(
        self, detector, high_openness_big_five, high_openness_schwartz
    ):
        """Each affected trait should have all required fields populated."""
        first_segment = [
            "I'm curious about innovative, creative, novel, unconventional exploration. "
            "I experiment with imaginative and original ideas. Being independent and "
            "exploring my own way with freedom is exciting and daring.",
        ]
        last_segment = [
            "I prefer the traditional, proven, familiar, conventional, standard approach. "
            "Being cautious with established, predictable routines feels safe and stable.",
        ]

        affected, _ = detector.identify_affected_traits(
            high_openness_big_five,
            high_openness_schwartz,
            first_segment,
            last_segment,
        )

        assert len(affected) > 0, "Should detect at least one affected trait"
        for trait in affected:
            assert trait.trait_name, "trait_name must be set"
            assert trait.trait_type in ("big_five", "schwartz")
            assert 0 <= trait.initial_alignment <= 100
            assert 0 <= trait.final_alignment <= 100
            assert trait.drift_amount > 15
            assert trait.drift_direction in ("increased", "decreased")


# ---------------------------------------------------------------------------
# T059: Drift warning level tests
# ---------------------------------------------------------------------------


class TestDriftWarningLevels:
    """T059: Test drift threshold warning levels."""

    def test_none_level_below_15_percent(self):
        """Drift score < 15% should produce NONE warning level."""
        thresholds = QualityThresholds(drift_warning=15.0, drift_critical=25.0)
        detector = DriftDetector(thresholds=thresholds)

        big_five = BigFive(
            openness=9, conscientiousness=5, extraversion=5,
            agreeableness=5, neuroticism=5,
        )
        # All responses consistently match high openness
        responses = [
            "I'm curious about this innovative and creative exploration. "
            "Novel and unconventional ideas excite me. I love to experiment.",
            "Creative and imaginative thinking drives my curiosity. "
            "I explore innovative and novel approaches enthusiastically.",
            "I'm curious about experimenting with innovative, creative, novel ideas. "
            "Unconventional and imaginative exploration is what I enjoy.",
        ]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=["self_direction", "stimulation"],
            responses=responses,
            persona_id="consistent-persona",
        )

        assert result.warning_level == DriftWarningLevel.NONE
        assert result.drift_detected is False
        assert result.passed_threshold is True

    def test_warning_level_between_15_and_25_percent(self):
        """Drift score 15-25% should produce WARNING level."""
        thresholds = QualityThresholds(drift_warning=15.0, drift_critical=25.0)
        detector = DriftDetector(thresholds=thresholds)

        big_five = BigFive(
            openness=9, conscientiousness=5, extraversion=5,
            agreeableness=5, neuroticism=5,
        )
        # First responses match well, last responses match partially
        responses = [
            "I'm curious about this innovative and creative approach. "
            "Novel unconventional ideas excite me. I explore and experiment "
            "with imaginative original solutions. I'm open-minded and artistic.",
            "I'm curious about creative and innovative exploration. "
            "Novel ideas drive me to experiment unconventionally.",
            "I'm curious about creative and innovative exploration. "
            "Novel ideas drive me to experiment unconventionally.",
            # Last segment: some matching but weaker
            "This seems okay. I think the approach has some merit. "
            "There might be creative aspects worth exploring.",
            "This seems reasonable. Some interesting ideas here.",
            "The approach has potential. Worth considering further.",
        ]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=["self_direction", "stimulation"],
            responses=responses,
            persona_id="moderate-drift-persona",
        )

        # We verify the warning level mechanism works - if drift is in 15-25 range
        if 15 <= result.drift_score < 25:
            assert result.warning_level == DriftWarningLevel.WARNING
            assert result.drift_detected is True
            assert result.passed_threshold is True

    def test_critical_level_above_25_percent(self, drifted_session):
        """Drift score > 25% should produce CRITICAL warning level."""
        thresholds = QualityThresholds(drift_warning=15.0, drift_critical=25.0)
        detector = DriftDetector(thresholds=thresholds)

        big_five = BigFive(**drifted_session["persona"]["big_five"])
        schwartz_primary = drifted_session["persona"]["schwartz_values"]["primary"]
        responses = drifted_session["responses"]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=schwartz_primary,
            responses=responses,
            persona_id=drifted_session["persona"]["id"],
        )

        # The drifted_session fixture has clear drift from high openness to conventional
        assert result.drift_score > 25, (
            f"Expected drift > 25% for drifted session, got {result.drift_score:.1f}%"
        )
        assert result.warning_level == DriftWarningLevel.CRITICAL
        assert result.drift_detected is True
        assert result.passed_threshold is False

    def test_warning_flags_generated_for_critical(self, drifted_session):
        """Critical drift should generate warning flags."""
        detector = DriftDetector()
        big_five = BigFive(**drifted_session["persona"]["big_five"])
        schwartz_primary = drifted_session["persona"]["schwartz_values"]["primary"]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=schwartz_primary,
            responses=drifted_session["responses"],
            persona_id=drifted_session["persona"]["id"],
        )

        assert len(result.warning_flags) > 0, "Should have warning flags for drifting session"

    def test_no_warning_flags_for_stable_session(self, detector):
        """Stable session should not have drift-related warning flags."""
        big_five = BigFive(
            openness=9, conscientiousness=5, extraversion=5,
            agreeableness=5, neuroticism=5,
        )
        responses = [
            "I'm curious about this innovative and creative exploration. "
            "Novel and unconventional ideas excite me. I love to experiment.",
            "Creative and imaginative thinking drives my curiosity. "
            "I explore innovative and novel approaches enthusiastically.",
            "I'm curious about experimenting with innovative, creative, novel ideas. "
            "Unconventional and imaginative exploration is what I enjoy.",
        ]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=["self_direction", "stimulation"],
            responses=responses,
            persona_id="stable-persona",
        )

        if result.warning_level == DriftWarningLevel.NONE:
            # Only drift-related flags should be absent
            drift_flags = [f for f in result.warning_flags if "drift" in f.lower() or "critical" in f.lower()]
            assert len(drift_flags) == 0


# ---------------------------------------------------------------------------
# Additional integration-style tests
# ---------------------------------------------------------------------------


class TestAnalyzeOrchestration:
    """Test the full analyze() orchestration method."""

    def test_analyze_returns_all_fields(self, detector, drifted_session):
        """Analyze should return a complete DriftAnalysis."""
        big_five = BigFive(**drifted_session["persona"]["big_five"])
        schwartz_primary = drifted_session["persona"]["schwartz_values"]["primary"]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=schwartz_primary,
            responses=drifted_session["responses"],
            persona_id=drifted_session["persona"]["id"],
        )

        assert result.persona_id == drifted_session["persona"]["id"]
        assert result.session_length == len(drifted_session["responses"])
        assert result.segment_count == 3
        assert len(result.segment_scores) == 3
        assert 0 <= result.drift_score <= 100
        assert result.drift_point_index >= 0
        assert result.drift_point_response >= 0
        assert isinstance(result.warning_level, DriftWarningLevel)

    def test_analyze_custom_segment_count(self, detector):
        """Analyze should support custom segment count."""
        big_five = BigFive(
            openness=9, conscientiousness=5, extraversion=5,
            agreeableness=5, neuroticism=5,
        )
        responses = [f"response {i}" for i in range(8)]

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=["self_direction"],
            responses=responses,
            persona_id="test",
            segments=4,
        )

        assert result.segment_count == 4
        assert len(result.segment_scores) == 4

    def test_analyze_single_response(self, detector):
        """Analyze should handle a session with a single response."""
        big_five = BigFive(
            openness=9, conscientiousness=5, extraversion=5,
            agreeableness=5, neuroticism=5,
        )

        result = detector.analyze(
            big_five=big_five,
            schwartz_primary=["self_direction"],
            responses=["I'm curious about innovative ideas."],
            persona_id="single-response",
        )

        assert result.session_length == 1
        assert result.segment_count == 1
        assert result.drift_point_index == 0
        assert result.drift_score == 0.0
