"""Unit tests for ResearchProtocol model.

Tests for protocol model validation, serialization, and type discrimination.
"""

import pytest
from datetime import datetime

from models.protocol import (
    ResearchProtocol,
    SurveyProtocol,
    InterviewProtocol,
    FocusGroupProtocol,
)
from models.enums import ResearchMethodType


class TestResearchProtocol:
    """Tests for base ResearchProtocol model."""

    def test_protocol_requires_id(self):
        """Protocol must have an id."""
        with pytest.raises(ValueError):
            ResearchProtocol(
                id="",
                version="1.0.0",
                type=ResearchMethodType.SURVEY,
                name="Test Protocol",
            )

    def test_protocol_id_must_be_kebab_case(self):
        """Protocol ID must be kebab-case format."""
        # Valid kebab-case
        protocol = ResearchProtocol(
            id="my-test-protocol",
            version="1.0.0",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
        )
        assert protocol.id == "my-test-protocol"

        # Invalid: uppercase
        with pytest.raises(ValueError):
            ResearchProtocol(
                id="MyTestProtocol",
                version="1.0.0",
                type=ResearchMethodType.SURVEY,
                name="Test Protocol",
            )

        # Invalid: spaces
        with pytest.raises(ValueError):
            ResearchProtocol(
                id="my test protocol",
                version="1.0.0",
                type=ResearchMethodType.SURVEY,
                name="Test Protocol",
            )

    def test_protocol_version_must_be_semver(self):
        """Protocol version must follow semver format."""
        # Valid semver
        protocol = ResearchProtocol(
            id="test-protocol",
            version="1.0.0",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
        )
        assert protocol.version == "1.0.0"

        protocol2 = ResearchProtocol(
            id="test-protocol",
            version="10.20.30",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
        )
        assert protocol2.version == "10.20.30"

        # Invalid: not semver
        with pytest.raises(ValueError):
            ResearchProtocol(
                id="test-protocol",
                version="1.0",
                type=ResearchMethodType.SURVEY,
                name="Test Protocol",
            )

        with pytest.raises(ValueError):
            ResearchProtocol(
                id="test-protocol",
                version="v1.0.0",
                type=ResearchMethodType.SURVEY,
                name="Test Protocol",
            )

    def test_protocol_has_default_created_at(self):
        """Protocol should have auto-generated created_at timestamp."""
        protocol = ResearchProtocol(
            id="test-protocol",
            version="1.0.0",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
        )
        assert protocol.created_at is not None
        assert isinstance(protocol.created_at, datetime)

    def test_protocol_tags_default_empty(self):
        """Protocol tags should default to empty list."""
        protocol = ResearchProtocol(
            id="test-protocol",
            version="1.0.0",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
        )
        assert protocol.tags == []

    def test_protocol_can_have_tags(self):
        """Protocol can have up to 10 tags."""
        protocol = ResearchProtocol(
            id="test-protocol",
            version="1.0.0",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
            tags=["concept-testing", "product-research"],
        )
        assert len(protocol.tags) == 2

    def test_protocol_description_optional(self):
        """Protocol description is optional."""
        protocol = ResearchProtocol(
            id="test-protocol",
            version="1.0.0",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
        )
        assert protocol.description is None

        protocol2 = ResearchProtocol(
            id="test-protocol",
            version="1.0.0",
            type=ResearchMethodType.SURVEY,
            name="Test Protocol",
            description="A test protocol for testing",
        )
        assert protocol2.description == "A test protocol for testing"


class TestSurveyProtocol:
    """Tests for SurveyProtocol model."""

    def test_survey_protocol_type_is_survey(self):
        """SurveyProtocol type must be SURVEY."""
        from models.survey import Survey, SurveyQuestion
        from models.enums import SurveyQuestionType

        question = SurveyQuestion(
            id="q1",
            text="How satisfied are you?",
            type=SurveyQuestionType.RATING,
            scale_min=1,
            scale_max=10,
        )
        survey = Survey(
            id="test-survey",
            version="1.0.0",
            name="Test Survey",
            questions=[question],
        )
        protocol = SurveyProtocol(
            id="test-survey-protocol",
            version="1.0.0",
            name="Test Survey Protocol",
            survey=survey,
        )
        assert protocol.type == ResearchMethodType.SURVEY


class TestInterviewProtocol:
    """Tests for InterviewProtocol model."""

    def test_interview_protocol_type_is_interview(self):
        """InterviewProtocol type must be INTERVIEW."""
        from models.interview import InterviewGuide, InterviewSection, InterviewQuestion

        question = InterviewQuestion(
            id="q1",
            text="Tell me about your experience.",
        )
        section = InterviewSection(
            id="background",
            name="Background",
            questions=[question],
        )
        guide = InterviewGuide(
            id="test-guide",
            version="1.0.0",
            name="Test Guide",
            topic="User Experience",
            sections=[section],
        )
        protocol = InterviewProtocol(
            id="test-interview-protocol",
            version="1.0.0",
            name="Test Interview Protocol",
            guide=guide,
        )
        assert protocol.type == ResearchMethodType.INTERVIEW


class TestFocusGroupProtocol:
    """Tests for FocusGroupProtocol model."""

    def test_focus_group_protocol_type_is_focus_group(self):
        """FocusGroupProtocol type must be FOCUS_GROUP."""
        from models.focus_group import FocusGroup

        focus_group = FocusGroup(
            id="test-focus-group",
            version="1.0.0",
            name="Test Focus Group",
            persona_ids=["p1", "p2", "p3", "p4"],
            discussion_topics=["Topic 1"],
        )
        protocol = FocusGroupProtocol(
            id="test-fg-protocol",
            version="1.0.0",
            name="Test Focus Group Protocol",
            focus_group=focus_group,
        )
        assert protocol.type == ResearchMethodType.FOCUS_GROUP
