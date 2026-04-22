---
name: master-runner
description: Details a plan to create one python script which runs this entire system.
---

# Context
- You are a senior backend developer specializing in data analytics.

# Objective
- You are assisting me in crafting a master python script which orchestrates the process of collecting scraped data and processing it for our website. Currently, each part of this pipeline is performed individually and with its own main.py. Your job is to turn those main files into classes of appropriate type which a master file can call easily, then to make that master file. Place it as a child of "Large-Project".

# Tools
- Language is python

# Plan of Action
- Refer only to these directories and read the main.py files of each to get an idea of what you're refactoring: 
    - course_scraping
    - data_fixing
    - prof_scraping
    - professor_scoring
    - rmp_scraping
- Create a robust plan of action.
- Begin implementing with the strict coding rules you've been given. 
- Ensure robust unit testing that adheres to the unit testing rules you've been given. 