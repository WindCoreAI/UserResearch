"""Integration tests for CLI commands."""

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner


class TestCLIPersonaValidate:
    """Integration tests for persona validate command."""

    def test_validate_valid_file(self, temp_persona_file):
        """Validate should succeed for valid persona file."""
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "validate", str(temp_persona_file)])

        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_validate_invalid_file_fails(self, tmp_path, invalid_persona_dict):
        """Validate should fail for invalid persona file."""
        from cli.main import cli

        invalid_file = tmp_path / "invalid.yaml"
        with open(invalid_file, "w") as f:
            yaml.dump(invalid_persona_dict, f)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "validate", str(invalid_file)])

        assert result.exit_code != 0

    def test_validate_json_output(self, temp_persona_file):
        """Validate with --json should output JSON."""
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(
            cli, ["persona", "validate", str(temp_persona_file), "--json"]
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is True


class TestCLIPersonaList:
    """Integration tests for persona list command."""

    def test_list_empty_directory(self, tmp_path, monkeypatch):
        """List should handle empty directory gracefully."""
        from cli.main import cli

        empty_dir = tmp_path / "personas" / "definitions"
        empty_dir.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "list"])

        assert result.exit_code == 0
        assert "no personas" in result.output.lower() or "0" in result.output

    def test_list_with_personas(self, temp_personas_dir, monkeypatch):
        """List should show available personas."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "list"])

        assert result.exit_code == 0
        assert "test-persona" in result.output

    def test_list_json_output(self, temp_personas_dir, monkeypatch):
        """List with --format json should output JSON."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "list", "--format", "json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "personas" in data
        assert len(data["personas"]) >= 1


class TestCLIPersonaShow:
    """Integration tests for persona show command."""

    def test_show_existing_persona(self, temp_personas_dir, monkeypatch):
        """Show should display persona details."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "show", "test-persona"])

        assert result.exit_code == 0
        assert "Test User" in result.output

    def test_show_nonexistent_persona(self, temp_personas_dir, monkeypatch):
        """Show should fail for nonexistent persona."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "show", "nonexistent"])

        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_show_json_output(self, temp_personas_dir, monkeypatch):
        """Show with --json should output JSON."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "show", "test-persona", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "demographics" in data or "id" in data

    def test_show_section_filter(self, temp_personas_dir, monkeypatch):
        """Show with --section should filter output."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(
            cli, ["persona", "show", "test-persona", "--section", "demographics"]
        )

        assert result.exit_code == 0
        assert "Age" in result.output or "age" in result.output


class TestCLIPersonaPrompt:
    """Integration tests for persona prompt command."""

    def test_prompt_generates_output(self, temp_personas_dir, monkeypatch):
        """Prompt should generate subagent prompt."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "prompt", "test-persona"])

        assert result.exit_code == 0
        assert "Test User" in result.output
        assert len(result.output) > 100  # Should be substantial

    def test_prompt_nonexistent_persona(self, temp_personas_dir, monkeypatch):
        """Prompt should fail for nonexistent persona."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)

        runner = CliRunner()
        result = runner.invoke(cli, ["persona", "prompt", "nonexistent"])

        assert result.exit_code != 0

    def test_prompt_output_to_file(self, temp_personas_dir, monkeypatch, tmp_path):
        """Prompt with -o should save to file."""
        from cli.main import cli

        monkeypatch.chdir(temp_personas_dir)
        output_file = tmp_path / "prompt.md"

        runner = CliRunner()
        result = runner.invoke(
            cli, ["persona", "prompt", "test-persona", "-o", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "Test User" in content


class TestCLIInit:
    """Integration tests for init command."""

    def test_init_creates_structure(self, tmp_path, monkeypatch):
        """Init should create project structure."""
        from cli.main import cli

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert (tmp_path / "personas" / "definitions").exists()
        assert (tmp_path / "personas" / "templates").exists()

    def test_init_success_message(self, tmp_path, monkeypatch):
        """Init should show success message."""
        from cli.main import cli

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert "success" in result.output.lower()


class TestCLIGlobalOptions:
    """Tests for global CLI options."""

    def test_version_option(self):
        """--version should show version."""
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.4.0" in result.output

    def test_help_option(self):
        """--help should show help text."""
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "persona" in result.output.lower()

    def test_quiet_option(self, temp_persona_file):
        """--quiet should suppress non-essential output."""
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(
            cli, ["-q", "persona", "validate", str(temp_persona_file)]
        )

        # Should still succeed
        assert result.exit_code == 0
