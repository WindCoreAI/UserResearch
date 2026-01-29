"""Tests for QualityDashboard service (T097-T099, T103-T108).

Validates session aggregation, trend calculation, overall status
determination, threshold checking, and full dashboard building
including edge cases like zero sessions and mixed statuses.
"""

import pytest
from datetime import datetime, date, timedelta

from services.quality_dashboard import QualityDashboard
from models.quality import SessionSummary, QualityDashboardMetrics
from models.calibration import QualityThresholds
from models.enums import QualityStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(
    session_id: str = "s1",
    status: QualityStatus = QualityStatus.HEALTHY,
    consistency: float = 85.0,
    sycophancy: float = 10.0,
    variance: float | None = None,
    drift: float | None = None,
    timestamp: datetime | None = None,
    warning_count: int = 0,
    session_type: str = "survey",
) -> SessionSummary:
    """Create a SessionSummary with sensible defaults."""
    return SessionSummary(
        session_id=session_id,
        session_type=session_type,
        quality_status=status,
        consistency_score=consistency,
        sycophancy_rate=sycophancy,
        variance_score=variance,
        drift_score=drift,
        timestamp=timestamp or datetime(2025, 6, 15, 12, 0, 0),
        warning_count=warning_count,
    )


# ===========================================================================
# T097: aggregate_sessions with multiple session summaries
# ===========================================================================


class TestAggregateSessions:
    """T097: aggregate_sessions with multiple session summaries."""

    def test_counts_by_status(self):
        """3 healthy, 1 warning, 1 critical are counted correctly."""
        sessions = [
            _make_session("s1", QualityStatus.HEALTHY),
            _make_session("s2", QualityStatus.HEALTHY),
            _make_session("s3", QualityStatus.HEALTHY),
            _make_session("s4", QualityStatus.WARNING),
            _make_session("s5", QualityStatus.CRITICAL),
        ]
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions(sessions)

        assert result["sessions_analyzed"] == 5
        assert result["sessions_healthy"] == 3
        assert result["sessions_warning"] == 1
        assert result["sessions_critical"] == 1

    def test_average_consistency_score(self):
        """Average consistency across sessions is calculated."""
        sessions = [
            _make_session("s1", consistency=80.0),
            _make_session("s2", consistency=90.0),
            _make_session("s3", consistency=70.0),
        ]
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions(sessions)
        assert result["avg_consistency_score"] == pytest.approx(80.0)

    def test_average_sycophancy_rate(self):
        """Average sycophancy rate across sessions is calculated."""
        sessions = [
            _make_session("s1", sycophancy=10.0),
            _make_session("s2", sycophancy=20.0),
            _make_session("s3", sycophancy=30.0),
        ]
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions(sessions)
        assert result["avg_sycophancy_rate"] == pytest.approx(20.0)

    def test_average_variance_only_from_present(self):
        """Variance average only uses sessions that have variance_score."""
        sessions = [
            _make_session("s1", variance=0.8),
            _make_session("s2", variance=0.6),
            _make_session("s3"),  # no variance
        ]
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions(sessions)
        assert result["avg_variance_score"] == pytest.approx(0.7)

    def test_max_drift_from_present(self):
        """Max drift uses only sessions that have drift_score."""
        sessions = [
            _make_session("s1", drift=5.0),
            _make_session("s2", drift=20.0),
            _make_session("s3"),  # no drift
        ]
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions(sessions)
        assert result["max_drift_score"] == pytest.approx(20.0)

    def test_no_variance_sessions_returns_zero(self):
        """When no sessions have variance, avg_variance_score is 0."""
        sessions = [_make_session("s1"), _make_session("s2")]
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions(sessions)
        assert result["avg_variance_score"] == 0.0

    def test_no_drift_sessions_returns_zero(self):
        """When no sessions have drift, max_drift_score is 0."""
        sessions = [_make_session("s1"), _make_session("s2")]
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions(sessions)
        assert result["max_drift_score"] == 0.0


# ===========================================================================
# T098: calculate_trends with session data over multiple dates
# ===========================================================================


