"""Rich output formatters for CLI display.

Formats research session results for terminal output using Rich.
"""

from typing import Callable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text

from models.aggregation import AggregatedResults, PanelQualityMetrics
from models.panel import PanelSession, PanelSessionStatus
from models.session import ResearchSession


def format_session_header(session: ResearchSession, console: Console) -> None:
    """Display the session header with persona and question info.

    Args:
        session: The research session to display.
        console: Rich console for output.
    """
    # Build header content
    header_lines = [
        f"[bold]Persona:[/bold] {session.persona_name} ({session.persona_id})",
        f"[bold]Question:[/bold] {session.question.text}",
    ]

    if session.question.type.value != "open_ended":
        header_lines.append(f"[bold]Type:[/bold] {session.question.type.value.replace('_', ' ').title()}")

    panel = Panel(
        "\n".join(header_lines),
        title="Research Session",
        border_style="blue",
    )
    console.print(panel)


def format_raw_response(session: ResearchSession, console: Console) -> None:
    """Display the raw response from the persona.

    Args:
        session: The research session with response.
        console: Rich console for output.
    """
    if not session.response:
        console.print("[yellow]No response available[/yellow]")
        return

    # Response timing
    response_time = session.response.response_time_ms / 1000
    console.print(f"\n[dim]Response time: {response_time:.2f}s[/dim]")

    # Raw response
    console.print("\n[bold]Raw Response:[/bold]")
    console.print(Panel(session.response.raw_text, border_style="dim"))


def format_session_status(session: ResearchSession, console: Console) -> None:
    """Display the session status.

    Args:
        session: The research session.
        console: Rich console for output.
    """
    status_colors = {
        "pending": "yellow",
        "running": "blue",
        "completed": "green",
        "failed": "red",
        "timeout": "red",
    }

    color = status_colors.get(session.status.value, "white")
    console.print(f"\n[bold]Status:[/bold] [{color}]{session.status.value.upper()}[/{color}]")


def format_limitations_disclaimer(console: Console) -> None:
    """Display the synthetic data limitations disclaimer.

    Args:
        console: Rich console for output.
    """
    disclaimer = Text()
    disclaimer.append("\n")
    disclaimer.append("SYNTHETIC DATA: ", style="bold yellow")
    disclaimer.append("Validate critical findings with real users.", style="yellow")
    console.print(disclaimer)


def format_parsed_response(session: ResearchSession, console: Console) -> None:
    """Display the parsed response with sentiment, concerns, suggestions.

    Args:
        session: The research session with parsed response.
        console: Rich console for output.
    """
    if not session.response or not session.response.parsed:
        return

    parsed = session.response.parsed

    # Response Summary Table
    console.print("\n[bold]Response Summary[/bold]")
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    # Sentiment with color
    sentiment_colors = {
        "positive": "green",
        "negative": "red",
        "mixed": "yellow",
        "neutral": "white",
    }
    sentiment_color = sentiment_colors.get(parsed.sentiment.value, "white")
    table.add_row("Sentiment", f"[{sentiment_color}]{parsed.sentiment.value.upper()}[/{sentiment_color}]")
    table.add_row("Overall Impression", parsed.overall_impression)

    # Rating if present
    if parsed.rating is not None:
        table.add_row("Rating", f"{parsed.rating}/10")

    # Selected option if present
    if parsed.selected_option:
        table.add_row("Selected Option", parsed.selected_option)

    console.print(table)

    # Concerns
    if parsed.concerns:
        console.print("\n[bold yellow]Concerns:[/bold yellow]")
        for concern in parsed.concerns:
            console.print(f"  • {concern}")
    else:
        console.print("\n[dim]No concerns raised[/dim]")

    # Suggestions
    if parsed.suggestions:
        console.print("\n[bold cyan]Suggestions:[/bold cyan]")
        for suggestion in parsed.suggestions:
            console.print(f"  • {suggestion}")
    else:
        console.print("\n[dim]No suggestions provided[/dim]")


def format_session_complete(
    session: ResearchSession,
    console: Console,
    show_raw: bool = True,
    show_parsed: bool = True,
) -> None:
    """Display a complete session with all available information.

    Args:
        session: The research session to display.
        console: Rich console for output.
        show_raw: Whether to show the raw response.
        show_parsed: Whether to show the parsed response.
    """
    format_session_header(session, console)
    format_session_status(session, console)

    if session.response:
        if show_parsed and session.response.parsed:
            format_parsed_response(session, console)

        if show_raw:
            format_raw_response(session, console)

    format_limitations_disclaimer(console)


# Panel Formatters

