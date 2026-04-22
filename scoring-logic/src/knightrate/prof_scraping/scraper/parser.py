from typing import List, Optional

from bs4 import BeautifulSoup, Tag

CONTENT_SELECTOR = "div.style__contentBody___gEuR0"


class CatalogParser:
    """Parses professor entry strings from UCF catalog HTML."""

    def parse(self, html: str) -> List[str]:
        """Extract all professor entry strings from rendered catalog HTML."""
        soup = BeautifulSoup(html, "html.parser")
        content_body = self._find_content_body(soup)
        if content_body is None:
            return []
        return self._extract_all_entries(content_body)

    def _find_content_body(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Locate the main content container div."""
        return soup.select_one(CONTENT_SELECTOR)

    def _extract_all_entries(self, container: Tag) -> List[str]:
        """Iterate paragraphs and collect those that have a <strong> child."""
        entries: List[str] = []
        for paragraph in container.find_all("p"):
            entry = self._extract_text_from_paragraph(paragraph)
            if entry:
                entries.append(entry)
        return entries

    def _extract_text_from_paragraph(self, paragraph: Tag) -> Optional[str]:
        """Return the full text for a <p> that contains a <strong>, else None.

        Collects text from all siblings after <strong> so that content split
        across a <br> tag is captured in full.
        """
        strong_tag = paragraph.find("strong")
        if strong_tag is None:
            return None
        strong_text = strong_tag.get_text(strip=True)
        trailing = self._collect_trailing_text(strong_tag)
        return " ".join((strong_text + trailing).split())

    def _collect_trailing_text(self, start_tag: Tag) -> str:
        """Collect raw text from every sibling after start_tag.

        NavigableStrings are used as-is; <br> elements are replaced with a
        single space; all other tags contribute their inner text.
        """
        parts = []
        for sibling in start_tag.next_siblings:
            if isinstance(sibling, str):
                parts.append(sibling)
            elif sibling.name == "br":
                parts.append(" ")
            else:
                parts.append(sibling.get_text())
        return "".join(parts)
