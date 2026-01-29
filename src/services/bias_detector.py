"""Service for detecting bias and sycophancy patterns in persona responses.

Provides comprehensive bias analysis including sycophancy phrase detection,
sentiment ratio calculation, clustering analysis, and skeptical persona
validation.
"""

from models.calibration import QualityThresholds
from models.quality import BiasAnalysis, FlaggedResponse, SentimentClustering
from services.quality_metrics import QualityMetricsCalculator


class BiasDetector:
    """Detects bias and sycophancy patterns in persona responses.

    Combines phrase-level sycophancy detection, sentiment ratio analysis,
    clustering detection, and skeptical persona validation into a unified
    bias analysis pipeline.
    """

    SYCOPHANCY_PHRASES = [
        "absolutely amazing",
        "love everything",
        "perfect in every way",
        "no concerns at all",
        "best thing ever",
        "couldn't be better",
        "nothing to improve",
        "wouldn't change anything",
        "this is exactly what i need",
        "i can't find any issues",
        "this is perfect",
        "i would definitely recommend",
        "this exceeds expectations",
        "i have no complaints",
        "i'm completely satisfied",
    ]

    # Keywords indicating concern or criticism in a response
    CONCERN_KEYWORDS = [
        "concern",
        "issue",
        "problem",
        "worry",
        "however",
        "but",
        "disagree",
        "doubt",
        "skeptical",
        "critical",
        "challenge",
        "question",
        "risk",
        "drawback",
        "flaw",
        "weakness",
        "disappointing",
        "frustrating",
        "confusing",
        "difficult",
    ]

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        """Initialize BiasDetector with optional quality thresholds.

        Args:
            thresholds: Quality thresholds for pass/fail determination.
                        Uses defaults if not provided.
        """
        self.thresholds = thresholds or QualityThresholds()
        self._metrics_calculator = QualityMetricsCalculator()

    def detect_sycophancy_phrases(self, response_text: str) -> list[str]:
        """Detect sycophancy phrases present in the response text.

        Args:
            response_text: The response text to analyze.

        Returns:
            List of sycophancy phrases found in the text.
        """
        lower_text = response_text.lower()
        return [phrase for phrase in self.SYCOPHANCY_PHRASES if phrase in lower_text]

    def calculate_sentiment_ratio(self, responses: list[str]) -> float:
        """Calculate the positive-to-negative keyword ratio across responses.

        Counts positive and negative keywords from the QualityMetricsCalculator
        keyword lists across all responses and returns the ratio.

        Args:
            responses: List of response texts to analyze.

        Returns:
            Ratio of positive to negative keywords. Capped at 10.0 if no
            negative keywords are found.
        """
        positive_keywords = self._metrics_calculator.POSITIVE_KEYWORDS
        negative_keywords = self._metrics_calculator.NEGATIVE_KEYWORDS

        positive_count = 0
        negative_count = 0

        for response in responses:
            lower = response.lower()
            positive_count += sum(1 for kw in positive_keywords if kw in lower)
            negative_count += sum(1 for kw in negative_keywords if kw in lower)

        if negative_count == 0:
            return 10.0
        return positive_count / negative_count

    def detect_clustering(self, sentiments: list[str]) -> SentimentClustering:
        """Detect unhealthy sentiment clustering across responses.

        Checks whether a single sentiment dominates more than 80% of
        responses, indicating potential bias.

        Args:
            sentiments: List of sentiment labels (e.g., "positive", "negative").

        Returns:
            SentimentClustering model with detection results.
        """
        if not sentiments:
            return SentimentClustering(
                detected=False,
                dominant_sentiment=None,
                dominant_percentage=0.0,
                expected_diversity=0.5,
            )

        total = len(sentiments)
        frequency: dict[str, int] = {}
        for s in sentiments:
            frequency[s] = frequency.get(s, 0) + 1

        dominant = max(frequency, key=frequency.get)  # type: ignore[arg-type]
        dominant_pct = (frequency[dominant] / total) * 100

        detected = dominant_pct > 80.0

        # Expected diversity: 1/N where N is number of unique sentiments possible
        # For typical sentiment analysis, expect at least some diversity
        unique_count = len(frequency)
        expected_diversity = 1.0 / max(unique_count, 2)

        return SentimentClustering(
            detected=detected,
            dominant_sentiment=dominant if detected else None,
            dominant_percentage=dominant_pct,
            expected_diversity=expected_diversity,
        )

    def validate_skeptical_personas(
        self,
        persona_traits: list[dict],
        responses: list[str],
    ) -> tuple[bool, int]:
        """Validate that skeptical personas include criticism in their responses.

        A persona is considered "skeptical" if agreeableness <= 3 or
        criticism_tendency == "critical". Skeptical personas should include
        concern or criticism keywords in their responses.

        Args:
            persona_traits: List of dicts with "agreeableness" and
                           "criticism_tendency" keys.
            responses: List of response texts, one per persona.

        Returns:
            Tuple of (all_passed, missing_criticism_count) where all_passed
            is True only if every skeptical persona expressed criticism.
        """
        missing_criticism_count = 0
        count = min(len(persona_traits), len(responses))

        for i in range(count):
            traits = persona_traits[i]
            agreeableness = traits.get("agreeableness", 5)
            criticism_tendency = traits.get("criticism_tendency", "balanced")

            is_skeptical = agreeableness <= 3 or criticism_tendency == "critical"

            if is_skeptical:
                lower_response = responses[i].lower()
                has_criticism = any(
                    kw in lower_response for kw in self.CONCERN_KEYWORDS
                )
                if not has_criticism:
                    missing_criticism_count += 1

        all_passed = missing_criticism_count == 0
        return (all_passed, missing_criticism_count)

    def full_analysis(
        self,
        responses: list[str],
        persona_traits: list[dict] | None = None,
        sentiments: list[str] | None = None,
    ) -> BiasAnalysis:
        """Run comprehensive bias analysis across all detection methods.

        Orchestrates sycophancy phrase detection, sentiment ratio calculation,
        clustering detection, and skeptical persona validation into a single
        BiasAnalysis result.

        Args:
            responses: List of response texts to analyze.
            persona_traits: Optional list of persona trait dicts for skeptical
                           persona validation.
            sentiments: Optional list of sentiment labels for clustering
                       detection.

        Returns:
            BiasAnalysis with all fields populated.
        """
        total = len(responses)
        if total == 0:
            return BiasAnalysis(
                sycophancy_rate=0.0,
                sycophancy_phrases_found=[],
                positive_negative_ratio=1.0,
                sentiment_clustering=SentimentClustering(
                    detected=False,
                    dominant_sentiment=None,
                    dominant_percentage=0.0,
                    expected_diversity=0.5,
                ),
                flagged_responses=[],
                passed_threshold=True,
                warning_flags=[],
                threshold_used=self.thresholds.sycophancy_maximum,
            )

        # Collect all sycophancy phrases and build flagged responses
        all_phrases: list[str] = []
        flagged: list[FlaggedResponse] = []

        for idx, response in enumerate(responses):
            phrases = self.detect_sycophancy_phrases(response)
            if phrases:
                all_phrases.extend(phrases)
                flagged.append(
                    FlaggedResponse(
                        response_index=idx,
                        response_text=response,
                        flag_type="sycophancy",
                        flag_reason=f"Sycophancy phrases detected: {', '.join(phrases)}",
                        confidence=min(1.0, len(phrases) * 0.25),
                    )
                )

        # Calculate sentiment ratio
        ratio = self.calculate_sentiment_ratio(responses)

        # Clustering detection
        if sentiments:
            clustering = self.detect_clustering(sentiments)
        else:
            clustering = SentimentClustering(
                detected=False,
                dominant_sentiment=None,
                dominant_percentage=0.0,
                expected_diversity=0.5,
            )

        # Skeptical persona validation
        missing_criticism = 0
        if persona_traits:
            _, missing_criticism = self.validate_skeptical_personas(
                persona_traits, responses
            )

        # Sycophancy rate
        sycophancy_rate = (len(flagged) / total) * 100

        # Build warning flags with weighted components
        warning_flags: list[str] = []

        # Weight: phrases 0.25
        if all_phrases:
            warning_flags.append(
                f"Sycophancy phrases detected (weight 0.25): {len(all_phrases)} phrases found"
            )

        # Weight: ratio 0.25
        if ratio > self.thresholds.positive_negative_ratio:
            warning_flags.append(
                f"High positive:negative ratio (weight 0.25): {ratio:.1f}:1 "
                f"exceeds threshold {self.thresholds.positive_negative_ratio:.1f}:1"
            )

        # Weight: missing_criticism 0.30
        if missing_criticism > 0:
            warning_flags.append(
                f"Missing criticism from skeptical personas (weight 0.30): "
                f"{missing_criticism} persona(s) missing expected criticism"
            )

        # Weight: clustering 0.20
        if clustering.detected:
            warning_flags.append(
                f"Sentiment clustering detected (weight 0.20): "
                f"{clustering.dominant_sentiment} at {clustering.dominant_percentage:.1f}%"
            )

        # Determine pass/fail
        passed = sycophancy_rate <= self.thresholds.sycophancy_maximum

        # Deduplicate phrases found
        unique_phrases = list(dict.fromkeys(all_phrases))

        return BiasAnalysis(
            sycophancy_rate=sycophancy_rate,
            sycophancy_phrases_found=unique_phrases,
            positive_negative_ratio=ratio,
            sentiment_clustering=clustering,
            flagged_responses=flagged,
            passed_threshold=passed,
            warning_flags=warning_flags,
            threshold_used=self.thresholds.sycophancy_maximum,
        )
