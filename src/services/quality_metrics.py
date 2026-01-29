"""Service for calculating response quality metrics.

Measures consistency with persona traits and detects sycophancy indicators.
"""

from typing import Any

from models.persona import BigFive
from models.session import QualityMetrics


class QualityMetricsCalculator:
    """Calculates quality metrics for persona responses.

    Measures consistency with Big Five traits and detects
    sycophancy patterns that indicate non-authentic responses.
    """

    # Trait-keyword mappings for Big Five traits
    # High values (7-10) should match these keywords
    HIGH_TRAIT_KEYWORDS = {
        "openness": [
            "curious", "innovative", "creative", "novel", "explore",
            "experiment", "imaginative", "unconventional", "new ideas",
            "original", "artistic", "inventive", "diverse", "abstract",
            "philosophical", "open-minded",
        ],
        "conscientiousness": [
            "organized", "planned", "thorough", "systematic", "careful",
            "detail", "discipline", "reliable", "responsible",
            "structured", "methodical", "precise", "orderly", "diligent",
            "meticulous", "punctual",
        ],
        "extraversion": [
            "excited", "energetic", "social", "enthusiastic", "outgoing",
            "collaborative", "team", "interact", "engaging",
            "talkative", "sociable", "assertive", "lively", "dynamic",
            "expressive", "vibrant",
        ],
        "agreeableness": [
            "cooperative", "helpful", "trust", "kind", "supportive",
            "understanding", "considerate", "harmony",
            "empathetic", "compassionate", "gentle", "agreeable", "patient",
            "tolerant", "warm",
        ],
        "neuroticism": [
            "worried", "anxious", "concerned", "stressed", "nervous",
            "uncertain", "sensitive", "overwhelmed",
            "tense", "apprehensive", "fearful", "moody", "insecure",
            "volatile", "distressed",
        ],
    }

    # Low values (1-3) should match these keywords
    LOW_TRAIT_KEYWORDS = {
        "openness": [
            "traditional", "proven", "familiar", "practical", "conventional",
            "standard", "cautious", "prefer existing",
            "routine", "predictable", "established", "tried and true", "stable",
        ],
        "conscientiousness": [
            "flexible", "spontaneous", "adaptable", "casual", "relaxed",
            "improvise", "go with the flow",
            "easygoing", "unstructured", "carefree", "laid-back", "informal",
        ],
        "extraversion": [
            "quiet", "reserved", "prefer solitude", "reflective", "independent",
            "thoughtful", "private", "introspective",
            "solitary", "withdrawn", "shy", "calm", "lone", "contemplative",
        ],
        "agreeableness": [
            "skeptical", "critical", "challenge", "competitive", "direct",
            "questioning", "disagree", "doubt",
            "stubborn", "adversarial", "blunt", "harsh", "demanding",
            "confrontational",
        ],
        "neuroticism": [
            "calm", "stable", "relaxed", "composed", "confident",
            "resilient", "steady", "unworried",
            "serene", "content", "secure", "optimistic", "even-tempered",
            "peaceful",
        ],
    }

    # Sycophancy indicator phrases
    SYCOPHANCY_PHRASES = [
        "absolutely amazing", "love everything", "perfect in every way",
        "no concerns at all", "best thing ever", "couldn't be better",
        "nothing to improve", "wouldn't change anything",
    ]

    # Schwartz value keyword mappings for value-based consistency checks
    SCHWARTZ_VALUE_KEYWORDS = {
        "self_direction": [
            "independent", "freedom", "autonomous", "self-reliant", "creative",
            "curious", "choose", "explore", "own way",
        ],
        "stimulation": [
            "exciting", "varied", "daring", "adventure", "novelty",
            "thrill", "dynamic", "challenge", "risk",
        ],
        "hedonism": [
            "pleasure", "enjoy", "gratification", "fun", "comfort",
            "leisure", "indulge", "delight",
        ],
        "achievement": [
            "success", "capable", "ambitious", "influential", "accomplished",
            "competent", "excel", "perform",
        ],
        "power": [
            "authority", "wealth", "control", "dominant", "status",
            "prestige", "lead", "command",
        ],
        "security": [
            "safe", "stable", "order", "clean", "protect",
            "secure", "reliable", "predictable", "certain",
        ],
        "conformity": [
            "obedient", "polite", "respect", "proper", "appropriate",
            "comply", "follow rules", "duty",
        ],
        "tradition": [
            "humble", "devout", "custom", "heritage", "cultural",
            "respect elders", "traditional", "values",
        ],
        "benevolence": [
            "loyal", "honest", "forgiving", "responsible", "caring",
            "generous", "nurturing", "community",
        ],
        "universalism": [
            "equality", "justice", "peace", "tolerance", "broad-minded",
            "environment", "fairness", "inclusive",
        ],
    }

    # Positive and negative keywords for ratio
    POSITIVE_KEYWORDS = [
        "love", "great", "excellent", "amazing", "fantastic",
        "wonderful", "perfect", "brilliant", "outstanding",
    ]

    NEGATIVE_KEYWORDS = [
        "concern", "issue", "problem", "worry", "dislike",
        "frustrating", "confusing", "difficult", "disappointing",
    ]

    # Quality thresholds
    CONSISTENCY_THRESHOLD = 70  # Minimum consistency score to pass
    SYCOPHANCY_RATIO_THRESHOLD = 4  # Max positive:negative ratio

    def calculate(self, big_five: BigFive, response_text: str) -> QualityMetrics:
        """Calculate quality metrics for a response.

        Args:
            big_five: The persona's Big Five traits.
            response_text: The raw response text.

        Returns:
            QualityMetrics with scores and indicators.
        """
        response_lower = response_text.lower()

        # Calculate consistency
        consistency_result = self._calculate_consistency(big_five, response_lower)
        consistency_score = consistency_result["score"]
        matched_traits = consistency_result["matched"]
        missing_traits = consistency_result["missing"]

        # Detect sycophancy
        sycophancy_result = self._detect_sycophancy(response_lower)

        # Check quality gates
        warnings = []
        passed_gates = True

        if consistency_score < self.CONSISTENCY_THRESHOLD:
            warnings.append(f"Low consistency score ({consistency_score:.0f}% < {self.CONSISTENCY_THRESHOLD}%)")
            passed_gates = False

        if sycophancy_result.get("excessive_praise", False):
            warnings.append("Response shows excessive praise - may indicate sycophancy")
            passed_gates = False

        ratio = sycophancy_result.get("positive_negative_ratio", 0)
        if ratio > self.SYCOPHANCY_RATIO_THRESHOLD:
            warnings.append(f"High positive:negative ratio ({ratio:.1f}:1 > {self.SYCOPHANCY_RATIO_THRESHOLD}:1)")
            passed_gates = False

        return QualityMetrics(
            consistency_score=consistency_score,
            sycophancy_indicators=sycophancy_result,
            warnings=warnings,
            passed_gates=passed_gates,
            matched_traits=matched_traits if matched_traits else None,
            missing_traits=missing_traits if missing_traits else None,
        )

    def _calculate_consistency(
        self,
        big_five: BigFive,
        response_lower: str,
    ) -> dict[str, Any]:
        """Calculate consistency between traits and response.

        Only checks extreme traits (high >=7 or low <=3) for consistency.
        Moderate traits (4-6) are given automatic credit.

        Args:
            big_five: The Big Five traits.
            response_lower: Lowercase response text.

        Returns:
            Dictionary with score, matched traits, and missing traits.
        """
        matched = []
        missing = []
        extreme_traits = 0
        extreme_matches = 0

        # Check each trait
        traits = {
            "openness": big_five.openness,
            "conscientiousness": big_five.conscientiousness,
            "extraversion": big_five.extraversion,
            "agreeableness": big_five.agreeableness,
            "neuroticism": big_five.neuroticism,
        }

        for trait_name, trait_value in traits.items():
            if trait_value >= 7:
                # High trait - must match high keywords
                extreme_traits += 1
                keywords = self.HIGH_TRAIT_KEYWORDS.get(trait_name, [])
                if any(kw in response_lower for kw in keywords):
                    extreme_matches += 1
                    matched.append(f"high_{trait_name}")
                else:
                    missing.append(f"high_{trait_name}")
            elif trait_value <= 3:
                # Low trait - must match low keywords
                extreme_traits += 1
                keywords = self.LOW_TRAIT_KEYWORDS.get(trait_name, [])
                if any(kw in response_lower for kw in keywords):
                    extreme_matches += 1
                    matched.append(f"low_{trait_name}")
                else:
                    missing.append(f"low_{trait_name}")
            else:
                # Medium trait - check if response has any related keywords (bonus)
                high_kw = self.HIGH_TRAIT_KEYWORDS.get(trait_name, [])
                low_kw = self.LOW_TRAIT_KEYWORDS.get(trait_name, [])
                if any(kw in response_lower for kw in high_kw + low_kw):
                    matched.append(f"moderate_{trait_name}")

        # Calculate score: 100% if no extreme traits, otherwise based on extreme trait matches
        if extreme_traits == 0:
            # No extreme traits - base score of 80%, bonus for moderate matches
            score = 80 + (len(matched) * 4)  # Up to 100% with 5 moderate matches
        else:
            # Score based on extreme trait matches
            base_score = (extreme_matches / extreme_traits * 100)
            # Bonus for matching moderate traits
            moderate_bonus = len([m for m in matched if "moderate" in m]) * 5
            score = min(100, base_score + moderate_bonus)

        return {
            "score": score,
            "matched": matched,
            "missing": missing,
        }

    def _detect_sycophancy(self, response_lower: str) -> dict[str, Any]:
        """Detect sycophancy indicators in response.

        Args:
            response_lower: Lowercase response text.

        Returns:
            Dictionary of sycophancy indicators.
        """
        indicators: dict[str, Any] = {}

        # Check for sycophancy phrases
        phrase_count = sum(1 for phrase in self.SYCOPHANCY_PHRASES if phrase in response_lower)
        indicators["sycophancy_phrase_count"] = phrase_count
        indicators["excessive_praise"] = phrase_count >= 2

        # Calculate positive:negative ratio
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in response_lower)
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in response_lower)

        if negative_count > 0:
            ratio = positive_count / negative_count
        elif positive_count > 0:
            ratio = float("inf")
        else:
            ratio = 1.0

        indicators["positive_count"] = positive_count
        indicators["negative_count"] = negative_count
        indicators["positive_negative_ratio"] = ratio if ratio != float("inf") else 10.0

        # Check for absence of concerns
        concern_keywords = ["concern", "issue", "problem", "worry", "but", "however"]
        has_concerns = any(kw in response_lower for kw in concern_keywords)
        indicators["no_concerns_raised"] = not has_concerns

        return indicators
