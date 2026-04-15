# RateMyProfessors Scraper

This tool continuously scrapes professor profiles and individual student reviews from RateMyProfessors for the **University of Central Florida (UCF)**.

It handles rate limits, GraphQL pagination, unhandled data types, and utilizes multi-threading with residential proxy rotation to rapidly bypass Cloudflare blockages. It also supports **persistent auto-saving**, meaning any partial progress is saved, and interrupted runs can be picked up safely from where they left off without restarting from scratch.

## Setup Requirements

1. **Python 3.8+**
2. **Environment variables via `.env`**
3. **Python Packages** (install from root or via virtual environment):
   
```bash
pip install requests python-dotenv pydantic
```

## Configuration

You must create a `.env` file in the root `Large-Project` directory (where you run the script from) containing your ProxyRack credentials. This is vital to prevent IP bans.

**`.env` Example:**
```env
PROXYRACK_URL=http://premium.residential.proxyrack.net:9000
PROXYRACK_USERNAME=YOUR_USERNAME
PROXYRACK_PASSWORD=YOUR_PASSWORD
```

## Usage Instructions

To run the scraper, navigate into the `rmp_scraping` directory (where the `.venv` virtual environment is located) and execute the `main.py` file.

```bash
cd rmp_scraping
```

### 1. The Standard Scrape (Full Production)

This command initiates the complete scraping sequence of scanning 6,000+ professors and all of their combined ~50,000+ individual reviews.

```bash
python main.py --all
```

**What it does:**
- Immediately loads any existing data from `ucf_professors_data.json` so you do not lose any past work.
- Uses the RMP API to find every single UCF professor and compares them against your local JSON file. It ignores any professors you already have saved, while appending new professors securely.
- Initiates 200 background threads to rapidly fetch reviews for those professors. 
- Auto-saves the dataset to your hard drive every time an additional 10 professors are completed.

**Interrupting & Resuming:**
Because of the auto-save functionality, you can safely abort this script at any time using `CTRL+C` (Keyboard Interrupt) or simply closing your laptop. 
When you rerun `python main.py --all`, it will resume from where it left off!

---

### 2. The Reviews-Only Scrape (Skip Professor Search)

If you already have a populated list of UCF professors in `ucf_professors_data.json` and want to skip querying RateMyProfessors for new entries, you can force the script to start downloading reviews immediately:

```bash
python main.py --reviews-only
```

---

### 3. Testing Scrapes (Partial Output)

If you only want to test the scraper's functionality or capture a tiny subset of the latest data without waiting 45 minutes, use the `--limit-professors` and `--limit-reviews` flags.

```bash
# Fetch exactly 25 professors, and 5 reviews each
python main.py --all --limit-professors 25 --limit-reviews 5
```

---

### 4. Retrying Network Failures

If the script lost internet connection or ProxyRack returned 407/500 errors, the scraper automatically saves those failed network requests to `failed_requests.json`. 

You can instruct the scraper to attempt to re-download only those exact failed requests and weave them back into your main dataset without re-scraping the whole state:

```bash
python main.py --retry-failed
```

## Output Locations

* **`rmp_scraping/ucf_professors_data.json`**: This is the master database where all successful scraped objects land securely. You can actively read from this file while the scraper is running in another terminal.
* **`rmp_scraping/failed_requests.json`**: This stores temporary GraphQL payload failures for retry attempts. It deletes itself once all retries succeed.
