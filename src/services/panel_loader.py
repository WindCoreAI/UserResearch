"""Service for loading and validating panel YAML files."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import ValidationError

from models.panel import ResearchPanel


class PanelLoaderError(Exception):
    """Error raised when panel loading fails."""

    def __init__(self, message: str, file_path: Union[str, Path, None] = None):
        self.file_path = file_path
        super().__init__(message)


@dataclass
class ValidationResult:
    """Result of panel validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class PersonaValidationResult:
    """Result of validating panel personas against available personas."""

    is_valid: bool
    missing_personas: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class PanelLoader:
    """Service for loading and validating panel YAML files."""

    def __init__(self, panels_dir: Optional[Union[str, Path]] = None):
        """Initialize the panel loader.

        Args:
            panels_dir: Root directory containing definitions/ and custom/ subdirs.
                       Defaults to 'panels/' in the project root.
        """
        if panels_dir is None:
            # Default to project root panels directory
            self.panels_dir = Path(__file__).parent.parent.parent / "panels"
        else:
            self.panels_dir = Path(panels_dir)

        self.definitions_dir = self.panels_dir / "definitions"
        self.custom_dir = self.panels_dir / "custom"

    def load(self, file_path: Union[str, Path]) -> ResearchPanel:
        """Load a panel from a YAML file.

        Args:
            file_path: Path to the panel YAML file.

        Returns:
            Validated ResearchPanel object.

        Raises:
            FileNotFoundError: If the file does not exist.
            PanelLoaderError: If the file contains invalid YAML or schema.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Panel file not found: {path}")

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PanelLoaderError(
                f"Invalid YAML syntax: {e}",
                file_path=path,
            ) from e

        if not data:
            raise PanelLoaderError(
                "Empty YAML file",
                file_path=path,
            )

        return self._parse_panel_data(data, path)

    def _parse_panel_data(
        self, data: dict, file_path: Optional[Path] = None
    ) -> ResearchPanel:
        """Parse panel data dictionary into ResearchPanel model.

        Args:
            data: Dictionary containing panel data.
            file_path: Optional path for error messages.

        Returns:
            Validated ResearchPanel object.

        Raises:
            PanelLoaderError: If validation fails.
        """
        # Handle 'created_at' field - convert string to datetime if needed
        if "created_at" in data and isinstance(data["created_at"], str):
            try:
                data["created_at"] = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            except ValueError:
                # Try parsing as date only
                data["created_at"] = datetime.strptime(
                    data["created_at"], "%Y-%m-%d"
                ).replace(tzinfo=timezone.utc)

        # If created_at is missing, set to now
        if "created_at" not in data:
            data["created_at"] = datetime.now(timezone.utc)

        # Determine if custom based on file location
        if "is_custom" not in data:
            if file_path:
                data["is_custom"] = "custom" in str(file_path)
            else:
                data["is_custom"] = False

        try:
            return ResearchPanel(**data)
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                location = " -> ".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{location}: {error['msg']}")

            raise PanelLoaderError(
                "Schema validation failed:\n" + "\n".join(error_messages),
                file_path=file_path,
            ) from e

    def validate(self, file_path: Union[str, Path]) -> ValidationResult:
        """Validate a panel file without raising exceptions.

        Args:
            file_path: Path to the panel YAML file.

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
        except PanelLoaderError as e:
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

    def load_from_string(self, yaml_content: str) -> ResearchPanel:
        """Load a panel from a YAML string.

        Args:
            yaml_content: YAML content as string.

        Returns:
            Validated ResearchPanel object.

        Raises:
            PanelLoaderError: If the content is invalid.
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise PanelLoaderError(f"Invalid YAML syntax: {e}") from e

        if not data:
            raise PanelLoaderError("Empty YAML content")

        return self._parse_panel_data(data)

    def load_all(self) -> list[ResearchPanel]:
        """Load all panels from definitions and custom directories.

        Returns:
            List of all valid ResearchPanel objects.
        """
        panels = []

        # Load pre-built panels
        if self.definitions_dir.exists():
            for panel_file in self.definitions_dir.glob("*.yaml"):
                try:
                    panel = self.load(panel_file)
                    panels.append(panel)
                except (PanelLoaderError, FileNotFoundError):
                    # Skip invalid panels
                    pass

        # Load custom panels
        if self.custom_dir.exists():
            for panel_file in self.custom_dir.glob("*.yaml"):
                try:
                    panel = self.load(panel_file)
                    panels.append(panel)
                except (PanelLoaderError, FileNotFoundError):
                    # Skip invalid panels
                    pass

        return panels

    def load_by_id(self, panel_id: str) -> ResearchPanel:
        """Load a specific panel by ID.

        Args:
            panel_id: The panel ID to find.

        Returns:
            ResearchPanel if found.

        Raises:
            PanelLoaderError: If panel is not found.
        """
        # Check definitions first
        definitions_path = self.definitions_dir / f"{panel_id}.yaml"
        if definitions_path.exists():
            return self.load(definitions_path)

        # Check custom panels
        custom_path = self.custom_dir / f"{panel_id}.yaml"
        if custom_path.exists():
            return self.load(custom_path)

        raise PanelLoaderError(f"Panel not found: {panel_id}")

    def list_panels(
        self, panel_type: str = "all"
    ) -> list[ResearchPanel]:
        """List panels filtered by type.

        Args:
            panel_type: Filter type - 'all', 'prebuilt', or 'custom'.

        Returns:
            List of ResearchPanel objects matching the filter.
        """
        panels = self.load_all()

        if panel_type == "prebuilt":
            return [p for p in panels if not p.is_custom]
        elif panel_type == "custom":
            return [p for p in panels if p.is_custom]
        else:
            return panels

    def validate_panel_personas(
        self,
        panel_id: str,
        available_persona_ids: list[str],
    ) -> PersonaValidationResult:
        """Validate that all personas in a panel exist.

        Args:
            panel_id: The panel to validate.
            available_persona_ids: List of valid persona IDs.

        Returns:
            PersonaValidationResult with any missing personas.
        """
        try:
            panel = self.load_by_id(panel_id)
        except PanelLoaderError as e:
            return PersonaValidationResult(
                is_valid=False,
                errors=[str(e)],
            )

        missing = [
            pid for pid in panel.persona_ids
            if pid not in available_persona_ids
        ]

        if missing:
            return PersonaValidationResult(
                is_valid=False,
                missing_personas=missing,
                errors=[f"Missing personas: {', '.join(missing)}"],
            )

        return PersonaValidationResult(is_valid=True)

    def save_custom_panel(self, panel: ResearchPanel) -> Path:
        """Save a custom panel to the custom directory.

        Args:
            panel: The panel to save.

        Returns:
            Path to the saved file.

        Raises:
            PanelLoaderError: If panel ID conflicts with pre-built panel.
        """
        # Check for conflict with pre-built panels
        prebuilt_path = self.definitions_dir / f"{panel.id}.yaml"
        if prebuilt_path.exists():
            raise PanelLoaderError(
                f"Cannot create custom panel with ID '{panel.id}': "
                "conflicts with pre-built panel"
            )

        # Ensure custom directory exists
        self.custom_dir.mkdir(parents=True, exist_ok=True)

        # Save panel
        output_path = self.custom_dir / f"{panel.id}.yaml"
        panel_data = panel.to_dict()

        with open(output_path, "w") as f:
            yaml.dump(panel_data, f, default_flow_style=False, sort_keys=False)

        return output_path

    def delete_custom_panel(self, panel_id: str) -> bool:
        """Delete a custom panel.

        Args:
            panel_id: The panel ID to delete.

        Returns:
            True if deleted successfully.

        Raises:
            PanelLoaderError: If trying to delete pre-built panel or panel not found.
        """
        # Check if it's a pre-built panel
        prebuilt_path = self.definitions_dir / f"{panel_id}.yaml"
        if prebuilt_path.exists():
            raise PanelLoaderError(
                f"Cannot delete pre-built panel: {panel_id}"
            )

        # Check if custom panel exists
        custom_path = self.custom_dir / f"{panel_id}.yaml"
        if not custom_path.exists():
            raise PanelLoaderError(f"Custom panel not found: {panel_id}")

        custom_path.unlink()
        return True

    def panel_exists(self, panel_id: str) -> bool:
        """Check if a panel exists by ID.

        Args:
            panel_id: The panel ID to check.

        Returns:
            True if panel exists.
        """
        definitions_path = self.definitions_dir / f"{panel_id}.yaml"
        custom_path = self.custom_dir / f"{panel_id}.yaml"
        return definitions_path.exists() or custom_path.exists()
