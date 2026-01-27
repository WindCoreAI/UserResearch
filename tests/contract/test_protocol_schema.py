"""Contract tests for protocol schema validation.

Tests that protocol schemas are validated correctly and consistently.
"""

import pytest
import yaml
from pydantic import ValidationError

from models.protocol import ResearchProtocol, SurveyProtocol, InterviewProtocol, FocusGroupProtocol
from models.survey import Survey, SurveyQuestion
from models.interview import InterviewGuide, InterviewSection, InterviewQuestion
from models.focus_group import FocusGroup
from models.enums import ResearchMethodType, SurveyQuestionType


class TestProtocolSchemaValidation:
    """Contract tests for protocol schema validation."""

    def test_protocol_id_schema_contract(self):
        """Protocol ID must match kebab-case pattern."""
        valid_ids = [
            "my-protocol",
            "test-123",
            "a",
            "abc-def-ghi",
            "protocol-v1",
        ]
        invalid_ids = [
            "MyProtocol",  # Uppercase
            "my protocol",  # Spaces
            "my_protocol",  # Underscores
            "",  # Empty
            "UPPERCASE",  # All caps
        ]

        for valid_id in valid_ids:
            protocol = ResearchProtocol(
                id=valid_id,
                version="1.0.0",
                type=ResearchMethodType.SURVEY,
                name="Test",
            )
            assert protocol.id == valid_id

        for invalid_id in invalid_ids:
            with pytest.raises(ValidationError):
                ResearchProtocol(
                    id=invalid_id,
                    version="1.0.0",
                    type=ResearchMethodType.SURVEY,
                    name="Test",
                )

    def test_protocol_version_schema_contract(self):
        """Protocol version must be semver format."""
        valid_versions = ["1.0.0", "0.0.1", "10.20.30", "999.999.999"]
        invalid_versions = ["1.0", "v1.0.0", "1", "1.0.0-beta", "1.0.0.0"]

        for valid_version in valid_versions:
            protocol = ResearchProtocol(
                id="test",
                version=valid_version,
                type=ResearchMethodType.SURVEY,
                name="Test",
            )
            assert protocol.version == valid_version

        for invalid_version in invalid_versions:
            with pytest.raises(ValidationError):
                ResearchProtocol(
                    id="test",
                    version=invalid_version,
                    type=ResearchMethodType.SURVEY,
                    name="Test",
                )

    def test_survey_protocol_schema_contract(self):
        """SurveyProtocol must contain valid Survey."""
        question = SurveyQuestion(
            id="q1",
            text="Test question",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        survey = Survey(
            id="test-survey",
            version="1.0.0",
            name="Test Survey",
            questions=[question],
        )

        protocol = SurveyProtocol(
            id="test-protocol",
            version="1.0.0",
            name="Test Protocol",
            survey=survey,
        )

        assert protocol.type == ResearchMethodType.SURVEY
        assert protocol.survey is not None
        assert len(protocol.survey.questions) == 1

    def test_interview_protocol_schema_contract(self):
        """InterviewProtocol must contain valid InterviewGuide."""
        question = InterviewQuestion(
            id="q1",
            text="Tell me about your experience.",
        )
        section = InterviewSection(
            id="intro",
            name="Introduction",
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
            id="test-protocol",
            version="1.0.0",
            name="Test Protocol",
            guide=guide,
        )

        assert protocol.type == ResearchMethodType.INTERVIEW
        assert protocol.guide is not None
        assert len(protocol.guide.sections) == 1

    def test_focus_group_protocol_schema_contract(self):
        """FocusGroupProtocol must contain valid FocusGroup."""
        focus_group = FocusGroup(
            id="test-group",
            version="1.0.0",
            name="Test Group",
            persona_ids=["p1", "p2", "p3", "p4"],
            discussion_topics=["Topic 1", "Topic 2"],
        )

        protocol = FocusGroupProtocol(
            id="test-protocol",
            version="1.0.0",
            name="Test Protocol",
            focus_group=focus_group,
        )

        assert protocol.type == ResearchMethodType.FOCUS_GROUP
        assert protocol.focus_group is not None
        assert len(protocol.focus_group.persona_ids) == 4


class TestYAMLSchemaContract:
    """Contract tests for YAML schema parsing."""

    def test_survey_yaml_schema(self):
        """Survey YAML must parse to valid SurveyProtocol."""
        yaml_content = """
protocol:
  id: test-survey
  version: "1.0.0"
  type: survey
  name: Test Survey

survey:
  id: test-survey
  version: "1.0.0"
  name: Test Survey
  questions:
    - id: q1
      text: "How satisfied are you?"
      type: rating
      scale_min: 1
      scale_max: 10
"""
        data = yaml.safe_load(yaml_content)

        # Parse survey
        survey = Survey(
            id=data["survey"]["id"],
            version=data["survey"]["version"],
            name=data["survey"]["name"],
            questions=[
                SurveyQuestion(**q) for q in data["survey"]["questions"]
            ],
        )

        # Parse protocol
        protocol = SurveyProtocol(
            id=data["protocol"]["id"],
            version=data["protocol"]["version"],
            name=data["protocol"]["name"],
            survey=survey,
        )

        assert protocol.id == "test-survey"
        assert protocol.type == ResearchMethodType.SURVEY

    def test_interview_yaml_schema(self):
        """Interview YAML must parse to valid InterviewProtocol."""
        yaml_content = """
protocol:
  id: test-interview
  version: "1.0.0"
  type: interview
  name: Test Interview

guide:
  id: test-interview
  version: "1.0.0"
  name: Test Interview Guide
  topic: User Experience
  sections:
    - id: intro
      name: Introduction
      questions:
        - id: q1
          text: "Tell me about yourself."
"""
        data = yaml.safe_load(yaml_content)

        # Parse guide
        sections = []
        for s in data["guide"]["sections"]:
            questions = [InterviewQuestion(**q) for q in s["questions"]]
            sections.append(InterviewSection(
                id=s["id"],
                name=s["name"],
                questions=questions,
            ))

        guide = InterviewGuide(
            id=data["guide"]["id"],
            version=data["guide"]["version"],
            name=data["guide"]["name"],
            topic=data["guide"]["topic"],
            sections=sections,
        )

        # Parse protocol
        protocol = InterviewProtocol(
            id=data["protocol"]["id"],
            version=data["protocol"]["version"],
            name=data["protocol"]["name"],
            guide=guide,
        )

        assert protocol.id == "test-interview"
        assert protocol.type == ResearchMethodType.INTERVIEW

    def test_focus_group_yaml_schema(self):
        """Focus group YAML must parse to valid FocusGroupProtocol."""
        yaml_content = """
protocol:
  id: test-focus-group
  version: "1.0.0"
  type: focus_group
  name: Test Focus Group

focus_group:
  id: test-focus-group
  version: "1.0.0"
  name: Test Focus Group
  persona_ids:
    - persona-1
    - persona-2
    - persona-3
    - persona-4
  discussion_topics:
    - "Topic 1"
    - "Topic 2"
"""
        data = yaml.safe_load(yaml_content)

        # Parse focus group
        focus_group = FocusGroup(
            id=data["focus_group"]["id"],
            version=data["focus_group"]["version"],
            name=data["focus_group"]["name"],
            persona_ids=data["focus_group"]["persona_ids"],
            discussion_topics=data["focus_group"]["discussion_topics"],
        )

        # Parse protocol
        protocol = FocusGroupProtocol(
            id=data["protocol"]["id"],
            version=data["protocol"]["version"],
            name=data["protocol"]["name"],
            focus_group=focus_group,
        )

        assert protocol.id == "test-focus-group"
        assert protocol.type == ResearchMethodType.FOCUS_GROUP
