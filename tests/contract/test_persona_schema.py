"""Contract tests for persona schema validation.

These tests ensure the persona YAML schema remains stable and
validates according to the documented requirements.
"""

import pytest


class TestPersonaSchemaContract:
    """Contract tests for the persona schema."""

    def test_valid_persona_passes_validation(self, sample_persona_dict):
        """A complete, valid persona should pass all validation."""
        from models.persona import Persona

        persona_data = sample_persona_dict["persona"]
        persona = Persona(**persona_data)

        assert persona.id == "test-persona"
        assert persona.version == "1.0.0"
        assert persona.name == "Test User"

    def test_persona_id_must_be_kebab_case(self):
        """Persona ID must follow kebab-case pattern."""
        from pydantic import ValidationError

        from models.persona import Persona

        # Valid kebab-case IDs
        valid_ids = ["test-persona", "my-persona-123", "a", "abc-def-ghi"]

        for valid_id in valid_ids:
            # Should not raise - just testing the pattern works
            persona_data = _minimal_persona(id=valid_id)
            persona = Persona(**persona_data)
            assert persona.id == valid_id

        # Invalid IDs (not kebab-case)
        invalid_ids = ["Test-Persona", "test_persona", "test persona", "-test", "test-"]

        for invalid_id in invalid_ids:
            persona_data = _minimal_persona(id=invalid_id)
            with pytest.raises(ValidationError):
                Persona(**persona_data)

    def test_version_must_be_semver(self):
        """Version must follow semantic versioning pattern."""
        from pydantic import ValidationError

        from models.persona import Persona

        # Valid semver
        valid_versions = ["1.0.0", "0.1.0", "10.20.30"]

        for version in valid_versions:
            persona_data = _minimal_persona(version=version)
            persona = Persona(**persona_data)
            assert persona.version == version

        # Invalid versions
        invalid_versions = ["1.0", "v1.0.0", "1.0.0.0", "1.0.0-beta"]

        for version in invalid_versions:
            persona_data = _minimal_persona(version=version)
            with pytest.raises(ValidationError):
                Persona(**persona_data)

    def test_big_five_traits_must_be_1_to_10(self):
        """All Big Five traits must be integers between 1 and 10."""
        from pydantic import ValidationError

        from models.persona import BigFive

        # Valid range
        valid_big_five = BigFive(
            openness=1,
            conscientiousness=5,
            extraversion=10,
            agreeableness=3,
            neuroticism=7,
        )
        assert valid_big_five.openness == 1
        assert valid_big_five.extraversion == 10

        # Out of range - too low
        with pytest.raises(ValidationError):
            BigFive(
                openness=0,  # Invalid
                conscientiousness=5,
                extraversion=5,
                agreeableness=5,
                neuroticism=5,
            )

        # Out of range - too high
        with pytest.raises(ValidationError):
            BigFive(
                openness=11,  # Invalid
                conscientiousness=5,
                extraversion=5,
                agreeableness=5,
                neuroticism=5,
            )

    def test_schwartz_values_requires_minimum_two_primary(self):
        """Primary Schwartz values must contain at least 2 values."""
        from pydantic import ValidationError

        from models.persona import SchwartzValues

        # Valid - 2 primary values
        valid = SchwartzValues(primary=["self_direction", "achievement"])
        assert len(valid.primary) == 2

        # Invalid - only 1 primary value
        with pytest.raises(ValidationError):
            SchwartzValues(primary=["self_direction"])

        # Invalid - empty primary
        with pytest.raises(ValidationError):
            SchwartzValues(primary=[])

    def test_demographics_age_must_be_18_to_100(self):
        """Age must be between 18 and 100 (adult users only)."""
        from pydantic import ValidationError

        from models.persona import Demographics, Occupation

        occupation = Occupation(title="Worker")

        # Valid ages
        for age in [18, 50, 100]:
            demo = Demographics(
                age=age,
                gender="any",
                location="Anywhere",
                occupation=occupation,
            )
            assert demo.age == age

        # Invalid - too young
        with pytest.raises(ValidationError):
            Demographics(
                age=17,
                gender="any",
                location="Anywhere",
                occupation=occupation,
            )

        # Invalid - too old
        with pytest.raises(ValidationError):
            Demographics(
                age=101,
                gender="any",
                location="Anywhere",
                occupation=occupation,
            )

    def test_background_requires_pain_points_and_goals(self):
        """Background must have at least 1 pain point and 1 goal."""
        from pydantic import ValidationError

        from models.persona import Background

        # Valid
        valid = Background(
            life_stage="Working",
            pain_points=["One pain point"],
            goals=["One goal"],
        )
        assert len(valid.pain_points) == 1
        assert len(valid.goals) == 1

        # Invalid - empty pain points
        with pytest.raises(ValidationError):
            Background(
                life_stage="Working",
                pain_points=[],
                goals=["One goal"],
            )

        # Invalid - empty goals
        with pytest.raises(ValidationError):
            Background(
                life_stage="Working",
                pain_points=["One pain point"],
                goals=[],
            )


def _minimal_persona(**overrides):
    """Create a minimal valid persona dict with optional overrides."""
    base = {
        "id": "test-persona",
        "version": "1.0.0",
        "name": "Test",
        "demographics": {
            "age": 30,
            "gender": "any",
            "location": "Anywhere",
            "occupation": {"title": "Worker"},
        },
        "psychological_profile": {
            "big_five": {
                "openness": 5,
                "conscientiousness": 5,
                "extraversion": 5,
                "agreeableness": 5,
                "neuroticism": 5,
            },
            "schwartz_values": {"primary": ["self_direction", "achievement"]},
            "tech_adoption": "early_majority",
        },
        "background": {
            "life_stage": "Working",
            "pain_points": ["Something"],
            "goals": ["Something"],
        },
        "response_calibration": {
            "verbosity": "moderate",
            "emotional_expressiveness": "moderate",
            "criticism_tendency": "balanced",
        },
    }
    base.update(overrides)
    return base
