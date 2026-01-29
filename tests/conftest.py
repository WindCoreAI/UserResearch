"""Pytest fixtures for research-cli tests."""

import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import pytest
import pytest_asyncio
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


# Panel testing fixtures

@pytest.fixture
def sample_panel_dict() -> dict[str, Any]:
    """Return a valid panel dictionary for testing."""
    return {
        "id": "test-panel",
        "name": "Test Panel",
        "description": "A test panel for unit testing",
        "purpose": "Testing panel functionality",
        "persona_ids": ["test-persona-1", "test-persona-2", "test-persona-3"],
        "is_custom": False,
        "created_at": "2026-01-25T00:00:00Z",
    }


@pytest.fixture
def sample_panel_yaml(sample_panel_dict) -> str:
    """Return sample panel as YAML string."""
    return yaml.dump(sample_panel_dict, default_flow_style=False)


@pytest.fixture
def temp_panel_file(sample_panel_yaml):
    """Create a temporary panel YAML file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write(sample_panel_yaml)
        f.flush()
        yield Path(f.name)
    os.unlink(f.name)


@pytest.fixture
def temp_panels_dir(sample_panel_dict):
    """Create a temporary directory with panel files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        panels_dir = Path(tmpdir) / "panels"
        definitions_dir = panels_dir / "definitions"
        custom_dir = panels_dir / "custom"
        definitions_dir.mkdir(parents=True)
        custom_dir.mkdir(parents=True)

        # Create test panel file
        panel_file = definitions_dir / "test-panel.yaml"
        with open(panel_file, "w") as f:
            yaml.dump(sample_panel_dict, f)

        yield Path(tmpdir)


@pytest.fixture
def sample_aggregation_result() -> dict[str, Any]:
    """Return a sample aggregation result for testing."""
    return {
        "executive_summary": "Panel shows mixed reception with enthusiasm from early adopters.",
        "themes": [
            {
                "name": "Innovation Enthusiasm",
                "description": "Early adopters are excited about new features",
                "frequency": 3,
                "percentage": 60.0,
                "supporting_quotes": [
                    {
                        "persona_id": "test-persona-1",
                        "persona_name": "Test User 1",
                        "quote": "This is exactly what I needed!",
                    }
                ],
                "sentiment_tendency": "POSITIVE",
            }
        ],
        "sentiment_distribution": {
            "positive": 60.0,
            "negative": 20.0,
            "mixed": 20.0,
            "neutral": 0.0,
            "dominant": "POSITIVE",
        },
        "consensus_points": [
            {
                "statement": "Feature has potential",
                "agreement_rate": 80.0,
                "supporting_personas": ["test-persona-1", "test-persona-2", "test-persona-3"],
                "key_quotes": [],
            }
        ],
        "divergence_points": [
            {
                "topic": "Privacy concerns",
                "positions": [
                    {
                        "stance": "Concerned",
                        "persona_ids": ["test-persona-2"],
                        "rationale": "Worried about data usage",
                    },
                    {
                        "stance": "Not concerned",
                        "persona_ids": ["test-persona-1", "test-persona-3"],
                        "rationale": "Trust the platform",
                    },
                ],
            }
        ],
        "aggregation_confidence": 85.0,
    }


@pytest.fixture
def sample_quality_metrics() -> dict[str, Any]:
    """Return sample panel quality metrics for testing."""
    return {
        "avg_consistency_score": 85.0,
        "completion_rate": 100.0,
        "theme_confidence": 80.0,
        "divergence_score": 40.0,
        "passed_gates": True,
        "warnings": [],
        "individual_metrics": [],
    }


@pytest_asyncio.fixture
async def async_panel_context():
    """Async context fixture for panel execution tests."""
    context = {
        "started_at": datetime.now(timezone.utc),
        "panel_id": "test-panel",
        "question": "What do you think of this feature?",
    }
    yield context
    # Cleanup if needed


# Quality & Calibration fixtures (Phase 4)


