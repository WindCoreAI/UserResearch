"""Service for executing survey research.

Handles survey execution with sequential question execution,
response parsing, and validation.
"""

import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from models.enums import SurveyQuestionType
from models.persona import Persona
from models.survey import (
    Survey,
    SurveyQuestion,
    SurveyResponse,
    SurveyResult,
)
from services.prompt_builder import PromptBuilder
from services.session_runner import SessionRunner

# Default survey question template
DEFAULT_SURVEY_PROMPT = """{{ persona_prompt }}

---

## Survey Question {{ question_number }} of {{ total_questions }}

{{ question.text }}

{% if question.type.value == "rating" %}
**Question Type**: Rating Scale ({{ question.scale_min }}-{{ question.scale_max }})

Please provide your rating as a number between {{ question.scale_min }} and {{ question.scale_max }}.
{% if question.scale_labels %}
Scale guide:
{% for value, label in question.scale_labels.items() %}
- {{ value }}: {{ label }}
{% endfor %}
{% endif %}

Respond with your rating number first, then explain your reasoning.
Format: "Rating: [number]. [Your explanation]"

{% elif question.type.value == "multiple_choice" %}
**Question Type**: Multiple Choice

Please select ONE of the following options:
{% for option in question.options %}
- {{ option }}
{% endfor %}

Respond with your chosen option first, then explain your choice.
Format: "Selected: [option]. [Your reasoning]"

{% else %}
**Question Type**: Open-Ended

Please share your detailed thoughts on this question. Be specific and provide examples where relevant.
{% endif %}

---

Remember to respond authentically as {{ persona_name }}, reflecting your personality traits, values, and typical communication style. Your honest feedback is valuable."""


