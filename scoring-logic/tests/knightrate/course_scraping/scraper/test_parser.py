import pytest
from src.knightrate.course_scraping.scraper.parser import Parser

@pytest.fixture
def parser():
    return Parser()

def test_extract_group_links_success(parser):
    html = '''
    <div>
        <a class="style__linkButton___zlNe4" href="/group1">Group 1</a>
        <a class="style__linkButton___zlNe4" href="/group2">Group 2</a>
    </div>
    '''
    links = parser.extract_group_links(html)
    assert links == ["/group1", "/group2"]

def test_extract_group_links_missing_a_tag(parser):
    html = '<div><span>No link</span></div>'
    links = parser.extract_group_links(html)
    assert links == []

def test_extract_course_titles_success(parser):
    html = '''
    <div class="style__columns___K01Hv">
        <a href="/course/1">COP3502C - Computer Science I</a>
    </div>
    <div class="style__columns___K01Hv">
        <a href="/course/2">ADE4382 - Teaching Adult Learners</a>
    </div>
    '''
    titles = parser.extract_course_titles(html)
    assert titles == ["COP3502C - Computer Science I", "ADE4382 - Teaching Adult Learners"]

def test_extract_course_titles_no_divs(parser):
    html = '<div><a href="/course/1">Not a course col</a></div>'
    titles = parser.extract_course_titles(html)
    assert titles == []

def test_extract_course_titles_no_a_tags(parser):
    html = '<div class="style__columns___K01Hv"><span>No link here</span></div>'
    titles = parser.extract_course_titles(html)
    assert titles == []