class TestCalculateTrends:
    """T098: calculate_trends produces trend data points per date."""

    def test_groups_by_date_with_averages(self):
        """Sessions on the same date are averaged into one data point."""
        sessions = [
            _make_session("s1", consistency=80.0, timestamp=datetime(2025, 6, 1, 10, 0)),
            _make_session("s2", consistency=90.0, timestamp=datetime(2025, 6, 1, 14, 0)),
            _make_session("s3", consistency=70.0, timestamp=datetime(2025, 6, 2, 10, 0)),
        ]
        dashboard = QualityDashboard()
        trend = dashboard.calculate_trends(sessions, "consistency")

        assert len(trend) == 2
        assert trend[0].date == date(2025, 6, 1)
        assert trend[0].metric_value == pytest.approx(85.0)
        assert trend[0].session_count == 2
        assert trend[1].date == date(2025, 6, 2)
        assert trend[1].metric_value == pytest.approx(70.0)
        assert trend[1].session_count == 1

    def test_sorted_by_date(self):
        """Trend data points are sorted ascending by date."""
        sessions = [
            _make_session("s1", timestamp=datetime(2025, 6, 3, 10, 0)),
            _make_session("s2", timestamp=datetime(2025, 6, 1, 10, 0)),
            _make_session("s3", timestamp=datetime(2025, 6, 2, 10, 0)),
        ]
        dashboard = QualityDashboard()
        trend = dashboard.calculate_trends(sessions)
        dates = [tp.date for tp in trend]
        assert dates == sorted(dates)

    def test_sycophancy_metric(self):
        """Trends can be computed for sycophancy metric."""
        sessions = [
            _make_session("s1", sycophancy=15.0, timestamp=datetime(2025, 6, 1, 10, 0)),
            _make_session("s2", sycophancy=25.0, timestamp=datetime(2025, 6, 1, 14, 0)),
        ]
        dashboard = QualityDashboard()
        trend = dashboard.calculate_trends(sessions, "sycophancy")

        assert len(trend) == 1
        assert trend[0].metric_value == pytest.approx(20.0)

    def test_empty_sessions_returns_empty_list(self):
        """Empty session list produces empty trend list."""
        dashboard = QualityDashboard()
        assert dashboard.calculate_trends([]) == []


# ===========================================================================
# T099: determine_overall_status
# ===========================================================================


class TestDetermineOverallStatus:
    """T099: determine_overall_status uses worst-case escalation."""

    def test_all_healthy_returns_healthy(self):
        """All healthy sessions produce HEALTHY status."""
        sessions = [
            _make_session("s1", QualityStatus.HEALTHY),
            _make_session("s2", QualityStatus.HEALTHY),
        ]
        dashboard = QualityDashboard()
        assert dashboard.determine_overall_status(sessions) == QualityStatus.HEALTHY

    def test_any_critical_returns_critical(self):
        """One critical session among healthy and warning produces CRITICAL."""
        sessions = [
            _make_session("s1", QualityStatus.HEALTHY),
            _make_session("s2", QualityStatus.WARNING),
            _make_session("s3", QualityStatus.CRITICAL),
        ]
        dashboard = QualityDashboard()
        assert dashboard.determine_overall_status(sessions) == QualityStatus.CRITICAL

    def test_warning_no_critical_returns_warning(self):
        """Warning sessions without any critical produce WARNING."""
        sessions = [
            _make_session("s1", QualityStatus.HEALTHY),
            _make_session("s2", QualityStatus.WARNING),
        ]
        dashboard = QualityDashboard()
        assert dashboard.determine_overall_status(sessions) == QualityStatus.WARNING

    def test_empty_sessions_returns_healthy(self):
        """Empty session list defaults to HEALTHY."""
        dashboard = QualityDashboard()
        assert dashboard.determine_overall_status([]) == QualityStatus.HEALTHY


# ===========================================================================
# T103: dashboard with zero sessions returns default values
# ===========================================================================


