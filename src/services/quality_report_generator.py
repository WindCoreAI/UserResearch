from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from models.calibration import CalibrationComparison
from models.quality import ExtendedQualityMetrics


class QualityReportGenerator:
    """Generates Markdown reports from quality analysis results."""

    def __init__(self, templates_dir: Path | None = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_quality_report(self, metrics: ExtendedQualityMetrics) -> str:
        """Generate a quality analysis report."""
        template = self.env.get_template("quality_report.j2")
        return template.render(**metrics.model_dump())

    def generate_calibration_report(self, comparison: CalibrationComparison) -> str:
        """Generate a calibration comparison report."""
        template = self.env.get_template("calibration_report.j2")
        data = comparison.model_dump()
        data["needs_calibration"] = comparison.needs_calibration
        return template.render(**data)

    def save_report(self, content: str, output_path: Path) -> Path:
        """Save report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        return output_path
