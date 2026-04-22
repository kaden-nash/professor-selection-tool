---
name: rmp-graphql-api
description: GraphQL API details for RateMyProfessors — exact query payloads, pagination mechanics, and response parsing rules. Read this before modifying parser.py or the query constants in engine.py.
---

# RMP GraphQL API Skill

The RMP website exposes all its data through a GraphQL endpoint. No HTML scraping is needed.

- **Endpoint:** `https://www.ratemyprofessors.com/graphql`
- **Method:** `POST` with `Content-Type: application/json`
- **School ID (UCF):** `U2Nob29sLTEwODI=`

---

## 1. Fetching All Professors (`TeacherSearchPaginationQuery`)

### Pagination Mechanics

- Results are **cursor-paginated**. Send `count: 5` to get 5 professors per page.
- **First request cursor:** `"YXJyYXljb25uZWN0aW9uOi0x"` (hardcoded sentinel for the beginning).
- After each response, update `cursor` to `pageInfo.endCursor`.
- Stop when `pageInfo.hasNextPage` is `false` or `endCursor` is empty.
- Save `resultCount` from the **first** response only; this is the total number of professors.

### Request Payload

The `variables` object is the only part that changes between requests:

```json
{
  "operationName": "TeacherSearchPaginationQuery",
  "variables": {
    "count": 5,
    "cursor": "<endCursor from previous response, or sentinel for first>",
    "query": {
      "text": "",
      "schoolID": "U2Nob29sLTEwODI=",
      "fallback": true
    }
  },
  "query": "<see PROFESSOR_QUERY_DICT in engine.py>"
}
```

### Response Path

```
data.search.teachers
  .edges[].node      → one Professor per node
  .pageInfo
    .hasNextPage     → bool: whether more pages exist
    .endCursor       → str: cursor to use in the next request
  .resultCount       → int: total number of professors (first response only)
```

### Fields to Extract Per Professor Node

| API Field | Maps to `Professor` Field |
|---|---|
| `id` | `id` |
| `firstName` | `first_name` |
| `lastName` | `last_name` |
| `department` | `department` |
| `numRatings` | `num_ratings` |
| `avgDifficulty` | `avg_difficulty` |
| `avgRating` | `avg_rating` |
| `wouldTakeAgainPercent` | `would_take_again_percent` |

---

## 2. Fetching Reviews for a Professor (`RatingsListQuery`)

### Pagination Mechanics

- Same cursor-pagination pattern as professors.
- **First request cursor:** `"YXJyYXljb25uZWN0aW9uOi0x"` (same sentinel).
- After each response, update `cursor` to `ratings.pageInfo.endCursor`.
- Stop when `ratings.pageInfo.hasNextPage` is `false` or `endCursor` is empty.
- When the loop ends with `hasNextPage == false`, set `allReviewsScraped = true` for the professor and write it to `rmp_prof_attrs.json`.

### Request Payload

```json
{
  "operationName": "RatingsListQuery",
  "variables": {
    "count": 5,
    "id": "<professor's RMP id>",
    "courseFilter": null,
    "cursor": "<endCursor from previous response, or sentinel for first>"
  },
  "query": "<see RATINGS_QUERY_DICT in engine.py>"
}
```

### Response Path

```
data.node
  .ratings
    .edges[].node    → one Rating per node
    .pageInfo
      .hasNextPage   → bool
      .endCursor     → str
```

### Fields to Extract Per Rating Node

| API Field | Maps to `Rating` Field | Notes |
|---|---|---|
| `id` | `id` | |
| `attendanceMandatory` | `attendance_mandatory` | |
| `clarityRating` | `clarity_rating` | |
| `class` | `course_class` | `class` is a Python keyword; uses alias |
| `comment` | `comment` | |
| `date` | `date` | |
| `difficultyRating` | `difficulty_rating` | |
| `grade` | `grade` | |
| `helpfulRating` | `helpful_rating` | |
| `isForCredit` | `is_for_credit` | |
| `isForOnlineClass` | `is_for_online_class` | |
| `ratingTags` | `rating_tags` | **Must be split** — see note below |
| `teacherNote` | `teacher_note` | |
| `textbookUse` | `textbook_use` | `-1` means not applicable |
| `thumbs` | `thumbs` | |
| `thumbsDownTotal` | `thumbs_down_total` | |
| `thumbsUpTotal` | `thumbs_up_total` | |
| `wouldTakeAgain` | `would_take_again` | |

> **`ratingTags` parsing rule:** The API returns a single `"--"`-delimited string (e.g., `"Accessible outside class--Caring"`). This **must** be split by `"--"` and stored as a `List[str]`. Empty or whitespace strings are dropped. This logic lives in `parser.py::parse_ratings`.

> **`prof_id` is NOT from the API.** After parsing a `Rating`, the engine sets `r.prof_id = prof.id` so the review can be correlated to its professor during the final merge step.

---

## 3. Error Handling

- `GraphQLRequestError` is raised (from `client.py`) after all retry attempts are exhausted.
- When caught, the failing raw payload is written to `failed_requests.json` via `storage.save_failed_request()`.
- Failed requests can be replayed via the `--retry` CLI mode.
- A response with HTTP 200 but a non-empty `errors` field in the JSON body is treated as a failure and retried.
