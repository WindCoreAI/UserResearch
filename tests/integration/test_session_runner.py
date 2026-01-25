"""Integration tests for session runner.

Tests the SessionRunner class with mock subagent execution.
"""

from unittest.mock import MagicMock, patch

import pytest

from models.persona import Persona
from models.question import QuestionType, ResearchQuestion
from models.session import SessionStatus


def _make_test_persona(
    persona_id: str = "test-persona",
    name: str = "Test User",
) -> Persona:
    """Create a test persona for testing."""
    return Persona(
        id=persona_id,
        version="1.0.0",
        name=name,
        demographics={
            "age": 30,
            "gender": "non-binary",
            "location": "New York, NY",
            "occupation": {"title": "Software Engineer"},
        },
        psychological_profile={
            "big_five": {
                "openness": 7,
                "conscientiousness": 6,
                "extraversion": 5,
                "agreeableness": 6,
                "neuroticism": 4,
            },
            "schwartz_values": {"primary": ["self_direction", "achievement"]},
            "tech_adoption": "early_adopter",
        },
        background={
            "life_stage": "Mid-career",
            "pain_points": ["Too many tools"],
            "goals": ["Improve productivity"],
        },
        response_calibration={
            "verbosity": "moderate",
            "emotional_expressiveness": "moderate",
            "criticism_tendency": "balanced",
        },
    )


class TestSessionRunner:
    """Tests for SessionRunner class."""

    def test_session_runner_initialization(self):
        """SessionRunner can be instantiated."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        assert runner is not None

    def test_build_prompt_includes_persona(self):
        """build_prompt() includes persona information."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        question = ResearchQuestion(text="What do you think of this feature?")
        persona = _make_test_persona(persona_id="tech-early-adopter", name="Alex Chen")

        prompt = runner.build_prompt(persona, question)

        assert "Alex Chen" in prompt
        assert "What do you think of this feature?" in prompt

    def test_build_prompt_includes_question(self):
        """build_prompt() includes the research question."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        question = ResearchQuestion(
            text="Rate this product from 1-10",
            type=QuestionType.RATING,
        )
        persona = _make_test_persona()

        prompt = runner.build_prompt(persona, question)

        assert "Rate this product from 1-10" in prompt

    def test_build_prompt_includes_response_format(self):
        """build_prompt() includes structured response format instructions."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        question = ResearchQuestion(text="Test question")
        persona = _make_test_persona()

        prompt = runner.build_prompt(persona, question)

        # Should include response format instructions
        assert "OVERALL_IMPRESSION" in prompt or "Response Format" in prompt

    def test_create_session_returns_pending_session(self):
        """create_session() returns a session in PENDING status."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        question = ResearchQuestion(text="Test question")

        mock_persona = MagicMock()
        mock_persona.id = "tech-early-adopter"
        mock_persona.name = "Alex Chen"

        session = runner.create_session(mock_persona, question)

        assert session.status == SessionStatus.PENDING
        assert session.persona_id == "tech-early-adopter"
        assert session.persona_name == "Alex Chen"
        assert session.question.text == "Test question"
        assert session.started_at is not None
        assert session.response is None

    def test_session_has_unique_id(self):
        """Each session should have a unique ID."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        question = ResearchQuestion(text="Test question")

        mock_persona = MagicMock()
        mock_persona.id = "test-persona"
        mock_persona.name = "Test User"

        session1 = runner.create_session(mock_persona, question)
        session2 = runner.create_session(mock_persona, question)

        assert session1.id != session2.id

    def test_execute_returns_task_specification(self):
        """execute() returns a task specification for Claude Code subagent."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        question = ResearchQuestion(text="What do you think?")

        mock_persona = MagicMock()
        mock_persona.id = "tech-early-adopter"
        mock_persona.name = "Alex Chen"

        session = runner.create_session(mock_persona, question)
        task_spec = runner.get_task_specification(session)

        # Task specification should include the prompt
        assert "prompt" in task_spec
        assert isinstance(task_spec["prompt"], str)

    def test_process_response_updates_session(self):
        """process_response() updates session with response data."""
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        question = ResearchQuestion(text="Test question")

        mock_persona = MagicMock()
        mock_persona.id = "test-persona"
        mock_persona.name = "Test User"

        session = runner.create_session(mock_persona, question)

        raw_response = "OVERALL_IMPRESSION: Great feature!\nSENTIMENT: positive"
        response_time_ms = 2500

        updated_session = runner.process_response(session, raw_response, response_time_ms)

        assert updated_session.status == SessionStatus.COMPLETED
        assert updated_session.response is not None
        assert updated_session.response.raw_text == raw_response
        assert updated_session.response.response_time_ms == response_time_ms
        assert updated_session.completed_at is not None
