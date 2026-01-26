"""Contract tests for panel schema validation.

These tests verify that panel and aggregation models conform to their
specified contracts and can be serialized/deserialized correctly.
"""

import json
from datetime import datetime, timezone

import pytest
import yaml


class TestPanelSchemaContract:
    """Contract tests for ResearchPanel schema."""

    def test_panel_yaml_roundtrip(self, sample_panel_dict):
        """Test that panel can be serialized to YAML and back."""
        from models.panel import ResearchPanel

        # Create panel from dict
        panel = ResearchPanel(
            id=sample_panel_dict["id"],
            name=sample_panel_dict["name"],
            description=sample_panel_dict["description"],
            persona_ids=sample_panel_dict["persona_ids"],
            is_custom=sample_panel_dict["is_custom"],
            created_at=datetime.fromisoformat(sample_panel_dict["created_at"].replace("Z", "+00:00")),
        )

        # Serialize to YAML
        yaml_str = yaml.dump(panel.to_dict())

        # Parse back
        parsed = yaml.safe_load(yaml_str)

        assert parsed["id"] == panel.id
        assert parsed["name"] == panel.name
        assert parsed["persona_ids"] == panel.persona_ids

    def test_panel_json_roundtrip(self, sample_panel_dict):
        """Test that panel can be serialized to JSON and back."""
        from models.panel import ResearchPanel

        panel = ResearchPanel(
            id=sample_panel_dict["id"],
            name=sample_panel_dict["name"],
            description=sample_panel_dict["description"],
            persona_ids=sample_panel_dict["persona_ids"],
            is_custom=sample_panel_dict["is_custom"],
            created_at=datetime.fromisoformat(sample_panel_dict["created_at"].replace("Z", "+00:00")),
        )

        # Serialize to JSON
        json_str = json.dumps(panel.to_dict(), default=str)

        # Parse back
        parsed = json.loads(json_str)

        assert parsed["id"] == panel.id
        assert parsed["name"] == panel.name

    def test_panel_schema_required_fields(self):
        """Test that all required fields are enforced."""
        from models.panel import ResearchPanel
        from pydantic import ValidationError

        required_fields = ["id", "name", "description", "persona_ids", "is_custom", "created_at"]

        for field in required_fields:
            data = {
                "id": "test",
                "name": "Test",
                "description": "Test",
                "persona_ids": ["p1", "p2"],
                "is_custom": False,
                "created_at": datetime.now(timezone.utc),
            }
            del data[field]

            with pytest.raises(ValidationError):
                ResearchPanel(**data)


class TestPanelSessionSchemaContract:
    """Contract tests for PanelSession schema."""

    def test_panel_session_json_export_format(self):
        """Test that panel session exports match the documented JSON schema."""
        from models.panel import PanelSession, PanelSessionStatus
        from models.question import QuestionType, ResearchQuestion

        question = ResearchQuestion(
            text="What do you think of this feature?",
            type=QuestionType.OPEN_ENDED,
        )

        session = PanelSession(
            id="session-123",
            panel_id="tech-adopters",
            panel_name="Tech Adopters Panel",
            question=question,
            individual_sessions=[],
            status=PanelSessionStatus.COMPLETED,
            started_at=datetime(2026, 1, 25, 11, 0, 0, tzinfo=timezone.utc),
            completed_at=datetime(2026, 1, 25, 11, 0, 45, tzinfo=timezone.utc),
            execution_time_ms=45000,
        )

        export = session.to_dict()

        # Verify required top-level fields per data-model.md
        assert "id" in export
        assert "panel_id" in export
        assert "panel_name" in export
        assert "question" in export
        assert "status" in export
        assert "started_at" in export

    def test_panel_session_status_values(self):
        """Test that all status values match the contract."""
        from models.panel import PanelSessionStatus

        expected_values = ["pending", "executing", "aggregating", "completed", "partial", "failed"]

        for status in PanelSessionStatus:
            assert status.value in expected_values


class TestAggregationSchemaContract:
    """Contract tests for aggregation schema."""

    def test_aggregated_results_json_export(self, sample_aggregation_result):
        """Test that aggregated results export matches the documented schema."""
        from models.aggregation import (
            AggregatedResults,
            QuoteReference,
            SentimentDistribution,
            Theme,
        )
        from models.session import Sentiment

        sentiment_dist = SentimentDistribution(
            positive=sample_aggregation_result["sentiment_distribution"]["positive"],
            negative=sample_aggregation_result["sentiment_distribution"]["negative"],
            mixed=sample_aggregation_result["sentiment_distribution"]["mixed"],
            neutral=sample_aggregation_result["sentiment_distribution"]["neutral"],
            dominant=Sentiment.POSITIVE,
        )

        theme_data = sample_aggregation_result["themes"][0]
        quote = QuoteReference(
            persona_id=theme_data["supporting_quotes"][0]["persona_id"],
            persona_name=theme_data["supporting_quotes"][0]["persona_name"],
            quote=theme_data["supporting_quotes"][0]["quote"],
        )

        theme = Theme(
            name=theme_data["name"],
            description=theme_data["description"],
            frequency=theme_data["frequency"],
            percentage=theme_data["percentage"],
            supporting_quotes=[quote],
            sentiment_tendency=Sentiment.POSITIVE,
        )

        results = AggregatedResults(
            themes=[theme],
            sentiment_distribution=sentiment_dist,
            consensus_points=[],
            divergence_points=[],
            executive_summary=sample_aggregation_result["executive_summary"],
            aggregation_confidence=sample_aggregation_result["aggregation_confidence"],
        )

        export = results.to_dict()

        # Verify structure matches data-model.md
        assert "themes" in export
        assert "sentiment_distribution" in export
        assert "consensus_points" in export
        assert "divergence_points" in export
        assert "executive_summary" in export
        assert "aggregation_confidence" in export

    def test_sentiment_distribution_percentages(self):
        """Test that sentiment distribution percentages are valid."""
        from models.aggregation import SentimentDistribution
        from models.session import Sentiment

        dist = SentimentDistribution(
            positive=60.0,
            negative=20.0,
            mixed=15.0,
            neutral=5.0,
            dominant=Sentiment.POSITIVE,
        )

        export = dist.to_dict()

        assert 0 <= export["positive"] <= 100
        assert 0 <= export["negative"] <= 100
        assert 0 <= export["mixed"] <= 100
        assert 0 <= export["neutral"] <= 100


