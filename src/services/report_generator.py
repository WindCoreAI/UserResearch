"""Service for generating Markdown research reports from panel sessions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Template

from models.panel import PanelSession, PanelSessionStatus


class ReportGeneratorError(Exception):
    """Error raised when report generation fails."""

    pass


class ReportGenerator:
    """Service for generating Markdown research reports.

    Creates formatted Markdown reports from completed panel sessions,
    including executive summary, methodology, findings, and quality metrics.
    """

    def __init__(self, template_path: Optional[Path] = None):
        """Initialize the report generator.

        Args:
            template_path: Path to report template. Defaults to panel_report.j2.
        """
        if template_path is None:
            template_path = Path(__file__).parent.parent / "templates" / "panel_report.j2"
        self.template_path = template_path

    def generate_report(self, session: PanelSession) -> str:
        """Generate a Markdown report from a panel session.

        Args:
            session: Completed panel session with aggregation and quality metrics.

        Returns:
            Formatted Markdown string.

        Raises:
            ReportGeneratorError: If report generation fails.
        """
        try:
            template = self._load_template()
            context = self._build_context(session)
            return template.render(**context)
        except Exception as e:
            raise ReportGeneratorError(f"Failed to generate report: {e}") from e

    def write_report(self, session: PanelSession, output_path: Path) -> Path:
        """Generate and write a report to a file.

        Args:
            session: Completed panel session.
            output_path: Path to write the report to.

        Returns:
            Path to the written report file.

        Raises:
            ReportGeneratorError: If writing fails.
        """
        try:
            report = self.generate_report(session)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding="utf-8")
            return output_path
        except Exception as e:
            raise ReportGeneratorError(f"Failed to write report to {output_path}: {e}") from e

    def _load_template(self) -> Template:
        """Load the Jinja2 report template.

        Returns:
            Loaded Jinja2 Template.
        """
        with open(self.template_path, encoding="utf-8") as f:
            return Template(f.read())

    def _build_context(self, session: PanelSession) -> dict:
        """Build template context from session data.

        Args:
            session: Panel session to extract data from.

        Returns:
            Dictionary of template context variables.
        """
        # Determine status display
        status_display = session.status.value
        if session.status == PanelSessionStatus.PARTIAL:
            status_display = "partial"

        # Format timestamps
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        started_at = (
            session.started_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            if session.started_at
            else "N/A"
        )
        completed_at = (
            session.completed_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            if session.completed_at
            else "N/A"
        )

        # Extract speedup factor from metadata
        speedup_factor = None
        if session.metadata and "speedup_factor" in session.metadata:
            speedup_factor = session.metadata["speedup_factor"]

        return {
            "panel_name": session.panel_name,
            "panel_id": session.panel_id,
            "question_text": session.question.text,
            "question_type": session.question.type.value.replace("_", " ").title(),
            "status": status_display,
            "persona_count": len(session.individual_sessions),
            "generated_at": generated_at,
            "started_at": started_at,
            "completed_at": completed_at,
            "execution_time_ms": session.execution_time_ms or 0,
            "speedup_factor": speedup_factor,
            "aggregation": session.aggregation,
            "quality": session.quality,
            "individual_sessions": session.individual_sessions,
        }
