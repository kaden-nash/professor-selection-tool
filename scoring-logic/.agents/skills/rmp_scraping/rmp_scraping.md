---
name: rmp-scraping
description: Full scraping architecture for the RateMyProfessors scraper — anti-bot strategy, concurrency model, storage pipeline, run modes, and extension guidelines. Read this before modifying engine.py, client.py, storage.py, rate_limiter.py, or main.py.
---

# RMP Scraping Architecture Skill

## 1. Anti-Bot Strategy

RateMyProfessors uses Cloudflare-based bot detection. All requests must look like legitimate browser traffic.

### Techniques in Use (in `client.py`)

| Technique | Implementation |
|---|---|
| **User-Agent rotation** | `USER_AGENTS` list in `client.py`; one is chosen at random per request |
| **Full browser header set** | `Accept`, `Accept-Language`, `Origin`, `Referer`, `Sec-Fetch-*` headers are included on every request |
| **Jittered exponential backoff** | On failure, sleeps `base_delay * 2^attempt + uniform(0.1, 1.5)` seconds before retrying |
| **Proxy rotation (ProxyRack)** | Configured via `.env` (`PROXYRACK_URL`, `PROXYRACK_USERNAME`, `PROXYRACK_PASSWORD`); the `requests.Session` is configured with proxy auth at init time |
| **Global rate limiting** | Token-bucket `RateLimiter` (5 req/s shared across all 200 threads, ≈40s per thread) |

### Adding a New Anti-Bot Technique

Add it inside `GraphQLClient._get_random_headers()` (for header-based techniques) or `GraphQLClient.execute()` (for delay/retry strategies).

---

## 2. Rate Limiter (`rate_limiter.py`)

`RateLimiter` is a thread-safe token bucket. All 200 threads share **one** `RateLimiter` instance.

- Initialized with `rate=5` (global requests per second).
- Call `rate_limiter.wait()` before every HTTP request. It blocks until a token is available.
- Tokens accumulate over time and are capped at `rate` to prevent bursting.

---

## 3. Storage Pipeline (`storage.py`)

The storage layer is completely **append-only during scraping**. No full-file rewrites happen mid-run.

### File Roles

| File | Format | Purpose |
|---|---|---|
| `rmp_prof_data.json` | JSON Lines | One professor per line; written during professor-fetch phase |
| `rmp_review_data.json` | JSON Lines | One review per line; written during review-fetch phase |
| `rmp_prof_attrs.json` | JSON Lines | `{prof_id, allReviewsScraped}` entries; written per-professor as reviews finish |
| `rmp_data.json` | JSON | Final correlated output; written once by `correlate_data()` |
| `failed_requests.json` | JSON array | Failed GraphQL payloads; appended on error, consumed by `--retry` mode |

### Thread Safety

`DataStorage` uses a single `threading.RLock` (`self.lock`). Every write method (`_append_jsonl`, `save_failed_request`, `append_prof_attrs`) acquires this lock. Always access any shared file through `DataStorage` methods — never write directly.

### Buffer Flush Strategy

- **Professor phase:** A local `professors_buffer` list collects new professors. When it reaches **50 items**, `storage.append_professors()` flushes it. Any remainder is flushed after the loop.
- **Review phase (per-professor thread):** A local `reviews_buffer` collects reviews. When it reaches **50 items**, `storage.append_reviews()` flushes it. Any remainder is flushed after the loop.
- **Why not keep all data in RAM?** The full dataset is ~6,000 professors × ~60 reviews each. Buffering only 50 items at a time keeps peak RAM low.

### Resuming an Interrupted Run

On startup, `DataStorage.load_all()` reads `rmp_prof_data.json` and `rmp_prof_attrs.json` into memory:
- Professors already in the file are loaded into a `prof_map = {id: Professor}`.
- Professors whose ID appears in `rmp_prof_attrs.json` with `allReviewsScraped: true` get their `all_reviews_scraped` flag set.
- The engine then skips any professor with `all_reviews_scraped == True`.

> **Deduplication:** A `seen_prof_ids` set is maintained during professor fetch; a `seen_review_ids` set is maintained per-professor during review fetch. This prevents double-writes if a cursor position overlaps.

### `correlate_data()`

Run once after all scraping is done (or on `--reviews-only` completion). It:
1. Loads all professors and attrs.
2. Streams through `rmp_review_data.json`, attaches each review to its professor (via `prof_id`), and deduplicates by `id`.
3. Rewrites `rmp_review_data.json` without duplicates.
4. Writes the fully nested structure to `rmp_data.json`.

---

## 4. Concurrency Model (`engine.py`)

- **Phase 1 — Professor fetch:** Single-threaded. Runs synchronously in `fetch_all_professors()`.
- **Phase 2 — Review fetch:** Multi-threaded. `ThreadPoolExecutor(max_workers=200)` submits one `fetch_reviews_for_professor(prof)` task per professor.
- `concurrent.futures.as_completed()` is used to collect results and bubble exceptions.
- The global `RateLimiter` is shared across all threads and enforces the 5 req/s ceiling.

### Cancellation

`engine._is_cancelled` is checked at the top of `fetch_reviews_for_professor()`. On `KeyboardInterrupt`, the engine simply exits — the last partial buffer (up to 50 items) may be lost, which is acceptable.

---

## 5. Run Modes (`main.py`)

| CLI Flag | Mode | Description |
|---|---|---|
| `--all` | Full run | Fetch professors then reviews |
| `--reviews-only` | Reviews only | Skip professor fetch; use existing `rmp_prof_data.json` |
| `--retry` | Retry failed | Replay all payloads from `failed_requests.json` |
| `--limit-professors N` | Limit (any mode) | Stop after N professors |
| `--limit-reviews N` | Limit (any mode) | Stop after N reviews per professor |

---

## 6. Monitoring (`monitor.py`)

`Monitor` wraps `tqdm` progress bars for the console:
- `monitor.init_professors(total)` — sets up the professor-count bar.
- `monitor.update_professors(n)` — increments it by `n`.
- `monitor.init_reviews(total)` — sets up the professor-completion bar (one tick per fully-scraped professor).
- `monitor.update_reviews(n)` — increments it by `n`.
- `monitor.close()` — flushes and closes all bars.

---

## 7. Extension Guidelines

### Adding a New Scraped Field to `Professor`

1. Add the field to `Professor` in `models.py` with the appropriate `Field(alias=...)`.
2. Verify `parse_professors()` in `parser.py` receives it in the node — if it does, Pydantic constructs it automatically.
3. If the field needs special processing (e.g., splitting a string), add that logic in `parse_professors()` before constructing the `Professor`.
4. Update `rmp_schema.md` to document the new field.

### Adding a New Scraped Field to `Rating`

Same pattern: update `Rating` in `models.py`, add any preprocessing in `parse_ratings()`, update `rmp_schema.md`.

### Adding a new Run Mode

1. Add the flag to the `argparse` parser in `main.py`.
2. Add a new method on `ScraperEngine` (keep it under 25 lines; decompose if needed).
3. Call the method from `main.py` based on the flag.
