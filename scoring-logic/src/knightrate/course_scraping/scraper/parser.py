from bs4 import BeautifulSoup

class Parser:
    """Parses HTML content to extract course links and titles."""

    def extract_group_links(self, html: str) -> list[str]:
        """Extracts group links from the root catalog page."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        a_tags = soup.find_all("a", class_="style__linkButton___zlNe4")
        for a_tag in a_tags:
            if a_tag.has_attr("href"):
                links.append(a_tag["href"])
                
        return links

    def extract_course_titles(self, html: str) -> list[str]:
        """Extracts course titles from a group page."""
        soup = BeautifulSoup(html, "html.parser")
        titles = []
        
        columns = soup.find_all("div", class_="style__columns___K01Hv")
        for col in columns:
            a_tag = col.find("a")
            if a_tag:
                title = a_tag.get_text(strip=True)
                if title:
                    titles.append(title)
                    
        return titles
