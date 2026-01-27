"""Service for executing focus group research.

Handles multi-persona discussion with turn-taking,
cross-references, and consensus/divergence analysis.
"""

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from models.enums import DiscussionInteractionType
from models.focus_group import (
    DiscussionLog,
    DiscussionReference,
    DiscussionTurn,
    FocusGroup,
)
from models.persona import Persona
from models.session import Sentiment
from services.prompt_builder import PromptBuilder

# Default focus group prompt template
DEFAULT_FOCUS_GROUP_PROMPT = """{{ persona_prompt }}

---

## Focus Group Discussion

**Topic**: {{ topic }}

You are participating in a focus group discussion with {{ participant_count }} other participants.

### Discussion Context

Round {{ round_number }} of {{ total_rounds }}

{% if previous_turns %}
### Previous Discussion

{% for turn in previous_turns %}
**{{ turn.persona_name }}**: {{ turn.statement }}

{% endfor %}
{% endif %}

---

## Your Turn

As {{ persona_name }}, share your thoughts on this topic. Consider:
- The discussion topic and any points raised by others
- Your personal perspective based on your values and experiences
- Whether you agree or disagree with others' viewpoints
{% if allow_references %}
- Feel free to reference or respond to specific points made by other participants
{% endif %}

{% if is_first_turn %}
You are starting the discussion. Share your initial thoughts on the topic.
{% else %}
Building on the discussion so far, share your perspective. You may agree, disagree, build on others' points, or raise new considerations.
{% endif %}

Respond naturally as yourself, maintaining your characteristic communication style.
"""


