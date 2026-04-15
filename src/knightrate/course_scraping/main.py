from scraper.html_fetcher import HtmlFetcher
from scraper.parser import Parser
from scraper.course_scraper import CourseScraper
from storage.data_storage import DataStorage

def main():
    root_url = "https://www.ucf.edu/catalog/undergraduate/#/courses"
    print(f"Starting UCF Course Scraper on {root_url}")
    
    fetcher = HtmlFetcher()
    parser = Parser()
    storage = DataStorage()
    
    scraper = CourseScraper(fetcher, parser)
    
    try:
        courses = scraper.run_scraping(root_url)
        if courses:
            storage.save_courses(courses)
            print(f"Successfully saved {len(courses)} courses.")
        else:
            print("Finished scraping but no courses were found.")
    finally:
        fetcher.close()

if __name__ == "__main__":
    main()
