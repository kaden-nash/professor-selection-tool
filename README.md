# KnightRate

A professor rating and selection tool for University of Central Florida (UCF) students. KnightRate aggregates professor data from RateMyProfessors and UCF's course catalog, then surfaces personalized recommendations using an algorithmic scoring system.

## Features

- Search professors by name or course code
- Compare professors side-by-side
- Save favorite professors to a personal starred list
- Archetype classification: **The Unicorn**, **The Mastermind**, **The NPC**, **The Saboteur**
- User accounts with email verification and password reset
- Data pipeline covering ~6,000 UCF professors and ~150,000 RMP reviews

## Architecture

| Layer | Tech |
|---|---|
| Frontend | React 19, TypeScript, Vite, React Router |
| Backend | Node.js, Express 5, MongoDB, JWT, SendGrid |
| Data Pipeline | Python 3.13, Playwright, BeautifulSoup, PyMongo |

```
.
├── Frontend/          # React + TypeScript SPA
├── backend/           # Express REST API
└── scoring-logic/     # Python ETL pipeline (scrape → clean → score)
```

## Prerequisites

- Node.js 18+
- Python 3.13+
- MongoDB Atlas cluster (or local MongoDB)
- SendGrid account (for email features)
- ProxyRack residential proxy credentials (for the scraper)

## Setup

### 1. Backend

```bash
cd backend
npm install
```

Create `backend/.env`:

```env
MONGO_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/backend
FRONTEND_URL=http://localhost:5173
JWT_SECRET=<your-secret>
PORT=5001
SENDGRID_API_KEY=<your-sendgrid-key>
EMAIL_FROM=<sender-email>
```

```bash
npm run dev   # starts on port 5001
```

### 2. Frontend

```bash
cd Frontend
npm install
```

Create `Frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:5001/api
```

```bash
npm run dev   # starts on http://localhost:5173
```

### 3. Data Pipeline

```bash
cd scoring-logic
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Create `scoring-logic/.env`:

```env
PROXYRACK_URL=http://premium.residential.proxyrack.net:10000
PROXYRACK_USERNAME=<username>
PROXYRACK_PASSWORD=<password>
MONGO_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/backend
MONGO_DB=backend
MONGO_COLLECTION_PROFESSORS=rawProfessorData
MONGO_COLLECTION_STATISTICS=rawGlobalStatistics
```

> **Note:** ProxyRack residential proxy credentials are required to bypass Cloudflare on RateMyProfessors. A full scrape takes approximately 3–4 hours.

Run the full pipeline:

```bash
python run_pipeline.py --scrape-rmp --scrape-profs --scrape-courses
```

Useful flags:

| Flag | Effect |
|---|---|
| `--scrape-rmp` | Scrape RateMyProfessors |
| `--scrape-profs` | Scrape UCF professor catalog |
| `--scrape-courses` | Scrape UCF course catalog |
| `--reviews-only` | Only fetch new reviews, skip full professor scrape |
| `--skip-fix` | Skip the data-cleaning step |
| `--skip-scoring` | Skip the scoring step |
| `--limit-profs N` | Cap the number of professors scraped |
| `--limit-reviews N` | Cap the number of reviews scraped |
| `--clean-scrape` | Ignore previously cached data |

## API Reference

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Log in |
| POST | `/auth/forgot-password` | Send reset email |
| POST | `/auth/reset-password` | Reset password |

### Professors

| Method | Endpoint | Description |
|---|---|---|
| GET | `/professors/search?filter=name&q=...` | Search by professor name |
| GET | `/professors/search?filter=course&q=...` | Search by course code |

### Users

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/starred` | Get starred professors |
| POST | `/users/starred/:id` | Star a professor |
| DELETE | `/users/starred/:id` | Unstar a professor |

### Stats

| Method | Endpoint | Description |
|---|---|---|
| GET | `/stats/global` | UCF-wide statistics |

## Scoring

Professors are scored on quality, difficulty, and retake likelihood using RateMyProfessors data. Only professors with **5 or more reviews** and **at least one review within the past 3 years** are included. Professors are then classified into one of four archetypes based on their difficulty and quality metrics.

## Testing

```bash
# Backend
cd backend && npm test

# Frontend
cd Frontend && npm test

# Python pipeline
cd scoring-logic && pytest
```

## AI Disclosure

Portions of this project were developed with AI assistance and reviewed and approved by the team:

- **README** — written by AI
- **Unit tests** (backend, frontend, and Python pipeline) — written by AI
- **Frontend** — UI touch-ups and minor improvements assisted by AI

All AI-generated code and content was reviewed and approved by Kaden Nash before inclusion.

## License

Copyright © 2025 Kaden Nash. All rights reserved.