class FocusGroupEngine:
    """Executes focus group discussion research.

    Manages turn-taking, cross-references between participants,
    and tracks consensus/divergence points.
    """

    def __init__(
        self,
        template_path: Path | None = None,
    ):
        """Initialize the focus group engine.

        Args:
            template_path: Optional path to custom templates.
        """
        self.prompt_builder = PromptBuilder()
        self.template_path = template_path
        self._template: Template | None = None

    def _get_template(self) -> Template:
        """Get the Jinja2 template for focus group prompts."""
        if self._template is not None:
            return self._template

        template_locations = [
            Path("src/templates/focus_group_prompt.j2"),
            Path(__file__).parent.parent / "templates" / "focus_group_prompt.j2",
        ]

        if self.template_path:
            template_locations.insert(0, self.template_path / "focus_group_prompt.j2")

        for path in template_locations:
            if path.exists():
                env = Environment(
                    loader=FileSystemLoader(path.parent),
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
                self._template = env.get_template(path.name)
                return self._template

        env = Environment(trim_blocks=True, lstrip_blocks=True)
        self._template = env.from_string(DEFAULT_FOCUS_GROUP_PROMPT)
        return self._template

    def _build_turn_prompt(
        self,
        topic: str,
        persona_prompt: str,
        persona_name: str,
        round_number: int,
        total_rounds: int,
        previous_turns: list[DiscussionTurn],
        allow_references: bool,
        participant_count: int,
    ) -> str:
        """Build prompt for a focus group turn."""
        template = self._get_template()
        return template.render(
            persona_prompt=persona_prompt,
            persona_name=persona_name,
            topic=topic,
            round_number=round_number,
            total_rounds=total_rounds,
            previous_turns=previous_turns,
            is_first_turn=len(previous_turns) == 0,
            allow_references=allow_references,
            participant_count=participant_count,
        )

    def _detect_references(
        self,
        statement: str,
        previous_turns: list[DiscussionTurn],
    ) -> list[DiscussionReference]:
        """Detect references to other participants in a statement.

        Args:
            statement: The current participant's statement.
            previous_turns: Previous turns in the discussion.

        Returns:
            List of detected references.
        """
        references = []
        statement_lower = statement.lower()

        # Keywords indicating different interaction types
        agreement_keywords = ["agree", "exactly", "good point", "right", "yes"]
        disagreement_keywords = ["disagree", "however", "but", "on the other hand", "not sure about"]
        building_keywords = ["building on", "to add to", "additionally", "also"]
        question_keywords = ["why", "how", "what do you mean", "could you explain"]

        for turn in previous_turns:
            # Check if persona name is mentioned
            if turn.persona_name.lower() in statement_lower:
                # Determine reference type
                ref_type = DiscussionInteractionType.NEW_POINT

                for keyword in agreement_keywords:
                    if keyword in statement_lower:
                        ref_type = DiscussionInteractionType.AGREEMENT
                        break
                for keyword in disagreement_keywords:
                    if keyword in statement_lower:
                        ref_type = DiscussionInteractionType.DISAGREEMENT
                        break
                for keyword in building_keywords:
                    if keyword in statement_lower:
                        ref_type = DiscussionInteractionType.BUILDING_ON
                        break
                for keyword in question_keywords:
                    if keyword in statement_lower:
                        ref_type = DiscussionInteractionType.QUESTION
                        break

                references.append(
                    DiscussionReference(
                        referenced_persona_id=turn.persona_id,
                        referenced_turn_index=turn.turn_index,
                        reference_type=ref_type,
                        quote_fragment=turn.statement[:100] + "..." if len(turn.statement) > 100 else turn.statement,
                    )
                )

        return references

    def _detect_interaction_type(
        self,
        statement: str,
        references: list[DiscussionReference],
    ) -> DiscussionInteractionType:
        """Determine the primary interaction type for a turn.

        Args:
            statement: The participant's statement.
            references: Detected references.

        Returns:
            Primary interaction type.
        """
        if references:
            # Use the first reference type
            return references[0].reference_type

        return DiscussionInteractionType.NEW_POINT

    def _detect_sentiment(self, statement: str) -> Sentiment:
        """Detect sentiment from statement text.

        Args:
            statement: The participant's statement.

        Returns:
            Detected sentiment.
        """
        statement_lower = statement.lower()

        positive_words = ["love", "great", "excellent", "amazing", "excited", "enthusiastic"]
        negative_words = ["hate", "terrible", "awful", "worried", "concerned", "frustrated"]
        mixed_words = ["however", "but", "on one hand", "mixed"]

        pos_count = sum(1 for w in positive_words if w in statement_lower)
        neg_count = sum(1 for w in negative_words if w in statement_lower)

        if any(w in statement_lower for w in mixed_words):
            return Sentiment.MIXED
        if pos_count > neg_count:
            return Sentiment.POSITIVE
        if neg_count > pos_count:
            return Sentiment.NEGATIVE
        return Sentiment.NEUTRAL

    def execute_focus_group(
        self,
        focus_group: FocusGroup,
        topic: str,
        personas: list[Persona],
        execute_fn: Callable[[str], str] | None = None,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> DiscussionLog:
        """Execute a focus group discussion.

        Args:
            focus_group: The focus group configuration.
            topic: Discussion topic.
            personas: List of personas participating.
            execute_fn: Optional function to execute prompts.
            progress_callback: Optional callback for progress updates.

        Returns:
            DiscussionLog with all turns and analysis.
        """
        started_at = datetime.now(UTC)
        config = focus_group.config

        # Build persona prompts
        persona_prompts = {p.id: self.prompt_builder.build(p) for p in personas}

        turns: list[DiscussionTurn] = []
        turn_index = 0
        interaction_counts = {
            "agreement": 0,
            "disagreement": 0,
            "building_on": 0,
            "question": 0,
            "new_point": 0,
        }

        for round_num in range(1, config.max_rounds + 1):
            for persona in personas:
                # Build turn prompt
                prompt = self._build_turn_prompt(
                    topic=topic,
                    persona_prompt=persona_prompts[persona.id],
                    persona_name=persona.name,
                    round_number=round_num,
                    total_rounds=config.max_rounds,
                    previous_turns=turns[-6:] if turns else [],  # Show last 6 turns
                    allow_references=config.allow_cross_references,
                    participant_count=len(personas),
                )

                # Execute
                if execute_fn:
                    statement = execute_fn(prompt)
                else:
                    statement = f"[Task specification for {persona.name} in round {round_num}]"

                # Detect references and interaction type
                references = self._detect_references(statement, turns) if config.allow_cross_references else []
                interaction_type = self._detect_interaction_type(statement, references)
                sentiment = self._detect_sentiment(statement)

                # Create turn
                turn = DiscussionTurn(
                    turn_index=turn_index,
                    round_number=round_num,
                    persona_id=persona.id,
                    persona_name=persona.name,
                    statement=statement,
                    timestamp=datetime.now(UTC),
                    references=references,
                    interaction_type=interaction_type,
                    sentiment=sentiment,
                )
                turns.append(turn)
                turn_index += 1

                # Track interaction counts
                interaction_counts[interaction_type.value] += 1

                if progress_callback:
                    progress_callback(round_num, turn_index, persona.id)

        completed_at = datetime.now(UTC)
        total_time_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Build participants list
        participants = [
            {"persona_id": p.id, "persona_name": p.name}
            for p in personas
        ]

        return DiscussionLog(
            group_id=focus_group.id,
            group_version=focus_group.version,
            topic=topic,
            participants=participants,
            turns=turns,
            started_at=started_at,
            completed_at=completed_at,
            total_time_ms=total_time_ms,
            total_rounds=config.max_rounds,
            interaction_summary=interaction_counts,
        )

    def get_task_specification(
        self,
        focus_group: FocusGroup,
        topic: str,
        personas: list[Persona],
    ) -> dict:
        """Generate task specification for a focus group.

        Args:
            focus_group: The focus group configuration.
            topic: Discussion topic.
            personas: List of personas.

        Returns:
            Dictionary with task specification.
        """
        persona_prompts = {p.id: self.prompt_builder.build(p) for p in personas}
        config = focus_group.config

        rounds_spec = []
        for round_num in range(1, config.max_rounds + 1):
            turns_spec = []
            for persona in personas:
                prompt = self._build_turn_prompt(
                    topic=topic,
                    persona_prompt=persona_prompts[persona.id],
                    persona_name=persona.name,
                    round_number=round_num,
                    total_rounds=config.max_rounds,
                    previous_turns=[],  # Will be filled during execution
                    allow_references=config.allow_cross_references,
                    participant_count=len(personas),
                )
                turns_spec.append({
                    "persona_id": persona.id,
                    "persona_name": persona.name,
                    "prompt_template": prompt,
                })
            rounds_spec.append({
                "round_number": round_num,
                "turns": turns_spec,
            })

        return {
            "group_id": focus_group.id,
            "group_version": focus_group.version,
            "topic": topic,
            "participants": [{"persona_id": p.id, "persona_name": p.name} for p in personas],
            "config": {
                "max_rounds": config.max_rounds,
                "turns_per_round": len(personas),
                "allow_cross_references": config.allow_cross_references,
            },
            "rounds": rounds_spec,
        }
