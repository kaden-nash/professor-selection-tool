---
name: rmp-schema
description: Data models, JSON file layout, and field naming conventions for the RateMyProfessors scraper. Read this before modifying models.py, storage.py, or any JSON output file.
---

# RMP Data Schema Skill

## 1. JSON File Layout

The scraper uses a **split-then-correlate** strategy. Three intermediate files are written during scraping, then merged into a final output.

### `rmp_prof_data.json`

JSON Lines format. One professor object per line. **Does not include `reviews`.**

```jsonl
{"id": "VGVhY2hlci0z...", "firstName": "Tanvir", "lastName": "Ahmed", "department": "Computer Science", "numRatings": 374, "avgDifficulty": 3.8, "avgRating": 3.9, "wouldTakeAgainPercent": 74.06, "allReviewsScraped": false}
```

### `rmp_review_data.json`

JSON Lines format. One review object per line. Includes `prof_id` to enable correlation.

```jsonl
{"id": "UmF0aW5nLTQy...", "prof_id": "VGVhY2hlci0z...", "clarityRating": 5, "class": "COP3502C", "comment": "...", ...}
```

### `rmp_prof_attrs.json`

JSON Lines format. Written incrementally to track which professors have had all reviews scraped.

```jsonl
{"prof_id": "VGVhY2hlci0z...", "allReviewsScraped": true}
```

### `rmp_data.json`

Standard JSON. Written once by `DataStorage.correlate_data()` after all scraping is done.

```json
{
  "professors": [
    {
      "id": "VGVhY2hlci0z...",
      "firstName": "Tanvir",
      "lastName": "Ahmed",
      "reviews": [
        { "id": "UmF0aW5nLTQy...", "prof_id": "VGVhY2hlci0z...", ... }
      ]
    }
  ]
}
```

> **Duplication handling:** `rmp_review_data.json` is rewritten without duplicates as part of `correlate_data()`.

---

## 2. Key Conventions

- **`ratingTags` is always a `List[str]`** even though the API returns it as a `"--"`-delimited string. The `parser.py` splits it before constructing the `Rating` model.
- **`prof_id` on `Rating` is not from the API.** It is set by `engine.py` (`r.prof_id = prof.id`) so that reviews can be linked back to professors during correlation.
- **`allReviewsScraped` is never saved in `rmp_prof_data.json`.** It is written separately to `rmp_prof_attrs.json` and merged at load time inside `DataStorage.load_all()`.
- **Model construction uses aliases.** When building a `Professor` or `Rating` from raw API JSON, pass the dict directly as `**kwargs` — Pydantic resolves aliases automatically because `populate_by_name=True` is set.
