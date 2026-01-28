"""Unit tests for Survey models.

Tests for Survey, SurveyQuestion, SurveyResponse, and SurveyResult models.
"""

import pytest
from datetime import datetime

from models.survey import (
    Survey,
    SurveyQuestion,
    SurveyResponse,
    SurveyResult,
    RatingStatistics,
    MultipleChoiceStatistics,
    SurveyAggregation,
)
from models.enums import SurveyQuestionType


class TestSurveyQuestion:
    """Tests for SurveyQuestion model."""

    def test_rating_question_requires_scale_bounds(self):
        """Rating questions must have scale_min and scale_max."""
        with pytest.raises(ValueError) as exc_info:
            SurveyQuestion(
                id="q1",
                text="How satisfied are you?",
                type=SurveyQuestionType.RATING,
            )
        assert "scale_min" in str(exc_info.value) or "scale_max" in str(exc_info.value)

    def test_rating_question_valid(self):
        """Rating question with valid scale bounds."""
        q = SurveyQuestion(
            id="q1",
            text="Rate your experience",
            type=SurveyQuestionType.RATING,
            scale_min=1,
            scale_max=10,
        )
        assert q.scale_min == 1
        assert q.scale_max == 10
        assert q.type == SurveyQuestionType.RATING

    def test_rating_question_scale_min_must_be_less_than_max(self):
        """scale_min must be less than scale_max."""
        with pytest.raises(ValueError) as exc_info:
            SurveyQuestion(
                id="q1",
                text="Rate your experience",
                type=SurveyQuestionType.RATING,
                scale_min=10,
                scale_max=1,
            )
        assert "scale_min must be less than scale_max" in str(exc_info.value)

    def test_multiple_choice_requires_options(self):
        """Multiple choice questions must have options."""
        with pytest.raises(ValueError) as exc_info:
            SurveyQuestion(
                id="q1",
                text="Which option do you prefer?",
                type=SurveyQuestionType.MULTIPLE_CHOICE,
            )
        assert "options" in str(exc_info.value)

    def test_multiple_choice_valid(self):
        """Multiple choice question with valid options."""
        q = SurveyQuestion(
            id="q1",
            text="Which option do you prefer?",
            type=SurveyQuestionType.MULTIPLE_CHOICE,
            options=["Option A", "Option B", "Option C"],
        )
        assert len(q.options) == 3
        assert q.type == SurveyQuestionType.MULTIPLE_CHOICE

    def test_open_ended_no_special_requirements(self):
        """Open-ended questions have no special requirements."""
        q = SurveyQuestion(
            id="q1",
            text="What are your thoughts?",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        assert q.type == SurveyQuestionType.OPEN_ENDED
        assert q.scale_min is None
        assert q.scale_max is None
        assert q.options is None

    def test_question_id_must_be_kebab_case(self):
        """Question ID must be kebab-case."""
        # Valid
        q = SurveyQuestion(
            id="my-question-1",
            text="Test",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        assert q.id == "my-question-1"

        # Invalid - uppercase
        with pytest.raises(ValueError):
            SurveyQuestion(
                id="MyQuestion",
                text="Test",
                type=SurveyQuestionType.OPEN_ENDED,
            )

    def test_question_required_defaults_true(self):
        """Questions are required by default."""
        q = SurveyQuestion(
            id="q1",
            text="Test",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        assert q.required is True

    def test_rating_question_with_scale_labels(self):
        """Rating question can have scale labels."""
        q = SurveyQuestion(
            id="q1",
            text="Rate your experience",
            type=SurveyQuestionType.RATING,
            scale_min=1,
            scale_max=5,
            scale_labels={1: "Poor", 3: "Average", 5: "Excellent"},
        )
        assert q.scale_labels[1] == "Poor"
        assert q.scale_labels[5] == "Excellent"


class TestSurvey:
    """Tests for Survey model."""

    def test_survey_requires_at_least_one_question(self):
        """Survey must have at least one question."""
        with pytest.raises(ValueError):
            Survey(
                id="test-survey",
                version="1.0.0",
                name="Test Survey",
                questions=[],
            )

    def test_survey_question_ids_must_be_unique(self):
        """Question IDs must be unique within a survey."""
        q1 = SurveyQuestion(
            id="same-id",
            text="Question 1",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        q2 = SurveyQuestion(
            id="same-id",
            text="Question 2",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        with pytest.raises(ValueError) as exc_info:
            Survey(
                id="test-survey",
                version="1.0.0",
                name="Test Survey",
                questions=[q1, q2],
            )
        assert "unique" in str(exc_info.value).lower()

    def test_survey_valid_creation(self):
        """Survey with valid questions."""
        q1 = SurveyQuestion(
            id="q1",
            text="Rate your experience",
            type=SurveyQuestionType.RATING,
            scale_min=1,
            scale_max=10,
        )
        q2 = SurveyQuestion(
            id="q2",
            text="What do you think?",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        survey = Survey(
            id="test-survey",
            version="1.0.0",
            name="Test Survey",
            questions=[q1, q2],
        )
        assert survey.id == "test-survey"
        assert len(survey.questions) == 2

    def test_survey_id_must_be_kebab_case(self):
        """Survey ID must be kebab-case."""
        q = SurveyQuestion(
            id="q1",
            text="Test",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        with pytest.raises(ValueError):
            Survey(
                id="TestSurvey",
                version="1.0.0",
                name="Test",
                questions=[q],
            )

    def test_survey_version_must_be_semver(self):
        """Survey version must be semver format."""
        q = SurveyQuestion(
            id="q1",
            text="Test",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        with pytest.raises(ValueError):
            Survey(
                id="test-survey",
                version="1.0",
                name="Test",
                questions=[q],
            )


class TestSurveyResponse:
    """Tests for SurveyResponse model."""

    def test_rating_response(self):
        """Response for a rating question."""
        response = SurveyResponse(
            question_id="q1",
            question_type=SurveyQuestionType.RATING,
            raw_response="I would give it an 8 out of 10",
            rating_value=8,
            is_valid=True,
        )
        assert response.rating_value == 8
        assert response.is_valid is True

    def test_multiple_choice_response(self):
        """Response for a multiple choice question."""
        response = SurveyResponse(
            question_id="q1",
            question_type=SurveyQuestionType.MULTIPLE_CHOICE,
            raw_response="I choose Option B",
            selected_option="Option B",
            is_valid=True,
        )
        assert response.selected_option == "Option B"

    def test_open_ended_response(self):
        """Response for an open-ended question."""
        response = SurveyResponse(
            question_id="q1",
            question_type=SurveyQuestionType.OPEN_ENDED,
            raw_response="This is my detailed feedback...",
            text_response="This is my detailed feedback...",
            is_valid=True,
        )
        assert response.text_response == "This is my detailed feedback..."

    def test_response_with_validation_warnings(self):
        """Response can have validation warnings."""
        response = SurveyResponse(
            question_id="q1",
            question_type=SurveyQuestionType.RATING,
            raw_response="I give it a solid 11",
            rating_value=10,
            is_valid=True,
            validation_warnings=["Value was clamped from 11 to 10"],
        )
        assert len(response.validation_warnings) == 1


class TestSurveyResult:
    """Tests for SurveyResult model."""

    def test_survey_result_creation(self):
        """SurveyResult with responses."""
        responses = [
            SurveyResponse(
                question_id="q1",
                question_type=SurveyQuestionType.RATING,
                raw_response="8",
                rating_value=8,
            ),
            SurveyResponse(
                question_id="q2",
                question_type=SurveyQuestionType.OPEN_ENDED,
                raw_response="Great product",
                text_response="Great product",
            ),
        ]
        result = SurveyResult(
            survey_id="test-survey",
            survey_version="1.0.0",
            persona_id="test-persona",
            responses=responses,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_time_ms=5000,
            completion_rate=1.0,
        )
        assert result.survey_id == "test-survey"
        assert len(result.responses) == 2
        assert result.completion_rate == 1.0


class TestRatingStatistics:
    """Tests for RatingStatistics model."""

    def test_rating_statistics(self):
        """RatingStatistics aggregation."""
        stats = RatingStatistics(
            question_id="q1",
            count=5,
            mean=7.4,
            median=8.0,
            stdev=1.2,
            min_value=5,
            max_value=10,
            distribution={5: 1, 7: 1, 8: 2, 10: 1},
        )
        assert stats.mean == 7.4
        assert stats.median == 8.0
        assert stats.count == 5


class TestMultipleChoiceStatistics:
    """Tests for MultipleChoiceStatistics model."""

    def test_multiple_choice_statistics(self):
        """MultipleChoiceStatistics aggregation."""
        stats = MultipleChoiceStatistics(
            question_id="q1",
            count=10,
            selection_counts={"Option A": 5, "Option B": 3, "Option C": 2},
            selection_percentages={"Option A": 50.0, "Option B": 30.0, "Option C": 20.0},
        )
        assert stats.selection_counts["Option A"] == 5
        assert stats.selection_percentages["Option A"] == 50.0


class TestSurveyAggregation:
    """Tests for SurveyAggregation model."""

    def test_survey_aggregation(self):
        """SurveyAggregation with statistics."""
        rating_stats = RatingStatistics(
            question_id="q1",
            count=5,
            mean=7.4,
            median=8.0,
            stdev=1.2,
            min_value=5,
            max_value=10,
            distribution={5: 1, 7: 1, 8: 2, 10: 1},
        )
        mc_stats = MultipleChoiceStatistics(
            question_id="q2",
            count=5,
            selection_counts={"A": 2, "B": 3},
            selection_percentages={"A": 40.0, "B": 60.0},
        )
        aggregation = SurveyAggregation(
            survey_id="test-survey",
            panel_id="test-panel",
            total_respondents=5,
            rating_statistics=[rating_stats],
            multiple_choice_statistics=[mc_stats],
        )
        assert aggregation.total_respondents == 5
        assert len(aggregation.rating_statistics) == 1
        assert len(aggregation.multiple_choice_statistics) == 1
