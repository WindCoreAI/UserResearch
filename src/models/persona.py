"""Pydantic models for persona schema validation.

Defines the complete persona data structure with validation rules
for psychological frameworks and demographic information.
"""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models.enums import (
    CertaintyLevel,
    CriticismLevel,
    ExpressivenessLevel,
    SchwartzValue,
    TechAdoptionCategory,
    VerbosityLevel,
)


class Occupation(BaseModel):
    """Employment details for the persona."""

    title: str = Field(..., min_length=1, description="Job title")
    industry: Optional[str] = Field(None, description="Industry sector")
    organization: Optional[str] = Field(None, description="Company/organization name")
    years_experience: Optional[int] = Field(
        None, ge=0, description="Years in current field"
    )


class Demographics(BaseModel):
    """Demographic characteristics of the persona."""

    age: int = Field(..., ge=18, le=100, description="Age in years (18-100)")
    gender: str = Field(..., description="Gender identity")
    location: str = Field(..., min_length=1, description="Geographic location")
    occupation: Occupation = Field(..., description="Job details")
    education: Optional[str] = Field(None, description="Highest education level")
    income_bracket: Optional[str] = Field(None, description="Relative income level")
    family_status: Optional[str] = Field(None, description="Family/relationship status")


class BigFive(BaseModel):
    """The Five Factor Model personality traits.

    All traits use a 1-10 integer scale where:
    - 1-3: Low
    - 4-6: Medium
    - 7-10: High
    """

    openness: int = Field(
        ..., ge=1, le=10, description="Openness to experience (1-10)"
    )
    conscientiousness: int = Field(
        ..., ge=1, le=10, description="Organization and dependability (1-10)"
    )
    extraversion: int = Field(
        ..., ge=1, le=10, description="Social energy and assertiveness (1-10)"
    )
    agreeableness: int = Field(
        ..., ge=1, le=10, description="Cooperation and trust (1-10)"
    )
    neuroticism: int = Field(
        ..., ge=1, le=10, description="Emotional reactivity (1-10)"
    )


class SchwartzValues(BaseModel):
    """Value priorities from Schwartz's Theory of Basic Values."""

    primary: list[SchwartzValue] = Field(
        ..., min_length=2, description="Primary value priorities (min 2)"
    )
    secondary: Optional[list[SchwartzValue]] = Field(
        None, description="Secondary values"
    )
    conflicts: Optional[list[str]] = Field(
        None, description="Described value tensions"
    )


class PsychologicalProfile(BaseModel):
    """Core psychological characteristics."""

    big_five: BigFive = Field(..., description="Big Five personality traits")
    schwartz_values: SchwartzValues = Field(..., description="Value priorities")
    tech_adoption: TechAdoptionCategory = Field(
        ..., description="Technology adoption category"
    )


class Background(BaseModel):
    """Life context and narrative elements."""

    life_stage: str = Field(..., min_length=1, description="Current life phase")
    key_experiences: Optional[list[str]] = Field(
        None, description="Formative experiences"
    )
    pain_points: list[str] = Field(
        ..., min_length=1, description="Current frustrations/challenges"
    )
    goals: list[str] = Field(..., min_length=1, description="Aspirations and objectives")


class ResponseCalibration(BaseModel):
    """Settings that tune how the persona responds."""

    verbosity: VerbosityLevel = Field(..., description="Response length tendency")
    emotional_expressiveness: ExpressivenessLevel = Field(
        ..., description="Emotional display level"
    )
    criticism_tendency: CriticismLevel = Field(
        ..., description="Positive vs critical lean"
    )
    certainty_level: Optional[CertaintyLevel] = Field(
        None, description="Confidence in opinions"
    )


class Metadata(BaseModel):
    """Tracking and organizational information."""

    created_date: Optional[str] = Field(None, description="Creation date (ISO format)")
    created_by: Optional[str] = Field(None, description="Creator identifier")
    panel_memberships: Optional[list[str]] = Field(
        None, description="Panels this persona belongs to"
    )
    tags: Optional[list[str]] = Field(None, description="Searchable tags")


# Pattern for kebab-case validation
KEBAB_CASE_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Pattern for semantic versioning
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


class Persona(BaseModel):
    """The top-level entity representing a synthetic user.

    A persona defines a complete synthetic user profile with psychological
    frameworks (Big Five, Schwartz values), demographic information,
    background narrative, and response calibration settings.
    """

    id: str = Field(..., description="Unique identifier (kebab-case)")
    version: str = Field(..., description="Semantic version (e.g., 1.0.0)")
    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    demographics: Demographics = Field(..., description="Demographic information")
    psychological_profile: PsychologicalProfile = Field(
        ..., description="Personality and values"
    )
    background: Background = Field(..., description="Life context and experiences")
    response_calibration: ResponseCalibration = Field(
        ..., description="Behavior tuning settings"
    )
    metadata: Optional[Metadata] = Field(None, description="Optional tracking info")

    @field_validator("id")
    @classmethod
    def validate_id_kebab_case(cls, v: str) -> str:
        """Validate that ID follows kebab-case pattern."""
        if not KEBAB_CASE_PATTERN.match(v):
            raise ValueError(
                f"ID must be kebab-case (lowercase letters, numbers, hyphens): {v}"
            )
        return v

    @field_validator("version")
    @classmethod
    def validate_version_semver(cls, v: str) -> str:
        """Validate that version follows semantic versioning."""
        if not SEMVER_PATTERN.match(v):
            raise ValueError(
                f"Version must follow semver format (X.Y.Z): {v}"
            )
        return v
