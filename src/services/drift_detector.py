"""Service for detecting persona drift during sessions (T063-T067).

Monitors consistency across session segments to detect when a persona's
behavior drifts from its defined profile over the course of a conversation.
Identifies drift points, affected traits, and severity levels.
"""

from models.calibration import QualityThresholds
from models.enums import DriftWarningLevel
from models.persona import BigFive
from models.quality import AffectedTrait, DriftAnalysis, SegmentScore
from services.consistency_checker import ConsistencyChecker


class DriftDetector:
    """Detects persona consistency drift across session segments.

    Divides a session into temporal segments, scores each segment's
    consistency independently, and identifies where and how the
    persona's behavior diverged from its defined profile.
    """

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        """Initialize the DriftDetector.

        Args:
            thresholds: Optional quality thresholds. Defaults to QualityThresholds()
                        which provides standard threshold values.
        """
        self.thresholds = thresholds or QualityThresholds()
        self._checker = ConsistencyChecker(thresholds=self.thresholds)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def segment_session(
        self, responses: list[str], segments: int = 3
    ) -> list[list[str]]:
        """Divide responses into n segments for drift analysis.

        Uses integer division for segment size with remaining responses
        appended to the last segment. If there are fewer responses than
        the requested number of segments, each response becomes its own
        segment.

        Args:
            responses: List of response texts from the session.
            segments: Number of segments to divide into (default 3).

        Returns:
            List of segments, each being a list of response strings.
        """
        if len(responses) <= segments:
            return [[r] for r in responses]

        segment_size = len(responses) // segments
        result: list[list[str]] = []

        for i in range(segments):
            if i < segments - 1:
                start = i * segment_size
                end = start + segment_size
                result.append(responses[start:end])
            else:
                # Last segment gets all remaining responses
                start = i * segment_size
                result.append(responses[start:])

        return result

    def calculate_segment_scores(
        self,
        big_five: BigFive,
        schwartz_primary: list[str],
        segments: list[list[str]],
    ) -> list[SegmentScore]:
        """Score each segment's consistency against the persona profile.

        Args:
            big_five: The persona's Big Five personality traits.
            schwartz_primary: List of primary Schwartz value names.
            segments: List of response segments to score.

        Returns:
            List of SegmentScore models, one per segment.
        """
        scores: list[SegmentScore] = []
        response_offset = 0

        for idx, segment in enumerate(segments):
            consistency = self._checker.calculate(big_five, schwartz_primary, segment)
            scores.append(
                SegmentScore(
                    segment_index=idx,
                    start_response=response_offset,
                    end_response=response_offset + len(segment) - 1,
                    consistency_score=consistency.overall_score,
                    response_count=len(segment),
                )
            )
            response_offset += len(segment)

        return scores

    def find_drift_point(self, segment_scores: list[SegmentScore]) -> int:
        """Find the segment where drift began.

        Identifies the maximum score delta between consecutive segments
        and returns the index of the later segment in the max-delta pair.

        Args:
            segment_scores: List of per-segment consistency scores.

        Returns:
            Index of the segment where drift began.
        """
        if len(segment_scores) <= 1:
            return 0

        max_delta = 0.0
        drift_index = 0

        for i in range(1, len(segment_scores)):
            delta = abs(
                segment_scores[i].consistency_score
                - segment_scores[i - 1].consistency_score
            )
            if delta > max_delta:
                max_delta = delta
                drift_index = i

        return drift_index

    def identify_affected_traits(
        self,
        big_five: BigFive,
        schwartz_primary: list[str],
        first_segment: list[str],
        last_segment: list[str],
    ) -> tuple[list[AffectedTrait], list[str]]:
        """Compare per-trait alignment between first and last segments.

        A trait is "affected" if its alignment changed by more than 15
        points between the first and last segments.

        Args:
            big_five: The persona's Big Five personality traits.
            schwartz_primary: List of primary Schwartz value names.
            first_segment: Responses from the first segment.
            last_segment: Responses from the last segment.

        Returns:
            Tuple of (affected_traits, stable_trait_names).
        """
        # Calculate per-trait alignment for first and last segments
        first_b5_score, first_b5_align = self._checker.calculate_big_five(
            big_five, first_segment
        )
        last_b5_score, last_b5_align = self._checker.calculate_big_five(
            big_five, last_segment
        )
        first_sw_score, first_sw_align = self._checker.calculate_schwartz(
            schwartz_primary, first_segment
        )
        last_sw_score, last_sw_align = self._checker.calculate_schwartz(
            schwartz_primary, last_segment
        )

        affected: list[AffectedTrait] = []
        stable: list[str] = []

        # Compare Big Five traits
        for first_a, last_a in zip(first_b5_align, last_b5_align, strict=False):
            drift_amount = abs(first_a.alignment_score - last_a.alignment_score)
            if drift_amount > 15:
                direction = (
                    "increased"
                    if last_a.alignment_score > first_a.alignment_score
                    else "decreased"
                )
                affected.append(
                    AffectedTrait(
                        trait_name=first_a.trait_name,
                        trait_type="big_five",
                        initial_alignment=first_a.alignment_score,
                        final_alignment=last_a.alignment_score,
                        drift_amount=drift_amount,
                        drift_direction=direction,
                    )
                )
            else:
                stable.append(first_a.trait_name)

        # Compare Schwartz values
        for first_a, last_a in zip(first_sw_align, last_sw_align, strict=False):
            drift_amount = abs(first_a.alignment_score - last_a.alignment_score)
            if drift_amount > 15:
                direction = (
                    "increased"
                    if last_a.alignment_score > first_a.alignment_score
                    else "decreased"
                )
                affected.append(
                    AffectedTrait(
                        trait_name=first_a.trait_name,
                        trait_type="schwartz",
                        initial_alignment=first_a.alignment_score,
                        final_alignment=last_a.alignment_score,
                        drift_amount=drift_amount,
                        drift_direction=direction,
                    )
                )
            else:
                stable.append(first_a.trait_name)

        return affected, stable

    def analyze(
        self,
        big_five: BigFive,
        schwartz_primary: list[str],
        responses: list[str],
        persona_id: str,
        segments: int = 3,
    ) -> DriftAnalysis:
        """Orchestrate full drift detection analysis.

        Segments the session, scores each segment, identifies the drift
        point, compares first/last segments for affected traits, and
        computes an overall drift score with warning levels.

        Args:
            big_five: The persona's Big Five personality traits.
            schwartz_primary: List of primary Schwartz value names.
            responses: All response texts from the session.
            persona_id: ID of the persona being analyzed.
            segments: Number of segments to divide session into (default 3).

        Returns:
            DriftAnalysis with complete drift detection results.
        """
        # Step 1: Segment the session
        session_segments = self.segment_session(responses, segments)
        actual_segment_count = len(session_segments)

        # Step 2: Score each segment
        segment_scores = self.calculate_segment_scores(
            big_five, schwartz_primary, session_segments
        )

        # Step 3: Find drift point
        drift_point_index = self.find_drift_point(segment_scores)
        drift_point_response = segment_scores[drift_point_index].start_response

        # Step 4: Identify affected traits (compare first and last segments)
        affected_traits, stable_traits = self.identify_affected_traits(
            big_five,
            schwartz_primary,
            session_segments[0],
            session_segments[-1],
        )

        # Step 5: Calculate drift score = |first_segment_score - last_segment_score|
        drift_score = abs(
            segment_scores[0].consistency_score
            - segment_scores[-1].consistency_score
        )

        # Step 6: Determine warning level
        if drift_score >= self.thresholds.drift_critical:
            warning_level = DriftWarningLevel.CRITICAL
        elif drift_score >= self.thresholds.drift_warning:
            warning_level = DriftWarningLevel.WARNING
        else:
            warning_level = DriftWarningLevel.NONE

        # Step 7: Determine pass/fail
        drift_detected = drift_score >= self.thresholds.drift_warning
        passed_threshold = drift_score < self.thresholds.drift_critical

        # Step 8: Generate warning flags
        warning_flags: list[str] = []
        if warning_level == DriftWarningLevel.CRITICAL:
            warning_flags.append(
                f"Critical drift detected ({drift_score:.1f}% >= "
                f"{self.thresholds.drift_critical:.1f}% threshold)"
            )
        elif warning_level == DriftWarningLevel.WARNING:
            warning_flags.append(
                f"Drift warning ({drift_score:.1f}% >= "
                f"{self.thresholds.drift_warning:.1f}% threshold)"
            )

        if affected_traits:
            trait_names = [t.trait_name for t in affected_traits]
            warning_flags.append(
                f"Affected traits: {', '.join(trait_names)}"
            )

        return DriftAnalysis(
            drift_score=drift_score,
            drift_detected=drift_detected,
            segment_scores=segment_scores,
            drift_point_index=drift_point_index,
            drift_point_response=drift_point_response,
            affected_traits=affected_traits,
            stable_traits=stable_traits,
            passed_threshold=passed_threshold,
            warning_level=warning_level,
            warning_flags=warning_flags,
            persona_id=persona_id,
            session_length=len(responses),
            segment_count=actual_segment_count,
        )
