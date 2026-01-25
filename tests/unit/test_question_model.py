"""Tests for question type models.

Validates QuestionType enum and ResearchQuestion model.
"""

import pytest
from pydantic import ValidationError

from models.question import QuestionType, ResearchQuestion


class TestQuestionType:
    """Tests for QuestionType enum."""

    def test_open_ended_value(self):
        """QuestionType has OPEN_ENDED value."""
        assert QuestionType.OPEN_ENDED == "open_ended"
        assert QuestionType.OPEN_ENDED.value == "open_ended"

    def test_rating_value(self):
        """QuestionType has RATING value."""
        assert QuestionType.RATING == "rating"
        assert QuestionType.RATING.value == "rating"

    def test_multiple_choice_value(self):
        """QuestionType has MULTIPLE_CHOICE value."""
        assert QuestionType.MULTIPLE_CHOICE == "multiple_choice"
        assert QuestionType.MULTIPLE_CHOICE.value == "multiple_choice"

    def test_all_question_types_defined(self):
        """All three question types are defined."""
        types = [qt.value for qt in QuestionType]
        assert len(types) == 3
        assert "open_ended" in types
        assert "rating" in types
        assert "multiple_choice" in types


class TestResearchQuestion:
    """Tests for ResearchQuestion Pydantic model."""

    def test_minimal_open_ended_question(self):
        """Create minimal open-ended question with just text."""
        question = ResearchQuestion(text="What do you think?")
        assert question.text == "What do you think?"
        assert question.type == QuestionType.OPEN_ENDED

    def test_explicit_question_type(self):
        """Create question with explicit type."""
        question = ResearchQuestion(text="Rate this feature", type=QuestionType.RATING)
        assert question.type == QuestionType.RATING

    def test_empty_text_rejected(self):
        """Empty question text is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ResearchQuestion(text="")
        assert "text" in str(exc_info.value).lower()

    def test_text_max_length(self):
        """Question text has maximum length of 2000 characters."""
        long_text = "x" * 2001
        with pytest.raises(ValidationError) as exc_info:
            ResearchQuestion(text=long_text)
        assert "2000" in str(exc_info.value) or "text" in str(exc_info.value).lower()

    def test_text_at_max_length(self):
        """Question text at exactly 2000 characters is valid."""
        max_text = "x" * 2000
        question = ResearchQuestion(text=max_text)
        assert len(question.text) == 2000

    def test_rating_question_default_scale(self):
        """Rating question has default 1-10 scale."""
        question = ResearchQuestion(text="Rate this", type=QuestionType.RATING)
        assert question.scale_min == 1
        assert question.scale_max == 10

    def test_rating_question_custom_scale(self):
        """Rating question accepts custom scale."""
        question = ResearchQuestion(
            text="Rate this",
            type=QuestionType.RATING,
            scale_min=1,
            scale_max=5
        )
        assert question.scale_min == 1
        assert question.scale_max == 5

    def test_rating_scale_min_less_than_max(self):
        """Rating scale min must be less than max."""
        with pytest.raises(ValidationError):
            ResearchQuestion(
                text="Rate this",
                type=QuestionType.RATING,
                scale_min=10,
                scale_max=1
            )

    def test_multiple_choice_requires_options(self):
        """Multiple choice question requires options."""
        with pytest.raises(ValidationError):
            ResearchQuestion(
                text="Choose one",
                type=QuestionType.MULTIPLE_CHOICE,
                options=None
            )

    def test_multiple_choice_minimum_options(self):
        """Multiple choice requires at least 2 options."""
        with pytest.raises(ValidationError):
            ResearchQuestion(
                text="Choose one",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["Only one"]
            )

    def test_multiple_choice_maximum_options(self):
        """Multiple choice allows maximum 10 options."""
        with pytest.raises(ValidationError):
            ResearchQuestion(
                text="Choose one",
                type=QuestionType.MULTIPLE_CHOICE,
                options=[f"Option {i}" for i in range(11)]
            )

    def test_multiple_choice_valid_options(self):
        """Multiple choice with 2-10 options is valid."""
        question = ResearchQuestion(
            text="Choose one",
            type=QuestionType.MULTIPLE_CHOICE,
            options=["A", "B", "C"]
        )
        assert question.options == ["A", "B", "C"]

    def test_open_ended_ignores_options(self):
        """Open-ended question ignores options field."""
        question = ResearchQuestion(
            text="What do you think?",
            type=QuestionType.OPEN_ENDED,
            options=["A", "B"]  # Should be ignored
        )
        assert question.type == QuestionType.OPEN_ENDED
