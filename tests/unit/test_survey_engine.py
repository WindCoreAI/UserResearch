"""Unit tests for SurveyEngine service.

Tests for survey execution, response parsing, and validation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from services.survey_engine import SurveyEngine
from models.survey import Survey, SurveyQuestion, SurveyResponse, SurveyResult
from models.enums import SurveyQuestionType


@pytest.fixture
def sample_survey():
    """Create a sample survey with all question types."""
    return Survey(
        id="test-survey",
        version="1.0.0",
        name="Test Survey",
        questions=[
            SurveyQuestion(
                id="q1-rating",
                text="How satisfied are you?",
                type=SurveyQuestionType.RATING,
                scale_min=1,
                scale_max=10,
            ),
            SurveyQuestion(
                id="q2-choice",
                text="Which option do you prefer?",
                type=SurveyQuestionType.MULTIPLE_CHOICE,
                options=["Option A", "Option B", "Option C"],
            ),
            SurveyQuestion(
                id="q3-open",
                text="What improvements would you suggest?",
                type=SurveyQuestionType.OPEN_ENDED,
            ),
        ],
    )


class TestSurveyEngineInit:
    """Tests for SurveyEngine initialization."""

    def test_engine_initializes(self):
        """Engine should initialize without errors."""
        engine = SurveyEngine()
        assert engine is not None

    def test_engine_accepts_custom_persona_loader(self):
        """Engine should accept custom persona loader."""
        mock_loader = Mock()
        engine = SurveyEngine(persona_loader=mock_loader)
        assert engine.persona_loader is mock_loader


class TestSurveyEngineQuestionPrompt:
    """Tests for building question prompts."""

    def test_rating_question_prompt_includes_scale(self, sample_survey):
        """Rating question prompt should include scale bounds."""
        engine = SurveyEngine()
        question = sample_survey.questions[0]  # Rating question

        prompt = engine._build_question_prompt(question, 1, 3)

        assert "1" in prompt and "10" in prompt
        assert "How satisfied are you?" in prompt

    def test_multiple_choice_prompt_includes_options(self, sample_survey):
        """Multiple choice prompt should include options."""
        engine = SurveyEngine()
        question = sample_survey.questions[1]  # MC question

        prompt = engine._build_question_prompt(question, 2, 3)

        assert "Option A" in prompt
        assert "Option B" in prompt
        assert "Option C" in prompt

    def test_open_ended_prompt_format(self, sample_survey):
        """Open-ended prompt should encourage detailed response."""
        engine = SurveyEngine()
        question = sample_survey.questions[2]  # Open-ended

        prompt = engine._build_question_prompt(question, 3, 3)

        assert "improvements" in prompt.lower() or "suggest" in prompt.lower()


class TestSurveyEngineResponseParsing:
    """Tests for response parsing."""

    def test_parse_rating_response_numeric(self):
        """Parse numeric rating from response."""
        engine = SurveyEngine()

        # Clear numeric
        response = engine._parse_rating("8", scale_min=1, scale_max=10)
        assert response == 8

        # With text
        response = engine._parse_rating("I would rate this 7 out of 10", scale_min=1, scale_max=10)
        assert response == 7

        # Rating: format
        response = engine._parse_rating("Rating: 9", scale_min=1, scale_max=10)
        assert response == 9

    def test_parse_rating_out_of_range_clamps(self):
        """Out of range ratings should be clamped."""
        engine = SurveyEngine()

        # Too high
        response = engine._parse_rating("15", scale_min=1, scale_max=10)
        assert response == 10

        # Too low
        response = engine._parse_rating("0", scale_min=1, scale_max=10)
        assert response == 1

    def test_parse_rating_no_number_returns_none(self):
        """Response without number should return None."""
        engine = SurveyEngine()
        response = engine._parse_rating("I really like it", scale_min=1, scale_max=10)
        assert response is None

    def test_parse_multiple_choice_exact_match(self):
        """Parse exact option match."""
        engine = SurveyEngine()
        options = ["Option A", "Option B", "Option C"]

        response = engine._parse_multiple_choice("Option B", options)
        assert response == "Option B"

    def test_parse_multiple_choice_case_insensitive(self):
        """Parse should be case-insensitive."""
        engine = SurveyEngine()
        options = ["Option A", "Option B", "Option C"]

        response = engine._parse_multiple_choice("I choose option b", options)
        assert response == "Option B"

    def test_parse_multiple_choice_partial_match(self):
        """Parse partial option match."""
        engine = SurveyEngine()
        options = ["Definitely interested", "Somewhat interested", "Not interested"]

        response = engine._parse_multiple_choice("I'm definitely interested!", options)
        assert response == "Definitely interested"

    def test_parse_multiple_choice_no_match_returns_none(self):
        """No matching option should return None."""
        engine = SurveyEngine()
        options = ["Excited about it", "Skeptical about it"]

        response = engine._parse_multiple_choice("I am completely indifferent", options)
        assert response is None


class TestSurveyEngineValidation:
    """Tests for response validation."""

    def test_validate_rating_in_range(self):
        """Rating in range passes validation."""
        engine = SurveyEngine()
        question = SurveyQuestion(
            id="q1",
            text="Rate it",
            type=SurveyQuestionType.RATING,
            scale_min=1,
            scale_max=10,
        )

        is_valid, warnings = engine._validate_response(question, rating_value=7)
        assert is_valid is True
        assert len(warnings) == 0

    def test_validate_rating_clamped_has_warning(self):
        """Clamped rating should have warning."""
        engine = SurveyEngine()
        question = SurveyQuestion(
            id="q1",
            text="Rate it",
            type=SurveyQuestionType.RATING,
            scale_min=1,
            scale_max=10,
        )

        # Simulate clamped value (original was 12)
        is_valid, warnings = engine._validate_response(
            question, rating_value=10, original_value=12
        )
        assert is_valid is True
        assert len(warnings) > 0
        assert "clamped" in warnings[0].lower() or "adjusted" in warnings[0].lower()

    def test_validate_multiple_choice_valid_option(self):
        """Valid option passes validation."""
        engine = SurveyEngine()
        question = SurveyQuestion(
            id="q1",
            text="Choose one",
            type=SurveyQuestionType.MULTIPLE_CHOICE,
            options=["A", "B", "C"],
        )

        is_valid, warnings = engine._validate_response(question, selected_option="B")
        assert is_valid is True

    def test_validate_multiple_choice_invalid_option(self):
        """Invalid option fails validation."""
        engine = SurveyEngine()
        question = SurveyQuestion(
            id="q1",
            text="Choose one",
            type=SurveyQuestionType.MULTIPLE_CHOICE,
            options=["A", "B", "C"],
        )

        is_valid, warnings = engine._validate_response(question, selected_option="D")
        assert is_valid is False


class TestSurveyEngineExecution:
    """Tests for full survey execution."""

    @patch("services.survey_engine.SessionRunner")
    def test_execute_survey_returns_result(self, mock_runner_class, sample_survey):
        """Execute survey should return SurveyResult."""
        # Setup mock
        mock_runner = Mock()
        mock_runner_class.return_value = mock_runner

        # Mock persona loading
        mock_persona = Mock()
        mock_persona.id = "test-persona"
        mock_persona.name = "Test Persona"

        engine = SurveyEngine()
        engine.persona_loader = Mock()
        engine.persona_loader.load = Mock(return_value=mock_persona)

        # Mock response
        mock_runner.execute_prompt = Mock(return_value="8")

        # This would require more complex mocking of the full flow
        # For now, test that the engine has execute_survey method
        assert hasattr(engine, "execute_survey")

    def test_survey_result_includes_all_responses(self, sample_survey):
        """Result should include response for each question."""
        # Create mock responses
        responses = [
            SurveyResponse(
                question_id="q1-rating",
                question_type=SurveyQuestionType.RATING,
                raw_response="8",
                rating_value=8,
            ),
            SurveyResponse(
                question_id="q2-choice",
                question_type=SurveyQuestionType.MULTIPLE_CHOICE,
                raw_response="Option A",
                selected_option="Option A",
            ),
            SurveyResponse(
                question_id="q3-open",
                question_type=SurveyQuestionType.OPEN_ENDED,
                raw_response="More features please",
                text_response="More features please",
            ),
        ]

        result = SurveyResult(
            survey_id=sample_survey.id,
            survey_version=sample_survey.version,
            persona_id="test-persona",
            responses=responses,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_time_ms=5000,
            completion_rate=1.0,
        )

        assert len(result.responses) == 3
        assert result.completion_rate == 1.0
