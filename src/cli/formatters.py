"""Rich output formatters for CLI display.

Formats research session results for terminal output using Rich.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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