class SurveyEngine:
    """Executes survey research sessions.

    Handles sequential question execution, response parsing,
    validation, and result aggregation.
    """

    def __init__(
        self,
        persona_loader=None,
        session_runner: SessionRunner | None = None,
        template_path: Path | None = None,
    ):
        """Initialize the survey engine.

        Args:
            persona_loader: Optional custom persona loader.
            session_runner: Optional custom session runner.
            template_path: Optional path to custom survey template.
        """
        self.persona_loader = persona_loader
        self.session_runner = session_runner or SessionRunner()
        self.prompt_builder = PromptBuilder()
        self.template_path = template_path
        self._template: Template | None = None

    def _get_survey_template(self) -> Template:
        """Get the Jinja2 template for survey prompts."""
        if self._template is not None:
            return self._template

        # Try to load from templates directory
        template_locations = [
            Path("src/templates/survey_prompt.j2"),
            Path(__file__).parent.parent / "templates" / "survey_prompt.j2",
        ]

        if self.template_path:
            template_locations.insert(0, self.template_path)

        for path in template_locations:
            if path.exists():
                env = Environment(
                    loader=FileSystemLoader(path.parent),
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
                self._template = env.get_template(path.name)
                return self._template

        # Fall back to default embedded template
        env = Environment(trim_blocks=True, lstrip_blocks=True)
        self._template = env.from_string(DEFAULT_SURVEY_PROMPT)
        return self._template

    def _build_question_prompt(
        self,
        question: SurveyQuestion,
        question_number: int,
        total_questions: int,
        persona_prompt: str = "",
        persona_name: str = "",
    ) -> str:
        """Build the prompt for a single survey question.

        Args:
            question: The question to render.
            question_number: Current question number (1-indexed).
            total_questions: Total number of questions.
            persona_prompt: The persona context prompt.
            persona_name: Persona's display name.

        Returns:
            Complete prompt text for the question.
        """
        template = self._get_survey_template()

        return template.render(
            persona_prompt=persona_prompt,
            persona_name=persona_name,
            question=question,
            question_number=question_number,
            total_questions=total_questions,
        )

    def _parse_rating(
        self, response: str, scale_min: int, scale_max: int
    ) -> int | None:
        """Parse a rating value from response text.

        Args:
            response: Raw response text.
            scale_min: Minimum scale value.
            scale_max: Maximum scale value.

        Returns:
            Parsed rating value (clamped to range), or None if not found.
        """
        # Look for numeric patterns
        patterns = [
            r"(?:rating[:\s]*)?(\d+)(?:/\d+)?",
            r"(?:score[:\s]*)(\d+)",
            r"^(\d+)\b",
            r"\b(\d+)\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                # Clamp to range
                return max(scale_min, min(scale_max, value))

        return None

    def _parse_multiple_choice(
        self, response: str, options: list[str]
    ) -> str | None:
        """Parse a multiple choice selection from response text.

        Args:
            response: Raw response text.
            options: Available options.

        Returns:
            Matched option, or None if not found.
        """
        response_lower = response.lower()

        # Try exact match first
        for option in options:
            if option.lower() in response_lower:
                return option

        # Try partial match
        for option in options:
            # Match first significant word
            first_word = option.split()[0].lower()
            if first_word in response_lower and len(first_word) > 3:
                return option

        return None

    def _validate_response(
        self,
        question: SurveyQuestion,
        rating_value: int | None = None,
        selected_option: str | None = None,
        original_value: int | None = None,
    ) -> tuple[bool, list[str]]:
        """Validate a parsed response.

        Args:
            question: The question being validated.
            rating_value: Parsed rating value.
            selected_option: Parsed selected option.
            original_value: Original value before clamping (for warnings).

        Returns:
            Tuple of (is_valid, warnings list).
        """
        warnings = []
        is_valid = True

        if question.type == SurveyQuestionType.RATING:
            if rating_value is None:
                is_valid = question.required is False
            elif original_value is not None and original_value != rating_value:
                warnings.append(
                    f"Value was clamped from {original_value} to {rating_value}"
                )

        elif question.type == SurveyQuestionType.MULTIPLE_CHOICE:
            if selected_option is None:
                is_valid = question.required is False
            elif question.options and selected_option not in question.options:
                is_valid = False
                warnings.append(f"Selected option '{selected_option}' is not valid")

        return is_valid, warnings

    def execute_survey(
        self,
        survey: Survey,
        persona: Persona,
        execute_fn: Callable[[str], str] | None = None,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> SurveyResult:
        """Execute a survey with a single persona.

        Args:
            survey: The survey to execute.
            persona: The persona to simulate.
            execute_fn: Optional function to execute prompts.
                        If None, creates task specification only.
            progress_callback: Optional callback for progress updates.

        Returns:
            SurveyResult with all responses.
        """
        started_at = datetime.now(UTC)
        responses: list[SurveyResponse] = []

        # Build persona prompt once
        persona_prompt = self.prompt_builder.build(persona)

        for i, question in enumerate(survey.questions):
            question_number = i + 1

            # Build question prompt
            prompt = self._build_question_prompt(
                question=question,
                question_number=question_number,
                total_questions=len(survey.questions),
                persona_prompt=persona_prompt,
                persona_name=persona.name,
            )

            # Execute if function provided
            if execute_fn:
                raw_response = execute_fn(prompt)
            else:
                raw_response = f"[Task specification generated for question {question_number}]"

            # Parse response based on type
            rating_value = None
            selected_option = None
            text_response = None

            if question.type == SurveyQuestionType.RATING:
                rating_value = self._parse_rating(
                    raw_response,
                    question.scale_min or 1,
                    question.scale_max or 10,
                )
            elif question.type == SurveyQuestionType.MULTIPLE_CHOICE:
                selected_option = self._parse_multiple_choice(
                    raw_response,
                    question.options or [],
                )
            else:
                text_response = raw_response

            # Validate
            is_valid, warnings = self._validate_response(
                question,
                rating_value=rating_value,
                selected_option=selected_option,
            )

            # Create response
            response = SurveyResponse(
                question_id=question.id,
                question_type=question.type,
                raw_response=raw_response,
                rating_value=rating_value,
                selected_option=selected_option,
                text_response=text_response,
                is_valid=is_valid,
                validation_warnings=warnings,
            )
            responses.append(response)

            # Progress callback
            if progress_callback:
                progress_callback(question_number, len(survey.questions), question.id)

        completed_at = datetime.now(UTC)
        total_time_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Calculate completion rate
        valid_responses = sum(1 for r in responses if r.is_valid)
        completion_rate = valid_responses / len(survey.questions) if survey.questions else 0

        return SurveyResult(
            survey_id=survey.id,
            survey_version=survey.version,
            persona_id=persona.id,
            responses=responses,
            started_at=started_at,
            completed_at=completed_at,
            total_time_ms=total_time_ms,
            completion_rate=completion_rate,
        )

    def get_task_specification(
        self,
        survey: Survey,
        persona: Persona,
    ) -> dict:
        """Generate task specification for a survey execution.

        Creates the full prompt and metadata needed to execute
        the survey with a Claude Code subagent.

        Args:
            survey: The survey to execute.
            persona: The persona to simulate.

        Returns:
            Dictionary with task specification.
        """
        persona_prompt = self.prompt_builder.build(persona)

        # Build prompts for all questions
        question_prompts = []
        for i, question in enumerate(survey.questions):
            prompt = self._build_question_prompt(
                question=question,
                question_number=i + 1,
                total_questions=len(survey.questions),
                persona_prompt=persona_prompt,
                persona_name=persona.name,
            )
            question_prompts.append({
                "question_id": question.id,
                "question_type": question.type.value,
                "prompt": prompt,
            })

        return {
            "survey_id": survey.id,
            "survey_version": survey.version,
            "persona_id": persona.id,
            "persona_name": persona.name,
            "total_questions": len(survey.questions),
            "question_prompts": question_prompts,
        }
