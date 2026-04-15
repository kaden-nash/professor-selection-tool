---
name: correlating_prof_data
description: Describes how to scrub and correlate all the professor and course data we've gathered so far.
---

# Context
- You are a senior backend developer specializing in data analytics.

# Objective
- You are assisting me in buildling a custom data scrubber and correlator so we can analyze data we've collected via web scraping.

# Tools
- Language is python

# Analysis Requirements
- We will likely need to rescrub and recorrelate data multiple times. Build this system with modularity, the principle of encapsulating what varies, and high reusability in mind. There will be lots of variation and edits to this system.
- Ensure you read all the data into memory once when performing the correlation as we'll need to cross reference items from multiple lists several times.

# Plan of Action
1. Refer to "correlation_specs.md" to get the scrubbing and correlating details.
2. Set up project with relevant parts like virtual environment for python (.venv). Create a sibling directory to rmp_scraping called "data_fixing" and put the project there.
3. Think about the system design of the project.
4. Implement the high level design (create files, folders, classes, etc)
5. Begin implementing the details of each specific piece. 
6. Ensure robust unit testing that adheres to the unit testing rules you've been given. 