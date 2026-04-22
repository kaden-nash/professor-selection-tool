import threading
from unittest.mock import MagicMock, patch

from src.knightrate.rmp_scraping.scraper.monitor import Monitor


class TestMonitor:
    """Unit tests for Monitor progress bar management."""

    def test_init_professors_creates_pbar(self):
        monitor = Monitor()
        with patch("knightrate.rmp_scraping.scraper.monitor.tqdm") as mock_tqdm:
            monitor.init_professors(100)
            mock_tqdm.assert_called_once_with(total=100, desc="Professors fetched", position=0)
        assert monitor._prof_pbar is not None

    def test_update_professors_increments_pbar(self):
        monitor = Monitor()
        mock_pbar = MagicMock()
        monitor._prof_pbar = mock_pbar
        monitor.update_professors(5)
        mock_pbar.update.assert_called_once_with(5)

    def test_update_professors_no_op_when_not_initialised(self):
        monitor = Monitor()
        monitor.update_professors(3)  # should not raise

    def test_init_reviews_creates_pbar(self):
        monitor = Monitor()
        with patch("knightrate.rmp_scraping.scraper.monitor.tqdm") as mock_tqdm:
            monitor.init_reviews(50)
            mock_tqdm.assert_called_once_with(
                total=50, desc="Professors whose reviews are all fetched", position=1
            )
        assert monitor._review_pbar is not None

    def test_update_reviews_increments_pbar(self):
        monitor = Monitor()
        mock_pbar = MagicMock()
        monitor._review_pbar = mock_pbar
        monitor.update_reviews(2)
        mock_pbar.update.assert_called_once_with(2)

    def test_update_reviews_no_op_when_not_initialised(self):
        monitor = Monitor()
        monitor.update_reviews(1)  # should not raise

    def test_close_shuts_both_pbars(self):
        monitor = Monitor()
        prof_bar = MagicMock()
        review_bar = MagicMock()
        monitor._prof_pbar = prof_bar
        monitor._review_pbar = review_bar
        monitor.close()
        prof_bar.close.assert_called_once()
        review_bar.close.assert_called_once()

    def test_close_is_no_op_when_not_initialised(self):
        monitor = Monitor()
        monitor.close()  # should not raise

    def test_close_suppresses_exception_from_pbar(self):
        monitor = Monitor()
        bad_bar = MagicMock()
        bad_bar.close.side_effect = RuntimeError("tqdm crash")
        monitor._prof_pbar = bad_bar
        monitor.close()  # should not propagate the exception

    def test_operations_are_thread_safe(self):
        monitor = Monitor()
        with patch("knightrate.rmp_scraping.scraper.monitor.tqdm"):
            monitor.init_professors(10)

        errors = []

        def updater():
            try:
                for _ in range(20):
                    monitor.update_professors(1)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=updater) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
