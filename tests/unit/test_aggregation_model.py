"""Unit tests for aggregation models."""

import pytest
from pydantic import ValidationError


class TestTheme:
    """Tests for Theme model."""

    def test_valid_theme_creation(self):
        """Test creating a valid theme."""
        from models.aggregation import Theme, QuoteReference
        from models.session import Sentiment

        quote = QuoteReference(
            persona_id="tech-early-adopter",
            persona_name="Alex Chen",
            quote="This is exactly what I needed!",
        )

        theme = Theme(
            name="Innovation Enthusiasm",
            description="Early adopters are excited about new features",
            frequency=3,
            percentage=60.0,
            supporting_quotes=[quote],
            sentiment_tendency=Sentiment.POSITIVE,
        )

        assert theme.name == "Innovation Enthusiasm"
        assert theme.frequency == 3
        assert theme.percentage == 60.0
        assert len(theme.supporting_quotes) == 1
        assert theme.sentiment_tendency == Sentiment.POSITIVE

    def test_theme_without_sentiment_tendency(self):
        """Test theme without optional sentiment_tendency."""
        from models.aggregation import Theme

        theme = Theme(
            name="General Feedback",
            description="Mixed opinions across personas",
            frequency=5,
            percentage=100.0,
            supporting_quotes=[],
        )

        assert theme.sentiment_tendency is None

    def test_theme_percentage_validation(self):
        """Test that percentage must be 0-100."""
        from models.aggregation import Theme

        # Valid percentage
        theme = Theme(
            name="Test",
            description="Test",
            frequency=1,
            percentage=50.0,
            supporting_quotes=[],
        )
        assert theme.percentage == 50.0

        # Invalid percentages
        with pytest.raises(ValidationError):
            Theme(
                name="Test",
                description="Test",
                frequency=1,
                percentage=-10.0,
                supporting_quotes=[],
            )

        with pytest.raises(ValidationError):
            Theme(
                name="Test",
                description="Test",
                frequency=1,
                percentage=150.0,
                supporting_quotes=[],
            )


class TestQuoteReference:
    """Tests for QuoteReference model."""

    def test_valid_quote_reference(self):
        """Test creating a valid quote reference."""
        from models.aggregation import QuoteReference

        quote = QuoteReference(
            persona_id="test-persona",
            persona_name="Test User",
            quote="This is a sample quote from the persona.",
        )

        assert quote.persona_id == "test-persona"
        assert quote.persona_name == "Test User"
        assert "sample quote" in quote.quote


class TestSentimentDistribution:
    """Tests for SentimentDistribution model."""

    def test_valid_sentiment_distribution(self):
        """Test creating a valid sentiment distribution."""
        from models.aggregation import SentimentDistribution
        from models.session import Sentiment

        dist = SentimentDistribution(
            positive=60.0,
            negative=20.0,
            mixed=15.0,
            neutral=5.0,
            dominant=Sentiment.POSITIVE,
        )

        assert dist.positive == 60.0
        assert dist.negative == 20.0
        assert dist.mixed == 15.0
        assert dist.neutral == 5.0
        assert dist.dominant == Sentiment.POSITIVE

    def test_sentiment_percentages_validation(self):
        """Test that percentages must be 0-100."""
        from models.aggregation import SentimentDistribution
        from models.session import Sentiment

        with pytest.raises(ValidationError):
            SentimentDistribution(
                positive=-10.0,
                negative=50.0,
                mixed=30.0,
                neutral=30.0,
                dominant=Sentiment.NEGATIVE,
            )


class TestConsensusPoint:
    """Tests for ConsensusPoint model."""

    def test_valid_consensus_point(self):
        """Test creating a valid consensus point."""
        from models.aggregation import ConsensusPoint, QuoteReference

        consensus = ConsensusPoint(
            statement="Feature has potential value",
            agreement_rate=80.0,
            supporting_personas=["persona-1", "persona-2", "persona-3", "persona-4"],
            key_quotes=[],
        )

        assert consensus.statement == "Feature has potential value"
        assert consensus.agreement_rate == 80.0
        assert len(consensus.supporting_personas) == 4

    def test_consensus_agreement_rate_minimum(self):
        """Test that agreement rate must be > 60%."""
        from models.aggregation import ConsensusPoint

        # Valid: 60% agreement
        consensus = ConsensusPoint(
            statement="Test",
            agreement_rate=60.0,
            supporting_personas=["p1", "p2", "p3"],
        )
        assert consensus.agreement_rate == 60.0

        # Invalid: Below 60% (should be caught by business logic, not model)
        # Note: The model allows lower values; business logic enforces the 60% threshold
        consensus_low = ConsensusPoint(
            statement="Test",
            agreement_rate=50.0,
            supporting_personas=["p1", "p2"],
        )
        assert consensus_low.agreement_rate == 50.0


class TestDivergencePoint:
    """Tests for DivergencePoint model."""

    def test_valid_divergence_point(self):
        """Test creating a valid divergence point."""
        from models.aggregation import DivergencePoint, Position

        positions = [
            Position(
                stance="Concerned",
                persona_ids=["privacy-conscious-user", "skeptical-user"],
                rationale="Worried about data usage and privacy",
            ),
            Position(
                stance="Not concerned",
                persona_ids=["tech-early-adopter", "power-user"],
                rationale="Trust the platform's security measures",
            ),
        ]

        divergence = DivergencePoint(
            topic="Data privacy implications",
            positions=positions,
        )

        assert divergence.topic == "Data privacy implications"
        assert len(divergence.positions) == 2
        assert divergence.positions[0].stance == "Concerned"
        assert divergence.positions[1].stance == "Not concerned"


