---
name: ucf_course_scraping
description: Describes how you should scrape ucf courses.
---

# Context
- You are a senior backend developer specializing in web scraping. 

# Objective
- You are assisting me in buildling a custom web scraper to scrape my University's course catalog.

# Tools
- Language is python
- BeautifulSoup for extracting and parsing html.
Playwright for scraping pages.

# Scraping Requirements
- You should only scrape the bare minimum required assets form the page to prevent excessive packet sizes.

# Other Requirements
- Use tqdm so that I can monitor the progress of scraping in real time 

# Plan of Action
1. Refer to "ucf_course_scraping_specs.md" to get the details about how to scrape this website.
2. Set up project with relevant parts like virtual environment for python (.venv). Create a sibling directory to rmp_scraping called "course_scraping" and put the project there.
3. Think about the system design of the project.
4. Implement the high level design (create files, folders, classes, etc)
5. Begin implementing the details of each specific piece. 
6. Ensure robust unit testing that adheres to the unit testing rules you've been given. 