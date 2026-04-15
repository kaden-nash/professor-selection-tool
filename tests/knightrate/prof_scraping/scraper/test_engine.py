import pytest # type: ignore
from unittest.mock import MagicMock
from knightrate.prof_scraping.scraper.engine import ScraperEngine, ScraperDependencies


FAKE_HTML = '<div class="style__contentBody___gEuR0"><p><strong>A, B</strong>, Prof</p></div>'
FAKE_ENTRIES = ["A, B, Prof"]


def _make_deps(client=None, parser=None, storage=None, monitor=None):
    """Build a ScraperDependencies from mocks, filling defaults as needed."""
    client = client or MagicMock(fetch_html=MagicMock(return_value=FAKE_HTML))
    parser = parser or MagicMock(parse=MagicMock(return_value=FAKE_ENTRIES))
    storage = storage or MagicMock(output_path="/fake/path.json")
    monitor = monitor or MagicMock()
    return ScraperDependencies(client=client, parser=parser, storage=storage, monitor=monitor)


class TestScraperEngineRun:
    """Tests for the ScraperEngine.run() orchestration."""

    def test_run_calls_client_fetch_html(self):
        deps = _make_deps()
        ScraperEngine(deps).run()
        deps.client.fetch_html.assert_called_once()

    def test_run_passes_html_to_parser(self):
        deps = _make_deps()
        ScraperEngine(deps).run()
        deps.parser.parse.assert_called_once_with(FAKE_HTML)

    def test_run_saves_parsed_entries(self):
        deps = _make_deps()
        ScraperEngine(deps).run()
        deps.storage.save.assert_called_once_with(FAKE_ENTRIES)

    def test_run_closes_monitor(self):
        deps = _make_deps()
        ScraperEngine(deps).run()
        deps.monitor.close.assert_called_once()

    def test_run_initialises_monitor_with_entry_count(self):
        deps = _make_deps()
        ScraperEngine(deps).run()
        deps.monitor.init.assert_called_once_with(len(FAKE_ENTRIES))

    def test_run_updates_monitor_with_entry_count(self):
        deps = _make_deps()
        ScraperEngine(deps).run()
        deps.monitor.update.assert_called_once_with(len(FAKE_ENTRIES))

    def test_run_with_zero_entries_still_saves(self):
        empty_parser = MagicMock(parse=MagicMock(return_value=[]))
        deps = _make_deps(parser=empty_parser)
        ScraperEngine(deps).run()
        deps.storage.save.assert_called_once_with([])


class TestScraperEnginePrivateMethods:
    """Tests for the internal helper methods."""

    def test_fetch_html_delegates_to_client(self):
        deps = _make_deps()
        engine = ScraperEngine(deps)
        result = engine._fetch_html()
        assert result == FAKE_HTML

    def test_parse_entries_delegates_to_parser(self):
        deps = _make_deps()
        engine = ScraperEngine(deps)
        result = engine._parse_entries(FAKE_HTML)
        assert result == FAKE_ENTRIES