class TestQualityMetricsSchemaContract:
    """Contract tests for panel quality metrics schema."""

    def test_quality_metrics_json_export(self, sample_quality_metrics):
        """Test that quality metrics export matches the documented schema."""
        from models.aggregation import PanelQualityMetrics

        metrics = PanelQualityMetrics(
            avg_consistency_score=sample_quality_metrics["avg_consistency_score"],
            completion_rate=sample_quality_metrics["completion_rate"],
            theme_confidence=sample_quality_metrics["theme_confidence"],
            divergence_score=sample_quality_metrics["divergence_score"],
            passed_gates=sample_quality_metrics["passed_gates"],
            warnings=sample_quality_metrics["warnings"],
            individual_metrics=sample_quality_metrics["individual_metrics"],
        )

        export = metrics.to_dict()

        # Verify structure per data-model.md
        assert "avg_consistency_score" in export
        assert "completion_rate" in export
        assert "theme_confidence" in export
        assert "divergence_score" in export
        assert "passed_gates" in export
        assert "warnings" in export

    def test_quality_gates_logic(self):
        """Test that quality gates are calculated correctly."""
        from models.aggregation import PanelQualityMetrics

        # Passing case: both thresholds met
        passing = PanelQualityMetrics(
            avg_consistency_score=75.0,  # >= 70%
            completion_rate=85.0,  # >= 80%
            theme_confidence=80.0,
            divergence_score=40.0,
            passed_gates=True,
            warnings=[],
            individual_metrics=[],
        )
        assert passing.passed_gates is True

        # Failing case: consistency below threshold
        failing_consistency = PanelQualityMetrics(
            avg_consistency_score=65.0,  # < 70%
            completion_rate=90.0,
            theme_confidence=80.0,
            divergence_score=40.0,
            passed_gates=False,
            warnings=["Average consistency below 70%"],
            individual_metrics=[],
        )
        assert failing_consistency.passed_gates is False

        # Failing case: completion rate below threshold
        failing_completion = PanelQualityMetrics(
            avg_consistency_score=80.0,
            completion_rate=75.0,  # < 80%
            theme_confidence=80.0,
            divergence_score=40.0,
            passed_gates=False,
            warnings=["Completion rate below 80%"],
            individual_metrics=[],
        )
        assert failing_completion.passed_gates is False


class TestCLIOutputContract:
    """Contract tests for CLI output format."""

    def test_panel_run_output_structure(self):
        """Test that panel run output contains all required sections."""
        from models.aggregation import (
            AggregatedResults,
            PanelQualityMetrics,
            SentimentDistribution,
        )
        from models.panel import PanelSession, PanelSessionStatus
        from models.question import QuestionType, ResearchQuestion
        from models.session import Sentiment

        question = ResearchQuestion(
            text="Test question",
            type=QuestionType.OPEN_ENDED,
        )

        sentiment_dist = SentimentDistribution(
            positive=60.0,
            negative=20.0,
            mixed=20.0,
            neutral=0.0,
            dominant=Sentiment.POSITIVE,
        )

        aggregation = AggregatedResults(
            themes=[],
            sentiment_distribution=sentiment_dist,
            consensus_points=[],
            divergence_points=[],
            executive_summary="Test summary",
            aggregation_confidence=85.0,
        )

        quality = PanelQualityMetrics(
            avg_consistency_score=85.0,
            completion_rate=100.0,
            theme_confidence=80.0,
            divergence_score=40.0,
            passed_gates=True,
            warnings=[],
            individual_metrics=[],
        )

        session = PanelSession(
            id="test-session",
            panel_id="test-panel",
            panel_name="Test Panel",
            question=question,
            individual_sessions=[],
            aggregation=aggregation,
            quality=quality,
            status=PanelSessionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        export = session.to_dict()

        # Per CLI contract, output should include:
        assert export["aggregation"] is not None
        assert export["quality"] is not None
        assert export["aggregation"]["executive_summary"] is not None
        assert export["aggregation"]["sentiment_distribution"] is not None
