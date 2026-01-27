"""CLI commands for interview research.

Provides commands for running interviews and creating interview guides.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from models.protocol import InterviewProtocol
from services.interview_engine import InterviewEngine
from services.protocol_loader import ProtocolLoader, ProtocolLoaderError

console = Console()


@click.group(name="interview")
def interview_group():
    """Interview research commands."""
    pass


@interview_group.command(name="run")
@click.option(
    "--guide", "-g",
    required=True,
    help="Interview guide ID",
)
@click.option(
    "--persona", "-p",
    required=True,
    help="Persona ID to interview",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Export transcript to JSON file",
)
@click.option(
    "--report", "-r",
    type=click.Path(),
    help="Generate Markdown transcript report",
)
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "--timeout",
    type=int,
    default=180,
    help="Per-section timeout in seconds (default: 180)",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed progress",
)
def run_interview(
    guide: str,
    persona: str,
    output: Optional[str],
    report: Optional[str],
    output_format: str,
    timeout: int,
    verbose: bool,
):
    """Execute an interview guide with a persona.

    Example:
        research-cli research interview run -g sample-interview -p tech-early-adopter
    """
    from services.persona_library import PersonaLibrary

    # Load protocol
    loader = ProtocolLoader()
    try:
        proto = loader.load_by_id(guide)
        if not isinstance(proto, InterviewProtocol):
            console.print(f"[red]Protocol '{guide}' is not an interview guide[/red]")
            sys.exit(1)
    except ProtocolLoaderError:
        console.print(f"[red]PROTOCOL_NOT_FOUND: Interview guide '{guide}' not found[/red]")
        console.print("[dim]Use 'research protocol list --type interview' to see available guides[/dim]")
        sys.exit(1)

    # Load persona
    library = PersonaLibrary()
    try:
        persona_obj = library.get_by_id(persona)
    except FileNotFoundError:
        console.print(f"[red]PERSONA_NOT_FOUND: Persona '{persona}' not found[/red]")
        console.print("[dim]Use 'research-cli persona list' to see available personas[/dim]")
        sys.exit(1)

    # Execute interview
    engine = InterviewEngine()
    interview_guide = proto.guide

    if verbose:
        console.print(Panel(
            f"[bold]Interview:[/bold] {interview_guide.name}\n"
            f"[bold]Topic:[/bold] {interview_guide.topic}\n"
            f"[bold]Persona:[/bold] {persona_obj.name} ({persona_obj.id})\n"
            f"[bold]Sections:[/bold] {len(interview_guide.sections)}",
            title="Interview Execution",
            border_style="blue",
        ))

    # Generate task specification
    spec = engine.get_task_specification(interview_guide, persona_obj)

    if output_format == "json":
        output_data = {
            "guide_id": interview_guide.id,
            "guide_version": interview_guide.version,
            "method": "interview",
            "persona_id": persona_obj.id,
            "persona_name": persona_obj.name,
            "topic": interview_guide.topic,
            "total_sections": len(interview_guide.sections),
            "timeout_per_section": timeout,
            "task_specification": spec,
            "metadata": {
                "started_at": datetime.utcnow().isoformat() + "Z",
            }
        }
        console.print_json(json.dumps(output_data, indent=2, default=str))
    else:
        _format_interview_task_spec(spec, interview_guide, persona_obj, console, verbose)

    if output:
        try:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(spec, f, indent=2, default=str)
            console.print(f"\n[green]Exported to {output_path}[/green]")
        except OSError as e:
            console.print(f"[red]Error writing output file: {e}[/red]")

    console.print("\n[yellow]SYNTHETIC DATA:[/yellow] Validate critical findings with real users.")


@interview_group.command(name="create")
@click.option(
    "--from-yaml", "-f",
    "yaml_path",
    type=click.Path(exists=True),
    help="Create from YAML file",
)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="Interactive creation wizard",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output path for created guide",
)
def create_interview(
    yaml_path: Optional[str],
    interactive: bool,
    output: Optional[str],
):
    """Create a new interview guide.

    Example:
        research-cli research interview create -f my-interview.yaml
    """
    import yaml as yaml_lib

    from models.enums import InterviewProbeType
    from models.interview import InterviewGuide, InterviewProbe, InterviewQuestion, InterviewSection

    if yaml_path:
        try:
            with open(yaml_path) as f:
                data = yaml_lib.safe_load(f)
        except (OSError, yaml_lib.YAMLError) as e:
            console.print(f"[red]Error reading YAML file: {e}[/red]")
            sys.exit(1)

        try:
            guide_data = data.get("guide", {})

            sections = []
            for s in guide_data.get("sections", []):
                questions = []
                for q in s.get("questions", []):
                    probes = []
                    for p in q.get("probes", []):
                        probes.append(InterviewProbe(
                            type=InterviewProbeType(p["type"]),
                            trigger=p.get("trigger"),
                            question_template=p["question_template"],
                        ))
                    questions.append(InterviewQuestion(
                        id=q["id"],
                        text=q["text"],
                        probes=probes,
                        allow_followups=q.get("allow_followups", True),
                        max_followup_depth=q.get("max_followup_depth", 3),
                    ))
                sections.append(InterviewSection(
                    id=s["id"],
                    name=s["name"],
                    description=s.get("description"),
                    questions=questions,
                    transition_prompt=s.get("transition_prompt"),
                ))

            guide = InterviewGuide(
                id=guide_data.get("id", ""),
                version=guide_data.get("version", "1.0.0"),
                name=guide_data.get("name", ""),
                topic=guide_data.get("topic", ""),
                description=guide_data.get("description"),
                sections=sections,
                min_response_length=guide_data.get("min_response_length", 50),
                default_max_followups=guide_data.get("default_max_followups", 3),
            )

            protocol = InterviewProtocol(
                id=data.get("protocol", {}).get("id", guide.id),
                version=data.get("protocol", {}).get("version", guide.version),
                name=data.get("protocol", {}).get("name", guide.name),
                description=data.get("protocol", {}).get("description"),
                tags=data.get("protocol", {}).get("tags", []),
                guide=guide,
            )

            loader = ProtocolLoader()
            saved_path = loader.save_protocol(protocol)
            console.print(f"[green]Created interview guide: {protocol.id}[/green]")
            console.print(f"[dim]Saved to: {saved_path}[/dim]")

        except Exception as e:
            console.print(f"[red]Error creating interview guide: {e}[/red]")
            sys.exit(1)

    elif interactive:
        console.print("[yellow]Interactive creation not yet implemented[/yellow]")
        sys.exit(0)
    else:
        console.print("[red]Error: Specify --from-yaml or --interactive[/red]")
        sys.exit(1)


def _format_interview_task_spec(
    spec: dict,
    guide,
    persona,
    console: Console,
    verbose: bool = False,
):
    """Format interview task specification for display."""
    console.print(Panel(
        f"[bold]Interview:[/bold] {guide.name} (v{guide.version})\n"
        f"[bold]Topic:[/bold] {guide.topic}\n"
        f"[bold]Persona:[/bold] {persona.name}\n"
        f"[bold]Sections:[/bold] {len(guide.sections)}",
        title="Interview Task Specification",
        border_style="blue",
    ))

    # Section tree
    tree = Tree("[bold]Interview Structure[/bold]")
    for section in guide.sections:
        section_branch = tree.add(f"[cyan]{section.name}[/cyan]")
        for question in section.questions:
            q_text = question.text[:40] + "..." if len(question.text) > 40 else question.text
            section_branch.add(f"[dim]{question.id}:[/dim] {q_text}")

    console.print(tree)

    if verbose:
        for section in spec.get("sections", []):
            console.print(f"\n[bold]Section: {section['section_name']}[/bold]")
            for q in section.get("questions", []):
                console.print(f"\n[dim]Question: {q['question_id']}[/dim]")
                prompt_preview = q["prompt"][:200] + "..." if len(q["prompt"]) > 200 else q["prompt"]
                console.print(Panel(prompt_preview, border_style="dim"))

    console.print("\n[yellow]Note:[/yellow] Execute the generated prompts with a Claude Code subagent.")
