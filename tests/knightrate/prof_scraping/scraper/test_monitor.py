import pytest
from knightrate.prof_scraping.scraper.monitor import Monitor


class TestMonitorInit:
    """Tests for Monitor.init()."""

    def test_init_creates_pbar(self):
        monitor = Monitor()
        monitor.init(10)
        assert monitor._pbar is not None
        monitor.close()

    def test_init_with_zero_total(self):
        monitor = Monitor()
        monitor.init(0)
        assert monitor._pbar is not None
        monitor.close()


class TestMonitorUpdate:
    """Tests for Monitor.update()."""

    def test_update_before_init_does_not_raise(self):
        """Calling update() before init() should silently no-op."""
        monitor = Monitor()
        monitor.update(5)  # Should not raise

    def test_update_advances_progress(self):
        monitor = Monitor()
        monitor.init(10)
        monitor.update(3)
        assert monitor._pbar.n == 3
        monitor.close()

    def test_update_default_step_is_one(self):
        monitor = Monitor()
        monitor.init(10)
        monitor.update()
        assert monitor._pbar.n == 1
        monitor.close()


class TestMonitorClose:
    """Tests for Monitor.close()."""

    def test_close_before_init_does_not_raise(self):
        monitor = Monitor()
        monitor.close()  # Should not raise

    def test_close_after_init_does_not_raise(self):
        monitor = Monitor()
        monitor.init(5)
        monitor.close()  # Should not raise

    def test_double_close_does_not_raise(self):
        monitor = Monitor()
        monitor.init(5)
        monitor.close()
        monitor.close()  # Should not raise

    def test_close_swallows_pbar_exception(self):
        """Verify close() silently ignores errors raised by the underlying pbar."""
        from unittest.mock import MagicMock
        monitor = Monitor()
        mock_pbar = MagicMock()
        mock_pbar.close.side_effect = RuntimeError("pbar exploded")
        monitor._pbar = mock_pbar
        monitor.close()  # Should not propagate the RuntimeError

