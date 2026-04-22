# RateMyProfessors Scraper

This tool continuously scrapes professor profiles and individual student reviews from RateMyProfessors for the University of Central Florida (UCF).

It handles rate limits, GraphQL pagination, unhandled data types, and utilizes multi-threading with residential proxy rotation to rapidly bypass Cloudflare blockages. It also supports persistent auto-saving, meaning any partial progress is saved. 

However, all previous data must be rescraped to ensure there are no gaps in information. You should set aside 3-4 hours for RMP scraping to complete. Stopping midway will force you to start the 3-4 hours process all over.

RMP scraping retrieves 6,000+ professors and all of their combined ~150,000+ individual reviews.

## Setup Requirements

1. Python 3.13+
2. Environment variables via `.env`
3. A local virtual environment
```bash
python -m venv .venv
```

4. Python Packages (install from directory containing pyproject.toml):
   
```bash
pip install -e .
```
- We do an editable install (-e) so you can make some edits without having to reinstall the package every time.

## Configuration

You must create a `.env` file in the root `scoring-logic` directory (where you run the script from) containing your ProxyRack credentials. This is vital to prevent IP bans.

**`.env` Example:**
```env
PROXYRACK_URL=http://premium.residential.proxyrack.net:10000
PROXYRACK_USERNAME=YOUR_USERNAME
PROXYRACK_PASSWORD=YOUR_PASSWORD
```

## Usage Instructions

The `run_pipeline.py` script is the master orchestrator for the UCF Professor Scraper. It allows you to run specific stages of the data pipeline or execute the entire process from collection to scoring.


Ensure you have activated your virtual environment and installed all the relevant dependencies. See instructions above.

## Command-Line Arguments

| Argument | Type | Description |
| :--- | :--- | :--- |
| `--scrape-rmp` | Flag | Enables the RateMyProfessors scraping stage. This is a network-bound, long-running process. |
| `--scrape-profs` | Flag | Enables the UCF Catalog professor scraping stage. |
| `--scrape-courses` | Flag | Enables the UCF Course Catalog scraping stage. |
| `--skip-fix` | Flag | Skips the data-fixing and professor-course correlation stage. |
| `--skip-scoring` | Flag | Skips the final professor scoring stage. |
| `--reviews-only` | Flag | (RMP) Only scrape reviews for professors already in the local database. Skip the search for new professors. |
| `--limit-profs <N>` | Integer | (RMP) Stop searching for new professors after reaching this limit. |
| `--limit-reviews <N>` | Integer | (RMP) Stop scraping reviews for each professor after reaching this limit per professor. |
| `--clean-scrape` | Flag | (RMP) Clears every output file used by the RMP scraper for a fresh run. |

---

## Use Case Examples

### 1. Minimal Test Run
**Command:** `python run_pipeline.py --scrape-rmp --limit-profs 5 --limit-reviews 10`

*   **What it does:** Runs the RMP scraper but caps it at the first 5 professors found, and only grabs 10 reviews per professor.
*   **Why use it:** Verifying that your network connection and parser are working without waiting for a full scrape.

### 2. Full Data Refresh
**Command:** `python run_pipeline.py --scrape-rmp --scrape-profs --scrape-courses --clean-scrape`

*   **What it does:** Executes every scraping stage and follows through with data fixing and professor scoring.
*   **Why use it:** Use this when you want to rebuild the entire database from scratch with current live data.

### 3. Update Reviews for Existing Professors
**Command:** `python run_pipeline.py --scrape-rmp --reviews-only --limit-reviews 50`

*   **What it does:** Skips the initial UCF searches on RMP. Instead, it looks at the professors you already have in `rmp_professors.json` and fetches up to 50 *new* reviews for each.
*   **Why use it:** Efficiently updates scores without re-scanning the entire UCF department list on RMP.

### 4. Recalculate Scores Only
**Command:** `python run_pipeline.py --skip-fix`

*   **What it does:** Skips all scraping and data-fixing logic. It immediately jumps to the scoring engine to recalculate grades based on existing local JSON data.
*   **Why use it:** If you've modified the scoring heuristics and want to see the new results instantly without hitting any network endpoints.

### 5. Catalog Correlation Only
**Command:** `python run_pipeline.py --scrape-profs --scrape-courses --skip-scoring`

*   **What it does:** Scrapes UCF's own websites (faculty list and course catalog) and correlates them, but skips the RMP integration and scoring.
*   **Why use it:** Useful if you only care about the internal UCF professor-to-course mapping.

---

> [!TIP]
> You can combine any of these flags. If no `--scrape-...` flags are provided, the script defaults to running only the local processing stages (`Data Fixing` and `Scoring`).

> [!IMPORTANT]
> The `--limit-...` and `--reviews-only` flags have no effect unless `--scrape-rmp` is also enabled.


## Output Locations

**src/output_files**: contains subfolders corresponding to each stage of the pipeline with relevant files for each stage within.

## Data Longevity
When it is time to get new data from RMP, use the --clean-scrape flag to ensure that the data is not stale. Professor attributes besides reviews will not update if you don't do this. You may end up with a professor that has 43 actual reviews but their "numRatings" attribute is 20. That will mess up the entire algorithm.

You may have noticed the "allReviewsScraped" flag on each professor. This flag is useful for picking up where you left off if the review scraping is interrupted by useless after completion of an entire scrape. It falls out of date as well. 

## Important constraints others working on this project should know.
- Graduate classes should be scraped from the course catalog. Currently there is no validation of those courses. Whatever a student puts goes. 
- Profs with <5 reviews are excluded from scoring.
- Profs that have not had a review in > 3 years are excluded from scoring.
