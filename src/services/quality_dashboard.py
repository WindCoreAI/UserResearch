"""QualityDashboard service for Phase 4 quality calibration (US6).

Aggregates session quality data into dashboard metrics, calculates trends
over time, determines overall quality status, and checks metrics against
configurable thresholds.
"""

from collections import defaultdict
from datetime import date, datetime
from statistics import mean as stats_mean

from models.calibration import QualityThresholds
from models.enums import QualityStatus
from models.quality import (
    QualityDashboardMetrics,
    SessionSummary,
    TrendDataPoint,
)


class QualityDashboard:
    """Builds aggregate quality dashboards from session summaries.

    Provides methods to aggregate session data, calculate trends,
    determine overall quality status, and compare metrics against
    configurable thresholds.
    """

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        """Initialise with optional quality thresholds.

        Args:
            thresholds: Quality threshold configuration. Uses defaults
                if not provided.
        """
        self.thresholds = thresholds or QualityThresholds()

    # ------------------------------------------------------------------
    # T105: aggregate_sessions
    # ------------------------------------------------------------------

    def aggregate_sessions(self, sessions: list[SessionSummary]) -> dict:
        """Aggregate multiple session summaries into dashboard statistics.

        Counts sessions by status, calculates average consistency and
        sycophancy scores, average variance (where available), and
        maximum drift score (where available).

        Args:
            sessions: List of session summaries to aggregate.

        Returns:
            Dictionary containing:
                - sessions_analyzed: total count
                - sessions_healthy / sessions_warning / sessions_critical
                - avg_consistency_score
                - avg_sycophancy_rate
                - avg_variance_score (from sessions that have variance)
                - max_drift_score (from sessions that have drift)
        """
        if not sessions:
            return {
                "sessions_analyzed": 0,
                "sessions_healthy": 0,
                "sessions_warning": 0,
                "sessions_critical": 0,
                "avg_consistency_score": 0.0,
                "avg_sycophancy_rate": 0.0,
                "avg_variance_score": 0.0,
                "max_drift_score": 0.0,
            }

        healthy = sum(
            1 for s in sessions if s.quality_status == QualityStatus.HEALTHY
        )
        warning = sum(
            1 for s in sessions if s.quality_status == QualityStatus.WARNING
        )
        critical = sum(
            1 for s in sessions if s.quality_status == QualityStatus.CRITICAL
        )

        avg_consistency = stats_mean(s.consistency_score for s in sessions)
        avg_sycophancy = stats_mean(s.sycophancy_rate for s in sessions)

        variance_values = [
            s.variance_score for s in sessions if s.variance_score is not None
        ]
        avg_variance = stats_mean(variance_values) if variance_values else 0.0

        drift_values = [
            s.drift_score for s in sessions if s.drift_score is not None
        ]
        max_drift = max(drift_values) if drift_values else 0.0

        return {
            "sessions_analyzed": len(sessions),
            "sessions_healthy": healthy,
            "sessions_warning": warning,
            "sessions_critical": critical,
            "avg_consistency_score": avg_consistency,
            "avg_sycophancy_rate": avg_sycophancy,
            "avg_variance_score": avg_variance,
            "max_drift_score": max_drift,
        }

    # ------------------------------------------------------------------
    # T106: calculate_trends
    # ------------------------------------------------------------------

    def calculate_trends(
        self,
        sessions: list[SessionSummary],
        metric: str = "consistency",
    ) -> list[TrendDataPoint]:
        """Calculate trend data points grouped by date for a given metric.

        Groups sessions by the date portion of their timestamp, then
        computes the average metric value and session count per date.

        Args:
            sessions: List of session summaries.
            metric: Which metric to trend. Supported values are
                ``"consistency"`` (default) and ``"sycophancy"``.

        Returns:
            List of :class:`TrendDataPoint` sorted ascending by date.
        """
        if not sessions:
            return []

        grouped: dict[date, list[float]] = defaultdict(list)
        for session in sessions:
            session_date = session.timestamp.date()
            if metric == "sycophancy":
                grouped[session_date].append(session.sycophancy_rate)
            else:
                grouped[session_date].append(session.consistency_score)

        trend_points: list[TrendDataPoint] = []
        for d in sorted(grouped.keys()):
            values = grouped[d]
            trend_points.append(
                TrendDataPoint(
                    date=d,
                    metric_value=stats_mean(values),
                    session_count=len(values),
                )
            )

        return trend_points

    # ------------------------------------------------------------------
    # T107: determine_overall_status
    # ------------------------------------------------------------------

    def determine_overall_status(
        self, sessions: list[SessionSummary]
    ) -> QualityStatus:
        """Determine the overall quality status across sessions.

        Uses a worst-case escalation model:
        - Any CRITICAL session -> CRITICAL
        - Any WARNING session (no critical) -> WARNING
        - Otherwise -> HEALTHY

        Args:
            sessions: List of session summaries.

        Returns:
            The aggregate :class:`QualityStatus`.
        """
        if not sessions:
            return QualityStatus.HEALTHY

        if any(s.quality_status == QualityStatus.CRITICAL for s in sessions):
            return QualityStatus.CRITICAL

        if any(s.quality_status == QualityStatus.WARNING for s in sessions):
            return QualityStatus.WARNING

        return QualityStatus.HEALTHY

    # ------------------------------------------------------------------
    # T108: check_thresholds
    # ------------------------------------------------------------------

    def check_thresholds(
        self,
        avg_consistency: float,
        avg_sycophancy: float,
        avg_variance: float,
        max_drift: float,
    ) -> tuple[list[str], list[str]]:
        """Compare metrics against configured thresholds.

        Returns two lists indicating which metrics exceed their
        acceptable thresholds (``above_threshold``) and which fall
        below their minimum thresholds (``below_threshold``).

        Args:
            avg_consistency: Average consistency score.
            avg_sycophancy: Average sycophancy rate.
            avg_variance: Average variance score.
            max_drift: Maximum drift score.

        Returns:
            Tuple of (above_threshold, below_threshold) metric name lists.
        """
        above: list[str] = []
        below: list[str] = []

        # Consistency: below minimum is bad
        if avg_consistency < self.thresholds.consistency_minimum:
            below.append("consistency")

        # Sycophancy: above maximum is bad
        if avg_sycophancy > self.thresholds.sycophancy_maximum:
            above.append("sycophancy")

        # Variance: below minimum ratio is bad (insufficient diversity)
        if avg_variance < self.thresholds.variance_minimum_ratio:
            below.append("variance")

        # Drift: above warning is bad
        if max_drift > self.thresholds.drift_warning:
            above.append("drift")

        return above, below

    # ------------------------------------------------------------------
    # T109 / T110: build_dashboard
    # ------------------------------------------------------------------

    def build_dashboard(
        self,
        sessions: list[SessionSummary],
        analysis_start: datetime | None = None,
        analysis_end: datetime | None = None,
    ) -> QualityDashboardMetrics:
        """Build a complete quality dashboard from session summaries.

        Orchestrates aggregation, trend calculation, status determination,
        and threshold checking into a single :class:`QualityDashboardMetrics`.

        Args:
            sessions: List of session summaries.
            analysis_start: Start of the analysis window. Defaults to the
                earliest session timestamp or ``datetime.now()``.
            analysis_end: End of the analysis window. Defaults to the
                latest session timestamp or ``datetime.now()``.

        Returns:
            Fully populated :class:`QualityDashboardMetrics`.
        """
        now = datetime.now()

        if not sessions:
            return QualityDashboardMetrics(
                overall_status=QualityStatus.HEALTHY,
                sessions_analyzed=0,
                sessions_healthy=0,
                sessions_warning=0,
                sessions_critical=0,
                avg_consistency_score=0.0,
                avg_sycophancy_rate=0.0,
                avg_variance_score=0.0,
                max_drift_score=0.0,
                thresholds=self.thresholds,
                metrics_above_threshold=[],
                metrics_below_threshold=[],
                recent_sessions=[],
                consistency_trend=None,
                sycophancy_trend=None,
                analysis_start=analysis_start or now,
                analysis_end=analysis_end or now,
            )

        agg = self.aggregate_sessions(sessions)
        overall_status = self.determine_overall_status(sessions)
        consistency_trend = self.calculate_trends(sessions, "consistency")
        sycophancy_trend = self.calculate_trends(sessions, "sycophancy")
        above, below = self.check_thresholds(
            avg_consistency=agg["avg_consistency_score"],
            avg_sycophancy=agg["avg_sycophancy_rate"],
            avg_variance=agg["avg_variance_score"],
            max_drift=agg["max_drift_score"],
        )

        # Determine analysis window from session timestamps if not provided
        timestamps = [s.timestamp for s in sessions]
        start = analysis_start or min(timestamps)
        end = analysis_end or max(timestamps)

        # Recent sessions: last 10, ordered by timestamp descending
        recent = sorted(sessions, key=lambda s: s.timestamp, reverse=True)[
            :10
        ]

        return QualityDashboardMetrics(
            overall_status=overall_status,
            sessions_analyzed=agg["sessions_analyzed"],
            sessions_healthy=agg["sessions_healthy"],
            sessions_warning=agg["sessions_warning"],
            sessions_critical=agg["sessions_critical"],
            avg_consistency_score=agg["avg_consistency_score"],
            avg_sycophancy_rate=agg["avg_sycophancy_rate"],
            avg_variance_score=agg["avg_variance_score"],
            max_drift_score=agg["max_drift_score"],
            thresholds=self.thresholds,
            metrics_above_threshold=above,
            metrics_below_threshold=below,
            recent_sessions=recent,
            consistency_trend=consistency_trend,
            sycophancy_trend=sycophancy_trend,
            analysis_start=start,
            analysis_end=end,
        )
