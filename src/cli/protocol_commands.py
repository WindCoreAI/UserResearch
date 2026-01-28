"""CLI commands for protocol management.

Provides commands for listing, showing, and deleting research protocols.
"""

import json
import sys
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.table import Table

from models.enums import ResearchMethodType
from services.protocol_loader import ProtocolLoader, ProtocolLoaderError

console = Console()


@click.group(name="protocol")
def protocol_group():
    """Manage research protocols - list, show, and delete."""
    pass


@protocol_group.command(name="list")
@click.option(
    "--type",
    "-t",
    "method_type",
    type=click.Choice(["survey", "interview", "focus-group"]),
    default=None,
    help="Filter by protocol type",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
def list_protocols(method_type: Optional[str], output_format: str):
    """List available research protocols."""
    loader = ProtocolLoader()

    # Convert type string to enum
    method_enum = None
    if method_type:
        type_map = {
            "survey": ResearchMethodType.SURVEY,
            "interview": ResearchMethodType.INTERVIEW,
            "focus-group": ResearchMethodType.FOCUS_GROUP,
        }
        method_enum = type_map.get(method_type)

    protocols = loader.list_protocols(method_type=method_enum)

    if output_format == "json":
        data = [
            {
                "id": p.id,
                "type": p.type.value,
                "version": p.version,
                "name": p.name,
                "description": p.description,
                "tags": p.tags,
            }
            for p in protocols
        ]
        console.print_json(json.dumps(data, indent=2))

    elif output_format == "yaml":
        data = [
            {
                "id": p.id,
                "type": p.type.value,
                "version": p.version,
                "name": p.name,
            }
            for p in protocols
        ]
        console.print(yaml.dump(data, default_flow_style=False))

    else:
        # Table format
        if not protocols:
            console.print("[dim]No protocols found[/dim]")
            return

        table = Table(title="Available Research Protocols")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Version")
        table.add_column("Name")

        for p in protocols:
            type_display = p.type.value.replace("_", "-")
            table.add_row(p.id, type_display, p.version, p.name)

        console.print(table)


@protocol_group.command(name="show")
@click.argument("protocol_id")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Output format",
)
def show_protocol(protocol_id: str, output_format: str):
    """Show details of a specific protocol."""
    loader = ProtocolLoader()

    try:
        protocol = loader.load_by_id(protocol_id)
    except ProtocolLoaderError:
        console.print(f"[red]PROTOCOL_NOT_FOUND: Protocol '{protocol_id}' not found[/red]")
        console.print("[dim]Use 'research protocol list' to see available protocols[/dim]")
        sys.exit(1)

    if output_format == "json":
        # Serialize to JSON
        data = _protocol_to_dict(protocol)
        console.print_json(json.dumps(data, indent=2, default=str))
    else:
        # YAML format
        data = _protocol_to_dict(protocol)
        console.print(yaml.dump(data, default_flow_style=False, sort_keys=False))


@protocol_group.command(name="delete")
@click.argument("protocol_id")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Skip confirmation prompt",
)
def delete_protocol(protocol_id: str, force: bool):
    """Delete a research protocol."""
    loader = ProtocolLoader()

    # Verify protocol exists
    try:
        loader.load_by_id(protocol_id)  # Just verify it exists
    except ProtocolLoaderError:
        console.print(f"[red]PROTOCOL_NOT_FOUND: Protocol '{protocol_id}' not found[/red]")
        console.print("[dim]Use 'research protocol list' to see available protocols[/dim]")
        sys.exit(1)

    # Confirm deletion
    if not force:
        if not click.confirm(
            f"Are you sure you want to delete protocol '{protocol_id}'?"
        ):
            console.print("[yellow]Cancelled[/yellow]")
            sys.exit(0)

    # Delete
    try:
        loader.delete_protocol(protocol_id)
        console.print(f"[green]Deleted protocol: {protocol_id}[/green]")
    except ProtocolLoaderError as e:
        console.print(f"[red]Error deleting protocol: {e}[/red]")
        sys.exit(1)


def _protocol_to_dict(protocol) -> dict:
    """Convert a protocol to a dictionary for serialization."""
    from models.protocol import FocusGroupProtocol, InterviewProtocol, SurveyProtocol

    base = {
        "protocol": {
            "id": protocol.id,
            "version": protocol.version,
            "type": protocol.type.value,
            "name": protocol.name,
            "description": protocol.description,
            "tags": protocol.tags,
            "created_at": protocol.created_at.isoformat() if protocol.created_at else None,
        }
    }

    if isinstance(protocol, SurveyProtocol):
        survey = protocol.survey
        base["survey"] = {
            "id": survey.id,
            "version": survey.version,
            "name": survey.name,
            "description": survey.description,
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "type": q.type.value,
                    "required": q.required,
                    "scale_min": q.scale_min,
                    "scale_max": q.scale_max,
                    "scale_labels": q.scale_labels,
                    "options": q.options,
                }
                for q in survey.questions
            ],
        }
    elif isinstance(protocol, InterviewProtocol):
        guide = protocol.guide
        base["guide"] = {
            "id": guide.id,
            "version": guide.version,
            "name": guide.name,
            "topic": guide.topic,
            "description": guide.description,
            "min_response_length": guide.min_response_length,
            "default_max_followups": guide.default_max_followups,
            "sections": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "transition_prompt": s.transition_prompt,
                    "questions": [
                        {
                            "id": q.id,
                            "text": q.text,
                            "allow_followups": q.allow_followups,
                            "max_followup_depth": q.max_followup_depth,
                            "probes": [
                                {
                                    "type": p.type.value,
                                    "trigger": p.trigger,
                                    "question_template": p.question_template,
                                }
                                for p in q.probes
                            ],
                        }
                        for q in s.questions
                    ],
                }
                for s in guide.sections
            ],
        }
    elif isinstance(protocol, FocusGroupProtocol):
        fg = protocol.focus_group
        base["focus_group"] = {
            "id": fg.id,
            "version": fg.version,
            "name": fg.name,
            "description": fg.description,
            "persona_ids": fg.persona_ids,
            "discussion_topics": fg.discussion_topics,
            "config": {
                "max_rounds": fg.config.max_rounds,
                "turns_per_round": fg.config.turns_per_round,
                "moderator_prompts_enabled": fg.config.moderator_prompts_enabled,
                "allow_cross_references": fg.config.allow_cross_references,
            },
        }

    return base
