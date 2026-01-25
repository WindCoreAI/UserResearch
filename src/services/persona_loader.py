"""Service for loading and validating persona YAML files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

import yaml
from pydantic import ValidationError

from models.persona import Persona


class PersonaLoaderError(Exception):
    """Error raised when persona loading fails."""

    def __init__(self, message: str, file_path: Union[str, Path, None] = None):
        self.file_path = file_path
        super().__init__(message)


@dataclass
class ValidationResult:
    """Result of persona validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class PersonaLoader:
    """Service for loading and validating persona YAML files."""

    def load(self, file_path: Union[str, Path]) -> Persona:
        """Load a persona from a YAML file.

        Args:
            file_path: Path to the persona YAML file.

        Returns:
            Validated Persona object.

        Raises:
            FileNotFoundError: If the file does not exist.
            PersonaLoaderError: If the file contains invalid YAML or schema.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Persona file not found: {path}")

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PersonaLoaderError(
                f"Invalid YAML syntax: {e}",
                file_path=path,
            ) from e

        if not data:
            raise PersonaLoaderError(
                "Empty YAML file",
                file_path=path,
            )

        # Extract persona data from wrapper if present
        if "persona" in data:
            persona_data = data["persona"]
        else:
            persona_data = data

        try:
            return Persona(**persona_data)
        except ValidationError as e:
            # Format validation errors with context
            error_messages = []
            for error in e.errors():
                location = " -> ".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{location}: {error['msg']}")

            raise PersonaLoaderError(
                "Schema validation failed:\n" + "\n".join(error_messages),
                file_path=path,
            ) from e

    def validate(self, file_path: Union[str, Path]) -> ValidationResult:
        """Validate a persona file without raising exceptions.

        Args:
            file_path: Path to the persona YAML file.

        Returns:
            ValidationResult with is_valid status and any errors.
        """
        path = Path(file_path)

        if not path.exists():
            return ValidationResult(
                is_valid=False,
                errors=[f"File not found: {path}"],
            )

        try:
            self.load(path)
            return ValidationResult(is_valid=True)
        except PersonaLoaderError as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(e)],
            )
        except FileNotFoundError as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(e)],
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unexpected error: {e}"],
            )

    def load_from_string(self, yaml_content: str) -> Persona:
        """Load a persona from a YAML string.

        Args:
            yaml_content: YAML content as string.

        Returns:
            Validated Persona object.

        Raises:
            PersonaLoaderError: If the content is invalid.
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise PersonaLoaderError(f"Invalid YAML syntax: {e}") from e

        if not data:
            raise PersonaLoaderError("Empty YAML content")

        # Extract persona data from wrapper if present
        if "persona" in data:
            persona_data = data["persona"]
        else:
            persona_data = data

        try:
            return Persona(**persona_data)
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                location = " -> ".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{location}: {error['msg']}")

            raise PersonaLoaderError(
                "Schema validation failed:\n" + "\n".join(error_messages)
            ) from e
