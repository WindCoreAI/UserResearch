"""CLI commands for focus group research.

Provides commands for running focus groups and creating configurations.
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

from models.protocol import FocusGroupProtocol
from services.focus_group_engine import FocusGroupEngine
from services.protocol_loader import ProtocolLoader, ProtocolLoaderError

console = Console()


@click.group(name="focus-group")
def focus_group_group():
    """Focus group research commands."""
    pass


@focus_group_group.command(name="run")
@click.option(
    "--config", "-c",
    required=True,
    help="Focus group config ID",
)
@click.option(
    "--topic", "-t",
    help="Discussion topic (overrides config default)",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Export discussion log to JSON file",
)
@click.option(
    "--report", "-r",
    type=click.Path(),
    help="Generate Markdown discussion report",
)
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "--rounds",
    type=int,
    help="Number of discussion rounds (default: from config)",
)
@click.option(
    "--timeout",
    type=int,
    default=60,
    help="Per-turn timeout in seconds (default: 60)",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show turn-by-turn progress",
)
def run_focus_group(
    config: str,
    topic: Optional[str],
    output: Optional[str],
    report: Optional[str],
    output_format: str,
    rounds: Optional[int],
    timeout: int,
    verbose: bool,
):
    """Execute a focus group discussion.

    Example:
        research-cli research focus-group run -c sample-focus-group -t "What do you think about our pricing?"
    """
    from services.persona_library import PersonaLibrary

    # Load protocol
    loader = ProtocolLoader()
    try:
        proto = loader.load_by_id(config)
        if not isinstance(proto, FocusGroupProtocol):
            console.print(f"[red]Protocol '{config}' is not a focus group config[/red]")
            sys.exit(1)
    except ProtocolLoaderError:
        console.print(f"[red]PROTOCOL_NOT_FOUND: Focus group config '{config}' not found[/red]")
        console.print("[dim]Use 'research protocol list --type focus-group' to see available configs[/dim]")
        sys.exit(1)

    focus_group = proto.focus_group

    # Load personas
    library = PersonaLibrary()
    personas = []
    missing_personas = []

    for persona_id in focus_group.persona_ids:
        try:
            persona_obj = library.get_by_id(persona_id)
            personas.append(persona_obj)
        except FileNotFoundError:
            missing_personas.append(persona_id)

    if missing_personas:
        console.print(f"[red]PERSONA_NOT_FOUND: Missing personas: {missing_personas}[/red]")
        console.print("[dim]Use 'research-cli persona list' to see available personas[/dim]")
        sys.exit(1)

    # Use topic from argument or config
    discussion_topic = topic or (focus_group.discussion_topics[0] if focus_group.discussion_topics else "General discussion")

    # Update rounds if specified
    if rounds:
        focus_group.config.max_rounds = rounds

    # Execute focus group
    engine = FocusGroupEngine()

    if verbose:
        console.print(Panel(
            f"[bold]Focus Group:[/bold] {focus_group.name}\n"
            f"[bold]Topic:[/bold] {discussion_topic}\n"
            f"[bold]Participants:[/bold] {len(personas)}\n"
            f"[bold]Rounds:[/bold] {focus_group.config.max_rounds}",
            title="Focus Group Execution",
            border_style="blue",
        ))

        # List participants
        table = Table(title="Participants")
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        for p in personas:
            table.add_row(p.id, p.name)
        console.print(table)

    # Generate task specification
    spec = engine.get_task_specification(focus_group, discussion_topic, personas)

    if output_format == "json":
        output_data = {
            "group_id": focus_group.id,
            "group_version": focus_group.version,
            "method": "focus_group",
            "topic": discussion_topic,
            "participants": [{"id": p.id, "name": p.name} for p in personas],
            "config": {
                "max_rounds": focus_group.config.max_rounds,
                "turns_per_round": len(personas),
                "allow_cross_references": focus_group.config.allow_cross_references,
            },
            "timeout_per_turn": timeout,
            "task_specification": spec,
            "metadata": {
                "started_at": datetime.utcnow().isoformat() + "Z",
            }
        }
        console.print_json(json.dumps(output_data, indent=2, default=str))
    else:
        _format_focus_group_task_spec(spec, focus_group, discussion_topic, personas, console, verbose)

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


@focus_group_group.command(name="create")
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
    help="Output path for created config",
)
def create_focus_group(
    yaml_path: Optional[str],
    interactive: bool,
    output: Optional[str],
):
    """Create a new focus group configuration.

    Example:
        research-cli research focus-group create -f my-focus-group.yaml
    """
    import yaml as yaml_lib

    from models.focus_group import FocusGroup, FocusGroupConfig

    if yaml_path:
        try:
            with open(yaml_path) as f:
                data = yaml_lib.safe_load(f)
        except (OSError, yaml_lib.YAMLError) as e:
            console.print(f"[red]Error reading YAML file: {e}[/red]")
            sys.exit(1)

        try:
            fg_data = data.get("focus_group", {})
            config_data = fg_data.get("config", {})

            config = FocusGroupConfig(
                max_rounds=config_data.get("max_rounds", 3),
                turns_per_round=config_data.get("turns_per_round", 6),
                moderator_prompts_enabled=config_data.get("moderator_prompts_enabled", True),
                allow_cross_references=config_data.get("allow_cross_references", True),
            )

            focus_group = FocusGroup(
                id=fg_data.get("id", ""),
                version=fg_data.get("version", "1.0.0"),
                name=fg_data.get("name", ""),
                description=fg_data.get("description"),
                persona_ids=fg_data.get("persona_ids", []),
                discussion_topics=fg_data.get("discussion_topics", []),
                config=config,
            )

            protocol = FocusGroupProtocol(
                id=data.get("protocol", {}).get("id", focus_group.id),
                version=data.get("protocol", {}).get("version", focus_group.version),
                name=data.get("protocol", {}).get("name", focus_group.name),
                description=data.get("protocol", {}).get("description"),
                tags=data.get("protocol", {}).get("tags", []),
                focus_group=focus_group,
            )

            loader = ProtocolLoader()
            saved_path = loader.save_protocol(protocol)
            console.print(f"[green]Created focus group config: {protocol.id}[/green]")
            console.print(f"[dim]Saved to: {saved_path}[/dim]")

        except Exception as e:
            console.print(f"[red]Error creating focus group config: {e}[/red]")
            sys.exit(1)

    elif interactive:
        console.print("[yellow]Interactive creation not yet implemented[/yellow]")
        sys.exit(0)
    else:
        console.print("[red]Error: Specify --from-yaml or --interactive[/red]")
        sys.exit(1)


def _format_focus_group_task_spec(
    spec: dict,
    focus_group,
    topic: str,
    personas: list,
    console: Console,
    verbose: bool = False,
):
    """Format focus group task specification for display."""
    console.print(Panel(
        f"[bold]Focus Group:[/bold] {focus_group.name} (v{focus_group.version})\n"
        f"[bold]Topic:[/bold] {topic}\n"
        f"[bold]Participants:[/bold] {len(personas)}\n"
        f"[bold]Rounds:[/bold] {focus_group.config.max_rounds}",
        title="Focus Group Task Specification",
        border_style="blue",
    ))

    # Participant table
    table = Table(title="Participants")
    table.add_column("Order", style="dim")
    table.add_column("ID", style="cyan")
    table.add_column("Name")

    for i, p in enumerate(personas, 1):
        table.add_row(str(i), p.id, p.name)

    console.print(table)

    # Discussion flow
    console.print("\n[bold]Discussion Flow:[/bold]")
    console.print(f"  Total Rounds: {focus_group.config.max_rounds}")
    console.print(f"  Turns per Round: {len(personas)}")
    console.print(f"  Total Turns: {focus_group.config.max_rounds * len(personas)}")
    console.print(f"  Cross-References: {'Enabled' if focus_group.config.allow_cross_references else 'Disabled'}")

    if verbose:
        console.print("\n[bold]Round 1 Turn Prompts (preview):[/bold]")
        rounds = spec.get("rounds", [])
        if rounds:
            first_round = rounds[0]
            for turn in first_round.get("turns", [])[:2]:
                console.print(f"\n[dim]Turn: {turn['persona_name']}[/dim]")
                prompt = turn.get("prompt_template", "")
                prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
                console.print(Panel(prompt_preview, border_style="dim"))

    console.print("\n[yellow]Note:[/yellow] Execute turns sequentially, updating previous_turns context.")
