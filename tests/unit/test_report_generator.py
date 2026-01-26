"""Unit tests for ReportGenerator service."""

from datetime import datetime
from uuid import uuid4

import pytest

from models.aggregation import (
    AggregatedResults,
    ConsensusPoint,
    DivergencePoint,
    PanelQualityMetrics,
    Position,
    QuoteReference,
    SentimentDistribution,
    Theme,
)
from models.panel import PanelSession, PanelSessionStatus
from models.question import QuestionType, ResearchQuestion
from models.session import (
    ParsedResponse,
    QualityMetrics,
    ResearchSession,
    SessionResponse,
    SessionStatus,
    Sentiment,
)
from services.report_generator import ReportGenerator


def create_mock_session(persona_id: str, persona_name: str) -> ResearchSession:
    """Create a mock research session for testing."""
    return ResearchSession(
        id=str(uuid4()),
        persona_id=persona_id,
        persona_name=persona_name,
        question=ResearchQuestion(text="Test question?", type=QuestionType.OPEN_ENDED),
        status=SessionStatus.COMPLETED,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        response=SessionResponse(
            raw_text="Raw response text",
            response_time_ms=1000,
            parsed=ParsedResponse(
                sentiment=Sentiment.POSITIVE,
                overall_impression="Great product!",
                concerns=["Minor issue"],
                suggestions=["Add more features"],
            ),
            quality=QualityMetrics(
                consistency_score=85.0,
                passed_gates=True,
            ),
        ),
    )


def create_sample_panel_session() -> PanelSession:
    """Create a sample panel session for testing."""
    sessions = [
        create_mock_session("tech-early-adopter", "Tech Early Adopter"),
        create_mock_session("power-user", "Power User"),
        create_mock_session("skeptical-late-adopter", "Skeptical Late Adopter"),
    ]

    aggregation = AggregatedResults(
        themes=[
            Theme(
                name="User Experience",
                description="Focus on ease of use and interface design",
                frequency=3,
                percentage=100.0,
                supporting_quotes=[
                    QuoteReference(
                        persona_id="tech-early-adopter",
                        persona_name="Tech Early Adopter",
                        quote="The interface is intuitive and modern.",
                    )
                ],
                sentiment_tendency=Sentiment.POSITIVE,
            ),
            Theme(
                name="Privacy Concerns",
                description="Data handling and privacy issues",
                frequency=2,
                percentage=66.7,
                supporting_quotes=[],
                sentiment_tendency=Sentiment.NEGATIVE,
            ),
        ],
        sentiment_distribution=SentimentDistribution(
            positive=66.7,
            negative=16.7,
            mixed=16.6,
            neutral=0.0,
            dominant=Sentiment.POSITIVE,
        ),
        consensus_points=[
            ConsensusPoint(
                statement="The product is easy to use",
                agreement_rate=100.0,
                supporting_personas=["tech-early-adopter", "power-user", "skeptical-late-adopter"],
            )
        ],
        divergence_points=[
            DivergencePoint(
                topic="Data Collection",
                positions=[
                    Position(
                        stance="Acceptable",
                        persona_ids=["tech-early-adopter", "power-user"],
                        rationale="Worth the trade-off for features",
                    ),
                    Position(
                        stance="Concerning",
                        persona_ids=["skeptical-late-adopter"],
                        rationale="Too much data being collected",
                    ),
                ],
            )
        ],
        executive_summary="Overall positive reception with some privacy concerns.",
        aggregation_confidence=85.0,
    )

    quality = PanelQualityMetrics(
        avg_consistency_score=85.0,
        completion_rate=100.0,
        theme_confidence=80.0,
        divergence_score=25.0,
        passed_gates=True,
        warnings=[],
        individual_metrics=[s.response.quality for s in sessions],
    )

    return PanelSession(
        id=str(uuid4()),
        panel_id="tech-adopters",
        panel_name="Technology Adopters Panel",
        question=ResearchQuestion(text="What do you think of our new product?", type=QuestionType.OPEN_ENDED),
        individual_sessions=sessions,
        aggregation=aggregation,
        quality=quality,
        status=PanelSessionStatus.COMPLETED,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        execution_time_ms=5000,
        metadata={"speedup_factor": 3},
    )


class TestReportGenerator:
    """Tests for ReportGenerator service."""

    def test_generator_initialization(self):
        """Test ReportGenerator can be initialized."""
        generator = ReportGenerator()
        assert generator is not None

    def test_generate_report_returns_markdown_string(self):
        """Test generate_report returns a Markdown string."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert isinstance(report, str)
        assert len(report) > 0

    def test_report_contains_executive_summary(self):
        """Test report contains executive summary section."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Executive Summary" in report
        assert "Overall positive reception" in report

    def test_report_contains_methodology_section(self):
        """Test report contains methodology section."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Methodology" in report
        assert "Technology Adopters Panel" in report
        assert "What do you think of our new product?" in report

    def test_report_contains_themes_section(self):
        """Test report contains themes section."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Key Themes" in report
        assert "User Experience" in report
        assert "Privacy Concerns" in report

    def test_report_contains_sentiment_section(self):
        """Test report contains sentiment distribution."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Sentiment Analysis" in report
        assert "Positive" in report

    def test_report_contains_consensus_section(self):
        """Test report contains consensus points."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Consensus Points" in report
        assert "easy to use" in report

    def test_report_contains_divergence_section(self):
        """Test report contains divergence points."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Divergence Points" in report
        assert "Data Collection" in report

    def test_report_contains_individual_responses(self):
        """Test report contains individual response summaries."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Individual Responses" in report
        assert "Tech Early Adopter" in report
        assert "Power User" in report

    def test_report_contains_quality_section(self):
        """Test report contains quality assessment."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Quality Assessment" in report
        assert "Consistency Score" in report

    def test_report_contains_synthetic_disclaimer(self):
        """Test report contains synthetic data disclaimer."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "## Important Limitations" in report
        assert "synthetic" in report.lower()

    def test_report_with_warnings(self):
        """Test report includes quality warnings when present."""
        generator = ReportGenerator()
        session = create_sample_panel_session()
        session.quality.warnings = ["Low completion rate", "High divergence"]

        report = generator.generate_report(session)

        assert "Low completion rate" in report
        assert "High divergence" in report

    def test_report_with_empty_aggregation(self):
        """Test report handles session with no aggregation."""
        generator = ReportGenerator()
        session = create_sample_panel_session()
        session.aggregation = None

        report = generator.generate_report(session)

        assert isinstance(report, str)
        assert "## Executive Summary" in report

    def test_report_with_partial_status(self):
        """Test report indicates partial completion."""
        generator = ReportGenerator()
        session = create_sample_panel_session()
        session.status = PanelSessionStatus.PARTIAL

        report = generator.generate_report(session)

        assert "partial" in report.lower() or "incomplete" in report.lower()

    def test_report_title_format(self):
        """Test report has proper title."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        assert "# " in report  # H1 heading
        assert "Research Report" in report

    def test_report_includes_timestamp(self):
        """Test report includes generation timestamp."""
        generator = ReportGenerator()
        session = create_sample_panel_session()

        report = generator.generate_report(session)

        # Should have some date reference
        assert "Generated" in report or "Date" in report