def format_panel_header(session: PanelSession, console: Console) -> None:
    """Display the panel research header.

    Args:
        session: The panel session to display.
        console: Rich console for output.
    """
    total = len(session.individual_sessions)
    completed = sum(
        1 for s in session.individual_sessions
        if s.status.value == "completed"
    )
    failed = total - completed

    header_lines = [
        f"[bold]Question:[/bold] {session.question.text}",
        f"[bold]Personas:[/bold] {total} | [green]Completed: {completed}[/green] | [red]Failed: {failed}[/red]",
    ]

    panel = Panel(
        "\n".join(header_lines),
        title=f"Panel Research: {session.panel_name}",
        border_style="blue",
    )
    console.print(panel)


def format_executive_summary(aggregation: AggregatedResults, console: Console) -> None:
    """Display the executive summary.

    Args:
        aggregation: The aggregated results.
        console: Rich console for output.
    """
    panel = Panel(
        aggregation.executive_summary,
        title="Executive Summary",
        border_style="green",
    )
    console.print(panel)


def format_themes(aggregation: AggregatedResults, console: Console) -> None:
    """Display the identified themes.

    Args:
        aggregation: The aggregated results.
        console: Rich console for output.
    """
    if not aggregation.themes:
        console.print("[dim]No themes identified[/dim]")
        return

    theme_lines = []
    for i, theme in enumerate(aggregation.themes, 1):
        sentiment_color = {
            "positive": "green",
            "negative": "red",
            "mixed": "yellow",
            "neutral": "white",
        }.get(theme.sentiment_tendency.value if theme.sentiment_tendency else "neutral", "white")

        theme_lines.append(f"[bold]{i}. {theme.name}[/bold] ({theme.percentage:.0f}%)")
        theme_lines.append(f"   {theme.description}")

        if theme.supporting_quotes:
            for quote in theme.supporting_quotes[:2]:
                theme_lines.append(f'   [dim]"{quote.quote}" - {quote.persona_name}[/dim]')

    panel = Panel(
        "\n".join(theme_lines),
        title=f"Themes ({len(aggregation.themes)})",
        border_style="cyan",
    )
    console.print(panel)


def format_sentiment_distribution(aggregation: AggregatedResults, console: Console) -> None:
    """Display the sentiment distribution.

    Args:
        aggregation: The aggregated results.
        console: Rich console for output.
    """
    dist = aggregation.sentiment_distribution
    sentiment_line = (
        f"[green]Positive: {dist.positive:.0f}%[/green] | "
        f"[red]Negative: {dist.negative:.0f}%[/red] | "
        f"[yellow]Mixed: {dist.mixed:.0f}%[/yellow] | "
        f"Neutral: {dist.neutral:.0f}%"
    )

    panel = Panel(
        sentiment_line,
        title="Sentiment Distribution",
        border_style="yellow",
    )
    console.print(panel)


def format_consensus_points(aggregation: AggregatedResults, console: Console) -> None:
    """Display consensus points.

    Args:
        aggregation: The aggregated results.
        console: Rich console for output.
    """
    if not aggregation.consensus_points:
        console.print(Panel("[dim]No strong consensus points identified[/dim]", title="Consensus Points", border_style="dim"))
        return

    lines = []
    for cp in aggregation.consensus_points:
        lines.append(f"[green]✓[/green] {cp.statement} ({cp.agreement_rate:.0f}% agreement)")

    panel = Panel(
        "\n".join(lines),
        title="Consensus Points",
        border_style="green",
    )
    console.print(panel)


def format_divergence_points(aggregation: AggregatedResults, console: Console) -> None:
    """Display divergence points.

    Args:
        aggregation: The aggregated results.
        console: Rich console for output.
    """
    if not aggregation.divergence_points:
        console.print(Panel("[dim]No significant divergence points identified[/dim]", title="Divergence Points", border_style="dim"))
        return

    lines = []
    for dp in aggregation.divergence_points:
        lines.append(f"[yellow]⚡[/yellow] [bold]{dp.topic}[/bold]")
        for pos in dp.positions:
            persona_names = ", ".join(pos.persona_ids)
            lines.append(f"   - {pos.stance}: {persona_names}")

    panel = Panel(
        "\n".join(lines),
        title="Divergence Points",
        border_style="yellow",
    )
    console.print(panel)


def format_panel_quality_metrics(quality: PanelQualityMetrics, console: Console) -> None:
    """Display panel quality metrics.

    Args:
        quality: The panel quality metrics.
        console: Rich console for output.
    """
    metrics_line = (
        f"Avg Consistency: {quality.avg_consistency_score:.0f}% | "
        f"Completion: {quality.completion_rate:.0f}% | "
        f"Theme Confidence: {quality.theme_confidence:.0f}%"
    )

    if quality.passed_gates:
        status = "[green]✓ All quality gates passed[/green]"
    else:
        status = "[red]✗ Quality gates failed[/red]"

    lines = [metrics_line, status]

    if quality.warnings:
        lines.append("")
        for warning in quality.warnings:
            lines.append(f"[yellow]⚠ {warning}[/yellow]")

    panel = Panel(
        "\n".join(lines),
        title="Quality Metrics",
        border_style="blue" if quality.passed_gates else "red",
    )
    console.print(panel)


