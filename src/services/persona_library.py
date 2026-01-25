"""Service for managing the persona library.

Provides functionality to list, search, and retrieve personas
from the personas directory.
"""

from pathlib import Path
from typing import Optional

from models.persona import Persona
from services.persona_loader import PersonaLoader


class PersonaLibrary:
    """Manages a collection of persona files."""

    def __init__(self, personas_dir: Optional[Path] = None):
        """Initialize the library.

        Args:
            personas_dir: Directory containing persona YAML files.
                         Defaults to personas/definitions/.
        """
        self.personas_dir = personas_dir or Path("personas/definitions")
        self._loader = PersonaLoader()
        self._cache: dict[str, Persona] = {}

    def list_all(self) -> list[Persona]:
        """List all valid personas in the library.

        Returns:
            List of Persona objects, sorted by ID.
        """
        if not self.personas_dir.exists():
            return []

        personas = []
        seen_ids: set[str] = set()

        for yaml_file in sorted(self.personas_dir.glob("*.yaml")):
            try:
                persona = self._loader.load(yaml_file)
                if persona.id in seen_ids:
                    # Duplicate ID warning - skip
                    continue
                seen_ids.add(persona.id)
                personas.append(persona)
                self._cache[persona.id] = persona
            except Exception:
                # Skip invalid files when listing
                continue

        return personas

    def get_by_id(self, persona_id: str) -> Persona:
        """Retrieve a persona by its ID.

        Args:
            persona_id: The unique identifier of the persona.

        Returns:
            The Persona object.

        Raises:
            FileNotFoundError: If no persona with the given ID exists.
        """
        # Check cache first
        if persona_id in self._cache:
            return self._cache[persona_id]

        if not self.personas_dir.exists():
            raise FileNotFoundError(f"Persona not found: {persona_id}")

        # Try direct file lookup
        potential_file = self.personas_dir / f"{persona_id}.yaml"
        if potential_file.exists():
            persona = self._loader.load(potential_file)
            self._cache[persona_id] = persona
            return persona

        # Scan all files to find matching ID
        for yaml_file in self.personas_dir.glob("*.yaml"):
            try:
                persona = self._loader.load(yaml_file)
                if persona.id == persona_id:
                    self._cache[persona_id] = persona
                    return persona
            except Exception:
                continue

        raise FileNotFoundError(f"Persona not found: {persona_id}")

    def search(
        self,
        tech_adoption: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        tags: Optional[list[str]] = None,
    ) -> list[Persona]:
        """Search personas by criteria.

        Args:
            tech_adoption: Filter by technology adoption category.
            min_age: Minimum age filter.
            max_age: Maximum age filter.
            tags: Filter by tags (any match).

        Returns:
            List of matching Persona objects.
        """
        all_personas = self.list_all()
        results = []

        for persona in all_personas:
            # Tech adoption filter
            if tech_adoption:
                if persona.psychological_profile.tech_adoption.value != tech_adoption:
                    continue

            # Age filters
            if min_age is not None and persona.demographics.age < min_age:
                continue
            if max_age is not None and persona.demographics.age > max_age:
                continue

            # Tags filter (any match)
            if tags:
                persona_tags = (
                    persona.metadata.tags if persona.metadata and persona.metadata.tags else []
                )
                if not any(tag in persona_tags for tag in tags):
                    continue

            results.append(persona)

        return results

    def clear_cache(self) -> None:
        """Clear the persona cache."""
        self._cache.clear()
