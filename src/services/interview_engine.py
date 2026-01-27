"""Service for executing in-depth interview research.

Handles interview execution with sections, probing,
and follow-up question logic.
"""

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from models.enums import InterviewProbeType
from models.interview import (
    InterviewExchange,
    InterviewGuide,
    InterviewQuestion,
    InterviewSection,
    InterviewTranscript,
    SectionTranscript,
)
from models.persona import Persona
from services.prompt_builder import PromptBuilder

# Default interview prompt template
DEFAULT_INTERVIEW_PROMPT = """{{ persona_prompt }}

---

## Interview Context

This is an in-depth interview about: **{{ guide.topic }}**

{% if section.transition_prompt %}
{{ section.transition_prompt }}
{% endif %}

### Section: {{ section.name }}
{% if section.description %}
{{ section.description }}
{% endif %}

---

## Question

{{ question.text }}

---

## Response Guidelines

As {{ persona_name }}, please share your thoughts openly and honestly. Consider:
- Your personal experiences related to this topic
- Specific examples from your life
- How this relates to your values and priorities
- What emotions or reactions this brings up

Provide a detailed, thoughtful response that reflects your unique perspective and personality.
"""


DEFAULT_FOLLOWUP_PROMPT = """{{ persona_prompt }}

---

## Interview Context (continued)

We are continuing our discussion about: **{{ guide.topic }}**

### Previous Exchange

**Question**: {{ previous_question }}

**Your Response**: {{ previous_response }}

---

## Follow-up Question

{{ followup_question }}

---

## Response Guidelines

As {{ persona_name }}, please elaborate on your previous answer. Consider:
{% if probe_type.value == "elaboration" %}
- Expand on the key points you mentioned
- Provide more detail about your experience
{% elif probe_type.value == "clarification" %}
- Clarify what you meant by the point in question
- Be more specific about your perspective
{% elif probe_type.value == "example" %}
- Share a specific example or story
- Describe a concrete situation you experienced
{% elif probe_type.value == "feeling" %}
- Describe how this made you feel emotionally
- Share the impact on your wellbeing or mindset
{% endif %}

Provide a thoughtful elaboration that maintains consistency with your previous response.
"""