class TestDashboardZeroSessions:
    """T103: Dashboard with zero sessions returns safe defaults."""

    def test_zero_sessions_returns_defaults(self):
        """build_dashboard with empty list returns zeroed metrics."""
        dashboard = QualityDashboard()
        result = dashboard.build_dashboard([])

        assert isinstance(result, QualityDashboardMetrics)
        assert result.overall_status == QualityStatus.HEALTHY
        assert result.sessions_analyzed == 0
        assert result.sessions_healthy == 0
        assert result.sessions_warning == 0
        assert result.sessions_critical == 0
        assert result.avg_consistency_score == 0.0
        assert result.avg_sycophancy_rate == 0.0
        assert result.avg_variance_score == 0.0
        assert result.max_drift_score == 0.0
        assert result.metrics_above_threshold == []
        assert result.metrics_below_threshold == []
        assert result.recent_sessions == []
        assert result.consistency_trend is None
        assert result.sycophancy_trend is None

    def test_zero_sessions_aggregate_returns_defaults(self):
        """aggregate_sessions with empty list returns zeroed dict."""
        dashboard = QualityDashboard()
        result = dashboard.aggregate_sessions([])
        assert result["sessions_analyzed"] == 0
        assert result["avg_consistency_score"] == 0.0


# ===========================================================================
# T104: metrics_above_threshold and metrics_below_threshold
# ===========================================================================


class TestThresholdLists:
    """T104: check_thresholds identifies above/below threshold metrics."""

    def test_consistency_below_threshold(self):
        """Low consistency is reported as below threshold."""
        thresholds = QualityThresholds(consistency_minimum=70.0)
        dashboard = QualityDashboard(thresholds=thresholds)
        above, below = dashboard.check_thresholds(
            avg_consistency=60.0,
            avg_sycophancy=10.0,
            avg_variance=0.8,
            max_drift=5.0,
        )
        assert "consistency" in below
        assert "consistency" not in above

    def test_sycophancy_above_threshold(self):
        """High sycophancy is reported as above threshold."""
        thresholds = QualityThresholds(sycophancy_maximum=30.0)
        dashboard = QualityDashboard(thresholds=thresholds)
        above, below = dashboard.check_thresholds(
            avg_consistency=85.0,
            avg_sycophancy=40.0,
            avg_variance=0.8,
            max_drift=5.0,
        )
        assert "sycophancy" in above

    def test_variance_below_threshold(self):
        """Low variance is reported as below threshold."""
        thresholds = QualityThresholds(variance_minimum_ratio=0.6)
        dashboard = QualityDashboard(thresholds=thresholds)
        above, below = dashboard.check_thresholds(
            avg_consistency=85.0,
            avg_sycophancy=10.0,
            avg_variance=0.3,
            max_drift=5.0,
        )
        assert "variance" in below

    def test_drift_above_threshold(self):
        """High drift is reported as above threshold."""
        thresholds = QualityThresholds(drift_warning=15.0)
        dashboard = QualityDashboard(thresholds=thresholds)
        above, below = dashboard.check_thresholds(
            avg_consistency=85.0,
            avg_sycophancy=10.0,
            avg_variance=0.8,
            max_drift=20.0,
        )
        assert "drift" in above

    def test_all_metrics_healthy(self):
        """When all metrics are within thresholds, both lists are empty."""
        dashboard = QualityDashboard()
        above, below = dashboard.check_thresholds(
            avg_consistency=85.0,
            avg_sycophancy=10.0,
            avg_variance=0.8,
            max_drift=5.0,
        )
        assert above == []
        assert below == []

    def test_multiple_metrics_flagged(self):
        """Multiple metrics can be flagged simultaneously."""
        thresholds = QualityThresholds(
            consistency_minimum=70.0,
            sycophancy_maximum=30.0,
            drift_warning=15.0,
        )
        dashboard = QualityDashboard(thresholds=thresholds)
        above, below = dashboard.check_thresholds(
            avg_consistency=50.0,
            avg_sycophancy=40.0,
            avg_variance=0.8,
            max_drift=20.0,
        )
        assert "consistency" in below
        assert "sycophancy" in above
        assert "drift" in above


# ===========================================================================
# T105-T110: build_dashboard integration
# ===========================================================================


