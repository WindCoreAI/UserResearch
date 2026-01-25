"""Service for executing single persona research sessions.

Orchestrates the execution of research sessions using Claude Code subagents.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template

from models.persona import Persona
from models.question import ResearchQuestion
from models.session import ResearchSession, SessionResponse, SessionStatus
from services.prompt_builder import PromptBuilder


# Default research prompt template
DEFAULT_RESEARCH_TEMPLATE = """{{ persona_prompt }}

---

## Research Question

{{ question.text }}

{% if question.type.value == 'rating' %}
**Question Type**: Rating Scale ({{ question.scale_min }}-{{ question.scale_max }})

Please provide:
1. Your rating as a number between {{ question.scale_min }} and {{ question.scale_max }}
2. Your reasoning for this rating
{% elif question.type.value == 'multiple_choice' %}
**Question Type**: Multiple Choice

Please select from these options:
{% for option in question.options %}
- {{ option }}
{% endfor %}

Provide your selection and explain your reasoning.
{% else %}
**Question Type**: Open-Ended

Please share your honest thoughts and perspective on this question.
{% endif %}

---

## Response Format

Please structure your response as follows:

1. **OVERALL_IMPRESSION**: Your gut reaction in 1-2 sentences
2. **SENTIMENT**: One of: positive, negative, mixed, neutral
{% if question.type.value == 'rating' %}
3. **RATING**: Your numeric rating ({{ question.scale_min }}-{{ question.scale_max }})
{% elif question.type.value == 'multiple_choice' %}
3. **SELECTED_OPTION**: Your chosen option from the list
{% endif %}
3. **CONCERNS**: List any concerns you have (bullet points, or "None" if none)
4. **SUGGESTIONS**: List any suggestions for improvement (bullet points, or "None" if none)
5. **DETAILED_RESPONSE**: Your full, detailed thoughts as {{ persona_name }}

Remember to respond authentically as your persona. Your feedback is valuable because it reflects genuine personality-consistent reactions, not generic positivity."""


class SessionRunner:
    """Executes single persona research sessions.

    Builds prompts combining persona definitions with research questions,
    creates sessions, and processes responses.
    """

    def __init__(self, template_path: Path | None = None):
        """Initialize the session runner.

        Args:
            template_path: Optional path to custom research prompt template.
        """
        self.prompt_builder = PromptBuilder()
        self.template_path = template_path
        self._template: Template | None = None

    def _get_research_template(self) -> Template:
        """Get the Jinja2 template for research prompts."""
        if self._template is not None:
            return self._template

        # Try to load from templates directory
        template_locations = [
            Path("src/templates/research_prompt.j2"),
            Path(__file__).parent.parent / "templates" / "research_prompt.j2",
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
        self._template = env.from_string(DEFAULT_RESEARCH_TEMPLATE)
        return self._template

    def build_prompt(self, persona: Persona, question: ResearchQuestion) -> str:
        """Build the complete prompt for a research session.

        Combines the persona prompt with research question and
        response format instructions.

        Args:
            persona: The persona to simulate.
            question: The research question to ask.

        Returns:
            Complete prompt text for the subagent.
        """
        # Generate the persona prompt
        persona_prompt = self.prompt_builder.build(persona)

        # Get the research template
        template = self._get_research_template()

        # Render the complete prompt
        return template.render(
            persona_prompt=persona_prompt,
            persona_name=persona.name,
            question=question,
        )

    def create_session(
        self,
        persona: Persona,
        question: ResearchQuestion,
        metadata: dict[str, Any] | None = None,
    ) -> ResearchSession:
        """Create a new research session.

        Args:
            persona: The persona to use for this session.
            question: The research question to ask.
            metadata: Optional session metadata.

        Returns:
            A new ResearchSession in PENDING status.
        """
        session_id = str(uuid.uuid4())

        return ResearchSession(
            id=session_id,
            persona_id=persona.id,
            persona_name=persona.name,
            question=question,
            status=SessionStatus.PENDING,
            started_at=datetime.now(timezone.utc),
            metadata=metadata,
        )

    def get_task_specification(self, session: ResearchSession) -> dict[str, Any]:
        """Generate the Task tool specification for this session.

        This creates the specification that can be used to invoke
        a Claude Code subagent via the Task tool.

        Args:
            session: The research session to execute.

        Returns:
            Dictionary with task specification including prompt.
        """
        # The actual prompt would be built with the persona
        # For now, return a specification structure
        return {
            "prompt": f"Research session {session.id} for {session.persona_name}",
            "session_id": session.id,
            "persona_id": session.persona_id,
            "question": session.question.text,
        }

    def process_response(
        self,
        session: ResearchSession,
        raw_response: str,
        response_time_ms: int,
    ) -> ResearchSession:
        """Process a response from the subagent.

        Updates the session with the response data and marks it complete.

        Args:
            session: The session to update.
            raw_response: The raw text response from the subagent.
            response_time_ms: Time taken to get the response.

        Returns:
            Updated session with response and COMPLETED status.
        """
        response = SessionResponse(
            raw_text=raw_response,
            response_time_ms=response_time_ms,
        )

        # Create updated session (Pydantic models are immutable by default)
        return ResearchSession(
            id=session.id,
            persona_id=session.persona_id,
            persona_name=session.persona_name,
            question=session.question,
            response=response,
            status=SessionStatus.COMPLETED,
            started_at=session.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=session.metadata,
        )
