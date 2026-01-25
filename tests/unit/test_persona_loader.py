"""Unit tests for PersonaLoader service."""

import pytest


class TestPersonaLoader:
    """Tests for PersonaLoader service."""

    def test_load_valid_persona_file(self, temp_persona_file):
        """Should load a valid persona from YAML file."""
        from services.persona_loader import PersonaLoader

        loader = PersonaLoader()
        persona = loader.load(temp_persona_file)

        assert persona.id == "test-persona"
        assert persona.name == "Test User"

    def test_load_returns_persona_object(self, temp_persona_file):
        """Loaded result should be a Persona object."""
        from models.persona import Persona
        from services.persona_loader import PersonaLoader

        loader = PersonaLoader()
        persona = loader.load(temp_persona_file)

        assert isinstance(persona, Persona)

    def test_load_nonexistent_file_raises_error(self, tmp_path):
        """Loading a nonexistent file should raise FileNotFoundError."""
        from services.persona_loader import PersonaLoader

        loader = PersonaLoader()
        nonexistent = tmp_path / "does_not_exist.yaml"

        with pytest.raises(FileNotFoundError):
            loader.load(nonexistent)

    def test_load_invalid_yaml_raises_error(self, tmp_path):
        """Loading invalid YAML should raise appropriate error."""
        from services.persona_loader import PersonaLoaderError, PersonaLoader

        loader = PersonaLoader()
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("{ invalid yaml content [")

        with pytest.raises(PersonaLoaderError):
            loader.load(invalid_file)

    def test_load_invalid_schema_raises_validation_error(self, tmp_path):
        """Loading YAML with invalid schema should raise validation error."""
        import yaml

        from services.persona_loader import PersonaLoaderError, PersonaLoader

        loader = PersonaLoader()
        invalid_persona = tmp_path / "invalid_persona.yaml"

        # Write persona with invalid Big Five value
        invalid_data = {
            "persona": {
                "id": "invalid",
                "version": "1.0.0",
                "name": "Invalid",
                "demographics": {
                    "age": 30,
                    "gender": "any",
                    "location": "Anywhere",
                    "occupation": {"title": "Worker"},
                },
                "psychological_profile": {
                    "big_five": {
                        "openness": 15,  # Invalid - out of range
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
        }

        with open(invalid_persona, "w") as f:
            yaml.dump(invalid_data, f)

        with pytest.raises(PersonaLoaderError) as exc_info:
            loader.load(invalid_persona)

        # Should provide helpful error message
        assert "openness" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()

    def test_validate_valid_persona(self, temp_persona_file):
        """Validate should return True for valid persona."""
        from services.persona_loader import PersonaLoader

        loader = PersonaLoader()
        result = loader.validate(temp_persona_file)

        assert result.is_valid is True
        assert result.errors == []

    def test_validate_invalid_persona_returns_errors(self, tmp_path, invalid_persona_dict):
        """Validate should return errors for invalid persona."""
        import yaml

        from services.persona_loader import PersonaLoader

        loader = PersonaLoader()
        invalid_file = tmp_path / "invalid.yaml"

        with open(invalid_file, "w") as f:
            yaml.dump(invalid_persona_dict, f)

        result = loader.validate(invalid_file)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_missing_file_returns_error(self, tmp_path):
        """Validate should return error for missing file."""
        from services.persona_loader import PersonaLoader

        loader = PersonaLoader()
        missing = tmp_path / "missing.yaml"

        result = loader.validate(missing)

        assert result.is_valid is False
        assert any("not found" in e.lower() or "does not exist" in e.lower() for e in result.errors)
