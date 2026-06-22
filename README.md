# EFI World Cup 26 Data Engine

Portfolio-grade full-stack data engine: Python crawler ingests Enhanced Football Intelligence (EFI) data into MySQL, FastAPI serves it, and a Svelte 5 editorial dashboard renders it — all behind one `docker compose up`.

**Featured match:** Germany 7–1 Curaçao · Group E · Match 10 · Houston · 14.06.2026

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

## Verification

After `make up` and waiting for services to be healthy:

```bash
# DB seeded correctly
docker compose exec db mysql -uwc26user -pwc26pass wc26 \
  -e "SELECT COUNT(*) FROM teams; SELECT match_no,is_featured FROM matches WHERE is_featured=1; SELECT matches_played,goals_total,avg_in_contest_pct FROM tournament_overview;"

# API working
curl http://localhost:8000/health/db
curl http://localhost:8000/api/v1/matches/10/possession
curl -s http://localhost:8000/api/v1/dashboard | python3 -c "import sys,json; print(list(json.load(sys.stdin).keys()))"
```

## Stack

- **DB:** MySQL 8.0, 11 EFI tables, scope discriminator for match vs aggregate stats
- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0 async, Pydantic v2
- **Frontend:** Node 20, SvelteKit, Svelte 5 runes, Bits UI, Sports Editorial design system
- **Infra:** Docker Compose, healthcheck-gated startup
