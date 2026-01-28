"""CLI commands for survey research.

Provides commands for running surveys and creating survey protocols.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from models.protocol import SurveyProtocol
from services.protocol_loader import ProtocolLoader, ProtocolLoaderError
from services.survey_engine import SurveyEngine

console = Console()


@click.group(name="survey")
def survey_group():
    """Survey research commands."""
    pass


@survey_group.command(name="run")
@click.option(
    "--protocol", "-p",
    required=True,
    help="Survey protocol ID",
)
@click.option(
    "--persona",
    required=True,
    help="Persona ID to execute survey with",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Export results to JSON file",
)
@click.option(
    "--report", "-r",
    type=click.Path(),
    help="Generate Markdown report to file",
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
    default=60,
    help="Per-question timeout in seconds (default: 60)",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed progress",
)
def run_survey(
    protocol: str,
    persona: str,
    output: Optional[str],
    report: Optional[str],
    output_format: str,
    timeout: int,
    verbose: bool,
):
    """Execute a survey protocol with a persona.

    Example:
        research-cli research survey run -p sample-survey --persona tech-early-adopter
    """
    from services.persona_library import PersonaLibrary

    # Load protocol
    loader = ProtocolLoader()
    try:
        proto = loader.load_by_id(protocol)
        if not isinstance(proto, SurveyProtocol):
            console.print(f"[red]Protocol '{protocol}' is not a survey protocol[/red]")
            sys.exit(1)
    except ProtocolLoaderError:
        console.print(f"[red]PROTOCOL_NOT_FOUND: Survey protocol '{protocol}' not found[/red]")
        console.print("[dim]Use 'research protocol list --type survey' to see available surveys[/dim]")
        sys.exit(1)

    # Load persona
    library = PersonaLibrary()
    try:
        persona_obj = library.get_by_id(persona)
    except FileNotFoundError:
        console.print(f"[red]PERSONA_NOT_FOUND: Persona '{persona}' not found[/red]")
        console.print("[dim]Use 'research-cli persona list' to see available personas[/dim]")
        sys.exit(1)

    # Execute survey
    engine = SurveyEngine()
    survey = proto.survey

    if verbose:
        console.print(Panel(
            f"[bold]Survey:[/bold] {survey.name}\n"
            f"[bold]Persona:[/bold] {persona_obj.name} ({persona_obj.id})\n"
            f"[bold]Questions:[/bold] {len(survey.questions)}",
            title="Survey Execution",
            border_style="blue",
        ))

    # Generate task specification (for now, actual LLM execution would happen here)
    spec = engine.get_task_specification(survey, persona_obj)

    if output_format == "json":
        # Output task specification as JSON
        output_data = {
            "survey_id": survey.id,
            "survey_version": survey.version,
            "method": "survey",
            "persona_id": persona_obj.id,
            "persona_name": persona_obj.name,
            "total_questions": len(survey.questions),
            "timeout_per_question": timeout,
            "task_specification": spec,
            "metadata": {
                "started_at": datetime.utcnow().isoformat() + "Z",
            }
        }
        console.print_json(json.dumps(output_data, indent=2, default=str))
    else:
        # Rich text output
        _format_survey_task_spec(spec, survey, persona_obj, console, verbose)

    # Export to file if requested
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


@survey_group.command(name="create")
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
    help="Output path for created protocol",
)
def create_survey(
    yaml_path: Optional[str],
    interactive: bool,
    output: Optional[str],
):
    """Create a new survey protocol.

    Example:
        research-cli research survey create -f my-survey.yaml
    """
    import yaml as yaml_lib

    from models.enums import SurveyQuestionType
    from models.survey import Survey, SurveyQuestion

    if yaml_path:
        # Create from YAML file
        try:
            with open(yaml_path) as f:
                data = yaml_lib.safe_load(f)
        except (OSError, yaml_lib.YAMLError) as e:
            console.print(f"[red]Error reading YAML file: {e}[/red]")
            sys.exit(1)

        # Validate and create survey
        try:
            survey_data = data.get("survey", {})
            questions = []
            for q in survey_data.get("questions", []):
                q["type"] = SurveyQuestionType(q["type"])
                questions.append(SurveyQuestion(**q))

            survey = Survey(
                id=survey_data.get("id", ""),
                version=survey_data.get("version", "1.0.0"),
                name=survey_data.get("name", ""),
                description=survey_data.get("description"),
                questions=questions,
            )

            protocol = SurveyProtocol(
                id=data.get("protocol", {}).get("id", survey.id),
                version=data.get("protocol", {}).get("version", survey.version),
                name=data.get("protocol", {}).get("name", survey.name),
                description=data.get("protocol", {}).get("description"),
                tags=data.get("protocol", {}).get("tags", []),
                survey=survey,
            )

            # Save protocol
            loader = ProtocolLoader()
            saved_path = loader.save_protocol(protocol)
            console.print(f"[green]Created survey protocol: {protocol.id}[/green]")
            console.print(f"[dim]Saved to: {saved_path}[/dim]")

        except Exception as e:
            console.print(f"[red]Error creating survey: {e}[/red]")
            sys.exit(1)

    elif interactive:
        console.print("[yellow]Interactive creation not yet implemented[/yellow]")
        console.print("[dim]Use --from-yaml to create from a YAML file[/dim]")
        sys.exit(0)

    else:
        console.print("[red]Error: Specify --from-yaml or --interactive[/red]")
        sys.exit(1)


def _format_survey_task_spec(
    spec: dict,
    survey,
    persona,
    console: Console,
    verbose: bool = False,
):
    """Format survey task specification for display."""
    console.print(Panel(
        f"[bold]Survey:[/bold] {survey.name} (v{survey.version})\n"
        f"[bold]Persona:[/bold] {persona.name}\n"
        f"[bold]Questions:[/bold] {spec['total_questions']}",
        title="Survey Task Specification",
        border_style="blue",
    ))

    # Question summary table
    table = Table(title="Questions")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Text")

    for q in survey.questions:
        q_type = q.type.value.replace("_", " ").title()
        text = q.text[:50] + "..." if len(q.text) > 50 else q.text
        table.add_row(q.id, q_type, text)

    console.print(table)

    if verbose:
        console.print("\n[bold]Question Prompts:[/bold]")
        for i, qp in enumerate(spec.get("question_prompts", []), 1):
            console.print(f"\n[dim]Question {i}: {qp['question_id']}[/dim]")
            prompt_preview = qp["prompt"][:200] + "..." if len(qp["prompt"]) > 200 else qp["prompt"]
            console.print(Panel(prompt_preview, border_style="dim"))

    console.print("\n[yellow]Note:[/yellow] Execute the generated prompts with a Claude Code subagent.")
