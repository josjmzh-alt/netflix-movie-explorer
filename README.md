# 🍿 Netflix Movie Library Explorer

Internal tool for browsing and querying movie metadata from Google Drive.

## Tech Stack

- **Backend:** Python 3.11 · FastAPI · Google Drive API v3
- **Frontend:** React 18 · TypeScript · Vite · served via nginx
- **Auth:** OAuth2 (Desktop app credentials — web flow, browser-based)
- **Storage:** In-memory (no external database)

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A `credentials.json` file (OAuth2 Desktop app credentials from GCP — provided separately)

---

## Running the app

```bash
# 1. Clone the repository
git clone <repo-url>
cd netflix-movie-explorer

# 2. Add your credentials file
cp /path/to/credentials.json credentials/credentials.json

# 3. Build and start
docker compose up --build
```

Open **http://localhost:3000** in your browser.

On first run you'll see a **"Connect to Google Drive"** button. Click it, log in with your Google account, and the app will load all movie data automatically. The OAuth token is saved in `credentials/token.json` — subsequent runs skip the login step.

To stop: `Ctrl+C` then `docker compose down`

---

## Auth flow

```
Browser clicks "Connect to Google Drive"
        │
        ▼
GET /api/auth/login-url  →  backend returns Google OAuth URL
        │
        ▼
Browser redirects to Google consent screen
        │
        ▼
Google redirects to http://localhost:3000/auth/callback?code=...
        │  (nginx proxies this to the backend)
        ▼
Backend exchanges code for token, saves credentials/token.json
        │
        ▼
Backend triggers Drive data load in background
        │
        ▼
Browser redirected back to http://localhost:3000 — app loads
```

**Note on credentials:** `credentials.json` identifies the application to Google (the "who is this app?" question). The OAuth login flow answers "who is this user?". Both are required by the OAuth2 spec. In production this would be replaced by a Service Account for server-to-server auth — no user login needed.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Auth state, load state, movie count |
| GET | `/api/stats` | Top 5 genres, average rating, movies by year |
| GET | `/api/movies/search?title=` | Search by title (partial match) |
| GET | `/api/movies/top-rated?limit=` | Top rated movies |
| POST | `/api/movies` | Add a movie (in-memory, not written to Drive) |
| GET | `/api/movies?genre=&min_rating=&year=` | Filtered list for technical users |

Interactive docs available at **http://localhost:8000/docs**

---

## Architecture

```
credentials/
├── credentials.json   ← OAuth2 app identity (you provide, not in git)
└── token.json         ← Generated after first login, persisted via volume

docker-compose
├── backend  (:8000)   ← FastAPI: auth + Drive traversal + REST API
└── frontend (:3000)   ← React app served by nginx, proxies /api and /auth to backend
```

### Backend layout

```
backend/
├── app/
│   ├── main.py              ← FastAPI app setup and router registration
│   ├── core/config.py       ← Environment-backed app settings
│   ├── api/router.py        ← Top-level router composition
│   ├── api/routes/          ← HTTP endpoints grouped by feature
│   ├── schemas/             ← Pydantic models split by API concern
│   └── services/            ← Drive auth/client/parser, loading, and in-memory store
├── Dockerfile
└── requirements.txt
```

### Key design decisions

**In-memory store:** All movie data loads once at startup into a Python list. O(n) scan performance is acceptable for thousands of records. A production version would index by genre/year in a database.

**Background loading:** Drive traversal runs in a thread pool executor so FastAPI stays responsive. The frontend polls `/api/status` until `loaded: true`.

**Flexible JSON parser:** `normalize_movie()` uses a priority list of field name aliases to handle the varied JSON structures across the Drive dataset.

**Debug logging:** Set `DEBUG_DRIVE_LOGS=true` in `docker-compose.yml` to emit detailed JSON logs for Drive auth, traversal, file download, and movie parsing.

**BFF pattern:** The React frontend only talks to the FastAPI backend — never directly to Google Drive. The backend acts as a Backend-for-Frontend, shaping data for the UI's needs.

**Local ports:** The React app is served through nginx on port 3000, which proxies `/api` and `/auth` to the backend. The backend is also exposed on port 8000 for FastAPI docs and direct API inspection during development.
