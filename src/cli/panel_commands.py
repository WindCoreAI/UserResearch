"""CLI commands for panel research operations.

Provides the 'research panel' command group with subcommands for
running panel research, listing panels, and managing custom panels.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from cli.formatters import (
    format_limitations_disclaimer,
    format_panel_details,
    format_panel_list,
    format_panel_session_complete,
)
from models.panel import PanelSession, PanelSessionStatus
from models.question import QuestionType, ResearchQuestion
from services.panel_loader import PanelLoader, PanelLoaderError
from services.panel_executor import PanelExecutor
from services.response_aggregator import ResponseAggregator

console = Console()


@click.group(name="panel")
def panel_group():
    """Panel research commands for multi-persona sessions."""
    pass


@panel_group.command(name="run")
@click.option(
    "--panel", "-p",
    required=True,
    help="Panel ID (pre-built or custom)",
)
@click.option(
    "--question", "-q",
    required=True,
    help="Research question to ask all personas (max 2000 chars)",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Export JSON data to file",
)
@click.option(
    "--report", "-r",
    type=click.Path(),
    help="Generate Markdown report to file",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress progress display",
)
@click.option(
    "--timeout",
    type=int,
    default=120,
    help="Per-persona timeout in seconds (default: 120)",
)
def run_panel(
    panel: str,
    question: str,
    format: str,
    output: Optional[str],
    report: Optional[str],
    quiet: bool,
    timeout: int,
):
    """Execute a panel research session with all personas in parallel."""
    # Validate question length
    if len(question) > 2000:
        console.print("[red]QUESTION_TOO_LONG: Question exceeds 2000 characters[/red]")
        console.print(f"[dim]Current length: {len(question)} characters. Please shorten the question.[/dim]")
        sys.exit(1)

    # Load panel
    loader = PanelLoader()
    try:
        research_panel = loader.load_by_id(panel)
    except PanelLoaderError as e:
        console.print(f"[red]PANEL_NOT_FOUND: Panel '{panel}' not found[/red]")
        console.print("[dim]Use 'research panel list' to see available panels[/dim]")
        sys.exit(1)

    # Create research question
    research_question = ResearchQuestion(
        text=question,
        type=QuestionType.OPEN_ENDED,
    )

    # Execute panel research
    executor = PanelExecutor(timeout_seconds=timeout)
    aggregator = ResponseAggregator()

    async def execute():
        if quiet:
            # Simple execution without progress display
            session = await executor.execute_panel(research_panel, research_question)
        else:
            # Execute with progress display
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Running panel: {research_panel.name}",
                    total=len(research_panel.persona_ids),
                )

                def progress_callback(completed: int, total: int, persona_id: str):
                    progress.update(task, completed=completed)

                session = await executor.execute_panel(
                    research_panel,
                    research_question,
                    progress_callback=progress_callback,
                )

        # Aggregate responses if we have successful ones
        if session.status != PanelSessionStatus.FAILED:
            session.status = PanelSessionStatus.AGGREGATING

            # Filter valid sessions for aggregation
            valid_sessions = [
                s for s in session.individual_sessions
                if s.response and s.response.parsed
            ]

            if valid_sessions:
                aggregation = await aggregator.aggregate_responses(
                    valid_sessions,
                    question,
                    research_panel.name,
                )
                session.aggregation = aggregation

                # Calculate quality metrics
                individual_metrics = [
                    s.response.quality
                    for s in valid_sessions
                    if s.response and s.response.quality
                ]

                completion_rate = (len(valid_sessions) / len(research_panel.persona_ids)) * 100
                session.quality = aggregator.calculate_panel_quality_metrics(
                    individual_metrics=individual_metrics,
                    completion_rate=completion_rate,
                    theme_confidence=aggregation.aggregation_confidence,
                    divergence_score=30.0,  # Placeholder - would be calculated from divergence points
                )

            session.status = PanelSessionStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)

        return session

    # Run the async execution
    session = asyncio.run(execute())

    # Handle output
    if format == "json":
        console.print_json(json.dumps(session.to_dict(), default=str))
    else:
        format_panel_session_complete(session, console)

    # Export to file if requested
    if output:
        try:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(session.to_dict(), f, indent=2, default=str)
            console.print(f"\n[green]✓ Exported to {output_path}[/green]")
        except (OSError, IOError) as e:
            console.print(f"[red]Error writing output file: {e}[/red]")

    # Generate report if requested
    if report:
        try:
            from services.report_generator import ReportGenerator
            generator = ReportGenerator()
            report_content = generator.generate_report(session)
            report_path = Path(report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w") as f:
                f.write(report_content)
            console.print(f"[green]✓ Report saved to {report_path}[/green]")
        except (OSError, IOError) as e:
            console.print(f"[red]Error writing report file: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error generating report: {e}[/red]")

    # Set exit code based on status
    if session.status == PanelSessionStatus.FAILED:
        sys.exit(1)
    elif session.status == PanelSessionStatus.PARTIAL or (session.quality and not session.quality.passed_gates):
        sys.exit(2)
    else:
        sys.exit(0)


@panel_group.command(name="list")
@click.option(
    "--type", "-t",
    type=click.Choice(["all", "prebuilt", "custom"]),
    default="all",
    help="Filter by panel type",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def list_panels(type: str, format: str):
    """List available research panels."""
    loader = PanelLoader()
    panels = loader.list_panels(panel_type=type)

    if format == "json":
        panel_data = [p.to_dict() for p in panels]
        console.print_json(json.dumps(panel_data, default=str))
    else:
        format_panel_list(panels, console, type)


@panel_group.command(name="show")
@click.argument("panel_id")
@click.option(
    "--format", "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def show_panel(panel_id: str, format: str):
    """Show details of a specific panel."""
    loader = PanelLoader()

    try:
        panel = loader.load_by_id(panel_id)
    except PanelLoaderError:
        console.print(f"[red]PANEL_NOT_FOUND: Panel '{panel_id}' not found[/red]")
        console.print("[dim]Use 'research panel list' to see available panels[/dim]")
        sys.exit(1)

    if format == "json":
        console.print_json(json.dumps(panel.to_dict(), default=str))
    else:
        format_panel_details(panel, console)


@panel_group.command(name="create")
@click.option(
    "--name", "-n",
    required=True,
    help="Panel ID (slug format: lowercase, hyphens)",
)
@click.option(
    "--personas", "-p",
    required=True,
    help="Comma-separated persona IDs",
)
@click.option(
    "--description", "-d",
    default="",
    help="Panel description",
)
def create_panel(name: str, personas: str, description: str):
    """Create a custom panel."""
    from models.panel import ResearchPanel
    from services.persona_library import PersonaLibrary

    # Parse persona IDs
    persona_ids = [p.strip() for p in personas.split(",") if p.strip()]

    if len(persona_ids) < 2:
        console.print("[red]Error: Panel must have at least 2 personas[/red]")
        sys.exit(1)

    if len(persona_ids) > 50:
        console.print("[red]Error: Panel cannot have more than 50 personas[/red]")
        sys.exit(1)

    # Validate persona IDs exist
    library = PersonaLibrary()
    available_personas = [p.id for p in library.list_all()]
    invalid_ids = [pid for pid in persona_ids if pid not in available_personas]

    if invalid_ids:
        console.print(f"[red]PERSONA_NOT_FOUND: Invalid persona IDs: {invalid_ids}[/red]")
        console.print("\n[bold]Available personas:[/bold]")
        for pid in available_personas:
            console.print(f"  - {pid}")
        sys.exit(1)

    # Create panel
    try:
        panel = ResearchPanel(
            id=name,
            name=name.replace("-", " ").title(),
            description=description or f"Custom panel: {name}",
            persona_ids=persona_ids,
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )
    except Exception as e:
        console.print(f"[red]Error: Invalid panel name format[/red]")
        console.print(f"[dim]Panel ID must be slug format (lowercase, hyphens only)[/dim]")
        sys.exit(1)

    # Save panel
    loader = PanelLoader()
    try:
        saved_path = loader.save_custom_panel(panel)
        console.print(f"[green]✓ Created custom panel: {name}[/green]")
        console.print(f"\n  Personas: {', '.join(persona_ids)}")
        console.print(f"  Saved to: {saved_path}")
        console.print(f"\n  Use with: research-cli research panel run --panel={name} --question=\"...\"")
    except PanelLoaderError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@panel_group.command(name="delete")
@click.argument("panel_id")
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Skip confirmation prompt",
)
def delete_panel(panel_id: str, force: bool):
    """Delete a custom panel."""
    loader = PanelLoader()

    # Check if panel exists and is custom
    try:
        panel = loader.load_by_id(panel_id)
    except PanelLoaderError:
        console.print(f"[red]PANEL_NOT_FOUND: Panel '{panel_id}' not found[/red]")
        console.print("[dim]Use 'research panel list' to see available panels[/dim]")
        sys.exit(1)

    if not panel.is_custom:
        console.print(f"[red]CANNOT_DELETE_PREBUILT: Cannot delete pre-built panel '{panel_id}'[/red]")
        console.print("[dim]Only custom panels can be deleted[/dim]")
        sys.exit(1)

    # Confirm deletion
    if not force:
        if not click.confirm(f"Are you sure you want to delete panel '{panel_id}'?"):
            console.print("[yellow]Cancelled[/yellow]")
            sys.exit(0)

    # Delete panel
    try:
        loader.delete_custom_panel(panel_id)
        console.print(f"[green]✓ Deleted panel: {panel_id}[/green]")
    except PanelLoaderError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
