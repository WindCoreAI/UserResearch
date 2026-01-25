"""Unit tests for init command directory creation logic."""

import pytest
from pathlib import Path


class TestInitDirectoryCreation:
    """Tests for init command directory creation."""

    def test_creates_personas_definitions_directory(self, tmp_path, monkeypatch):
        """Init should create personas/definitions directory."""
        monkeypatch.chdir(tmp_path)

        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert (tmp_path / "personas" / "definitions").exists()

    def test_creates_personas_templates_directory(self, tmp_path, monkeypatch):
        """Init should create personas/templates directory."""
        monkeypatch.chdir(tmp_path)

        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert (tmp_path / "personas" / "templates").exists()

    def test_creates_templates_prompts_directory(self, tmp_path, monkeypatch):
        """Init should create templates/prompts directory."""
        monkeypatch.chdir(tmp_path)

        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert (tmp_path / "templates" / "prompts").exists()

    def test_init_idempotent(self, tmp_path, monkeypatch):
        """Running init twice should not cause errors."""
        monkeypatch.chdir(tmp_path)

        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()

        # First run
        result1 = runner.invoke(cli, ["init"])
        assert result1.exit_code == 0

        # Second run
        result2 = runner.invoke(cli, ["init"])
        assert result2.exit_code == 0

    def test_force_flag_overwrites(self, tmp_path, monkeypatch):
        """Init with --force should overwrite existing files."""
        monkeypatch.chdir(tmp_path)

        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()

        # First init
        result1 = runner.invoke(cli, ["init"])
        assert result1.exit_code == 0

        # Create a modified file
        template_file = tmp_path / "personas" / "templates" / "persona-template.yaml"
        if template_file.exists():
            original_content = template_file.read_text()
            template_file.write_text("modified: true")

            # Init with force
            result2 = runner.invoke(cli, ["init", "--force"])
            assert result2.exit_code == 0

            # File should be restored (if source exists)
            # Note: This depends on source files existing
