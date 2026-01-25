"""Pytest fixtures for research-cli tests."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def sample_persona_dict():
    """Return a valid persona dictionary for testing."""
    return {
        "persona": {
            "id": "test-persona",
            "version": "1.0.0",
            "name": "Test User",
            "demographics": {
                "age": 30,
                "gender": "non-binary",
                "location": "New York, NY",
                "occupation": {
                    "title": "Software Engineer",
                    "industry": "Technology",
                    "years_experience": 5,
                },
            },
            "psychological_profile": {
                "big_five": {
                    "openness": 7,
                    "conscientiousness": 6,
                    "extraversion": 5,
                    "agreeableness": 6,
                    "neuroticism": 4,
                },
                "schwartz_values": {
                    "primary": ["self_direction", "achievement"],
                    "secondary": ["stimulation"],
                },
                "tech_adoption": "early_adopter",
            },
            "background": {
                "life_stage": "Mid-career professional",
                "pain_points": ["Too many tools to manage"],
                "goals": ["Improve productivity"],
            },
            "response_calibration": {
                "verbosity": "moderate",
                "emotional_expressiveness": "moderate",
                "criticism_tendency": "balanced",
            },
        }
    }


@pytest.fixture
def sample_persona_yaml(sample_persona_dict):
    """Return sample persona as YAML string."""
    return yaml.dump(sample_persona_dict, default_flow_style=False)


@pytest.fixture
def temp_persona_file(sample_persona_yaml):
    """Create a temporary persona YAML file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write(sample_persona_yaml)
        f.flush()
        yield Path(f.name)
    os.unlink(f.name)


@pytest.fixture
def temp_personas_dir(sample_persona_dict):
    """Create a temporary directory with persona files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        personas_dir = Path(tmpdir) / "personas" / "definitions"
        personas_dir.mkdir(parents=True)

        # Create test persona file
        persona_file = personas_dir / "test-persona.yaml"
        with open(persona_file, "w") as f:
            yaml.dump(sample_persona_dict, f)

        yield Path(tmpdir)


@pytest.fixture
def invalid_persona_dict():
    """Return an invalid persona dictionary for testing validation errors."""
    return {
        "persona": {
            "id": "invalid-persona",
            "version": "1.0.0",
            "name": "Invalid",
            "demographics": {
                "age": 150,  # Invalid: age > 100
                "gender": "male",
                "location": "Unknown",
                "occupation": {"title": "Worker"},
            },
            "psychological_profile": {
                "big_five": {
                    "openness": 15,  # Invalid: > 10
                    "conscientiousness": 5,
                    "extraversion": 5,
                    "agreeableness": 5,
                    "neuroticism": 5,
                },
                "schwartz_values": {
                    "primary": ["self_direction"],  # Invalid: needs 2+ values
                },
                "tech_adoption": "early_adopter",
            },
            "background": {
                "life_stage": "Unknown",
                "pain_points": [],  # Invalid: needs at least 1
                "goals": ["Something"],
            },
            "response_calibration": {
                "verbosity": "moderate",
                "emotional_expressiveness": "moderate",
                "criticism_tendency": "balanced",
            },
        }
    }
