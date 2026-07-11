# EFI World Cup 26 Data Engine

Portfolio-grade full-stack data engine: Python pipeline ingests FIFA Enhanced Football Intelligence (EFI) Post Match Summary PDFs into MySQL 8.0, FastAPI serves the data, and a Svelte 5 editorial dashboard renders it — all behind one `docker compose up`.

The home hero always shows the **latest ingested match** (by match date) — currently through the Round of 16.

## Features

- **96 matches ingested** from real FIFA PMSR PDFs — possession, phases, spatial, line breaks, final-third zones, defensive actions
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
| `make ingest` | Run the PDF drop-folder watcher in the ingestion container |
| `make test` | Run all test suites |
| `make contract` | Regenerate OpenAPI TypeScript types |
| `make fmt` | Format all code |
| `make logs` | Tail compose logs |

## PDF ingestion pipeline

### Ingest PDFs manually

Run from the `ingestion/` directory (the pipeline is `parse_pmsr.py` + `pmsr_to_sql.py`; the legacy `parse_efi_pdf` module has been removed):

```bash
cd ingestion

# Parse a single PDF to SQL, print to stdout
python -m ingestion.pmsr_to_sql path/to/Match_10_GER_CUR.pdf

# Parse all PDFs in a drop dir and regenerate the combined seed file
python -m ingestion.pmsr_to_sql --batch --data-dir path/to/pdfs --out ../db/seeds/04_all_matches.sql
```

### Automatic drop-folder watcher (cron / Phusion Passenger)

Set `PDF_WATCH_DIR` in `.env` to an absolute path:

```dotenv
# .env
PDF_WATCH_DIR=/home/myuser/efi_pdf_drop
```

Then add a cron job:

```cron
# Ingest new PDFs every 5 minutes (run from the ingestion/ package root)
*/5 * * * * cd /path/to/project/ingestion && python -m ingestion.watch_pdfs >> /var/log/efi_watch.log 2>&1
```

Flags: `--dry-run` (parse only), `--force` (re-process all), `--dir <path>` (override env).

## Verification

After `make up` and waiting for services to be healthy:

```bash
# DB seeded correctly
docker compose exec db mysql -uwc26user -pwc26pass wc26 \
  -e "SELECT COUNT(*) FROM teams; \
      SELECT match_no, match_date FROM matches ORDER BY match_date DESC LIMIT 1;"

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

## Documentation

Architecture, data model, API surface and conventions: see [DOCS.md](DOCS.md).
Deployment walkthrough: [DEPLOY.md](DEPLOY.md).
Pre-1.0 audit — security, correctness, accessibility (BFSG/WCAG 2.1 AA),
dependencies — with fixed and deferred findings: [AUDIT.md](AUDIT.md).

> **Accessibility note:** 1.0 fixes the critical keyboard and contrast issues but
> does **not** yet claim full BFSG/WCAG 2.1 AA conformance — see the tracked
> backlog in [AUDIT.md](AUDIT.md) §7.

## Stack

| Layer | Technology |
|-------|-----------|
| Database | MySQL 8.0 — 19 EFI tables, scope discriminator for match vs aggregate |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 |
| Ingestion | PyMuPDF (fitz), SQLAlchemy sync |
| Frontend | Node 20, SvelteKit, Svelte 5 runes, Bits UI |
| Design | Sports editorial design system — light/dark, CSS custom properties |
| i18n | 6-locale writable store (EN/DE/ES/PT/FR/AR), RTL Arabic |
| Testing | Vitest + happy-dom, pytest, Playwright e2e |
| Infra | Docker Compose, healthcheck-gated startup, Makefile |

## Routes

| URL | Description |
|-----|-------------|
| `/` | Overview — latest match, KPIs |
| `/matches` | All ingested matches, grouped by group/round |
| `/matches/[id]` | Full match detail — 7 EFI data sections |
| `/teams` | All 48 teams with stats |
| `/teams/[id]` | Team detail — aggregate stats + match history |
| `/players` | 1 248-player roster — searchable and filterable |
| `/phases` | Tournament progress — phases, KPIs |
