"""Unit tests for PanelExecutor service."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch


def create_mock_session(persona_id: str, question_text: str):
    """Helper to create a mock ResearchSession object."""
    from models.session import (
        ParsedResponse,
        ResearchSession,
        SessionResponse,
        SessionStatus,
        Sentiment,
    )
    from models.question import QuestionType, ResearchQuestion

    question = ResearchQuestion(
        text=question_text,
        type=QuestionType.OPEN_ENDED,
    )

    parsed = ParsedResponse(
        sentiment=Sentiment.POSITIVE,
        overall_impression="Test impression",
        concerns=["Test concern"],
        suggestions=["Test suggestion"],
    )

    response = SessionResponse(
        raw_text="Test response",
        response_time_ms=1000,
        parsed=parsed,
    )

    return ResearchSession(
        id=f"session-{persona_id}",
        persona_id=persona_id,
        persona_name=f"Test Persona {persona_id}",
        question=question,
        response=response,
        status=SessionStatus.COMPLETED,
        started_at=datetime.now(timezone.utc),
    )


class TestPanelExecutor:
    """Tests for PanelExecutor service."""

    def test_executor_initialization(self):
        """Test PanelExecutor can be initialized."""
        from services.panel_executor import PanelExecutor

        executor = PanelExecutor()
        assert executor is not None

    def test_executor_with_custom_timeout(self):
        """Test PanelExecutor with custom timeout."""
        from services.panel_executor import PanelExecutor

        executor = PanelExecutor(timeout_seconds=60)
        assert executor.timeout_seconds == 60

    @pytest.mark.asyncio
    async def test_execute_panel_returns_panel_session(self):
        """Test that execute_panel returns a PanelSession."""
        from services.panel_executor import PanelExecutor
        from models.panel import PanelSession, PanelSessionStatus, ResearchPanel
        from models.question import QuestionType, ResearchQuestion

        panel = ResearchPanel(
            id="test-panel",
            name="Test Panel",
            description="Test",
            persona_ids=["p1", "p2"],
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )

        question = ResearchQuestion(
            text="Test question?",
            type=QuestionType.OPEN_ENDED,
        )

        executor = PanelExecutor()

        async def mock_run(persona_id, question_text):
            return create_mock_session(persona_id, question_text)

        with patch.object(executor, '_run_single_session', side_effect=mock_run):
            result = await executor.execute_panel(panel, question)

            assert isinstance(result, PanelSession)
            assert result.panel_id == "test-panel"
            assert len(result.individual_sessions) == 2

    @pytest.mark.asyncio
    async def test_execute_panel_handles_partial_failure(self):
        """Test that partial failures are handled gracefully."""
        from services.panel_executor import PanelExecutor
        from models.panel import PanelSession, PanelSessionStatus, ResearchPanel
        from models.question import QuestionType, ResearchQuestion

        panel = ResearchPanel(
            id="test-panel",
            name="Test Panel",
            description="Test",
            persona_ids=["p1", "p2", "p3"],
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )

        question = ResearchQuestion(
            text="Test question?",
            type=QuestionType.OPEN_ENDED,
        )

        executor = PanelExecutor()

        async def mock_run_session(persona_id, question_text):
            if persona_id == "p2":
                raise Exception("Simulated failure")
            return create_mock_session(persona_id, question_text)

        with patch.object(executor, '_run_single_session', side_effect=mock_run_session):
            result = await executor.execute_panel(panel, question)

            assert isinstance(result, PanelSession)
            # Status should be PARTIAL due to failure
            assert result.status == PanelSessionStatus.PARTIAL
            assert len(result.individual_sessions) == 3  # Includes failed session

    @pytest.mark.asyncio
    async def test_execute_panel_with_progress_callback(self):
        """Test progress callback is called during execution."""
        from services.panel_executor import PanelExecutor
        from models.panel import ResearchPanel
        from models.question import QuestionType, ResearchQuestion

        panel = ResearchPanel(
            id="test-panel",
            name="Test Panel",
            description="Test",
            persona_ids=["p1", "p2"],
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )

        question = ResearchQuestion(
            text="Test question?",
            type=QuestionType.OPEN_ENDED,
        )

        executor = PanelExecutor()
        progress_calls = []

        def progress_callback(completed: int, total: int, persona_id: str):
            progress_calls.append((completed, total, persona_id))

        async def mock_run(persona_id, question_text):
            return create_mock_session(persona_id, question_text)

        with patch.object(executor, '_run_single_session', side_effect=mock_run):
            await executor.execute_panel(
                panel, question, progress_callback=progress_callback
            )

            # Should have called progress for each persona
            assert len(progress_calls) == 2

    @pytest.mark.asyncio
    async def test_execute_panel_respects_timeout(self):
        """Test that per-persona timeout is respected."""
        from services.panel_executor import PanelExecutor
        from models.panel import ResearchPanel, PanelSessionStatus
        from models.question import QuestionType, ResearchQuestion
        import asyncio

        panel = ResearchPanel(
            id="test-panel",
            name="Test Panel",
            description="Test",
            persona_ids=["p1", "p2"],  # Need at least 2 personas
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )

        question = ResearchQuestion(
            text="Test question?",
            type=QuestionType.OPEN_ENDED,
        )

        executor = PanelExecutor(timeout_seconds=1)

        async def slow_run(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return create_mock_session("p1", "test")

        with patch.object(executor, '_run_single_session', side_effect=slow_run):
            result = await executor.execute_panel(panel, question)

            # Should complete with timeout handling - all failed
            assert result is not None
            assert result.status == PanelSessionStatus.FAILED


class TestPanelExecutorIntegration:
    """Integration tests for PanelExecutor."""

    @pytest.mark.asyncio
    async def test_execute_with_mock_personas(self, temp_personas_dir):
        """Test execution with mocked persona data."""
        from services.panel_executor import PanelExecutor
        from models.panel import ResearchPanel
        from models.question import QuestionType, ResearchQuestion

        panel = ResearchPanel(
            id="mock-panel",
            name="Mock Panel",
            description="Mock test panel",
            persona_ids=["test-persona", "test-persona-2"],  # Need at least 2
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )

        question = ResearchQuestion(
            text="What do you think?",
            type=QuestionType.OPEN_ENDED,
        )

        executor = PanelExecutor()

        async def mock_run(persona_id, question_text):
            return create_mock_session(persona_id, question_text)

        with patch.object(executor, '_run_single_session', side_effect=mock_run):
            result = await executor.execute_panel(panel, question)

            assert result.panel_id == "mock-panel"
            assert len(result.individual_sessions) == 2


class TestPanelExecutorParallel:
    """Tests for parallel execution in PanelExecutor."""

    @pytest.mark.asyncio
    async def test_parallel_execution_faster_than_sequential(self):
        """Test that parallel execution provides speedup."""
        from services.panel_executor import PanelExecutor
        from models.panel import ResearchPanel
        from models.question import QuestionType, ResearchQuestion
        import asyncio
        import time

        panel = ResearchPanel(
            id="parallel-test",
            name="Parallel Test Panel",
            description="Test",
            persona_ids=["p1", "p2", "p3", "p4", "p5"],
            is_custom=True,
            created_at=datetime.now(timezone.utc),
        )

        question = ResearchQuestion(
            text="Test?",
            type=QuestionType.OPEN_ENDED,
        )

        executor = PanelExecutor()
        delay_per_persona = 0.1  # 100ms per persona

        async def delayed_run(persona_id, question_text):
            await asyncio.sleep(delay_per_persona)
            return create_mock_session(persona_id, question_text)

        with patch.object(executor, '_run_single_session', side_effect=delayed_run):
            start = time.time()
            await executor.execute_panel(panel, question)
            elapsed = time.time() - start

            # If sequential: 5 * 0.1 = 0.5s
            # If parallel: ~0.1s
            # Allow some overhead, should be < 0.3s for parallel
            assert elapsed < 0.3, f"Execution took {elapsed}s, expected parallel execution"

    def test_calculate_speedup_factor(self):
        """Test speedup factor calculation."""
        from services.panel_executor import PanelExecutor

        executor = PanelExecutor()

        # 5 personas, 15s avg each = 75s sequential
        # 25s parallel = 3x speedup
        speedup = executor.calculate_speedup_factor(
            execution_time_ms=25000,
            persona_count=5,
            avg_response_time_ms=15000,
        )

        assert speedup == 3.0

    def test_calculate_speedup_factor_zero_time(self):
        """Test speedup factor with zero execution time."""
        from services.panel_executor import PanelExecutor

        executor = PanelExecutor()

        speedup = executor.calculate_speedup_factor(
            execution_time_ms=0,
            persona_count=5,
        )

        assert speedup == 1.0
