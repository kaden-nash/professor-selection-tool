import pytest
from src.knightrate.prof_scraping.scraper.parser import CatalogParser

CONTENT_DIV = '<div class="style__contentBody___gEuR0">{}</div>'


def _make_html(inner: str) -> str:
    return CONTENT_DIV.format(inner)


class TestCatalogParserHappyPath:
    """Tests for well-formed catalog HTML."""

    def setup_method(self):
        self.parser = CatalogParser()

    def test_single_entry_returns_one_string(self):
        html = _make_html("<p><strong>Abbas, Hadi</strong>, Professor (8/8/1995)</p>")
        result = self.parser.parse(html)
        assert result == ["Abbas, Hadi, Professor (8/8/1995)"]

    def test_multiple_entries_returns_all(self):
        inner = (
            "<p><strong>Abbas, Hadi</strong>, Professor</p>"
            "<p><strong>Smith, Jane</strong>, Lecturer</p>"
        )
        result = self.parser.parse(_make_html(inner))
        assert len(result) == 2
        assert result[0] == "Abbas, Hadi, Professor"
        assert result[1] == "Smith, Jane, Lecturer"

    def test_strong_only_no_trailing_text(self):
        html = _make_html("<p><strong>Abbas, Hadi</strong></p>")
        result = self.parser.parse(html)
        assert result == ["Abbas, Hadi"]

    def test_preserves_special_characters(self):
        html = _make_html("<p><strong>Müller, Hans</strong>, Prof. &amp; Head</p>")
        result = self.parser.parse(html)
        assert "Müller, Hans" in result[0]

    def test_text_after_br_is_captured(self):
        """Verifies the real-world pattern: name <strong>, text <br> more text."""
        inner = (
            "<p><strong>Abbas, Hadi,</strong> Professor of School of Visual Arts"
            "<br>(8/8/1995), M.F.A. (Wichita State University)</p>"
        )
        result = self.parser.parse(_make_html(inner))
        assert len(result) == 1
        assert result[0] == (
            "Abbas, Hadi, Professor of School of Visual Arts "
            "(8/8/1995), M.F.A. (Wichita State University)"
        )

    def test_whitespace_is_normalised_across_br(self):
        """Excess newlines and spaces around a br should collapse to one space."""
        inner = "<p><strong>Smith, Jane,</strong>   Lecturer\n<br>\n  (1/1/2000)</p>"
        result = self.parser.parse(_make_html(inner))
        assert result == ["Smith, Jane, Lecturer (1/1/2000)"]

    def test_inline_tag_sibling_text_is_captured(self):
        """Non-br inline tags (e.g. span) after strong have their text collected."""
        inner = "<p><strong>Doe, John,</strong><span> Assistant Professor</span></p>"
        result = self.parser.parse(_make_html(inner))
        assert result == ["Doe, John, Assistant Professor"]



class TestCatalogParserFiltering:
    """Tests for paragraphs that should be skipped."""

    def setup_method(self):
        self.parser = CatalogParser()

    def test_paragraph_without_strong_is_skipped(self):
        html = _make_html("<p>This is a plain intro paragraph.</p>")
        result = self.parser.parse(html)
        assert result == []

    def test_mixed_paragraphs_skips_non_strong(self):
        inner = (
            "<p>Intro text with no strong.</p>"
            "<p><strong>Abbas, Hadi</strong>, Professor</p>"
        )
        result = self.parser.parse(_make_html(inner))
        assert len(result) == 1
        assert result[0].startswith("Abbas, Hadi")

    def test_empty_container_returns_empty_list(self):
        result = self.parser.parse(_make_html(""))
        assert result == []


class TestCatalogParserMissingContainer:
    """Tests for HTML that lacks the expected content div."""

    def setup_method(self):
        self.parser = CatalogParser()

    def test_missing_content_div_returns_empty_list(self):
        result = self.parser.parse("<html><body><p><strong>X</strong></p></body></html>")
        assert result == []

    def test_empty_html_returns_empty_list(self):
        result = self.parser.parse("")
        assert result == []
