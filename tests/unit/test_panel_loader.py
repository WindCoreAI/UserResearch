"""Unit tests for PanelLoader service."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml


class TestPanelLoader:
    """Tests for PanelLoader service."""

    def test_load_valid_panel(self, temp_panel_file):
        """Test loading a valid panel from YAML file."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader()
        panel = loader.load(temp_panel_file)

        assert panel.id == "test-panel"
        assert panel.name == "Test Panel"
        assert len(panel.persona_ids) == 3

    def test_load_nonexistent_file(self):
        """Test loading from a file that doesn't exist."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader()

        with pytest.raises(FileNotFoundError):
            loader.load("/nonexistent/path/panel.yaml")

    def test_load_invalid_yaml(self):
        """Test loading from a file with invalid YAML syntax."""
        from services.panel_loader import PanelLoader, PanelLoaderError

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = PanelLoader()
            with pytest.raises(PanelLoaderError) as exc_info:
                loader.load(temp_path)
            assert "YAML" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    def test_load_empty_file(self):
        """Test loading from an empty file."""
        from services.panel_loader import PanelLoader, PanelLoaderError

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = PanelLoader()
            with pytest.raises(PanelLoaderError) as exc_info:
                loader.load(temp_path)
            assert "Empty" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    def test_load_invalid_schema(self):
        """Test loading from a file with invalid panel schema."""
        from services.panel_loader import PanelLoader, PanelLoaderError

        invalid_panel = {
            "id": "test",
            "name": "Test",
            # Missing required fields
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(invalid_panel, f)
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = PanelLoader()
            with pytest.raises(PanelLoaderError) as exc_info:
                loader.load(temp_path)
            assert "validation" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)

    def test_validate_valid_file(self, temp_panel_file):
        """Test validation of a valid panel file."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader()
        result = loader.validate(temp_panel_file)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_file(self):
        """Test validation of an invalid panel file."""
        from services.panel_loader import PanelLoader

        invalid_panel = {"id": "test"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(invalid_panel, f)
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = PanelLoader()
            result = loader.validate(temp_path)

            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            os.unlink(temp_path)

    def test_validate_nonexistent_file(self):
        """Test validation of a nonexistent file."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader()
        result = loader.validate("/nonexistent/panel.yaml")

        assert result.is_valid is False
        assert any("not found" in err.lower() for err in result.errors)

    def test_load_from_string(self, sample_panel_yaml):
        """Test loading a panel from YAML string."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader()
        panel = loader.load_from_string(sample_panel_yaml)

        assert panel.id == "test-panel"
        assert panel.name == "Test Panel"

    def test_load_from_string_invalid(self):
        """Test loading from invalid YAML string."""
        from services.panel_loader import PanelLoader, PanelLoaderError

        loader = PanelLoader()

        with pytest.raises(PanelLoaderError):
            loader.load_from_string("invalid: yaml: [")


class TestPanelLoaderDirectories:
    """Tests for PanelLoader directory operations."""

    def test_load_all_panels(self, temp_panels_dir):
        """Test loading all panels from definitions directory."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader(panels_dir=temp_panels_dir / "panels")
        panels = loader.load_all()

        assert len(panels) >= 1
        assert any(p.id == "test-panel" for p in panels)

    def test_load_all_with_custom_panels(self, temp_panels_dir, sample_panel_dict):
        """Test loading all panels including custom panels."""
        from services.panel_loader import PanelLoader

        # Create a custom panel
        custom_panel = sample_panel_dict.copy()
        custom_panel["id"] = "custom-panel"
        custom_panel["is_custom"] = True

        custom_dir = temp_panels_dir / "panels" / "custom"
        with open(custom_dir / "custom-panel.yaml", "w") as f:
            yaml.dump(custom_panel, f)

        loader = PanelLoader(panels_dir=temp_panels_dir / "panels")
        panels = loader.load_all()

        assert len(panels) >= 2
        assert any(p.id == "custom-panel" for p in panels)
        assert any(p.id == "test-panel" for p in panels)

    def test_load_panel_by_id(self, temp_panels_dir):
        """Test loading a specific panel by ID."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader(panels_dir=temp_panels_dir / "panels")
        panel = loader.load_by_id("test-panel")

        assert panel.id == "test-panel"

    def test_load_panel_by_id_not_found(self, temp_panels_dir):
        """Test loading a nonexistent panel by ID."""
        from services.panel_loader import PanelLoader, PanelLoaderError

        loader = PanelLoader(panels_dir=temp_panels_dir / "panels")

        with pytest.raises(PanelLoaderError) as exc_info:
            loader.load_by_id("nonexistent-panel")

        assert "not found" in str(exc_info.value).lower()

    def test_list_prebuilt_panels(self, temp_panels_dir):
        """Test listing only pre-built panels."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader(panels_dir=temp_panels_dir / "panels")
        panels = loader.list_panels(panel_type="prebuilt")

        assert all(not p.is_custom for p in panels)

    def test_list_custom_panels(self, temp_panels_dir, sample_panel_dict):
        """Test listing only custom panels."""
        from services.panel_loader import PanelLoader

        # Create a custom panel
        custom_panel = sample_panel_dict.copy()
        custom_panel["id"] = "my-custom"
        custom_panel["is_custom"] = True

        custom_dir = temp_panels_dir / "panels" / "custom"
        with open(custom_dir / "my-custom.yaml", "w") as f:
            yaml.dump(custom_panel, f)

        loader = PanelLoader(panels_dir=temp_panels_dir / "panels")
        panels = loader.list_panels(panel_type="custom")

        assert all(p.is_custom for p in panels)


class TestPanelLoaderValidation:
    """Tests for PanelLoader validation of persona IDs."""

    def test_validate_panel_with_invalid_personas(self, temp_panels_dir):
        """Test that validation catches invalid persona IDs."""
        from services.panel_loader import PanelLoader

        loader = PanelLoader(panels_dir=temp_panels_dir / "panels")

        # Validate should check personas exist (when persona loader is available)
        result = loader.validate_panel_personas(
            panel_id="test-panel",
            available_persona_ids=["persona-a", "persona-b"],
        )

        # The test-panel has personas not in available list
        assert result.is_valid is False
        assert len(result.missing_personas) > 0
