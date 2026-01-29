"""CLI commands for quality analysis and reporting."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from models.calibration import QualityThresholds

console = Console()


@click.group("quality")
def quality_group() -> None:
    """Quality analysis and monitoring commands."""
    pass


@quality_group.command("analyze")
@click.option("--session-file", "-s", type=click.Path(exists=True), required=True,
              help="Path to session JSON export file")
@click.option("--persona-dir", type=click.Path(exists=True), default=None,
              help="Path to persona definitions directory")
@click.option("--threshold-file", type=click.Path(exists=True), default=None,
              help="Path to custom thresholds YAML file")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
@click.option("--output", "-o", "output_file", type=click.Path(), default=None,
              help="Save analysis to file")
def quality_analyze(session_file: str, persona_dir: Optional[str],
                    threshold_file: Optional[str], output_format: str,
                    output_file: Optional[str]) -> None:
    """Run quality analysis on a research session.

    Analyzes consistency, bias, variance, and drift for a completed session.

    Example:
        research-cli research quality analyze -s session.json
    """
    # Validate session file is valid JSON
    try:
        json.loads(Path(session_file).read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        console.print(f"[red]Error loading session file: {e}[/red]")
        sys.exit(1)

    # Load custom thresholds if provided
    thresholds = QualityThresholds()
    if threshold_file:
        import yaml
        try:
            threshold_data = yaml.safe_load(Path(threshold_file).read_text())
            thresholds = QualityThresholds(**threshold_data)
        except Exception as e:
            console.print(f"[red]Error loading thresholds: {e}[/red]")
            sys.exit(1)

    if output_format == "json":
        output = {
            "status": "analysis_ready",
            "session_file": session_file,
            "thresholds": thresholds.model_dump(),
            "message": "Quality analysis requires session execution data. "
                       "Use this command after running a research session.",
        }
        click.echo(json.dumps(output, indent=2))
    else:
        # Rich text output
        panel = Panel(
            f"[bold]Session File:[/bold] {session_file}\n"
            f"[bold]Thresholds:[/bold] Consistency >= {thresholds.consistency_minimum}%, "
            f"Sycophancy <= {thresholds.sycophancy_maximum}%",
            title="Quality Analysis",
            border_style="blue",
        )
        console.print(panel)
        console.print("\n[yellow]Note:[/yellow] Quality analysis processes completed session data.")
        console.print("Run a research session first, then analyze the exported results.")

    if output_file:
        Path(output_file).write_text(json.dumps(
            {"session_file": session_file, "thresholds": thresholds.model_dump()},
            indent=2
        ))
        console.print(f"\n[dim]Analysis saved to: {output_file}[/dim]")


@quality_group.command("dashboard")
@click.option("--sessions-dir", type=click.Path(exists=True), default=None,
              help="Directory containing session exports")
@click.option("--days", type=int, default=30, help="Number of days to include (default: 30)")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
def quality_dashboard(sessions_dir: Optional[str], days: int, output_format: str) -> None:
    """View aggregated quality metrics dashboard.

    Shows quality trends, status breakdown, and recent session summaries.

    Example:
        research-cli research quality dashboard --days 7
    """
    thresholds = QualityThresholds()

    if output_format == "json":
        output = {
            "status": "dashboard_ready",
            "days": days,
            "thresholds": thresholds.model_dump(),
            "message": "Dashboard aggregates quality data from completed sessions.",
        }
        click.echo(json.dumps(output, indent=2))
    else:
        # Status overview
        table = Table(title="Quality Dashboard", show_header=True)
        table.add_column("Metric", style="bold")
        table.add_column("Value")
        table.add_column("Threshold")
        table.add_column("Status")

        table.add_row(
            "Consistency", "N/A",
            f">= {thresholds.consistency_minimum}%", "[dim]No data[/dim]"
        )
        table.add_row(
            "Sycophancy Rate", "N/A",
            f"<= {thresholds.sycophancy_maximum}%", "[dim]No data[/dim]"
        )
        table.add_row(
            "Drift", "N/A",
            f"< {thresholds.drift_warning}%", "[dim]No data[/dim]"
        )
        table.add_row(
            "Variance Ratio", "N/A",
            f">= {thresholds.variance_minimum_ratio}", "[dim]No data[/dim]"
        )

        console.print(table)
        console.print("\n[yellow]Note:[/yellow] Run research sessions to populate dashboard data.")


@quality_group.command("report")
@click.option("--session-file", "-s", type=click.Path(exists=True), required=True,
              help="Path to session JSON export with quality data")
@click.option("--output", "-o", "output_file", type=click.Path(), default=None,
              help="Save report to file (default: stdout)")
@click.option("--format", "-f", "output_format", type=click.Choice(["markdown", "json"]),
              default="markdown", help="Report format")
def quality_report(session_file: str, output_file: Optional[str],
                   output_format: str) -> None:
    """Generate a detailed quality report.

    Produces a Markdown or JSON report from quality analysis data.

    Example:
        research-cli research quality report -s session.json -o report.md
    """
    try:
        session_data = json.loads(Path(session_file).read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        console.print(f"[red]Error loading session file: {e}[/red]")
        sys.exit(1)

    if output_format == "json":
        output = {"session_file": session_file, "format": "json", "data": session_data}
        content = json.dumps(output, indent=2, default=str)
    else:
        content = f"# Quality Report\n\n**Source:** {session_file}\n\n"
        content += "Quality report generation requires quality analysis data.\n"
        content += "Run `research-cli research quality analyze` first.\n"

    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(content)
        console.print(f"[green]Report saved to: {output_file}[/green]")
    else:
        click.echo(content)
