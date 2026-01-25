"""Unit tests for PromptBuilder service."""

import pytest


class TestPromptBuilder:
    """Tests for PromptBuilder service."""

    def test_build_returns_string(self, sample_persona_dict):
        """Build should return a non-empty string."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_build_includes_persona_name(self, sample_persona_dict):
        """Prompt should include the persona's name."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        assert persona.name in prompt

    def test_build_includes_demographics(self, sample_persona_dict):
        """Prompt should include demographic information."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        assert str(persona.demographics.age) in prompt
        assert persona.demographics.location in prompt
        assert persona.demographics.occupation.title in prompt

    def test_build_includes_big_five_traits(self, sample_persona_dict):
        """Prompt should include Big Five personality traits."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        # Should mention openness, conscientiousness, etc.
        assert "openness" in prompt.lower() or "Openness" in prompt
        assert "conscientiousness" in prompt.lower() or "Conscientiousness" in prompt

    def test_build_includes_schwartz_values(self, sample_persona_dict):
        """Prompt should include Schwartz values."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        # Should mention primary values
        assert "self direction" in prompt.lower() or "Self Direction" in prompt

    def test_build_includes_tech_adoption(self, sample_persona_dict):
        """Prompt should include technology adoption category."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        # Should describe the adoption category
        assert "early adopter" in prompt.lower() or "Early Adopter" in prompt

    def test_build_includes_pain_points(self, sample_persona_dict):
        """Prompt should include pain points from background."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        for pain_point in persona.background.pain_points:
            assert pain_point in prompt

    def test_build_includes_goals(self, sample_persona_dict):
        """Prompt should include goals from background."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        for goal in persona.background.goals:
            assert goal in prompt

    def test_build_includes_response_calibration(self, sample_persona_dict):
        """Prompt should include response calibration guidelines."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        # Should describe verbosity and other calibration settings
        assert "verbosity" in prompt.lower() or "Verbosity" in prompt

    def test_build_includes_anti_sycophancy_instructions(self, sample_persona_dict):
        """Prompt should include anti-sycophancy instructions."""
        from models.persona import Persona
        from services.prompt_builder import PromptBuilder

        persona = Persona(**sample_persona_dict["persona"])
        builder = PromptBuilder()

        prompt = builder.build(persona)

        # Should include key anti-sycophancy phrases
        assert "not be overly positive" in prompt.lower() or "skepticism" in prompt.lower()