class TestBuildDashboard:
    """T105-T110: build_dashboard orchestrates all methods."""

    def test_build_with_mixed_sessions(self):
        """Dashboard correctly aggregates mixed-status sessions."""
        sessions = [
            _make_session("s1", QualityStatus.HEALTHY, consistency=90.0, sycophancy=5.0,
                          timestamp=datetime(2025, 6, 1, 10, 0)),
            _make_session("s2", QualityStatus.HEALTHY, consistency=85.0, sycophancy=8.0,
                          timestamp=datetime(2025, 6, 1, 14, 0)),
            _make_session("s3", QualityStatus.HEALTHY, consistency=80.0, sycophancy=12.0,
                          timestamp=datetime(2025, 6, 2, 10, 0)),
            _make_session("s4", QualityStatus.WARNING, consistency=72.0, sycophancy=22.0,
                          variance=0.5, timestamp=datetime(2025, 6, 2, 14, 0)),
            _make_session("s5", QualityStatus.CRITICAL, consistency=55.0, sycophancy=45.0,
                          drift=30.0, timestamp=datetime(2025, 6, 3, 10, 0)),
        ]
        dashboard = QualityDashboard()
        result = dashboard.build_dashboard(sessions)

        assert result.sessions_analyzed == 5
        assert result.sessions_healthy == 3
        assert result.sessions_warning == 1
        assert result.sessions_critical == 1
        assert result.overall_status == QualityStatus.CRITICAL

    def test_build_includes_trends(self):
        """Dashboard includes consistency and sycophancy trends."""
        sessions = [
            _make_session("s1", timestamp=datetime(2025, 6, 1, 10, 0)),
            _make_session("s2", timestamp=datetime(2025, 6, 2, 10, 0)),
        ]
        dashboard = QualityDashboard()
        result = dashboard.build_dashboard(sessions)

        assert result.consistency_trend is not None
        assert len(result.consistency_trend) == 2
        assert result.sycophancy_trend is not None
        assert len(result.sycophancy_trend) == 2

    def test_build_uses_custom_thresholds(self):
        """Dashboard uses provided thresholds for checking."""
        thresholds = QualityThresholds(consistency_minimum=95.0)
        sessions = [
            _make_session("s1", consistency=85.0,
                          timestamp=datetime(2025, 6, 1, 10, 0)),
        ]
        dashboard = QualityDashboard(thresholds=thresholds)
        result = dashboard.build_dashboard(sessions)

        assert "consistency" in result.metrics_below_threshold

    def test_build_analysis_window_from_sessions(self):
        """Analysis window defaults to session timestamp range."""
        sessions = [
            _make_session("s1", timestamp=datetime(2025, 6, 1, 10, 0)),
            _make_session("s2", timestamp=datetime(2025, 6, 5, 14, 0)),
        ]
        dashboard = QualityDashboard()
        result = dashboard.build_dashboard(sessions)

        assert result.analysis_start == datetime(2025, 6, 1, 10, 0)
        assert result.analysis_end == datetime(2025, 6, 5, 14, 0)

    def test_build_explicit_analysis_window(self):
        """Explicit start/end override session-derived window."""
        sessions = [
            _make_session("s1", timestamp=datetime(2025, 6, 3, 10, 0)),
        ]
        start = datetime(2025, 6, 1)
        end = datetime(2025, 6, 30)
        dashboard = QualityDashboard()
        result = dashboard.build_dashboard(sessions, analysis_start=start, analysis_end=end)

        assert result.analysis_start == start
        assert result.analysis_end == end

    def test_build_recent_sessions_ordered(self):
        """Recent sessions are ordered most recent first."""
        sessions = [
            _make_session("s1", timestamp=datetime(2025, 6, 1, 10, 0)),
            _make_session("s2", timestamp=datetime(2025, 6, 3, 10, 0)),
            _make_session("s3", timestamp=datetime(2025, 6, 2, 10, 0)),
        ]
        dashboard = QualityDashboard()
        result = dashboard.build_dashboard(sessions)

        assert result.recent_sessions[0].session_id == "s2"
        assert result.recent_sessions[1].session_id == "s3"
        assert result.recent_sessions[2].session_id == "s1"

    def test_build_recent_sessions_max_ten(self):
        """Recent sessions list is capped at 10 entries."""
        sessions = [
            _make_session(f"s{i}", timestamp=datetime(2025, 6, 1 + i, 10, 0))
            for i in range(15)
        ]
        dashboard = QualityDashboard()
        result = dashboard.build_dashboard(sessions)

        assert len(result.recent_sessions) == 10

    def test_build_thresholds_in_result(self):
        """Dashboard result includes the thresholds used."""
        thresholds = QualityThresholds(consistency_minimum=75.0)
        dashboard = QualityDashboard(thresholds=thresholds)
        result = dashboard.build_dashboard([])
        assert result.thresholds.consistency_minimum == 75.0
