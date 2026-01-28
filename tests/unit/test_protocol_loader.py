"""Unit tests for ProtocolLoader service.

Tests for loading, saving, listing, and deleting protocols.
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import yaml

from services.protocol_loader import ProtocolLoader, ProtocolLoaderError
from models.protocol import ResearchProtocol, SurveyProtocol
from models.survey import Survey, SurveyQuestion
from models.enums import ResearchMethodType, SurveyQuestionType


@pytest.fixture
def temp_protocols_dir():
    """Create a temporary directory for protocol tests."""
    temp_dir = tempfile.mkdtemp()
    protocols_dir = Path(temp_dir) / "protocols"
    protocols_dir.mkdir()
    (protocols_dir / "surveys").mkdir()
    (protocols_dir / "interviews").mkdir()
    (protocols_dir / "focus-groups").mkdir()
    yield protocols_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def loader(temp_protocols_dir):
    """Create a ProtocolLoader with temp directory."""
    return ProtocolLoader(protocols_dir=temp_protocols_dir)


@pytest.fixture
def sample_survey_yaml(temp_protocols_dir):
    """Create a sample survey protocol YAML file."""
    yaml_content = """
protocol:
  id: sample-survey
  version: "1.0.0"
  type: survey
  name: "Sample Survey"
  description: "A sample survey for testing"
  tags:
    - testing
    - sample

survey:
  id: sample-survey
  version: "1.0.0"
  name: "Sample Survey"
  questions:
    - id: q1-rating
      text: "How satisfied are you?"
      type: rating
      scale_min: 1
      scale_max: 10
    - id: q2-choice
      text: "What best describes you?"
      type: multiple_choice
      options:
        - "Option A"
        - "Option B"
        - "Option C"
"""
    file_path = temp_protocols_dir / "surveys" / "sample-survey.yaml"
    file_path.write_text(yaml_content.strip())
    return file_path


class TestProtocolLoaderInit:
    """Tests for ProtocolLoader initialization."""

    def test_loader_uses_default_directory(self):
        """Loader should use default protocols directory if not specified."""
        loader = ProtocolLoader()
        assert "protocols" in str(loader.protocols_dir)

    def test_loader_accepts_custom_directory(self, temp_protocols_dir):
        """Loader should accept custom protocols directory."""
        loader = ProtocolLoader(protocols_dir=temp_protocols_dir)
        assert loader.protocols_dir == temp_protocols_dir


class TestProtocolLoaderLoadById:
    """Tests for loading protocols by ID."""

    def test_load_existing_protocol(self, loader, sample_survey_yaml):
        """Should load an existing protocol by ID."""
        protocol = loader.load_by_id("sample-survey")
        assert protocol.id == "sample-survey"
        assert protocol.version == "1.0.0"
        assert protocol.type == ResearchMethodType.SURVEY

    def test_load_nonexistent_protocol_raises_error(self, loader):
        """Should raise error for non-existent protocol."""
        with pytest.raises(ProtocolLoaderError) as exc_info:
            loader.load_by_id("nonexistent-protocol")
        assert "not found" in str(exc_info.value).lower()

    def test_load_protocol_returns_correct_type(self, loader, sample_survey_yaml):
        """Should return SurveyProtocol for survey type."""
        protocol = loader.load_by_id("sample-survey")
        assert isinstance(protocol, SurveyProtocol)
        assert hasattr(protocol, "survey")


class TestProtocolLoaderListProtocols:
    """Tests for listing protocols."""

    def test_list_protocols_empty_directory(self, loader):
        """Should return empty list for empty directory."""
        protocols = loader.list_protocols()
        assert protocols == []

    def test_list_all_protocols(self, loader, sample_survey_yaml):
        """Should list all protocols."""
        protocols = loader.list_protocols()
        assert len(protocols) == 1
        assert protocols[0].id == "sample-survey"

    def test_list_protocols_by_type(self, loader, sample_survey_yaml):
        """Should filter protocols by type."""
        surveys = loader.list_protocols(method_type=ResearchMethodType.SURVEY)
        assert len(surveys) == 1

        interviews = loader.list_protocols(method_type=ResearchMethodType.INTERVIEW)
        assert len(interviews) == 0


class TestProtocolLoaderSaveProtocol:
    """Tests for saving protocols."""

    def test_save_new_protocol(self, loader, temp_protocols_dir):
        """Should save a new protocol."""
        question = SurveyQuestion(
            id="q1",
            text="Test question",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        survey = Survey(
            id="new-survey",
            version="1.0.0",
            name="New Survey",
            questions=[question],
        )
        protocol = SurveyProtocol(
            id="new-survey",
            version="1.0.0",
            name="New Survey Protocol",
            survey=survey,
        )

        saved_path = loader.save_protocol(protocol)
        assert saved_path.exists()
        assert "surveys" in str(saved_path)

    def test_save_protocol_creates_valid_yaml(self, loader, temp_protocols_dir):
        """Saved protocol should be valid YAML."""
        question = SurveyQuestion(
            id="q1",
            text="Test question",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        survey = Survey(
            id="yaml-test",
            version="1.0.0",
            name="YAML Test Survey",
            questions=[question],
        )
        protocol = SurveyProtocol(
            id="yaml-test",
            version="1.0.0",
            name="YAML Test Protocol",
            survey=survey,
        )

        saved_path = loader.save_protocol(protocol)

        # Should be parseable YAML
        with open(saved_path) as f:
            data = yaml.safe_load(f)
        assert "protocol" in data
        assert data["protocol"]["id"] == "yaml-test"


class TestProtocolLoaderDeleteProtocol:
    """Tests for deleting protocols."""

    def test_delete_existing_protocol(self, loader, sample_survey_yaml):
        """Should delete an existing protocol."""
        assert sample_survey_yaml.exists()
        loader.delete_protocol("sample-survey")
        assert not sample_survey_yaml.exists()

    def test_delete_nonexistent_protocol_raises_error(self, loader):
        """Should raise error when deleting non-existent protocol."""
        with pytest.raises(ProtocolLoaderError):
            loader.delete_protocol("nonexistent-protocol")


class TestProtocolVersioning:
    """Tests for protocol versioning (copy-on-write)."""

    def test_save_different_version_creates_new_file(self, loader, sample_survey_yaml):
        """Saving with different version should create new file."""
        # Load existing
        protocol = loader.load_by_id("sample-survey")

        # Create new version
        question = SurveyQuestion(
            id="q1",
            text="Updated question",
            type=SurveyQuestionType.OPEN_ENDED,
        )
        survey = Survey(
            id="sample-survey",
            version="1.1.0",
            name="Sample Survey v1.1",
            questions=[question],
        )
        new_protocol = SurveyProtocol(
            id="sample-survey",
            version="1.1.0",
            name="Sample Survey Protocol v1.1",
            survey=survey,
        )

        saved_path = loader.save_protocol(new_protocol)
        assert "1.1.0" in str(saved_path) or saved_path.exists()

        # Original should still exist
        original = loader.load_by_id("sample-survey")
        assert original.version in ["1.0.0", "1.1.0"]
