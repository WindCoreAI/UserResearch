"""Unit tests for Pydantic persona models."""

import pytest
from pydantic import ValidationError


class TestBigFiveModel:
    """Tests for BigFive personality model."""

    def test_valid_big_five_creation(self):
        """Valid Big Five traits should create successfully."""
        from models.persona import BigFive

        big_five = BigFive(
            openness=7,
            conscientiousness=6,
            extraversion=5,
            agreeableness=8,
            neuroticism=3,
        )

        assert big_five.openness == 7
        assert big_five.conscientiousness == 6
        assert big_five.extraversion == 5
        assert big_five.agreeableness == 8
        assert big_five.neuroticism == 3

    def test_big_five_boundary_values(self):
        """Big Five should accept boundary values 1 and 10."""
        from models.persona import BigFive

        big_five = BigFive(
            openness=1,
            conscientiousness=10,
            extraversion=1,
            agreeableness=10,
            neuroticism=5,
        )

        assert big_five.openness == 1
        assert big_five.conscientiousness == 10

    def test_big_five_rejects_out_of_range(self):
        """Big Five should reject values outside 1-10 range."""
        from models.persona import BigFive

        with pytest.raises(ValidationError) as exc_info:
            BigFive(
                openness=0,
                conscientiousness=5,
                extraversion=5,
                agreeableness=5,
                neuroticism=5,
            )
        assert "openness" in str(exc_info.value).lower()

        with pytest.raises(ValidationError):
            BigFive(
                openness=5,
                conscientiousness=11,
                extraversion=5,
                agreeableness=5,
                neuroticism=5,
            )

    def test_big_five_requires_all_traits(self):
        """Big Five should require all five traits."""
        from models.persona import BigFive

        with pytest.raises(ValidationError):
            BigFive(
                openness=5,
                conscientiousness=5,
                # Missing extraversion, agreeableness, neuroticism
            )


class TestDemographicsModel:
    """Tests for Demographics model."""

    def test_valid_demographics_creation(self):
        """Valid demographics should create successfully."""
        from models.persona import Demographics, Occupation

        occupation = Occupation(
            title="Software Engineer",
            industry="Technology",
            years_experience=5,
        )

        demographics = Demographics(
            age=30,
            gender="non-binary",
            location="San Francisco, CA",
            occupation=occupation,
            education="Bachelor's degree",
            income_bracket="middle",
        )

        assert demographics.age == 30
        assert demographics.gender == "non-binary"
        assert demographics.occupation.title == "Software Engineer"

    def test_demographics_age_validation(self):
        """Demographics should validate age range 18-100."""
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

        # Invalid ages
        for age in [0, 17, 101, 150]:
            with pytest.raises(ValidationError):
                Demographics(
                    age=age,
                    gender="any",
                    location="Anywhere",
                    occupation=occupation,
                )

    def test_occupation_years_experience_non_negative(self):
        """Occupation years_experience must be non-negative."""
        from models.persona import Occupation

        # Valid
        occ = Occupation(title="Developer", years_experience=0)
        assert occ.years_experience == 0

        occ = Occupation(title="Developer", years_experience=20)
        assert occ.years_experience == 20

        # Invalid
        with pytest.raises(ValidationError):
            Occupation(title="Developer", years_experience=-1)


class TestSchwartzValuesModel:
    """Tests for SchwartzValues model."""

    def test_valid_schwartz_values_creation(self):
        """Valid Schwartz values should create successfully."""
        from models.persona import SchwartzValues

        values = SchwartzValues(
            primary=["self_direction", "achievement"],
            secondary=["stimulation"],
            conflicts=["Values independence but works on dependent team"],
        )

        assert "self_direction" in values.primary
        assert "achievement" in values.primary
        assert "stimulation" in values.secondary

    def test_schwartz_values_minimum_primary(self):
        """Schwartz values requires minimum 2 primary values."""
        from models.persona import SchwartzValues

        # Valid - exactly 2
        values = SchwartzValues(primary=["self_direction", "achievement"])
        assert len(values.primary) == 2

        # Valid - more than 2
        values = SchwartzValues(
            primary=["self_direction", "achievement", "power"]
        )
        assert len(values.primary) == 3

        # Invalid - only 1
        with pytest.raises(ValidationError):
            SchwartzValues(primary=["self_direction"])

    def test_schwartz_values_validates_enum_values(self):
        """Schwartz values must be from the defined enum."""
        from models.persona import SchwartzValues

        # Valid enum values
        values = SchwartzValues(primary=["self_direction", "universalism"])
        assert len(values.primary) == 2

        # Invalid enum value
        with pytest.raises(ValidationError):
            SchwartzValues(primary=["self_direction", "invalid_value"])

    def test_schwartz_values_secondary_optional(self):
        """Secondary values should be optional."""
        from models.persona import SchwartzValues

        values = SchwartzValues(primary=["self_direction", "achievement"])
        assert values.secondary is None or values.secondary == []


class TestPersonaModel:
    """Tests for the root Persona model."""

    def test_valid_persona_creation(self, sample_persona_dict):
        """A complete valid persona should create successfully."""
        from models.persona import Persona

        persona_data = sample_persona_dict["persona"]
        persona = Persona(**persona_data)

        assert persona.id == "test-persona"
        assert persona.version == "1.0.0"
        assert persona.name == "Test User"
        assert persona.demographics.age == 30
        assert persona.psychological_profile.big_five.openness == 7

    def test_persona_requires_all_sections(self):
        """Persona must have all required sections."""
        from models.persona import Persona

        # Missing demographics
        with pytest.raises(ValidationError):
            Persona(
                id="test",
                version="1.0.0",
                name="Test",
                # Missing demographics
                psychological_profile={
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
                background={
                    "life_stage": "Working",
                    "pain_points": ["Something"],
                    "goals": ["Something"],
                },
                response_calibration={
                    "verbosity": "moderate",
                    "emotional_expressiveness": "moderate",
                    "criticism_tendency": "balanced",
                },
            )

    def test_persona_metadata_optional(self, sample_persona_dict):
        """Metadata section should be optional."""
        from models.persona import Persona

        persona_data = sample_persona_dict["persona"]
        # Remove metadata if present
        persona_data.pop("metadata", None)

        persona = Persona(**persona_data)
        assert persona.metadata is None
