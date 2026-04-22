---
name: rmp-skills-index
description: Index of all available skills for the RateMyProfessors scraping project. Read this first to find the right skill for your task.
---

# RMP Scraper Skills Index

This project contains modular skills broken out by concern. Read the relevant skill before working on any part of the scraper.

| Skill File | When to Use |
|---|---|
| [rmp_schema.md](rmp_schema.md) | Whenever you need to understand or modify the data models (`Professor`, `Rating`), the JSON file layout, or field naming conventions. |
| [rmp_graphql_api.md](rmp_graphql_api.md) | Whenever you need to understand the GraphQL API — exact query payloads, pagination cursors, or response parsing rules. |
| [rmp_scraping.md](rmp_scraping.md) | Whenever you need to understand or change the scraper's architecture, anti-bot strategy, concurrency model, storage pipeline, or run modes. |

## Project Layout

```
rmp_scraping/
├── main.py               # CLI entry point
└── scraper/
    ├── models.py         # Pydantic data models  → see rmp_schema.md
    ├── parser.py         # GraphQL response parsing → see rmp_graphql_api.md
    ├── client.py         # HTTP + anti-bot layer  → see rmp_scraping.md
    ├── rate_limiter.py   # Token-bucket rate limiter → see rmp_scraping.md
    ├── engine.py         # Orchestration & concurrency → see rmp_scraping.md
    ├── storage.py        # Thread-safe JSON I/O   → see rmp_scraping.md
    └── monitor.py        # Progress bar display   → see rmp_scraping.md
```