def format_individual_responses_summary(session: PanelSession, console: Console) -> None:
    """Display a summary of individual persona responses.

    Args:
        session: The panel session.
        console: Rich console for output.
    """
    lines = []
    sentiment_symbols = {
        "positive": "[green]POSITIVE[/green]",
        "negative": "[red]NEGATIVE[/red]",
        "mixed": "[yellow]MIXED[/yellow]",
        "neutral": "NEUTRAL",
    }

    for s in session.individual_sessions:
        status_symbol = "✓" if s.status.value == "completed" else "✗"
        status_color = "green" if s.status.value == "completed" else "red"

        if s.response and s.response.parsed:
            sentiment = sentiment_symbols.get(s.response.parsed.sentiment.value, "N/A")
            consistency = f"{s.response.quality.consistency_score:.0f}%" if s.response.quality else "N/A"
            lines.append(
                f"[{status_color}]{status_symbol}[/{status_color}] {s.persona_name} ({s.persona_id}) - "
                f"{sentiment} - {consistency} consistency"
            )
        else:
            lines.append(
                f"[{status_color}]{status_symbol}[/{status_color}] {s.persona_name} ({s.persona_id}) - "
                f"[red]No response[/red]"
            )

    panel = Panel(
        "\n".join(lines),
        title="Individual Responses",
        border_style="dim",
    )
    console.print(panel)


def format_panel_session_complete(
    session: PanelSession,
    console: Console,
    show_individual: bool = True,
) -> None:
    """Display a complete panel session with all available information.

    Args:
        session: The panel session to display.
        console: Rich console for output.
        show_individual: Whether to show individual response summaries.
    """
    format_panel_header(session, console)

    if session.aggregation:
        console.print()
        format_executive_summary(session.aggregation, console)
        console.print()
        format_themes(session.aggregation, console)
        console.print()
        format_sentiment_distribution(session.aggregation, console)
        console.print()
        format_consensus_points(session.aggregation, console)
        console.print()
        format_divergence_points(session.aggregation, console)

    if session.quality:
        console.print()
        format_panel_quality_metrics(session.quality, console)

    if show_individual and session.individual_sessions:
        console.print()
        format_individual_responses_summary(session, console)

    format_limitations_disclaimer(console)


def create_panel_progress() -> Progress:
    """Create a Rich Progress instance for panel execution.

    Returns:
        Configured Progress instance.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=Console(),
    )


def format_panel_list(panels: list, console: Console, panel_type: str = "all") -> None:
    """Display a list of available panels.

    Args:
        panels: List of ResearchPanel objects.
        console: Rich console for output.
        panel_type: Type filter that was applied.
    """
    prebuilt = [p for p in panels if not p.is_custom]
    custom = [p for p in panels if p.is_custom]

    if prebuilt:
        lines = []
        for p in prebuilt:
            lines.append(f"  [bold]{p.id}[/bold] ({len(p.persona_ids)} personas)")
            lines.append(f"    {p.description}")
            lines.append("")

        panel = Panel(
            "\n".join(lines).rstrip(),
            title="Pre-Built Panels",
            border_style="blue",
        )
        console.print(panel)

    if custom:
        console.print()
        lines = []
        for p in custom:
            created = p.created_at.strftime("%Y-%m-%d") if p.created_at else "Unknown"
            lines.append(f"  [bold]{p.id}[/bold] ({len(p.persona_ids)} personas)")
            lines.append(f"    Created: {created}")
            lines.append("")

        panel = Panel(
            "\n".join(lines).rstrip(),
            title="Custom Panels",
            border_style="green",
        )
        console.print(panel)

    if not prebuilt and not custom:
        console.print("[dim]No panels found[/dim]")


def format_panel_details(panel, console: Console) -> None:
    """Display detailed information about a panel.

    Args:
        panel: ResearchPanel object.
        console: Rich console for output.
    """
    panel_type = "Custom" if panel.is_custom else "Pre-built"

    lines = [
        f"[bold]Name:[/bold] {panel.name}",
        f"[bold]Type:[/bold] {panel_type}",
    ]

    if panel.purpose:
        lines.append(f"[bold]Purpose:[/bold] {panel.purpose}")

    lines.append(f"\n[bold]Personas ({len(panel.persona_ids)}):[/bold]")

    # Create a simple table for personas
    table = Table(show_header=True, box=None)
    table.add_column("ID", style="cyan")
    table.add_column("Details")

    for persona_id in panel.persona_ids:
        table.add_row(persona_id, "[dim]Persona details would appear here[/dim]")

    output = Panel(
        "\n".join(lines),
        title=f"Panel: {panel.id}",
        border_style="blue",
    )
    console.print(output)
    console.print(table)
