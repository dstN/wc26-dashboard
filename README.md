# EFI World Cup 26 Data Engine

Portfolio-grade full-stack data engine: Python pipeline ingests FIFA Enhanced Football Intelligence (EFI) Post Match Summary PDFs into MySQL 8.0, FastAPI serves the data, and a Svelte 5 editorial dashboard renders it — all behind one `docker compose up`.

**Featured match:** Germany 7–1 Curaçao · Group E · Match 10 · Houston · 14.06.2026

## Features

- **36 matches ingested** from real FIFA PMSR PDFs — possession, phases, spatial, line breaks, final-third zones, defensive actions
- **Full match detail pages** — 7 EFI data sections per match (Possession, Head-to-Head, Phase Analysis, Line Breaks, Spatial Control, Defensive Actions, Final Third Zones)
- **Team detail pages** — aggregate stats and per-match history
- **1 248 players** — searchable and filterable roster across all 48 teams
- **6 languages** — EN · DE · ES · PT · FR · AR, with RTL layout for Arabic
- **Responsive** — works from 400px mobile up to 1440px desktop
- **PDF drop-folder watcher** — drop new PMSR PDFs into a folder; a cron job picks them up automatically

## Quickstart

```bash
cp .env.example .env
make up
```

- **Dashboard:** http://localhost:5173
- **API docs:** http://localhost:8000/docs
- **API health:** http://localhost:8000/health

## Make targets

| Target | Description |
|--------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make reset` | Wipe DB volume and restart (re-seeds automatically) |
| `make crawl` | Run full 48-team EFI crawl |
| `make test` | Run all test suites |
| `make contract` | Regenerate OpenAPI TypeScript types |
| `make fmt` | Format all code |
| `make logs` | Tail compose logs |

## PDF ingestion pipeline

### Ingest PDFs manually

```bash
# Parse a single PDF to SQL, print to stdout
python -m ingestion.parse_efi_pdf path/to/Match_10_GER_CUR.pdf

# Parse multiple PDFs and write seed file
python -m ingestion.parse_efi_pdf path/to/pdfs/*.pdf --out db/seeds/04_matches.sql
```

### Automatic drop-folder watcher (cron / Phusion Passenger)

Set `PDF_WATCH_DIR` in `.env` to an absolute path:

```dotenv
# .env
PDF_WATCH_DIR=/home/myuser/efi_pdf_drop
```

Then add a cron job:

```cron
# Ingest new PDFs every 5 minutes
*/5 * * * * cd /path/to/project && python -m ingestion.watch_pdfs >> /var/log/efi_watch.log 2>&1
```

Flags: `--dry-run` (parse only), `--force` (re-process all), `--dir <path>` (override env).

## Verification

After `make up` and waiting for services to be healthy:

```bash
# DB seeded correctly
docker compose exec db mysql -uwc26user -pwc26pass wc26 \
  -e "SELECT COUNT(*) FROM teams; \
      SELECT match_no, is_featured FROM matches WHERE is_featured=1; \
      SELECT matches_played, goals_total, avg_in_contest_pct FROM tournament_overview;"

# API working
curl http://localhost:8000/health/db
curl http://localhost:8000/api/v1/matches/10/possession
curl http://localhost:8000/api/v1/teams/
curl http://localhost:8000/api/v1/players/

# Frontend running
curl -s http://localhost:5173/ | grep -o '<title>[^<]*</title>'
```

## Tests

```bash
# Frontend (Vitest + happy-dom)
cd frontend && npx vitest run

# Backend (pytest)
cd ingestion && python3 -m pytest tests/ -v

# Ingestion watcher
cd ingestion && python3 -m pytest tests/test_watch_pdfs.py -v
```

## Stack

| Layer | Technology |
|-------|-----------|
| Database | MySQL 8.0 — 11 EFI tables, scope discriminator for match vs aggregate |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 |
| Ingestion | PyMuPDF (fitz), pandas, SQLAlchemy sync |
| Frontend | Node 20, SvelteKit, Svelte 5 runes, Bits UI |
| Design | Sports editorial design system — light/dark, CSS custom properties |
| i18n | 6-locale writable store (EN/DE/ES/PT/FR/AR), RTL Arabic |
| Testing | Vitest + happy-dom, pytest, Playwright e2e |
| Infra | Docker Compose, healthcheck-gated startup, Makefile |

## Routes

| URL | Description |
|-----|-------------|
| `/` | Overview — featured match, KPIs, recent results |
| `/matches` | All 36 group-stage matches, grouped by group |
| `/matches/[id]` | Full match detail — 7 EFI data sections |
| `/teams` | All 48 teams with stats |
| `/teams/[id]` | Team detail — aggregate stats + match history |
| `/players` | 1 248-player roster — searchable and filterable |
| `/tournament` | Tournament progress — phases, KPIs |
