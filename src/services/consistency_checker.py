"""Service for checking persona-response consistency (T017-T022).

Evaluates how well responses align with a persona's Big Five traits
and Schwartz values, producing detailed consistency scores with
per-trait alignment breakdowns and threshold-based warnings.
"""

import statistics

from models.calibration import QualityThresholds
from models.persona import BigFive
from models.quality import ConsistencyScore, TraitAlignment
from services.quality_metrics import QualityMetricsCalculator


class ConsistencyChecker:
    """Checks consistency between persona definitions and their responses.

    Uses keyword-based matching against Big Five personality traits and
    Schwartz value frameworks, with extremity-based weighting so that
    strongly defined traits matter more than neutral ones.
    """

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        """Initialize the ConsistencyChecker.

        Args:
            thresholds: Optional quality thresholds. Defaults to QualityThresholds()
                        which provides standard threshold values.
        """
        self.thresholds = thresholds or QualityThresholds()
        self._metrics = QualityMetricsCalculator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_big_five(
        self,
        big_five: BigFive,
        responses: list[str],
    ) -> tuple[float, list[TraitAlignment]]:
        """Calculate Big Five consistency score across all responses.

        For each trait, determines the expected keyword set based on
        the trait value (high >= 7, low <= 3, moderate 4-6), counts
        keyword matches across all responses, and computes a weighted
        aggregate score where extremity increases weight.

        Args:
            big_five: The persona's Big Five personality traits.
            responses: List of response texts to evaluate.

        Returns:
            Tuple of (overall_big_five_score, list_of_per_trait_alignments).
        """
        traits = {
            "openness": big_five.openness,
            "conscientiousness": big_five.conscientiousness,
            "extraversion": big_five.extraversion,
            "agreeableness": big_five.agreeableness,
            "neuroticism": big_five.neuroticism,
        }

        combined_lower = " ".join(r.lower() for r in responses)
        alignments: list[TraitAlignment] = []

        for trait_name, trait_value in traits.items():
            weight = abs(trait_value - 5) / 5.0

            if trait_value >= 7:
                expected_keywords = list(self._metrics.HIGH_TRAIT_KEYWORDS.get(trait_name, []))
                matched = [kw for kw in expected_keywords if kw in combined_lower]
                score = min(100.0, len(matched) / max(1, len(expected_keywords)) * 100)
            elif trait_value <= 3:
                expected_keywords = list(self._metrics.LOW_TRAIT_KEYWORDS.get(trait_name, []))
                matched = [kw for kw in expected_keywords if kw in combined_lower]
                score = min(100.0, len(matched) / max(1, len(expected_keywords)) * 100)
            else:
                # Moderate trait (4-6)
                high_kw = self._metrics.HIGH_TRAIT_KEYWORDS.get(trait_name, [])
                low_kw = self._metrics.LOW_TRAIT_KEYWORDS.get(trait_name, [])
                expected_keywords = list(high_kw) + list(low_kw)
                matched = [kw for kw in expected_keywords if kw in combined_lower]
                score = 70.0 if matched else 50.0

            alignments.append(TraitAlignment(
                trait_name=trait_name,
                trait_value=float(trait_value),
                alignment_score=score,
                matched_keywords=matched,
                expected_keywords=expected_keywords,
                weight=weight,
            ))

        # Compute weighted aggregate
        total_weight = sum(a.weight for a in alignments)
        if total_weight == 0:
            # All traits neutral – use equal weights
            big_five_score = sum(a.alignment_score for a in alignments) / len(alignments)
        else:
            big_five_score = (
                sum(a.alignment_score * a.weight for a in alignments) / total_weight
            )

        return big_five_score, alignments

    def calculate_schwartz(
        self,
        schwartz_primary: list[str],
        responses: list[str],
    ) -> tuple[float, list[TraitAlignment]]:
        """Calculate Schwartz value consistency score.

        For each primary Schwartz value, checks whether any of its
        keywords appear in any response. Score is the proportion of
        values reflected.

        Args:
            schwartz_primary: List of primary Schwartz value names.
            responses: List of response texts to evaluate.

        Returns:
            Tuple of (schwartz_score, list_of_per_value_alignments).
        """
        combined_lower = " ".join(r.lower() for r in responses)
        alignments: list[TraitAlignment] = []
        values_reflected = 0

        for value_name in schwartz_primary:
            keywords = list(self._metrics.SCHWARTZ_VALUE_KEYWORDS.get(value_name, []))
            matched = [kw for kw in keywords if kw in combined_lower]
            reflected = len(matched) > 0

            if reflected:
                values_reflected += 1

            alignments.append(TraitAlignment(
                trait_name=value_name,
                trait_value=1.0,  # Binary: value is defined
                alignment_score=100.0 if reflected else 0.0,
                matched_keywords=matched,
                expected_keywords=keywords,
                weight=1.0,
            ))

        values_defined = max(1, len(schwartz_primary))
        score = values_reflected / values_defined * 100

        return score, alignments

    def per_response_breakdown(
        self,
        big_five: BigFive,
        responses: list[str],
    ) -> list[float]:
        """Score each response individually against the persona's Big Five traits.

        Uses the same trait-keyword matching logic as calculate_big_five
        but applies it to each response in isolation.

        Args:
            big_five: The persona's Big Five personality traits.
            responses: List of response texts to evaluate.

        Returns:
            List of per-response consistency scores.
        """
        scores: list[float] = []

        for response in responses:
            score, _ = self.calculate_big_five(big_five, [response])
            scores.append(score)

        return scores

    def calculate(
        self,
        big_five: BigFive,
        schwartz_primary: list[str],
        responses: list[str],
    ) -> ConsistencyScore:
        """Orchestrate full consistency analysis.

        Combines Big Five and Schwartz scoring with configurable
        weighting (60/40), computes per-response variance, and
        evaluates against the configured consistency threshold.

        Args:
            big_five: The persona's Big Five personality traits.
            schwartz_primary: List of primary Schwartz value names.
            responses: List of response texts to evaluate.

        Returns:
            ConsistencyScore with all analysis details.
        """
        big_five_score, big_five_alignment = self.calculate_big_five(big_five, responses)
        schwartz_score, schwartz_alignment = self.calculate_schwartz(schwartz_primary, responses)
        per_response_scores = self.per_response_breakdown(big_five, responses)

        # Weighted overall: 60% Big Five, 40% Schwartz
        overall_score = big_five_score * 0.6 + schwartz_score * 0.4

        # Response variance
        if len(per_response_scores) > 1:
            response_variance = statistics.variance(per_response_scores)
        else:
            response_variance = 0.0

        # Threshold check
        threshold = self.thresholds.consistency_minimum
        passed_threshold = overall_score >= threshold

        # Warning flags
        warning_flags: list[str] = []
        if not passed_threshold:
            warning_flags.append(
                f"Low consistency score ({overall_score:.1f}% < {threshold:.1f}% threshold)"
            )
        if response_variance > 500:
            warning_flags.append(
                f"High response variance ({response_variance:.1f}) indicates inconsistent quality"
            )

        return ConsistencyScore(
            overall_score=overall_score,
            big_five_score=big_five_score,
            schwartz_score=schwartz_score,
            big_five_alignment=big_five_alignment,
            schwartz_alignment=schwartz_alignment,
            per_response_scores=per_response_scores,
            response_variance=response_variance,
            passed_threshold=passed_threshold,
            warning_flags=warning_flags,
            threshold_used=threshold,
            calculation_method="weighted",
        )
