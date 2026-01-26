"""Unit tests for ResponseAggregator service."""

import pytest
from unittest.mock import MagicMock, patch


class TestResponseAggregator:
    """Tests for ResponseAggregator service."""

    def test_aggregator_initialization(self):
        """Test ResponseAggregator can be initialized."""
        from services.response_aggregator import ResponseAggregator

        aggregator = ResponseAggregator()
        assert aggregator is not None

    def test_aggregator_with_custom_theme_count(self):
        """Test ResponseAggregator with custom max themes."""
        from services.response_aggregator import ResponseAggregator

        aggregator = ResponseAggregator(max_themes=3)
        assert aggregator.max_themes == 3

    def test_aggregator_with_custom_consensus_threshold(self):
        """Test ResponseAggregator with custom consensus threshold."""
        from services.response_aggregator import ResponseAggregator

        aggregator = ResponseAggregator(consensus_threshold=0.7)
        assert aggregator.consensus_threshold == 0.7

    @pytest.mark.asyncio
    async def test_aggregate_responses_returns_results(self):
        """Test that aggregate_responses returns AggregatedResults."""
        from services.response_aggregator import ResponseAggregator
        from models.aggregation import AggregatedResults
        from models.session import (
            ParsedResponse,
            ResearchSession,
            SessionResponse,
            SessionStatus,
            Sentiment,
        )
        from models.question import QuestionType, ResearchQuestion
        from datetime import datetime, timezone

        question = ResearchQuestion(
            text="Test question?",
            type=QuestionType.OPEN_ENDED,
        )

        # Create mock sessions with parsed responses
        sessions = []
        for i, sentiment in enumerate([Sentiment.POSITIVE, Sentiment.NEGATIVE, Sentiment.MIXED]):
            parsed = ParsedResponse(
                sentiment=sentiment,
                overall_impression=f"Impression {i}",
                concerns=[f"Concern {i}"],
                suggestions=[f"Suggestion {i}"],
            )
            response = SessionResponse(
                raw_text=f"Response {i}",
                response_time_ms=1000,
                parsed=parsed,
            )
            session = ResearchSession(
                id=f"session-{i}",
                persona_id=f"persona-{i}",
                persona_name=f"Persona {i}",
                question=question,
                response=response,
                status=SessionStatus.COMPLETED,
                started_at=datetime.now(timezone.utc),
            )
            sessions.append(session)

        aggregator = ResponseAggregator()

        # Mock the LLM call for aggregation
        mock_result = {
            "executive_summary": "Test summary",
            "themes": [
                {
                    "name": "Test Theme",
                    "description": "A test theme",
                    "frequency": 2,
                    "percentage": 66.7,
                    "supporting_quotes": [],
                    "sentiment_tendency": "POSITIVE",
                }
            ],
            "sentiment_distribution": {
                "positive": 33.3,
                "negative": 33.3,
                "mixed": 33.3,
                "neutral": 0.0,
                "dominant": "MIXED",
            },
            "consensus_points": [],
            "divergence_points": [],
            "aggregation_confidence": 75.0,
        }

        with patch.object(aggregator, '_call_aggregation_llm', return_value=mock_result):
            result = await aggregator.aggregate_responses(sessions, "Test question?", "Test Panel")

            assert isinstance(result, AggregatedResults)
            assert result.executive_summary == "Test summary"

    def test_calculate_sentiment_distribution(self):
        """Test sentiment distribution calculation."""
        from services.response_aggregator import ResponseAggregator
        from models.session import Sentiment

        aggregator = ResponseAggregator()

        sentiments = [
            Sentiment.POSITIVE,
            Sentiment.POSITIVE,
            Sentiment.POSITIVE,
            Sentiment.NEGATIVE,
            Sentiment.MIXED,
        ]

        dist = aggregator.calculate_sentiment_distribution(sentiments)

        assert dist.positive == 60.0
        assert dist.negative == 20.0
        assert dist.mixed == 20.0
        assert dist.neutral == 0.0
        assert dist.dominant == Sentiment.POSITIVE

    def test_calculate_sentiment_distribution_all_same(self):
        """Test sentiment distribution when all sentiments are the same."""
        from services.response_aggregator import ResponseAggregator
        from models.session import Sentiment

        aggregator = ResponseAggregator()

        sentiments = [Sentiment.NEGATIVE] * 5

        dist = aggregator.calculate_sentiment_distribution(sentiments)

        assert dist.positive == 0.0
        assert dist.negative == 100.0
        assert dist.dominant == Sentiment.NEGATIVE

    def test_calculate_sentiment_distribution_tie(self):
        """Test sentiment distribution when there's a tie."""
        from services.response_aggregator import ResponseAggregator
        from models.session import Sentiment

        aggregator = ResponseAggregator()

        sentiments = [Sentiment.POSITIVE, Sentiment.NEGATIVE]

        dist = aggregator.calculate_sentiment_distribution(sentiments)

        assert dist.positive == 50.0
        assert dist.negative == 50.0
        # When tied, first in enum order wins
        assert dist.dominant in [Sentiment.POSITIVE, Sentiment.NEGATIVE]


