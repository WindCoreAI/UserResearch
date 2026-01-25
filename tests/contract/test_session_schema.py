"""Contract tests for research session schema.

These tests ensure the session JSON export schema remains stable and
validates according to the documented requirements in data-model.md.
"""

import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models.question import QuestionType, ResearchQuestion
from models.session import (
    ResearchSession,
    SessionResponse,
    SessionStatus,
)


class TestResearchSessionSchema:
    """Contract tests for ResearchSession model."""

    def test_minimal_session_creation(self):
        """Create a minimal research session with required fields."""
        session = ResearchSession(
            id="test-session-001",
            persona_id="tech-early-adopter",
            persona_name="Alex Chen",
            question=ResearchQuestion(text="What do you think?"),
            status=SessionStatus.PENDING,
            started_at=datetime.now(timezone.utc),
        )

        assert session.id == "test-session-001"
        assert session.persona_id == "tech-early-adopter"
        assert session.persona_name == "Alex Chen"
        assert session.status == SessionStatus.PENDING
        assert session.response is None
        assert session.completed_at is None

    def test_session_with_response(self):
        """Session can include a response when completed."""
        session = ResearchSession(
            id="test-session-002",
            persona_id="tech-early-adopter",
            persona_name="Alex Chen",
            question=ResearchQuestion(text="What do you think?"),
            status=SessionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            response=SessionResponse(
                raw_text="This is my response as Alex.",
                response_time_ms=1500,
            ),
        )

        assert session.status == SessionStatus.COMPLETED
        assert session.response is not None
        assert session.response.raw_text == "This is my response as Alex."
        assert session.response.response_time_ms == 1500

    def test_session_uuid_format(self):
        """Session ID should be a valid string identifier."""
        # UUID format
        session = ResearchSession(
            id="550e8400-e29b-41d4-a716-446655440000",
            persona_id="test-persona",
            persona_name="Test User",
            question=ResearchQuestion(text="Question"),
            status=SessionStatus.PENDING,
            started_at=datetime.now(timezone.utc),
        )
        assert "-" in session.id

    def test_session_json_export(self):
        """Session can be exported to JSON format."""
        session = ResearchSession(
            id="test-session-003",
            persona_id="tech-early-adopter",
            persona_name="Alex Chen",
            question=ResearchQuestion(text="What features do you want?"),
            status=SessionStatus.COMPLETED,
            started_at=datetime(2026, 1, 25, 10, 30, 0, tzinfo=timezone.utc),
            completed_at=datetime(2026, 1, 25, 10, 30, 15, tzinfo=timezone.utc),
            response=SessionResponse(
                raw_text="I would like more automation features.",
                response_time_ms=15000,
            ),
            metadata={
                "platform_version": "0.2.0",
                "model_used": "sonnet",
            },
        )

        json_output = session.model_dump_json()
        parsed = json.loads(json_output)

        assert parsed["id"] == "test-session-003"
        assert parsed["persona_id"] == "tech-early-adopter"
        assert parsed["status"] == "completed"
        assert "response" in parsed
        assert parsed["response"]["response_time_ms"] == 15000

    def test_session_metadata_optional(self):
        """Session metadata is optional."""
        session = ResearchSession(
            id="test-session-004",
            persona_id="test-persona",
            persona_name="Test User",
            question=ResearchQuestion(text="Question"),
            status=SessionStatus.PENDING,
            started_at=datetime.now(timezone.utc),
        )

        assert session.metadata is None

    def test_session_with_metadata(self):
        """Session can include metadata."""
        session = ResearchSession(
            id="test-session-005",
            persona_id="test-persona",
            persona_name="Test User",
            question=ResearchQuestion(text="Question"),
            status=SessionStatus.PENDING,
            started_at=datetime.now(timezone.utc),
            metadata={
                "platform_version": "0.2.0",
                "persona_version": "1.0.0",
                "model_used": "sonnet",
                "limitations_acknowledged": True,
            },
        )

        assert session.metadata["platform_version"] == "0.2.0"
        assert session.metadata["limitations_acknowledged"] is True


class TestSessionResponseSchema:
    """Contract tests for SessionResponse model."""

    def test_minimal_response(self):
        """Create minimal response with required fields only."""
        response = SessionResponse(
            raw_text="This is the raw response text.",
            response_time_ms=1000,
        )

        assert response.raw_text == "This is the raw response text."
        assert response.response_time_ms == 1000
        assert response.parsed is None
        assert response.quality is None

    def test_response_time_must_be_positive(self):
        """Response time must be non-negative."""
        # Zero is valid
        response = SessionResponse(raw_text="Test", response_time_ms=0)
        assert response.response_time_ms == 0

        # Positive is valid
        response = SessionResponse(raw_text="Test", response_time_ms=5000)
        assert response.response_time_ms == 5000

        # Negative should be rejected
        with pytest.raises(ValidationError):
            SessionResponse(raw_text="Test", response_time_ms=-100)

    def test_response_raw_text_required(self):
        """Response must have raw text."""
        with pytest.raises(ValidationError):
            SessionResponse(response_time_ms=1000)

    def test_response_parse_errors_optional(self):
        """Parse errors list is optional."""
        response = SessionResponse(
            raw_text="Some text",
            response_time_ms=500,
            parse_errors=["Failed to extract sentiment"],
        )

        assert response.parse_errors == ["Failed to extract sentiment"]
