"""Unit tests for ResearchPanel model validation."""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError


class TestResearchPanel:
    """Tests for ResearchPanel model."""

    def test_valid_panel_creation(self):
        """Test creating a valid panel with all required fields."""
        from models.panel import ResearchPanel

        panel = ResearchPanel(
            id="tech-adopters",
            name="Technology Adopters Panel",
            description="Full spectrum of technology adoption attitudes",
            persona_ids=["persona-1", "persona-2", "persona-3"],
            is_custom=False,
            created_at=datetime.now(timezone.utc),
        )

        assert panel.id == "tech-adopters"
        assert panel.name == "Technology Adopters Panel"
        assert len(panel.persona_ids) == 3
        assert panel.is_custom is False

    def test_panel_with_optional_purpose(self):
        """Test panel with optional purpose field."""
        from models.panel import ResearchPanel

        panel = ResearchPanel(
            id="test-panel",
            name="Test Panel",
            description="A test panel",
            purpose="Testing panel functionality",
            persona_ids=["persona-1", "persona-2"],
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )

        assert panel.purpose == "Testing panel functionality"

    def test_panel_id_slug_format_validation(self):
        """Test that panel ID must be in slug format (lowercase, hyphens)."""
        from models.panel import ResearchPanel

        # Valid slug IDs
        for valid_id in ["tech-adopters", "my-panel", "panel123", "a-b-c"]:
            panel = ResearchPanel(
                id=valid_id,
                name="Test",
                description="Test",
                persona_ids=["p1", "p2"],
                is_custom=True,
                created_at=datetime.now(timezone.utc),
            )
            assert panel.id == valid_id

    def test_panel_id_invalid_format_rejected(self):
        """Test that invalid panel IDs are rejected."""
        from models.panel import ResearchPanel

        invalid_ids = ["Tech Adopters", "UPPERCASE", "has spaces", "has_underscore"]

        for invalid_id in invalid_ids:
            with pytest.raises(ValidationError):
                ResearchPanel(
                    id=invalid_id,
                    name="Test",
                    description="Test",
                    persona_ids=["p1", "p2"],
                    is_custom=True,
                    created_at=datetime.now(timezone.utc),
                )

    def test_panel_requires_minimum_two_personas(self):
        """Test that panel requires at least 2 personas."""
        from models.panel import ResearchPanel

        with pytest.raises(ValidationError) as exc_info:
            ResearchPanel(
                id="test-panel",
                name="Test",
                description="Test",
                persona_ids=["only-one"],
                is_custom=True,
                created_at=datetime.now(timezone.utc),
            )

        assert "at least 2" in str(exc_info.value).lower() or "min_length" in str(exc_info.value)

    def test_panel_maximum_fifty_personas(self):
        """Test that panel allows up to 50 personas."""
        from models.panel import ResearchPanel

        # 50 personas should be valid
        panel = ResearchPanel(
            id="large-panel",
            name="Large Panel",
            description="Test",
            persona_ids=[f"persona-{i}" for i in range(50)],
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )
        assert len(panel.persona_ids) == 50

        # 51 personas should fail
        with pytest.raises(ValidationError):
            ResearchPanel(
                id="too-large-panel",
                name="Too Large Panel",
                description="Test",
                persona_ids=[f"persona-{i}" for i in range(51)],
                is_custom=True,
                created_at=datetime.now(timezone.utc),
            )

    def test_panel_persona_ids_must_be_unique(self):
        """Test that duplicate persona IDs are rejected."""
        from models.panel import ResearchPanel

        with pytest.raises(ValidationError) as exc_info:
            ResearchPanel(
                id="test-panel",
                name="Test",
                description="Test",
                persona_ids=["persona-1", "persona-1", "persona-2"],
                is_custom=True,
                created_at=datetime.now(timezone.utc),
            )

        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()

    def test_panel_to_dict(self):
        """Test panel serialization to dictionary."""
        from models.panel import ResearchPanel

        created = datetime(2026, 1, 25, 0, 0, 0, tzinfo=timezone.utc)
        panel = ResearchPanel(
            id="test-panel",
            name="Test Panel",
            description="A test panel",
            persona_ids=["p1", "p2"],
            is_custom=False,
            created_at=created,
        )

        data = panel.to_dict()

        assert data["id"] == "test-panel"
        assert data["name"] == "Test Panel"
        assert data["description"] == "A test panel"
        assert data["persona_ids"] == ["p1", "p2"]
        assert data["is_custom"] is False


class TestPanelSessionStatus:
    """Tests for PanelSessionStatus enum."""

    def test_all_statuses_exist(self):
        """Test that all required statuses are defined."""
        from models.panel import PanelSessionStatus

        expected_statuses = ["PENDING", "EXECUTING", "AGGREGATING", "COMPLETED", "PARTIAL", "FAILED"]

        for status in expected_statuses:
            assert hasattr(PanelSessionStatus, status)

    def test_status_values(self):
        """Test status string values."""
        from models.panel import PanelSessionStatus

        assert PanelSessionStatus.PENDING.value == "pending"
        assert PanelSessionStatus.EXECUTING.value == "executing"
        assert PanelSessionStatus.AGGREGATING.value == "aggregating"
        assert PanelSessionStatus.COMPLETED.value == "completed"
        assert PanelSessionStatus.PARTIAL.value == "partial"
        assert PanelSessionStatus.FAILED.value == "failed"


class TestPanelSession:
    """Tests for PanelSession model."""

    def test_valid_panel_session_creation(self):
        """Test creating a valid panel session."""
        from models.panel import PanelSession, PanelSessionStatus
        from models.question import QuestionType, ResearchQuestion

        question = ResearchQuestion(
            text="What do you think of this feature?",
            type=QuestionType.OPEN_ENDED,
        )

        session = PanelSession(
            id="session-123",
            panel_id="tech-adopters",
            panel_name="Technology Adopters Panel",
            question=question,
            individual_sessions=[],
            status=PanelSessionStatus.PENDING,
            started_at=datetime.now(timezone.utc),
        )

        assert session.id == "session-123"
        assert session.panel_id == "tech-adopters"
        assert session.status == PanelSessionStatus.PENDING
        assert session.aggregation is None
        assert session.quality is None

    def test_panel_session_with_aggregation(self):
        """Test panel session with aggregation results."""
        from models.panel import PanelSession, PanelSessionStatus
        from models.aggregation import AggregatedResults, SentimentDistribution
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

        session = PanelSession(
            id="session-456",
            panel_id="test-panel",
            panel_name="Test Panel",
            question=question,
            individual_sessions=[],
            aggregation=aggregation,
            status=PanelSessionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        assert session.aggregation is not None
        assert session.aggregation.executive_summary == "Test summary"

    def test_panel_session_to_dict(self):
        """Test panel session serialization."""
        from models.panel import PanelSession, PanelSessionStatus
        from models.question import QuestionType, ResearchQuestion

        question = ResearchQuestion(
            text="Test question",
            type=QuestionType.OPEN_ENDED,
        )

        session = PanelSession(
            id="session-789",
            panel_id="test-panel",
            panel_name="Test Panel",
            question=question,
            individual_sessions=[],
            status=PanelSessionStatus.PENDING,
            started_at=datetime.now(timezone.utc),
        )

        data = session.to_dict()

        assert data["id"] == "session-789"
        assert data["panel_id"] == "test-panel"
        assert data["status"] == "pending"