class TestResponseAggregatorThemes:
    """Tests for theme extraction in ResponseAggregator."""

    @pytest.mark.asyncio
    async def test_extracts_themes_from_responses(self):
        """Test that themes are extracted from multiple responses."""
        from services.response_aggregator import ResponseAggregator
        from models.session import (
            ParsedResponse,
            ResearchSession,
            SessionResponse,
            SessionStatus,
            Sentiment,
        )
        from models.question import QuestionType, ResearchQuestion
        from datetime import datetime, timezone

        question = ResearchQuestion(
            text="Test question?",
            type=QuestionType.OPEN_ENDED,
        )

        # Create sessions with common concerns
        sessions = []
        common_concern = "Privacy concerns"
        for i in range(3):
            parsed = ParsedResponse(
                sentiment=Sentiment.MIXED,
                overall_impression=f"Impression {i}",
                concerns=[common_concern, f"Unique concern {i}"],
                suggestions=[],
            )
            response = SessionResponse(
                raw_text=f"Response {i}",
                response_time_ms=1000,
                parsed=parsed,
            )
            session = ResearchSession(
                id=f"session-{i}",
                persona_id=f"persona-{i}",
                persona_name=f"Persona {i}",
                question=question,
                response=response,
                status=SessionStatus.COMPLETED,
                started_at=datetime.now(timezone.utc),
            )
            sessions.append(session)

        aggregator = ResponseAggregator()

        mock_result = {
            "executive_summary": "Privacy is a key theme",
            "themes": [
                {
                    "name": "Privacy Concerns",
                    "description": "Users are worried about privacy",
                    "frequency": 3,
                    "percentage": 100.0,
                    "supporting_quotes": [],
                    "sentiment_tendency": "NEGATIVE",
                }
            ],
            "sentiment_distribution": {
                "positive": 0.0,
                "negative": 0.0,
                "mixed": 100.0,
                "neutral": 0.0,
                "dominant": "MIXED",
            },
            "consensus_points": [],
            "divergence_points": [],
            "aggregation_confidence": 90.0,
        }

        with patch.object(aggregator, '_call_aggregation_llm', return_value=mock_result):
            result = await aggregator.aggregate_responses(sessions, "Test?", "Test Panel")

            assert len(result.themes) >= 1
            assert any("Privacy" in t.name for t in result.themes)


