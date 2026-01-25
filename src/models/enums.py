"""Enumerations for persona schema validation.

Defines the constrained value sets for psychological frameworks
and response calibration settings.
"""

from enum import Enum


class TechAdoptionCategory(str, Enum):
    """Rogers' Diffusion of Innovations categories.

    Represents how quickly individuals adopt new technologies.
    Population distribution percentages are approximate.
    """

    INNOVATOR = "innovator"  # ~2.5% - Risk-tolerant, first to try
    EARLY_ADOPTER = "early_adopter"  # ~13.5% - Opinion leaders, strategic
    EARLY_MAJORITY = "early_majority"  # ~34% - Pragmatic, waits for proof
    LATE_MAJORITY = "late_majority"  # ~34% - Skeptical, peer pressure
    LAGGARD = "laggard"  # ~16% - Traditional, resists change


class SchwartzValue(str, Enum):
    """Schwartz's Theory of Basic Human Values.

    Ten universal values validated across 82+ countries.
    Adjacent values on the circumplex are compatible;
    opposite values may create behavioral tension.
    """

    SELF_DIRECTION = "self_direction"  # Independence, creativity, curiosity
    STIMULATION = "stimulation"  # Excitement, novelty, challenge
    HEDONISM = "hedonism"  # Pleasure, enjoyment
    ACHIEVEMENT = "achievement"  # Personal success, competence
    POWER = "power"  # Dominance, control, wealth
    SECURITY = "security"  # Safety, stability, order
    CONFORMITY = "conformity"  # Restraint, obedience to norms
    TRADITION = "tradition"  # Respect for customs, culture
    BENEVOLENCE = "benevolence"  # Welfare of close others
    UNIVERSALISM = "universalism"  # Tolerance, equality for all


class VerbosityLevel(str, Enum):
    """Response length tendency for persona calibration."""

    CONCISE = "concise"  # Brief, to-the-point responses
    MODERATE = "moderate"  # Balanced detail level
    DETAILED = "detailed"  # Thorough, elaborate responses


class ExpressivenessLevel(str, Enum):
    """Emotional display level for persona calibration."""

    RESERVED = "reserved"  # Minimal emotional display
    MODERATE = "moderate"  # Natural emotional expression
    EXPRESSIVE = "expressive"  # Strong emotional display


class CriticismLevel(str, Enum):
    """Tendency toward positive or critical feedback."""

    POSITIVE = "positive"  # Tends toward optimistic feedback
    BALANCED = "balanced"  # Mix of positive and negative
    CRITICAL = "critical"  # Tends toward skeptical feedback


class CertaintyLevel(str, Enum):
    """Confidence level in expressing opinions."""

    CERTAIN = "certain"  # Strong, definitive opinions
    QUESTIONING = "questioning"  # Exploratory, considers alternatives
    UNCERTAIN = "uncertain"  # Hesitant, acknowledges limitations
