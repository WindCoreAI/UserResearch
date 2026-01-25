"""Unit tests for PersonaLibrary service."""

import pytest
import yaml


class TestPersonaLibrary:
    """Tests for PersonaLibrary service."""

    def test_list_all_returns_list(self, temp_personas_dir):
        """list_all should return a list of personas."""
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(
            personas_dir=temp_personas_dir / "personas" / "definitions"
        )
        personas = library.list_all()

        assert isinstance(personas, list)
        assert len(personas) >= 1

    def test_list_all_returns_persona_objects(self, temp_personas_dir):
        """list_all should return Persona objects."""
        from models.persona import Persona
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(
            personas_dir=temp_personas_dir / "personas" / "definitions"
        )
        personas = library.list_all()

        for persona in personas:
            assert isinstance(persona, Persona)

    def test_list_all_empty_directory(self, tmp_path):
        """list_all should return empty list for empty directory."""
        from services.persona_library import PersonaLibrary

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        library = PersonaLibrary(personas_dir=empty_dir)
        personas = library.list_all()

        assert personas == []

    def test_list_all_nonexistent_directory(self, tmp_path):
        """list_all should return empty list for nonexistent directory."""
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(personas_dir=tmp_path / "does_not_exist")
        personas = library.list_all()

        assert personas == []

    def test_get_by_id_returns_persona(self, temp_personas_dir):
        """get_by_id should return the matching persona."""
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(
            personas_dir=temp_personas_dir / "personas" / "definitions"
        )
        persona = library.get_by_id("test-persona")

        assert persona.id == "test-persona"

    def test_get_by_id_not_found_raises(self, temp_personas_dir):
        """get_by_id should raise FileNotFoundError for unknown ID."""
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(
            personas_dir=temp_personas_dir / "personas" / "definitions"
        )

        with pytest.raises(FileNotFoundError):
            library.get_by_id("nonexistent-persona")

    def test_search_by_tech_adoption(self, temp_personas_dir, sample_persona_dict):
        """search should filter by tech adoption category."""
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(
            personas_dir=temp_personas_dir / "personas" / "definitions"
        )

        # Search for the test persona's adoption category
        results = library.search(tech_adoption="early_adopter")

        assert len(results) >= 1
        for persona in results:
            assert persona.psychological_profile.tech_adoption.value == "early_adopter"

    def test_search_by_age_range(self, temp_personas_dir):
        """search should filter by age range."""
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(
            personas_dir=temp_personas_dir / "personas" / "definitions"
        )

        # Test persona has age 30
        results = library.search(min_age=25, max_age=35)

        assert len(results) >= 1
        for persona in results:
            assert 25 <= persona.demographics.age <= 35

    def test_search_no_matches(self, temp_personas_dir):
        """search should return empty list when no matches."""
        from services.persona_library import PersonaLibrary

        library = PersonaLibrary(
            personas_dir=temp_personas_dir / "personas" / "definitions"
        )

        # Search for impossible criteria
        results = library.search(min_age=200)

        assert results == []

    def test_handles_invalid_yaml_files(self, tmp_path, sample_persona_dict):
        """list_all should skip invalid YAML files without crashing."""
        from services.persona_library import PersonaLibrary

        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()

        # Create a valid persona
        valid_file = personas_dir / "valid.yaml"
        with open(valid_file, "w") as f:
            yaml.dump(sample_persona_dict, f)

        # Create an invalid file
        invalid_file = personas_dir / "invalid.yaml"
        invalid_file.write_text("{ invalid yaml [")

        library = PersonaLibrary(personas_dir=personas_dir)
        personas = library.list_all()

        # Should have the valid persona
        assert len(personas) == 1
        assert personas[0].id == "test-persona"

    def test_handles_duplicate_ids(self, tmp_path, sample_persona_dict):
        """list_all should skip duplicate IDs."""
        from services.persona_library import PersonaLibrary

        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()

        # Create two files with same persona ID
        file1 = personas_dir / "persona1.yaml"
        file2 = personas_dir / "persona2.yaml"

        with open(file1, "w") as f:
            yaml.dump(sample_persona_dict, f)

        with open(file2, "w") as f:
            yaml.dump(sample_persona_dict, f)  # Same ID

        library = PersonaLibrary(personas_dir=personas_dir)
        personas = library.list_all()

        # Should only have one persona (duplicate skipped)
        assert len(personas) == 1