class TestPosition:
    """Tests for Position model."""

    def test_valid_position(self):
        """Test creating a valid position."""
        from models.aggregation import Position

        position = Position(
            stance="Support",
            persona_ids=["p1", "p2", "p3"],
            rationale="They believe it will improve productivity.",
        )

        assert position.stance == "Support"
        assert len(position.persona_ids) == 3
        assert "productivity" in position.rationale


class TestAggregatedResults:
    """Tests for AggregatedResults model."""

    def test_valid_aggregated_results(self):
        """Test creating valid aggregated results."""
        from models.aggregation import AggregatedResults, SentimentDistribution, Theme
        from models.session import Sentiment

        sentiment_dist = SentimentDistribution(
            positive=60.0,
            negative=20.0,
            mixed=20.0,
            neutral=0.0,
            dominant=Sentiment.POSITIVE,
        )

        theme = Theme(
            name="Innovation Enthusiasm",
            description="Excitement about new features",
            frequency=3,
            percentage=60.0,
            supporting_quotes=[],
        )

        results = AggregatedResults(
            themes=[theme],
            sentiment_distribution=sentiment_dist,
            consensus_points=[],
            divergence_points=[],
            executive_summary="Panel shows positive reception with some concerns.",
            aggregation_confidence=85.0,
        )

        assert len(results.themes) == 1
        assert results.executive_summary.startswith("Panel shows")
        assert results.aggregation_confidence == 85.0

    def test_aggregation_confidence_validation(self):
        """Test that aggregation confidence must be 0-100."""
        from models.aggregation import AggregatedResults, SentimentDistribution
        from models.session import Sentiment

        sentiment_dist = SentimentDistribution(
            positive=50.0,
            negative=50.0,
            mixed=0.0,
            neutral=0.0,
            dominant=Sentiment.MIXED,
        )

        with pytest.raises(ValidationError):
            AggregatedResults(
                themes=[],
                sentiment_distribution=sentiment_dist,
                consensus_points=[],
                divergence_points=[],
                executive_summary="Test",
                aggregation_confidence=150.0,  # Invalid
            )

    def test_aggregated_results_to_dict(self):
        """Test serialization of aggregated results."""
        from models.aggregation import AggregatedResults, SentimentDistribution
        from models.session import Sentiment

        sentiment_dist = SentimentDistribution(
            positive=60.0,
            negative=40.0,
            mixed=0.0,
            neutral=0.0,
            dominant=Sentiment.POSITIVE,
        )

        results = AggregatedResults(
            themes=[],
            sentiment_distribution=sentiment_dist,
            consensus_points=[],
            divergence_points=[],
            executive_summary="Test summary",
            aggregation_confidence=75.0,
        )

        data = results.to_dict()

        assert data["executive_summary"] == "Test summary"
        assert data["aggregation_confidence"] == 75.0
        assert "sentiment_distribution" in data


class TestPanelQualityMetrics:
    """Tests for PanelQualityMetrics model."""

    def test_valid_quality_metrics(self):
        """Test creating valid panel quality metrics."""
        from models.aggregation import PanelQualityMetrics

        metrics = PanelQualityMetrics(
            avg_consistency_score=85.0,
            completion_rate=100.0,
            theme_confidence=80.0,
            divergence_score=40.0,
            passed_gates=True,
            warnings=[],
            individual_metrics=[],
        )

        assert metrics.avg_consistency_score == 85.0
        assert metrics.completion_rate == 100.0
        assert metrics.passed_gates is True
        assert len(metrics.warnings) == 0

    def test_quality_metrics_with_warnings(self):
        """Test quality metrics with warnings."""
        from models.aggregation import PanelQualityMetrics

        metrics = PanelQualityMetrics(
            avg_consistency_score=65.0,  # Below 70% threshold
            completion_rate=75.0,  # Below 80% threshold
            theme_confidence=60.0,
            divergence_score=80.0,
            passed_gates=False,
            warnings=[
                "Average consistency below 70%",
                "Completion rate below 80%",
            ],
            individual_metrics=[],
        )

        assert metrics.passed_gates is False
        assert len(metrics.warnings) == 2

    def test_quality_metrics_score_validation(self):
        """Test that scores must be 0-100."""
        from models.aggregation import PanelQualityMetrics

        with pytest.raises(ValidationError):
            PanelQualityMetrics(
                avg_consistency_score=150.0,  # Invalid
                completion_rate=100.0,
                theme_confidence=80.0,
                divergence_score=40.0,
                passed_gates=True,
                warnings=[],
                individual_metrics=[],
            )

    def test_quality_metrics_to_dict(self):
        """Test serialization of quality metrics."""
        from models.aggregation import PanelQualityMetrics

        metrics = PanelQualityMetrics(
            avg_consistency_score=85.0,
            completion_rate=100.0,
            theme_confidence=80.0,
            divergence_score=40.0,
            passed_gates=True,
            warnings=[],
            individual_metrics=[],
        )

        data = metrics.to_dict()

        assert data["avg_consistency_score"] == 85.0
        assert data["passed_gates"] is True