class InterviewEngine:
    """Executes in-depth interview research sessions.

    Handles section-based execution, probing strategies,
    and follow-up question logic.
    """

    def __init__(
        self,
        template_path: Path | None = None,
    ):
        """Initialize the interview engine.

        Args:
            template_path: Optional path to custom templates.
        """
        self.prompt_builder = PromptBuilder()
        self.template_path = template_path
        self._interview_template: Template | None = None
        self._followup_template: Template | None = None

    def _get_interview_template(self) -> Template:
        """Get the Jinja2 template for interview prompts."""
        if self._interview_template is not None:
            return self._interview_template

        template_locations = [
            Path("src/templates/interview_prompt.j2"),
            Path(__file__).parent.parent / "templates" / "interview_prompt.j2",
        ]

        if self.template_path:
            template_locations.insert(0, self.template_path / "interview_prompt.j2")

        for path in template_locations:
            if path.exists():
                env = Environment(
                    loader=FileSystemLoader(path.parent),
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
                self._interview_template = env.get_template(path.name)
                return self._interview_template

        env = Environment(trim_blocks=True, lstrip_blocks=True)
        self._interview_template = env.from_string(DEFAULT_INTERVIEW_PROMPT)
        return self._interview_template

    def _get_followup_template(self) -> Template:
        """Get the Jinja2 template for follow-up prompts."""
        if self._followup_template is not None:
            return self._followup_template

        template_locations = [
            Path("src/templates/interview_followup.j2"),
            Path(__file__).parent.parent / "templates" / "interview_followup.j2",
        ]

        for path in template_locations:
            if path.exists():
                env = Environment(
                    loader=FileSystemLoader(path.parent),
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
                self._followup_template = env.get_template(path.name)
                return self._followup_template

        env = Environment(trim_blocks=True, lstrip_blocks=True)
        self._followup_template = env.from_string(DEFAULT_FOLLOWUP_PROMPT)
        return self._followup_template

    def _build_question_prompt(
        self,
        guide: InterviewGuide,
        section: InterviewSection,
        question: InterviewQuestion,
        persona_prompt: str,
        persona_name: str,
    ) -> str:
        """Build prompt for an interview question."""
        template = self._get_interview_template()
        return template.render(
            persona_prompt=persona_prompt,
            persona_name=persona_name,
            guide=guide,
            section=section,
            question=question,
        )

    def _build_followup_prompt(
        self,
        guide: InterviewGuide,
        previous_question: str,
        previous_response: str,
        followup_question: str,
        probe_type: InterviewProbeType,
        persona_prompt: str,
        persona_name: str,
    ) -> str:
        """Build prompt for a follow-up question."""
        template = self._get_followup_template()
        return template.render(
            persona_prompt=persona_prompt,
            persona_name=persona_name,
            guide=guide,
            previous_question=previous_question,
            previous_response=previous_response,
            followup_question=followup_question,
            probe_type=probe_type,
        )

    def _should_probe(
        self,
        question: InterviewQuestion,
        response: str,
        min_response_length: int,
    ) -> InterviewProbeType | None:
        """Determine if probing is needed based on response.

        Args:
            question: The question that was asked.
            response: The persona's response.
            min_response_length: Minimum acceptable response length.

        Returns:
            Probe type to use, or None if no probing needed.
        """
        if not question.probes:
            return None

        # Check response length
        if len(response) < min_response_length:
            return InterviewProbeType.ELABORATION

        # Check for trigger words in probes
        response_lower = response.lower()
        for probe in question.probes:
            if probe.trigger and probe.trigger.lower() in response_lower:
                return probe.type

        return None

    def _generate_probe_question(
        self,
        probe_type: InterviewProbeType,
        question: InterviewQuestion,
        response: str,
    ) -> str:
        """Generate a probing question based on type.

        Args:
            probe_type: Type of probe to generate.
            question: Original question.
            response: Previous response.

        Returns:
            Probe question text.
        """
        # Check for custom probe template
        for probe in question.probes:
            if probe.type == probe_type:
                return probe.question_template

        # Default probe templates
        templates = {
            InterviewProbeType.ELABORATION: "Can you tell me more about that?",
            InterviewProbeType.CLARIFICATION: "What do you mean by that? Could you clarify?",
            InterviewProbeType.EXAMPLE: "Can you give me a specific example?",
            InterviewProbeType.FEELING: "How did that make you feel?",
        }
        return templates.get(probe_type, "Could you expand on that?")

    def execute_interview(
        self,
        guide: InterviewGuide,
        persona: Persona,
        execute_fn: Callable[[str], str] | None = None,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> InterviewTranscript:
        """Execute an interview with a persona.

        Args:
            guide: The interview guide to follow.
            persona: The persona to interview.
            execute_fn: Optional function to execute prompts.
            progress_callback: Optional callback for progress updates.

        Returns:
            InterviewTranscript with all exchanges.
        """
        started_at = datetime.now(UTC)
        persona_prompt = self.prompt_builder.build(persona)

        section_transcripts: list[SectionTranscript] = []
        total_exchanges = 0

        for section in guide.sections:
            section_started = datetime.now(UTC)
            exchanges: list[InterviewExchange] = []

            for question in section.questions:
                # Build main question prompt
                prompt = self._build_question_prompt(
                    guide=guide,
                    section=section,
                    question=question,
                    persona_prompt=persona_prompt,
                    persona_name=persona.name,
                )

                # Execute
                if execute_fn:
                    response = execute_fn(prompt)
                else:
                    response = f"[Task specification for question: {question.id}]"

                # Create exchange
                exchange = InterviewExchange(
                    question_id=question.id,
                    question_text=question.text,
                    response=response,
                    timestamp=datetime.now(UTC),
                    response_length=len(response),
                    followups=[],
                )

                # Check for probing
                if question.allow_followups:
                    probe_type = self._should_probe(
                        question, response, guide.min_response_length
                    )
                    if probe_type:
                        followup_question = self._generate_probe_question(
                            probe_type, question, response
                        )
                        followup_prompt = self._build_followup_prompt(
                            guide=guide,
                            previous_question=question.text,
                            previous_response=response,
                            followup_question=followup_question,
                            probe_type=probe_type,
                            persona_prompt=persona_prompt,
                            persona_name=persona.name,
                        )

                        if execute_fn:
                            followup_response = execute_fn(followup_prompt)
                        else:
                            followup_response = f"[Follow-up response for: {question.id}]"

                        followup_exchange = InterviewExchange(
                            question_id=f"{question.id}-followup",
                            question_text=followup_question,
                            response=followup_response,
                            timestamp=datetime.now(UTC),
                            response_length=len(followup_response),
                            probe_used=probe_type,
                        )
                        exchange.followups.append(followup_exchange)
                        total_exchanges += 1

                exchanges.append(exchange)
                total_exchanges += 1

                if progress_callback:
                    progress_callback(section.id, len(exchanges), len(section.questions))

            section_completed = datetime.now(UTC)
            section_transcripts.append(
                SectionTranscript(
                    section_id=section.id,
                    section_name=section.name,
                    exchanges=exchanges,
                    started_at=section_started,
                    completed_at=section_completed,
                    total_exchanges=len(exchanges) + sum(len(e.followups) for e in exchanges),
                )
            )

        completed_at = datetime.now(UTC)
        total_time_ms = int((completed_at - started_at).total_seconds() * 1000)

        return InterviewTranscript(
            guide_id=guide.id,
            guide_version=guide.version,
            persona_id=persona.id,
            persona_name=persona.name,
            sections=section_transcripts,
            started_at=started_at,
            completed_at=completed_at,
            total_time_ms=total_time_ms,
        )

    def get_task_specification(
        self,
        guide: InterviewGuide,
        persona: Persona,
    ) -> dict:
        """Generate task specification for an interview.

        Args:
            guide: The interview guide.
            persona: The persona to interview.

        Returns:
            Dictionary with task specification.
        """
        persona_prompt = self.prompt_builder.build(persona)

        sections_spec = []
        for section in guide.sections:
            questions_spec = []
            for question in section.questions:
                prompt = self._build_question_prompt(
                    guide=guide,
                    section=section,
                    question=question,
                    persona_prompt=persona_prompt,
                    persona_name=persona.name,
                )
                questions_spec.append({
                    "question_id": question.id,
                    "question_text": question.text,
                    "allow_followups": question.allow_followups,
                    "max_followup_depth": question.max_followup_depth,
                    "prompt": prompt,
                })
            sections_spec.append({
                "section_id": section.id,
                "section_name": section.name,
                "questions": questions_spec,
            })

        return {
            "guide_id": guide.id,
            "guide_version": guide.version,
            "topic": guide.topic,
            "persona_id": persona.id,
            "persona_name": persona.name,
            "sections": sections_spec,
        }
