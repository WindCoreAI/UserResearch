"""CLI commands for calibration baseline management."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from services.calibration_pipeline import CalibrationPipeline

console = Console()


@click.group("calibration")
def calibration_group() -> None:
    """Calibration baseline management commands."""
    pass


@calibration_group.command("import")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--name", "-n", required=True, help="Baseline name")
@click.option("--source", "-s", default="", help="Data source description")
@click.option("--format", "-f", "file_format", type=click.Choice(["csv", "json"]),
              default="csv", help="Import file format")
@click.option("--tags", "-t", multiple=True, help="Demographic tags")
@click.option("--baselines-dir", type=click.Path(), default=None,
              help="Directory for baseline storage")
@click.option("--output", "-o", "output_format", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
def calibration_import(file_path: str, name: str, source: str,
                       file_format: str, tags: tuple, baselines_dir: Optional[str],
                       output_format: str) -> None:
    """Import real user data as a calibration baseline.

    Supports CSV and JSON formats with rating and multiple-choice response data.

    Example:
        research-cli research calibration import data.csv -n "Q1 Survey" -s "Field study"
    """
    pipeline = CalibrationPipeline(
        baselines_dir=Path(baselines_dir) if baselines_dir else None,
    )

    try:
        path = Path(file_path)
        tag_list = list(tags) if tags else None

        if file_format == "csv":
            baseline = pipeline.import_csv(path, name=name, source=source, tags=tag_list)
        else:
            baseline = pipeline.import_json(path, name=name, source=source, tags=tag_list)

        saved_path = pipeline.save_baseline(baseline)

        if output_format == "json":
            click.echo(json.dumps({
                "id": baseline.id,
                "name": baseline.name,
                "sample_size": baseline.sample_size,
                "distributions": len(baseline.distributions),
                "saved_to": str(saved_path),
            }, indent=2))
        else:
            console.print("[green]Baseline imported successfully![/green]")
            console.print(f"  ID: {baseline.id}")
            console.print(f"  Name: {baseline.name}")
            console.print(f"  Sample Size: {baseline.sample_size}")
            console.print(f"  Distributions: {len(baseline.distributions)}")
            console.print(f"  Saved to: {saved_path}")

    except Exception as e:
        console.print(f"[red]Error importing baseline: {e}[/red]")
        sys.exit(1)


@calibration_group.command("list")
@click.option("--tags", "-t", multiple=True, help="Filter by tags")
@click.option("--baselines-dir", type=click.Path(), default=None,
              help="Directory for baseline storage")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
def calibration_list(tags: tuple, baselines_dir: Optional[str],
                     output_format: str) -> None:
    """List available calibration baselines.

    Example:
        research-cli research calibration list --tags early_adopter
    """
    pipeline = CalibrationPipeline(
        baselines_dir=Path(baselines_dir) if baselines_dir else None,
    )

    tag_list = list(tags) if tags else None
    baselines = pipeline.list_baselines(tags=tag_list)

    if output_format == "json":
        output = [{
            "id": b.id,
            "name": b.name,
            "sample_size": b.sample_size,
            "distributions": len(b.distributions),
            "tags": b.demographic_tags,
        } for b in baselines]
        click.echo(json.dumps(output, indent=2, default=str))
    else:
        if not baselines:
            console.print("[dim]No calibration baselines found.[/dim]")
            console.print("Import data using: research-cli research calibration import <file>")
            return

        table = Table(title="Calibration Baselines", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Samples", justify="right")
        table.add_column("Distributions", justify="right")
        table.add_column("Tags")

        for b in baselines:
            table.add_row(
                b.id, b.name,
                str(b.sample_size),
                str(len(b.distributions)),
                ", ".join(b.demographic_tags) if b.demographic_tags else "-",
            )

        console.print(table)


@calibration_group.command("compare")
@click.option("--baseline", "-b", required=True, help="Baseline ID to compare against")
@click.option("--session-file", "-s", type=click.Path(exists=True), required=True,
              help="Path to session JSON export")
@click.option("--baselines-dir", type=click.Path(), default=None,
              help="Directory for baseline storage")
@click.option("--output", "-o", "output_file", type=click.Path(), default=None,
              help="Save comparison to file")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
def calibration_compare(baseline: str, session_file: str,
                        baselines_dir: Optional[str], output_file: Optional[str],
                        output_format: str) -> None:
    """Compare synthetic results against a calibration baseline.

    Example:
        research-cli research calibration compare -b baseline-2026 -s session.json
    """
    pipeline = CalibrationPipeline(
        baselines_dir=Path(baselines_dir) if baselines_dir else None,
    )

    try:
        session_data = json.loads(Path(session_file).read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        console.print(f"[red]Error loading session file: {e}[/red]")
        sys.exit(1)

    try:
        # Extract synthetic results from session
        synthetic_results = session_data.get("results", [])
        comparison = pipeline.compare(baseline, synthetic_results)

        if output_format == "json":
            output = comparison.model_dump(mode="json")
            content = json.dumps(output, indent=2, default=str)
            if output_file:
                Path(output_file).write_text(content)
                console.print(f"[green]Comparison saved to: {output_file}[/green]")
            else:
                click.echo(content)
        else:
            # Rich text output
            status_color = {
                "aligned": "green",
                "partial": "yellow",
                "divergent": "red",
            }.get(comparison.alignment_status.value, "white")

            panel = Panel(
                f"[bold]Baseline:[/bold] {comparison.baseline_id}\n"
                f"[bold]Overall Overlap:[/bold] {comparison.overall_overlap:.1f}%\n"
                f"[bold]Status:[/bold] [{status_color}]"
                f"{comparison.alignment_status.value.upper()}[/{status_color}]",
                title="Calibration Comparison",
                border_style=status_color,
            )
            console.print(panel)

            if comparison.recommendations:
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in comparison.recommendations:
                    console.print(f"  [{rec.priority.value.upper()}] {rec.rationale}")

            if output_file:
                Path(output_file).write_text(json.dumps(
                    comparison.model_dump(mode="json"), indent=2, default=str
                ))
                console.print(f"\n[dim]Saved to: {output_file}[/dim]")

    except FileNotFoundError:
        console.print(f"[red]Baseline not found: {baseline}[/red]")
        console.print("Use 'research-cli research calibration list' to see available baselines.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error comparing: {e}[/red]")
        sys.exit(1)