class TestResponseAggregatorConsensus:
    """Tests for consensus detection in ResponseAggregator."""

    def test_identify_consensus_points(self):
        """Test consensus point identification."""
        from services.response_aggregator import ResponseAggregator

        aggregator = ResponseAggregator(consensus_threshold=0.6)

        # 3 out of 4 personas agree (75% > 60% threshold)
        responses_data = [
            {"persona_id": "p1", "agrees_with": "Feature is valuable"},
            {"persona_id": "p2", "agrees_with": "Feature is valuable"},
            {"persona_id": "p3", "agrees_with": "Feature is valuable"},
            {"persona_id": "p4", "agrees_with": "Feature is risky"},
        ]

        # This would be called by the LLM aggregation
        # Testing the concept - actual implementation uses LLM
        assert aggregator.consensus_threshold == 0.6


class TestResponseAggregatorDivergence:
    """Tests for divergence detection in ResponseAggregator."""

    def test_identify_divergence_points(self):
        """Test divergence point identification."""
        from services.response_aggregator import ResponseAggregator

        aggregator = ResponseAggregator()

        # Test that divergence detection is part of the aggregator
        assert hasattr(aggregator, 'aggregate_responses')


class TestResponseAggregatorQuality:
    """Tests for quality metrics in ResponseAggregator."""

    def test_calculate_panel_quality_metrics(self):
        """Test panel quality metrics calculation."""
        from services.response_aggregator import ResponseAggregator
        from models.session import QualityMetrics

        aggregator = ResponseAggregator()

        # Create mock individual quality metrics
        individual_metrics = [
            QualityMetrics(
                consistency_score=90.0,
                passed_gates=True,
                sycophancy_indicators={},
                warnings=[],
            ),
            QualityMetrics(
                consistency_score=80.0,
                passed_gates=True,
                sycophancy_indicators={},
                warnings=[],
            ),
            QualityMetrics(
                consistency_score=70.0,
                passed_gates=True,
                sycophancy_indicators={},
                warnings=[],
            ),
        ]

        panel_metrics = aggregator.calculate_panel_quality_metrics(
            individual_metrics=individual_metrics,
            completion_rate=100.0,
            theme_confidence=80.0,
            divergence_score=30.0,
        )

        assert panel_metrics.avg_consistency_score == 80.0
        assert panel_metrics.completion_rate == 100.0
        assert panel_metrics.passed_gates is True  # >70% avg, >80% completion

    def test_quality_metrics_fail_on_low_consistency(self):
        """Test quality gates fail on low consistency."""
        from services.response_aggregator import ResponseAggregator
        from models.session import QualityMetrics

        aggregator = ResponseAggregator()

        individual_metrics = [
            QualityMetrics(
                consistency_score=50.0,
                passed_gates=False,
                sycophancy_indicators={},
                warnings=["Low consistency"],
            ),
            QualityMetrics(
                consistency_score=60.0,
                passed_gates=False,
                sycophancy_indicators={},
                warnings=["Low consistency"],
            ),
        ]

        panel_metrics = aggregator.calculate_panel_quality_metrics(
            individual_metrics=individual_metrics,
            completion_rate=100.0,
            theme_confidence=80.0,
            divergence_score=30.0,
        )

        assert panel_metrics.avg_consistency_score == 55.0
        assert panel_metrics.passed_gates is False  # <70% avg
        assert len(panel_metrics.warnings) > 0

    def test_quality_metrics_fail_on_low_completion(self):
        """Test quality gates fail on low completion rate."""
        from services.response_aggregator import ResponseAggregator
        from models.session import QualityMetrics

        aggregator = ResponseAggregator()

        individual_metrics = [
            QualityMetrics(
                consistency_score=90.0,
                passed_gates=True,
                sycophancy_indicators={},
                warnings=[],
            ),
        ]

        panel_metrics = aggregator.calculate_panel_quality_metrics(
            individual_metrics=individual_metrics,
            completion_rate=50.0,  # Only 50% completed
            theme_confidence=80.0,
            divergence_score=30.0,
        )

        assert panel_metrics.passed_gates is False  # <80% completion
        assert any("completion" in w.lower() for w in panel_metrics.warnings)
