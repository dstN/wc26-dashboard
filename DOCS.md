# DOCS — EFI World Cup 26 Data Engine

Architecture and system documentation, reflecting the **actual state** of the codebase
(last synced 2026-07-05). Successor to the original design spec that lived in
`.claude/ARCHITECTURE.md` — the web-crawler pipeline described there was removed on
2026-07-04; PDF ingestion is the sole data path.

## 1. System overview

Full-stack data engine: a Python pipeline parses FIFA *Enhanced Football Intelligence*
(EFI) Post Match Summary Report (PMSR) PDFs into MySQL, FastAPI serves the data, and a
SvelteKit dashboard renders it.

| Layer | Technology |
| --- | --- |
| Ingestion | Python 3.10+, PyMuPDF (fitz), SQLAlchemy (sync, PyMySQL) |
| Database | MySQL 8.0 — 19 tables, `scope` discriminator (`match` vs `team_aggregate`) |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 async (asyncmy), Pydantic v2 |
| Frontend | Node 20, SvelteKit, Svelte 5 runes, Bits UI v2, hand-rolled SVG/CSS viz |
| i18n | 6 locales (EN · DE · ES · PT · FR · AR), RTL for Arabic, ~625 keys per locale |
| Infra | Docker Compose (db / backend / frontend + `ingest`/`test` profiles), Makefile |
| Production | Phusion Passenger + cron watcher + token-protected upload endpoint |

## 2. Data pipeline (PDF → MySQL)

The only sanctioned pipeline is `parse_pmsr.py` + `pmsr_to_sql.py`, orchestrated by
`watch_pdfs.py`. There is no web crawler.

```text
PMSR PDF (52–54 pages)
  └─ ingestion/ingestion/parse_pmsr.py    → structured dict (44 data pages)
      └─ ingestion/ingestion/pmsr_to_sql.py  → escaped SQL (INSERT … ON DUPLICATE KEY)
          └─ MySQL (direct execute via watch_pdfs, or seed file via --batch)
```

- **`parse_pmsr.py`** — coordinate-based PyMuPDF extraction of all PMSR pages.
  Handles variable page counts: extra shot-log pages are detected by scanning
  consecutive "Attempts at Goal" pages from `doc[17]` (`extra = 0/1/2/…`).
  `reclassify_red_cards()` turns orphaned sub-off markers (no matching sub-on
  within ±2 min) into red cards; a co-located yellow (±1 min) becomes
  `second_yellow`. **Do not change these business rules.**
