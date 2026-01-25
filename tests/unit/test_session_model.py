"""Tests for session models.

Validates SessionStatus, Sentiment enums and session-related models.
"""

import pytest

from models.session import Sentiment, SessionStatus


class TestSessionStatus:
    """Tests for SessionStatus enum."""

    def test_pending_value(self):
        """SessionStatus has PENDING value."""
        assert SessionStatus.PENDING == "pending"
        assert SessionStatus.PENDING.value == "pending"

    def test_running_value(self):
        """SessionStatus has RUNNING value."""
        assert SessionStatus.RUNNING == "running"
        assert SessionStatus.RUNNING.value == "running"

    def test_completed_value(self):
        """SessionStatus has COMPLETED value."""
        assert SessionStatus.COMPLETED == "completed"
        assert SessionStatus.COMPLETED.value == "completed"

    def test_failed_value(self):
        """SessionStatus has FAILED value."""
        assert SessionStatus.FAILED == "failed"
        assert SessionStatus.FAILED.value == "failed"

    def test_timeout_value(self):
        """SessionStatus has TIMEOUT value."""
        assert SessionStatus.TIMEOUT == "timeout"
        assert SessionStatus.TIMEOUT.value == "timeout"

    def test_all_statuses_defined(self):
        """All five session statuses are defined."""
        statuses = [s.value for s in SessionStatus]
        assert len(statuses) == 5
        assert "pending" in statuses
        assert "running" in statuses
        assert "completed" in statuses
        assert "failed" in statuses
        assert "timeout" in statuses


class TestSentiment:
    """Tests for Sentiment enum."""

    def test_positive_value(self):
        """Sentiment has POSITIVE value."""
        assert Sentiment.POSITIVE == "positive"
        assert Sentiment.POSITIVE.value == "positive"

    def test_negative_value(self):
        """Sentiment has NEGATIVE value."""
        assert Sentiment.NEGATIVE == "negative"
        assert Sentiment.NEGATIVE.value == "negative"

    def test_mixed_value(self):
        """Sentiment has MIXED value."""
        assert Sentiment.MIXED == "mixed"
        assert Sentiment.MIXED.value == "mixed"

    def test_neutral_value(self):
        """Sentiment has NEUTRAL value."""
        assert Sentiment.NEUTRAL == "neutral"
        assert Sentiment.NEUTRAL.value == "neutral"

    def test_all_sentiments_defined(self):
        """All four sentiment values are defined."""
        sentiments = [s.value for s in Sentiment]
        assert len(sentiments) == 4
        assert "positive" in sentiments
        assert "negative" in sentiments
        assert "mixed" in sentiments
        assert "neutral" in sentiments
