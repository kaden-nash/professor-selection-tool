import os
import signal

import pytest
from unittest.mock import Mock, patch

from knightrate.rmp_scraping.rmp_scrape_runner import RmpScrapeRunner

_MODULE = "knightrate.rmp_scraping.rmp_scrape_runner"


@pytest.fixture
def mock_components():
    """Patches all injected components so no real I/O occurs."""
    with (
        patch(f"{_MODULE}.GraphQLClient") as mc,
        patch(f"{_MODULE}.RateLimiter") as mr,
        patch(f"{_MODULE}.DataStorage") as ms,
        patch(f"{_MODULE}.Monitor") as mm,
        patch(f"{_MODULE}.ScraperConfig") as mcfg,
        patch(f"{_MODULE}.ScraperEngine") as me,
    ):
        yield {
            "client": mc,
            "limiter": mr,
            "storage": ms,
            "monitor": mm,
            "config": mcfg,
            "engine": me,
        }


@pytest.fixture
def mock_dotenv():
    with patch(f"{_MODULE}.load_dotenv") as mock_ld:
        yield mock_ld


class TestRmpScrapeRunnerInit:
    """Tests for RmpScrapeRunner.__init__."""

    def test_stores_constructor_arguments(self):
        runner = RmpScrapeRunner("/test", limit_professors=10, limit_reviews=5)
        assert runner._output_dir == "/test"
        assert runner._limit_professors == 10
        assert runner._limit_reviews == 5

    def test_defaults_limits_to_none(self):
        runner = RmpScrapeRunner("/test")
        assert runner._limit_professors is None
        assert runner._limit_reviews is None


class TestRmpScrapeRunnerRun:
    """Tests for RmpScrapeRunner.run()."""

    def test_successful_run_invokes_engine(self, mock_components, mock_dotenv, capsys):
        runner = RmpScrapeRunner("/test", 10, 5)
        mock_engine_inst = mock_components["engine"].return_value

        with patch(f"{_MODULE}.signal.signal"):
            runner.run()

        mock_dotenv.assert_called_once()
        mock_engine_inst.run.assert_called_once()

        captured = capsys.readouterr()
        assert "Beginning RMP scraping" in captured.out
        assert "Completed RMP scraping" in captured.out

    def test_exception_re_raised_and_cancel_called(self, mock_components, mock_dotenv):
        runner = RmpScrapeRunner("/test")
        mock_engine_inst = mock_components["engine"].return_value
        mock_engine_inst.run.side_effect = RuntimeError("Crash")

        with patch(f"{_MODULE}.signal.signal"):
            with pytest.raises(RuntimeError, match="Crash"):
                runner.run()

        mock_engine_inst.cancel.assert_called_once()

    def test_error_message_printed_on_exception(self, mock_components, mock_dotenv, capsys):
        runner = RmpScrapeRunner("/test")
        mock_components["engine"].return_value.run.side_effect = Exception("Boom")

        with patch(f"{_MODULE}.signal.signal"):
            with pytest.raises(Exception):
                runner.run()

        captured = capsys.readouterr()
        assert "An error occurred during scraping: Boom" in captured.out

    def test_signal_handler_calls_cancel_and_exits(self, mock_components, mock_dotenv):
        runner = RmpScrapeRunner("/test")
        registered_handler = None

        def capture_signal(sig, handler):
            nonlocal registered_handler
            registered_handler = handler

        with patch(f"{_MODULE}.signal.signal", side_effect=capture_signal):
            runner.run()

        assert registered_handler is not None

        mock_engine_inst = mock_components["engine"].return_value
        with patch(f"{_MODULE}.os._exit") as mock_exit:
            registered_handler(signal.SIGINT, None)

        mock_engine_inst.cancel.assert_called_once()
        mock_exit.assert_called_once_with(1)

    def test_signal_handler_prints_interrupt_message(self, mock_components, mock_dotenv, capsys):
        runner = RmpScrapeRunner("/test")
        registered_handler = None

        def capture_signal(sig, handler):
            nonlocal registered_handler
            registered_handler = handler

        with patch(f"{_MODULE}.signal.signal", side_effect=capture_signal):
            runner.run()

        with patch(f"{_MODULE}.os._exit"):
            registered_handler(signal.SIGINT, None)

        captured = capsys.readouterr()
        assert "Scraping interrupted by user" in captured.out
