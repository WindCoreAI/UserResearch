"""Service for executing panel research sessions with parallel persona queries."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from models.panel import PanelSession, PanelSessionStatus, ResearchPanel
from models.question import ResearchQuestion
from models.session import ResearchSession, SessionStatus


class PanelExecutorError(Exception):
    """Error raised when panel execution fails."""

    def __init__(self, message: str, panel_id: Optional[str] = None):
        self.panel_id = panel_id
        super().__init__(message)


ProgressCallback = Callable[[int, int, str], None]


class PanelExecutor:
    """Service for executing panel research sessions with parallel persona queries.

    Uses asyncio for concurrent execution of persona sessions to achieve
    speedup over sequential execution.
    """

    def __init__(
        self,
        timeout_seconds: int = 120,
        max_concurrent: int = 10,
    ):
        """Initialize the panel executor.

        Args:
            timeout_seconds: Per-persona timeout in seconds.
            max_concurrent: Maximum concurrent persona sessions.
        """
        self.timeout_seconds = timeout_seconds
        self.max_concurrent = max_concurrent

    async def execute_panel(
        self,
        panel: ResearchPanel,
        question: ResearchQuestion,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> PanelSession:
        """Execute a panel research session with all personas in parallel.

        Args:
            panel: The panel definition with persona IDs.
            question: The research question to ask all personas.
            progress_callback: Optional callback(completed, total, persona_id).

        Returns:
            PanelSession with all individual sessions and status.
        """
        session_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        total_personas = len(panel.persona_ids)
        completed_count = 0
        failed_count = 0
        individual_sessions: list[ResearchSession] = []

        # Create semaphore for limiting concurrent executions
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def run_with_semaphore(persona_id: str) -> tuple[str, Optional[ResearchSession], Optional[Exception]]:
            nonlocal completed_count
            async with semaphore:
                try:
                    session = await asyncio.wait_for(
                        self._run_single_session(persona_id, question.text),
                        timeout=self.timeout_seconds,
                    )
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_personas, persona_id)
                    return (persona_id, session, None)
                except asyncio.TimeoutError:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_personas, persona_id)
                    return (persona_id, None, TimeoutError(f"Timeout for persona {persona_id}"))
                except Exception as e:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_personas, persona_id)
                    return (persona_id, None, e)

        # Execute all personas in parallel
        tasks = [run_with_semaphore(pid) for pid in panel.persona_ids]
        results = await asyncio.gather(*tasks)

        # Process results
        for persona_id, session, error in results:
            if session is not None:
                individual_sessions.append(session)
            else:
                failed_count += 1
                # Create a failed session placeholder
                failed_session = self._create_failed_session(
                    persona_id, question, str(error) if error else "Unknown error"
                )
                individual_sessions.append(failed_session)

        # Determine overall status
        if failed_count == total_personas:
            status = PanelSessionStatus.FAILED
        elif failed_count > 0:
            status = PanelSessionStatus.PARTIAL
        else:
            status = PanelSessionStatus.AGGREGATING

        completed_at = datetime.now(timezone.utc)
        execution_time_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Create panel session
        panel_session = PanelSession(
            id=session_id,
            panel_id=panel.id,
            panel_name=panel.name,
            question=question,
            individual_sessions=individual_sessions,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            execution_time_ms=execution_time_ms,
            metadata={
                "platform_version": "0.3.0",
                "parallel_execution": True,
                "persona_count": total_personas,
                "success_count": total_personas - failed_count,
                "failure_count": failed_count,
            },
        )

        return panel_session

    async def _run_single_session(
        self,
        persona_id: str,
        question_text: str,
    ) -> ResearchSession:
        """Run a single persona research session.

        This method should be overridden or mocked in tests.
        In production, it would use the SessionRunner service.

        Args:
            persona_id: The persona ID to query.
            question_text: The question to ask.

        Returns:
            ResearchSession with the persona's response.
        """
        # Import here to avoid circular imports
        from services.session_runner import SessionRunner

        runner = SessionRunner()
        return await runner.run_async(persona_id, question_text)

    def _create_failed_session(
        self,
        persona_id: str,
        question: ResearchQuestion,
        error_message: str,
    ) -> ResearchSession:
        """Create a placeholder session for a failed persona.

        Args:
            persona_id: The persona that failed.
            question: The question that was asked.
            error_message: The error that occurred.

        Returns:
            ResearchSession with FAILED status.
        """
        return ResearchSession(
            id=str(uuid.uuid4()),
            persona_id=persona_id,
            persona_name=f"[Failed: {persona_id}]",
            question=question,
            response=None,
            status=SessionStatus.FAILED,
            started_at=datetime.now(timezone.utc),
            metadata={"error": error_message},
        )

    def calculate_speedup_factor(
        self,
        execution_time_ms: int,
        persona_count: int,
        avg_response_time_ms: int = 15000,
    ) -> float:
        """Calculate the speedup factor compared to sequential execution.

        Args:
            execution_time_ms: Actual parallel execution time.
            persona_count: Number of personas in the panel.
            avg_response_time_ms: Estimated average time per persona.

        Returns:
            Speedup factor (sequential_time / parallel_time).
        """
        if execution_time_ms <= 0:
            return 1.0

        estimated_sequential = persona_count * avg_response_time_ms
        return estimated_sequential / execution_time_ms


async def export_session_to_json(
    session: PanelSession,
    output_path: str,
    include_metadata: bool = True,
) -> None:
    """Export a panel session to JSON file.

    Args:
        session: The panel session to export.
        output_path: Path to write the JSON file.
        include_metadata: Whether to include execution metadata.
    """
    import json

    data = session.to_dict()

    if include_metadata and session.metadata:
        data["metadata"]["limitations"] = (
            "This is synthetic research data. Validate critical findings with real users."
        )

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
