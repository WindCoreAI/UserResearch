"""Service for aggregating and analyzing panel responses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from jinja2 import Template

from models.aggregation import (
    AggregatedResults,
    ConsensusPoint,
    DivergencePoint,
    PanelQualityMetrics,
    Position,
    QuoteReference,
    SentimentDistribution,
    Theme,
)
from models.session import QualityMetrics, ResearchSession, Sentiment


class ResponseAggregatorError(Exception):
    """Error raised when response aggregation fails."""

    pass


class ResponseAggregator:
    """Service for aggregating and analyzing panel responses.

    Uses LLM-based aggregation to identify themes, consensus points,
    and divergence points from multiple persona responses.
    """

    def __init__(
        self,
        max_themes: int = 5,
        consensus_threshold: float = 0.6,
        template_path: Optional[Path] = None,
    ):
        """Initialize the response aggregator.

        Args:
            max_themes: Maximum number of themes to extract.
            consensus_threshold: Minimum agreement rate for consensus (0-1).
            template_path: Path to aggregation prompt template.
        """
        self.max_themes = max_themes
        self.consensus_threshold = consensus_threshold

        if template_path is None:
            template_path = (
                Path(__file__).parent.parent / "templates" / "aggregation_prompt.j2"
            )
        self.template_path = template_path

    async def aggregate_responses(
        self,
        sessions: list[ResearchSession],
        question: str,
        panel_name: str,
    ) -> AggregatedResults:
        """Aggregate multiple persona responses into synthesized results.

        Args:
            sessions: List of completed research sessions.
            question: The research question asked.
            panel_name: Name of the panel for context.

        Returns:
            AggregatedResults with themes, sentiment, consensus, and divergence.
        """
        # Filter to completed sessions with parsed responses
        valid_sessions = [
            s for s in sessions
            if s.response and s.response.parsed
        ]

        if not valid_sessions:
            # Return empty results if no valid responses
            return self._create_empty_results()

        # Prepare response data for the aggregation prompt
        responses_data = self._prepare_responses_data(valid_sessions)

        # Call LLM for aggregation
        llm_result = await self._call_aggregation_llm(
            responses_data=responses_data,
            question=question,
            panel_name=panel_name,
            persona_count=len(valid_sessions),
        )

        # Parse LLM result into AggregatedResults
        return self._parse_llm_result(llm_result, valid_sessions)

    def calculate_sentiment_distribution(
        self,
        sentiments: list[Sentiment],
    ) -> SentimentDistribution:
        """Calculate sentiment distribution from a list of sentiments.

        Args:
            sentiments: List of Sentiment values from responses.

        Returns:
            SentimentDistribution with percentages and dominant sentiment.
        """
        if not sentiments:
            return SentimentDistribution(
                positive=0.0,
                negative=0.0,
                mixed=0.0,
                neutral=0.0,
                dominant=Sentiment.NEUTRAL,
            )

        total = len(sentiments)
        counts = {
            Sentiment.POSITIVE: 0,
            Sentiment.NEGATIVE: 0,
            Sentiment.MIXED: 0,
            Sentiment.NEUTRAL: 0,
        }

        for s in sentiments:
            counts[s] += 1

        # Calculate percentages
        positive = (counts[Sentiment.POSITIVE] / total) * 100
        negative = (counts[Sentiment.NEGATIVE] / total) * 100
        mixed = (counts[Sentiment.MIXED] / total) * 100
        neutral = (counts[Sentiment.NEUTRAL] / total) * 100

        # Find dominant (most frequent) sentiment
        dominant = max(counts, key=counts.get)

        return SentimentDistribution(
            positive=positive,
            negative=negative,
            mixed=mixed,
            neutral=neutral,
            dominant=dominant,
        )

    def calculate_panel_quality_metrics(
        self,
        individual_metrics: list[QualityMetrics],
        completion_rate: float,
        theme_confidence: float,
        divergence_score: float,
    ) -> PanelQualityMetrics:
        """Calculate panel-level quality metrics.

        Args:
            individual_metrics: QualityMetrics from each persona.
            completion_rate: Percentage of personas that completed.
            theme_confidence: Confidence in theme extraction (0-100).
            divergence_score: Degree of disagreement (0-100).

        Returns:
            PanelQualityMetrics with gates and warnings.
        """
        warnings: list[str] = []

        # Calculate average consistency
        if individual_metrics:
            avg_consistency = sum(m.consistency_score for m in individual_metrics) / len(
                individual_metrics
            )
        else:
            avg_consistency = 0.0

        # Check quality gates
        passed_gates = True

        if avg_consistency < 70.0:
            passed_gates = False
            warnings.append(f"Average consistency ({avg_consistency:.1f}%) below 70% threshold")

        if completion_rate < 80.0:
            passed_gates = False
            warnings.append(f"Completion rate ({completion_rate:.1f}%) below 80% threshold")

        if divergence_score > 80.0:
            warnings.append(
                f"High divergence score ({divergence_score:.1f}%) - "
                "individual responses may be more useful than aggregation"
            )

        return PanelQualityMetrics(
            avg_consistency_score=avg_consistency,
            completion_rate=completion_rate,
            theme_confidence=theme_confidence,
            divergence_score=divergence_score,
            passed_gates=passed_gates,
            warnings=warnings,
            individual_metrics=individual_metrics,
        )

    def _prepare_responses_data(
        self,
        sessions: list[ResearchSession],
    ) -> list[dict[str, Any]]:
        """Prepare response data for the aggregation prompt.

        Args:
            sessions: List of completed research sessions.

        Returns:
            List of response dictionaries for the template.
        """
        responses = []
        for session in sessions:
            if session.response and session.response.parsed:
                parsed = session.response.parsed
                responses.append({
                    "persona_id": session.persona_id,
                    "persona_name": session.persona_name,
                    "sentiment": parsed.sentiment.value.upper(),
                    "overall_impression": parsed.overall_impression,
                    "concerns": parsed.concerns,
                    "suggestions": parsed.suggestions,
                    "key_quotes": parsed.key_quotes or [],
                })
        return responses

    async def _call_aggregation_llm(
        self,
        responses_data: list[dict[str, Any]],
        question: str,
        panel_name: str,
        persona_count: int,
    ) -> dict[str, Any]:
        """Call LLM to aggregate responses.

        This method should be overridden or mocked in tests.
        In production, it would use Claude Task tool.

        Args:
            responses_data: Prepared response data.
            question: The research question.
            panel_name: Panel name for context.
            persona_count: Number of personas.

        Returns:
            Dictionary with aggregation results.
        """
        # Load and render template
        with open(self.template_path) as f:
            template = Template(f.read())

        prompt = template.render(
            responses=responses_data,
            question=question,
            panel_name=panel_name,
            persona_count=persona_count,
        )

        # In production, this would call Claude via Task tool
        # For now, return a fallback result based on the data
        return self._generate_fallback_aggregation(responses_data)

    def _generate_fallback_aggregation(
        self,
        responses_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate a basic aggregation without LLM.

        Used as fallback when LLM is not available.

        Args:
            responses_data: Prepared response data.

        Returns:
            Basic aggregation dictionary.
        """
        # Count sentiments
        sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "MIXED": 0, "NEUTRAL": 0}
        for r in responses_data:
            sentiment = r.get("sentiment", "NEUTRAL")
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

        total = len(responses_data) or 1
        dominant = max(sentiment_counts, key=sentiment_counts.get)

        # Extract common concerns as themes
        all_concerns = []
        for r in responses_data:
            all_concerns.extend(r.get("concerns", []))

        themes = []
        if all_concerns:
            # Simple frequency-based theme extraction
            from collections import Counter
            concern_counts = Counter(all_concerns)
            for concern, count in concern_counts.most_common(self.max_themes):
                themes.append({
                    "name": concern[:50],
                    "description": f"Mentioned by {count} persona(s)",
                    "frequency": count,
                    "percentage": (count / total) * 100,
                    "supporting_quotes": [],
                    "sentiment_tendency": None,
                })

        return {
            "executive_summary": f"Analysis of {total} persona responses.",
            "themes": themes,
            "sentiment_distribution": {
                "positive": (sentiment_counts["POSITIVE"] / total) * 100,
                "negative": (sentiment_counts["NEGATIVE"] / total) * 100,
                "mixed": (sentiment_counts["MIXED"] / total) * 100,
                "neutral": (sentiment_counts["NEUTRAL"] / total) * 100,
                "dominant": dominant,
            },
            "consensus_points": [],
            "divergence_points": [],
            "aggregation_confidence": 50.0,  # Low confidence for fallback
        }

    def _parse_llm_result(
        self,
        result: dict[str, Any],
        sessions: list[ResearchSession],
    ) -> AggregatedResults:
        """Parse LLM aggregation result into AggregatedResults model.

        Args:
            result: Dictionary from LLM.
            sessions: Original sessions for reference.

        Returns:
            Validated AggregatedResults.
        """
        # Parse themes
        themes = []
        for t in result.get("themes", []):
            quotes = []
            for q in t.get("supporting_quotes", []):
                quotes.append(QuoteReference(
                    persona_id=q.get("persona_id", "unknown"),
                    persona_name=q.get("persona_name", "Unknown"),
                    quote=q.get("quote", ""),
                ))

            sentiment = None
            if t.get("sentiment_tendency"):
                try:
                    sentiment = Sentiment(t["sentiment_tendency"].lower())
                except (ValueError, AttributeError):
                    pass

            themes.append(Theme(
                name=t.get("name", "Unknown Theme"),
                description=t.get("description", ""),
                frequency=t.get("frequency", 1),
                percentage=t.get("percentage", 0.0),
                supporting_quotes=quotes,
                sentiment_tendency=sentiment,
            ))

        # Parse sentiment distribution
        sd = result.get("sentiment_distribution", {})
        try:
            dominant = Sentiment(sd.get("dominant", "neutral").lower())
        except (ValueError, AttributeError):
            dominant = Sentiment.NEUTRAL

        sentiment_distribution = SentimentDistribution(
            positive=sd.get("positive", 0.0),
            negative=sd.get("negative", 0.0),
            mixed=sd.get("mixed", 0.0),
            neutral=sd.get("neutral", 0.0),
            dominant=dominant,
        )

        # Parse consensus points
        consensus_points = []
        for cp in result.get("consensus_points", []):
            key_quotes = []
            for q in cp.get("key_quotes", []):
                if isinstance(q, dict):
                    key_quotes.append(QuoteReference(
                        persona_id=q.get("persona_id", "unknown"),
                        persona_name=q.get("persona_name", "Unknown"),
                        quote=q.get("quote", ""),
                    ))

            consensus_points.append(ConsensusPoint(
                statement=cp.get("statement", ""),
                agreement_rate=cp.get("agreement_rate", 0.0),
                supporting_personas=cp.get("supporting_personas", []),
                key_quotes=key_quotes if key_quotes else None,
            ))

        # Parse divergence points
        divergence_points = []
        for dp in result.get("divergence_points", []):
            positions = []
            for pos in dp.get("positions", []):
                positions.append(Position(
                    stance=pos.get("stance", ""),
                    persona_ids=pos.get("persona_ids", []),
                    rationale=pos.get("rationale", ""),
                ))

            if len(positions) >= 2:
                divergence_points.append(DivergencePoint(
                    topic=dp.get("topic", ""),
                    positions=positions,
                ))

        return AggregatedResults(
            themes=themes,
            sentiment_distribution=sentiment_distribution,
            consensus_points=consensus_points,
            divergence_points=divergence_points,
            executive_summary=result.get("executive_summary", ""),
            aggregation_confidence=result.get("aggregation_confidence", 0.0),
        )

    def _create_empty_results(self) -> AggregatedResults:
        """Create empty aggregation results.

        Returns:
            AggregatedResults with empty/default values.
        """
        return AggregatedResults(
            themes=[],
            sentiment_distribution=SentimentDistribution(
                positive=0.0,
                negative=0.0,
                mixed=0.0,
                neutral=100.0,
                dominant=Sentiment.NEUTRAL,
            ),
            consensus_points=[],
            divergence_points=[],
            executive_summary="No valid responses to aggregate.",
            aggregation_confidence=0.0,
        )