@pytest.fixture
def high_consistency_session() -> dict[str, Any]:
    """Session with responses perfectly matching high-openness persona traits.

    Persona: openness=9, conscientiousness=3, extraversion=7, agreeableness=5, neuroticism=2
    """
    return {
        "persona": {
            "id": "high-open-persona",
            "name": "Creative Explorer",
            "big_five": {
                "openness": 9,
                "conscientiousness": 3,
                "extraversion": 7,
                "agreeableness": 5,
                "neuroticism": 2,
            },
            "schwartz_values": {
                "primary": ["self_direction", "stimulation"],
                "secondary": ["universalism"],
            },
        },
        "responses": [
            "I find this incredibly innovative and creative. I'm curious about the novel approaches "
            "used here. It's exciting to explore new ideas and experiment with unconventional methods. "
            "I feel energetic and enthusiastic about collaborating on this.",
            "This is a fascinating concept that sparks my imagination. I love to explore and experiment "
            "with new approaches. The creative possibilities are endless, and I'm excited to engage "
            "with the team on this innovative project.",
            "As someone who values independence and creativity, I appreciate how this encourages "
            "exploration. I'm confident and calm about trying unconventional solutions. "
            "The flexibility and spontaneous nature of this approach appeals to me.",
        ],
    }


@pytest.fixture
def sycophantic_session() -> dict[str, Any]:
    """Session with obvious sycophantic patterns."""
    return {
        "persona": {
            "id": "skeptical-user",
            "name": "Skeptical Reviewer",
            "big_five": {
                "openness": 4,
                "conscientiousness": 7,
                "extraversion": 3,
                "agreeableness": 3,
                "neuroticism": 6,
            },
            "schwartz_values": {
                "primary": ["security", "conformity"],
            },
        },
        "responses": [
            "This is absolutely amazing! I love everything about it. This is perfect and "
            "I can't find any issues at all. This is exactly what I need! Great work!",
            "I absolutely love this feature. It's the best thing ever and I have no complaints. "
            "This exceeds expectations in every way. I would definitely recommend this to everyone.",
            "This is perfect in every way. No concerns at all. I'm completely satisfied "
            "and couldn't be better. Nothing to improve whatsoever. Wonderful and fantastic!",
        ],
    }


@pytest.fixture
def drifted_session() -> dict[str, Any]:
    """Session showing clear character drift from high openness to conventional responses."""
    return {
        "persona": {
            "id": "drifting-persona",
            "name": "Drifting User",
            "big_five": {
                "openness": 9,
                "conscientiousness": 5,
                "extraversion": 6,
                "agreeableness": 5,
                "neuroticism": 4,
            },
            "schwartz_values": {
                "primary": ["self_direction", "stimulation"],
            },
        },
        "responses": [
            # Segment 1: High openness - creative, innovative
            "I find this incredibly innovative and creative. I'm curious about exploring "
            "novel approaches and experimenting with unconventional solutions. New ideas excite me.",
            "This sparks my imagination. I love to explore and experiment with creative possibilities. "
            "The innovative design is unconventional and imaginative.",
            "Fascinating concept! I'm curious how we can push this further with novel experiments. "
            "Creative and innovative thinking is what drives progress.",
            # Segment 2: Moderate - transitioning
            "This seems reasonable. There are some interesting aspects worth considering. "
            "I think we should look at the practical implications carefully.",
            "The approach has merit. Let me think about the standard considerations here. "
            "We should be careful about the implementation details.",
            "It's a decent solution. I can see both the creative aspects and the need for "
            "proven approaches in some areas.",
            # Segment 3: Low openness - conventional, traditional
            "I think we should stick with the traditional approach. It's proven and familiar. "
            "The conventional methods are more practical and standard.",
            "Let's go with the standard solution. I prefer existing approaches that are "
            "cautious and conventional. Traditional methods work best.",
            "I'd recommend the proven, familiar approach. Being cautious and practical is "
            "important. Let's use conventional, standard solutions.",
        ],
    }


@pytest.fixture
def calibration_baseline() -> dict[str, Any]:
    """Sample calibration baseline data for testing."""
    return {
        "id": "test-baseline-2026",
        "name": "Test Survey Baseline",
        "version": "1.0.0",
        "source": "Test User Survey",
        "sample_size": 50,
        "collection_date": "2026-01-15",
        "demographic_tags": ["early_adopter", "professional"],
        "distributions": [
            {
                "question_id": "q1_likelihood",
                "question_text": "How likely are you to use this feature?",
                "distribution_type": "numeric",
                "numeric": {
                    "mean": 6.2,
                    "stdev": 2.3,
                    "min_value": 1.0,
                    "max_value": 10.0,
                    "histogram": [2, 3, 5, 7, 8, 10, 7, 4, 3, 1],
                    "bucket_labels": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                },
            },
            {
                "question_id": "q2_concern",
                "question_text": "What is your primary concern?",
                "distribution_type": "categorical",
                "categorical": {
                    "frequencies": {
                        "Privacy": 0.35,
                        "Complexity": 0.28,
                        "Cost": 0.22,
                        "None": 0.15,
                    },
                    "total_responses": 50,
                },
            },
        ],
    }