- **`pmsr_to_sql.py`** — converts the parsed dict to SQL. All string values go
  through `_q()`/`_qs()` (quote escaping). A page-29 sentinel ("Defensive
  Pressure") fails loudly if page-shift detection misfired.
  CLI: `python -m ingestion.pmsr_to_sql <pdf>` (SQL to stdout) or
  `--batch --data-dir <dir> --out <file>` (combined seed, PDFs moved to `done/`).
- **`watch_pdfs.py`** — cron-compatible drop-folder watcher. Tracks processed
  files in `<watch_dir>/.processed_pdfs`. Flags: `--dry-run`, `--force`,
  `--dir <path>`, `--file <pdf>` (single-file mode, used by the upload endpoint).
  Reads `ingestion/.env`, falls back to the project-root `.env`.
  Run from the `ingestion/` directory: `python -m ingestion.watch_pdfs`.
- **`POST /api/v1/ingest/upload`** — Bearer-token-protected (constant-time
  compare against `INGEST_SECRET_KEY`); validates `%PDF-` magic bytes and a 50 MB
  limit; sanitizes the filename (basename + containment check); triggers
  `watch_pdfs --force --file <upload>` in a worker thread (180 s timeout);
  removes the PDF on failure so cron does not retry it forever.

## 3. Data model (19 tables)

Grouped by concern; every match-level table carries `scope`
(`match` | `team_aggregate`) and references `teams` / `matches`.

| Group | Tables |
| --- | --- |
| Core | `teams`, `matches` (incl. `formation_a/b`; `group_letter` holds `A`–`L` or knockout labels `R32/R16/QF/SF/3RD/FIN` — the Final uses `FIN`, never a bare `F`, to avoid colliding with group F; `went_to_extra_time` + `penalty_score_a/b` for knockout matches decided beyond 90') |
| Match stats | `match_stats` (possession, xG, shots, ball recovery), `match_phases` (17 phase names), `team_spatial_stats` (defensive + in-possession blocks, `width_m`), `line_breaks`, `final_third_entries`, `defensive_actions` (incl. blocks/contests breakdown, most-regains callout) |
| Event-level | `shot_events`, `passing_connections`, `cross_stats` |
| Aggregate detail | `match_offering_stats`, `match_movement_stats` (incl. pitch-third breakdown), `match_pressure_stats`, `match_gk_stats` (29+ GK fields incl. aerial/crosses-faced/intervention breakdowns), `match_set_play_stats` (corner delivery/zone breakdowns) |
| Players | `players` (48 squads), `player_stats` (60+ columns: passing, offers, OOP, distance zones, cards), `player_line_breaks` |

Notes:

- `final_third_entries` has **no PDF source page** — it is populated exclusively by
  `db/seeds/05_final_third_entries.sql` (idempotent via DELETE guard).
- Extra time / penalties: `score_a/score_b` already include extra-time goals.
  `went_to_extra_time` is derived in `parse_pmsr.py` from the lineup page's
  minute markers — this PDF format anchors normal-time stoppage at base
  minute 90 with a "+" suffix (e.g. `90+6'`), so any marker whose **total**
  minute (base + stoppage) reaches 105 is a genuine extra-time-period clock
  minute. `penalty_score_a/b` come from the page-1 parenthetical note (e.g.
  `(Paraguay win 3-4 on Penalties)` — home-away order, not winner-loser
  order) and are `NULL` unless a shootout occurred.
  `player_stats.minutes_played` uses 120 (not 90) as the final-whistle
  baseline for that match's starters/subs when `went_to_extra_time` is true.
- Seed order (initdb + `make seed`): `01_schema` → `02_match_10_ger_cur` →
  `03_team_aggregates` → `04_all_matches` (mysqldump of all ingested match data) →
  `05_final_third_entries`.

## 4. API surface (FastAPI, `/api/v1`)

| Prefix | Endpoints |
| --- | --- |
| `/matches` | `GET /` (list incl. formations), `GET /{id}`, per-match: `possession`, `phases`, `spatial`, `line-breaks`, `final-third`, `defensive`, `key-stats` (46 fields; GK intentionally excluded), `gk-stats`, `shots`, `passing-network`, `crosses`, `offerings`, `movement`, `pressure`, `lineup`, `player-name-map` |
| `/teams` | `GET /` (list + aggregate stats, goals computed from real scores), `GET /{id}/general`, `players`, `phases`, `matches`, `avg-stats` |
| `/players` | `GET /` (1 248-player roster), `GET /{id}` (totals + per-match), `GET /{id}/stats`, `GET /{id}/line-breaks` |
| `/stats` | `leaderboards` (scorers, cards, 48-team rankings), `player-stats-summary`, `goalkeeper-rankings` |
| misc | `GET /dashboard` (**latest match** by `match_date`, then `match_no` — matches the "Latest Match" hero label), `GET /overview` (computed live), `POST /contact` (SMTP, in-memory rate limit 3/IP/h), `POST /ingest/upload`, `GET /health`, `GET /health/db` |

Serialization rule: DB `DECIMAL` values are always converted (`float()`/`int()`/
Pydantic `float` fields) before JSON — string-serialized Decimals have caused
frontend `.toFixed()` crashes repeatedly.

**Tournament-stage filter**: `leaderboards`, `player-stats-summary` and
`goalkeeper-rankings` accept `?stage=group` / `?stage=knockout` (FastAPI
`Literal`, 422 on anything else; omit for all matches). Implemented once in
`backend/app/stage_filter.py` as a condition on `Match.group_letter`
(`char_length == 1` → group, `> 1` → knockout) and joined in wherever a query
aggregates `scope='match'` rows. The `/matches`, `/teams`, `/players` listing
pages expose this as an "All / Group Stage / Knockout" pill filter — client-side
on `/matches` (all matches already loaded), URL-param-driven
(`?stage=…`, triggers `+page.ts` reload) on `/teams` and `/players`. Frontend
mirror of the length convention: `frontend/src/lib/stage.ts`.

## 5. Frontend (SvelteKit, Svelte 5 runes)

- **Routes:** `/` (latest match + KPIs), `/matches`, `/matches/[id]` (17 parallel
  data fetches, all EFI sections), `/teams`, `/teams/[id]`, `/players`,
  `/players/[id]`, `/phases` (tournament progress, 104-match format),
  `/compare` (teams/players/matches, URL-serialised via `comparison.svelte.ts`
  store), `/admin` (key-protected PDF upload, not in nav), `/_kitchen-sink` (dev).
- **Conventions:**
  - Svelte 5 runes only (`$props/$state/$derived/$effect`, snippets) — no legacy
    syntax.
  - **No TS `as`-casts or type annotations in template markup** — they have broken
    the rollup SSR build twice; keep casts in the `<script>` block (helper
    functions / `$derived`).
  - `{@const}` only as immediate child of control blocks.
  - All user-facing strings via `$t.*` (`src/lib/i18n/{en,de,es,pt,fr,ar}.ts` —
    keep the six files structurally identical).
  - RTL: logical CSS properties (`inset-inline-*`, `border-inline-*`) or
    `[dir='rtl']` overrides; no hard `left`/`right` for direction-sensitive UI.
  - Design tokens in `app.css` ("Sports Editorial" system, light/dark via
    `data-theme`); text on light accent colors uses the `*-ink` /
    `--accent-fg` / `--tc-text` tokens, never plain white.
- **Testing:** Vitest + happy-dom (component tests), Playwright e2e via the
  compose `test` profile.

## 6. Local development

```bash
cp .env.example .env
make up          # db + backend + frontend (frontend on :5175, API on :8000)
```

| Target | Description |
| --- | --- |
| `make up` / `down` / `reset` | compose lifecycle (`reset` wipes the DB volume) |
| `make seed` | apply all seeds to the running DB |
| `make ingest` | run the PDF watcher inside the ingestion container |
| `make test` | frontend check/lint, backend pytest, e2e profile |
| `make contract` | regenerate OpenAPI TypeScript types |
| `make fmt` | ruff/black + prettier |

Ingestion tests: `cd ingestion && python3 -m pytest tests/` (watcher suite).

## 7. Production

Passenger-hosted; see `DEPLOY.md` for the full walkthrough. Required env:
`INGEST_SECRET_KEY`, `PDF_WATCH_DIR`, `INGESTION_PYTHON`, `INGESTION_MODULE_DIR`,
`MYSQL_*`, SMTP settings for `/contact`. Cron fallback:

```cron
*/5 * * * * cd /path/to/project/ingestion && python -m ingestion.watch_pdfs >> /var/log/efi_watch.log 2>&1
```
