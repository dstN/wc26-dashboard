# Roadmap — EFI WC26 Data Engine

## 1.0.0 — Pre-release audit & remediation (2026-07-11)

Five-track audit (Security · Backend/Ingestion correctness · Frontend
best-practice · Accessibility BFSG/WCAG 2.1 AA · Dependency currency). Full
record in [`AUDIT.md`](AUDIT.md). Verification: svelte-check 0/0 · build green ·
eslint green · vitest 10/10 · backend black/ruff green · backend pytest 10/10 ·
ingestion pytest 14/14 · fresh-volume seed boot clean · live smoke test green.
(Known gap: Playwright visual baselines need regeneration after the markup changes.)

**Fixed:**

- [x] **CRITICAL** production API base URL — `import.meta.env.PUBLIC_API_URL` is
  `undefined` in the browser; client-side nav fell back to localhost. New
  `$lib/api-base.ts` via `$env/dynamic/public`, applied to all 11 loaders + admin
- [x] Security: backslash SQL escaping (`_q`/`_qs` + `exec_driver_sql`); loopback
  DB/backend ports; upload `file.size` pre-check; contact control-char validator
  + SMTP timeout + `OSError`→502
- [x] Backend: `make contract` module-mode fix; locale-independent date parse
  (would break every ingest on the German host); `/health/db` 503; rewrote
  `test_matches.py` (had tested non-existent columns) → 10/10
- [x] A11Y: contrast `-ink` variants for teal/orange/red/blue/indigo + call-site
  fixes; keyboard-operable sortable headers (41) + compare ARIA combobox;
  `role="img"` removed from text figures; `aria-pressed`/`aria-current` on
  toggles/filters; skip link + `a11y.skipToContent` in 6 locales
- [x] Tooling: working ESLint flat-config gate (`npm run lint` was dead); dep
  floors for CVEs (`pymysql`, `python-multipart`, `cryptography`); `mysql:8.0.46`,
  Node 24 in CI/test container
- [x] Docs: new `AUDIT.md`; README/DEPLOY counts 88 → 96

**Backlog closed (second remediation wave):**

- [x] SSR `lang`/`dir` from an `efi-locale` cookie + `hooks.server.ts` (verified
  `ar` → `lang="ar" dir="rtl"`)
- [x] Live-region announcements (contact/admin forms, filter counts) + dialog names
- [x] Table semantics: real `<th>` in StatTable; ARIA table roles on
  KeyStats/ShotTimeline/Gk/Pressure/Defensive; PhaseFingerprint data-table + legend
- [x] Remaining hardcoded control labels + page titles → new `a11y.*` i18n namespace
  (671 keys/locale, parity verified); dead `NavTabs.svelte` removed
- [x] Backend data integrity re-ingested: `direction_*` NULLs fixed (192/192),
  sub-off minutes corrected
- [x] N+1 batching (`/stats/leaderboards`, `/teams/{id}/avg-stats`, `/matches`);
  `response_model` on `/overview`; Python deps pinned; `npm update` (safe minors)
- [x] UI: filter active-state specificity, mobile scoreline stacking, header
  right-alignment, players search moved above rankings
- [x] DEPLOY.md rewritten (DAU step-by-step) + shared deployment artifact synced
- [x] vitest suite: `npm run test` was `--project logic` (no such project → 0
  files, exit 1) → `vitest run`; StatTable/PossessionBar tests updated for the
  new a11y markup — **10/10 green**
- [x] Fresh-volume boot verified (`down -v && up`, seeds 01→05 clean) — proves
  the corrected pressure-directions/minutes data shipped in the regenerated seed

**Still deferred (tracked in `AUDIT.md` §7):**

- [ ] Extra-shot-log page attribution (B-D2) — high-risk parser rewrite
- [ ] A11y long tail: `aria-sort`, players tablist keyboard model, mobile-menu
  focus trap; composite endpoint response models
- [ ] Post-1.0 dep majors: mysql 8.4 LTS, vite 8 + vitest 4, eslint 10 / TS 7

**Conformance:** substantially WCAG 2.1 AA — Critical/High failures fixed; formal
BFSG certification needs an external audit of the long tail. See `AUDIT.md` §7.

## Round of 16 ingest (2026-07-08)

- [x] 8 R16 PDFs ingested (matches 89–96): Paraguay–France, Canada–Morocco, Brazil–Norway,
  Mexico–England, Portugal–Spain, USA–Belgium, Argentina–Egypt, Switzerland–Colombia —
  8/8 OK, all correctly labeled `R16` (first live use of that adapter mapping since it
  was added for R32)
- [x] First live end-to-end verification of the AET/penalty feature (added 2026-07-05 but
  untested against a real shootout until now): Switzerland–Colombia finished 0–0, AET,
  4–3 on pens — home hero and `/matches/555` both render the "AET" badge and "4-3 pens"
  correctly, `GET /overview` `stage_counts.R16` = 8
- [x] `db/seeds/04_all_matches.sql` regenerated (96 matches); 8 PDFs moved to
  `.claude/data/done/` (now 96)
- [x] Deploy-doc floors bumped `≥ 88` → `≥ 96` in DEPLOY.md **and** the shared
  artifact (done 2026-07-11, 1.0.0 wave 2)

## Deployment docs synced with is_featured/tournament_overview teardown (2026-07-06)

- [x] `DEPLOY.md`: removed the deleted `db/seeds/05_featured_match.sql` from the seed
  import list and the `02→03→04→05→05b` checklist order; expected-count floors bumped
  from the pre-R32-ingest `≥ 40 Matches` to `≥ 88 Matches` (48 teams is still exact)
- [x] Shared Claude artifact deployment guide (`claude.ai/code/artifact/5abcff1b-…`)
  synced the same seed/count fixes, plus two issues only present there: the
  "Datenbank direkt" verification query still selected `WHERE is_featured = 1` and
  `FROM tournament_overview` (both dropped in the earlier teardown) — replaced with
  a query for the actual latest match (`ORDER BY match_date DESC, match_no DESC`)
  including the new `went_to_extra_time`/`penalty_score_*` columns, with a note that
  tournament-wide KPIs are now computed live via `GET /api/v1/overview`. Also fixed
  a pre-existing (unrelated to this session's changes) doc bug: the `/health/db`
  example response showed `{"db":"ok","teams":48}`, but `backend/app/routers/health.py`
  has only ever returned `{"status":"ok"}`.

## Match detail polish + team-color bug fix (2026-07-05)

- [x] Match detail: Phase Fingerprint + Shot Log combined into one two-col row (was two full-width sections, Fingerprint only needs ~480px)
- [x] Shot log jersey-number/name whitespace bug fixed (Svelte trims whitespace at `{/if}` block boundaries — built the label as a plain string in the script block instead)
- [x] Team-color text bug: `PhasesBar`, `PitchSpatial`, `SpatialMobilePicker` used `teamColorVar()` (raw brand color, background-only) as `color:` for text — washed-out/pale for light team colors (yellow/lime/lavender/pink), fine for dark ones, hence "sometimes matches the badge, sometimes doesn't". Switched to `teamTextColor()` (the ink-adjusted variant already used correctly elsewhere); `PhasesBar` had imported `teamTextColor` and never called it
- [x] Goalkeepers now clickable in the `/players` Goalkeepers tab — `GET /stats/goalkeeper-rankings` resolves `player_id` via a `(gk_name, team_id)` → `players` join (0 unmatched across 176 rows)
- [x] Player detail match history now links to `/matches/{id}` and shows "Group J · Match 19" instead of bare "Match #74" — `GET /players/{id}` and `GET /players/{id}/line-breaks` now return `match_id` + `group_letter`
- [x] `.pr__callout` / `.dd__callout` colored-left-border stat cards replaced with the app's established plain-card style (`var(--surface)` + `var(--border)` + `var(--shadow-card)`) plus a colored dot next to the name, reusing the existing legend-swatch idiom instead of a new pattern
- [x] Checked SVG `<text fill=…>` usages for the same `teamColorVar`-as-text mistake — none found; PhaseFingerprint's polygon `fill`/`stroke` uses are legitimate shape-fill usage, not text

## Group Stage / Knockout stats filter (2026-07-05)

- [x] `stage=group|knockout` query param added to `GET /stats/leaderboards`, `GET /stats/player-stats-summary`, `GET /stats/goalkeeper-rankings` (shared `backend/app/stage_filter.py`, condition on `Match.group_letter` char length — no hardcoded letter lists)
- [x] `/matches` — client-side "All / Group Stage / Knockout" pill filter (reuses already-loaded `group_letter`); resets the per-round dropdown on stage change
- [x] `/teams`, `/players` — same pill filter as URL param (`?stage=…`, bookmarkable, reuses the `/compare`-style URL-driven load pattern); covers every ranking tab/table on both pages
- [x] Dropped `teams/+page.ts`'s unused `GET /teams/` fetch while touching that loader (confirmed zero consumers on the page)
- [ ] Not extended to `/teams/[id]` or `/players/[id]` detail pages (out of scope for this request — those show one entity's full history, not a filterable ranking) — revisit if requested

## Extra time (AET) + penalty shootout display (2026-07-05)

- [x] `matches.went_to_extra_time` / `penalty_score_a/b` added (schema + `Match` model + `MatchMeta` schema at all 4 construction sites). Detected in `parse_pmsr.py` from lineup-page minute markers (total minute ≥ 105 = genuine extra time — empirically separates all 16 R32 PDFs correctly); penalty score parsed from the page-1 `(Team win X-Y on Penalties)` note (home-away order, verified against all 3 known shootouts)
- [x] Fixed a real bug found along the way: `player_stats.minutes_played` was hardcoded to a 90-minute baseline regardless of extra time — undercounted every unsubbed player in the 5 ET/penalty matches by up to 30 minutes. Now uses 120 when `went_to_extra_time`. All 88 matches re-ingested, dump regenerated
- [x] `/matches`, home page, match detail, team-detail match history, and `/compare` match entity header all show "AET" / "3-4 pens" — verified live via SSR HTML on every surface
- [x] Correctness fix: team-detail match history win/draw/loss badge used raw score comparison, showing "D" (Draw) for penalty-shootout matches instead of the actual W/L outcome. Now uses `penalty_score_a/b` when present
- [x] Drive-by: match detail page + team-detail match history still showed raw "Group R32" (never got the `groupHeading()` round-name treatment applied to `/matches` and home page during the earlier F/FIN fix) — fixed with the same local-helper pattern
- [ ] Not extended to the `<title>` tag on the match detail page (still shows bare "GER 1:1 PAR", no AET/pens suffix) — cosmetic, low priority

## Tournament page stage-counting fix (2026-07-05)

- [x] `/phases` page was rendering R32 matches as group-stage matches: `GET /overview` returned one global `matches_played` count, divided by hardcoded thresholds that assumed strictly-sequential bracket ingestion. `overview_service.get_overview()` now returns `stage_counts` (GROUP BY `group_letter`, bucketed group vs. R32/R16/QF/SF/3RD/FIN); `/phases` shows real per-stage `played/total` progress bars instead of "available from match N" guesses. Verified live: group 72/72, R32 16/16, rest 0.
- [ ] `GET /dashboard`'s `TournamentOverviewSchema` (home hero KPIs) does not carry `stage_counts` — fine today since the home page doesn't render phase progress, but keep in mind if that ever changes.

## Hotfixes after the R32 ingest (2026-07-05)

- [x] Hero/"Latest Match" fixed: `get_latest_match_id()` orders by `match_date DESC, match_no DESC` (audit change had pinned the seeded GER–CUR showcase match under a label that says "Latest") — hero now shows Match 88
- [x] Knockout round labels: `matches.group_letter` → `VARCHAR(3)`, adapter maps stages to `R32/R16/QF/SF/3RD/F`, matches 73–88 backfilled, matches page + home band render round names via `$t.tournament.*` (groups A–L first, rounds in bracket order); dump regenerated
- [x] `Match.is_featured` + `tournament_overview` REMOVED (2026-07-05, user-approved via explicit confirmation after the auto-mode classifier initially blocked the DDL): live `ALTER TABLE matches DROP COLUMN is_featured` + `DROP TABLE tournament_overview` applied; removed from `01_schema.sql`, `models/match.py`, `models/tournament.py` (deleted), `models/__init__.py`, `pmsr_to_sql.py` INSERT, `backend/tests/factories.py`; `05_featured_match.sql` deleted; `04_all_matches.sql` re-dumped (10 values/row, was 11) and idempotency-verified against the live DB

## Docs + Matches 73–88 (2026-07-05)

- [x] `DOCS.md` (repo root) — architecture doc rewritten to the actual state; superseded `.claude/ARCHITECTURE.md` (still described the removed web crawler) deleted; README links `DOCS.md`/`DEPLOY.md` and stale facts fixed (36→88 matches, `/tournament`→`/phases`)
- [x] 16 new PDFs ingested via the rewired `watch_pdfs.py` (16/16 OK incl. one 54-page PDF) — DB at **88 matches**; all new-match endpoints verified live
- [x] `04_all_matches.sql` regenerated as `REPLACE INTO` dump without `final_third_entries` — re-runnable AND no longer collides with the 02/03 team seeds on fresh initdb (defuses part of the open fresh-volume item); idempotency verified by re-applying to the live DB

## Deep Codebase Audit ✅ REMEDIATED (2026-07-04)

Full-stack audit (Svelte 5 compliance, i18n/RTL, security, async hygiene, N+1,
deprecated-pipeline references) with autonomous remediation — details in CHANGELOG.
Verification: svelte-check 39 errors/18 warnings → 0/0 · vitest 10/10 · pytest 38/38 ·
production build green · live API smoke tests green.

**Fixed in this sweep:**

- [x] `watch_pdfs.py` rewired from deprecated `parse_efi_pdf` to sanctioned `parse_pmsr + pmsr_to_sql` (cron AND upload endpoint ran the legacy parser)
- [x] README manual-ingestion + cron instructions corrected (deprecated module, wrong cwd)
- [x] Upload endpoint hardened: path traversal, timing-safe token compare, `%PDF-` magic bytes, non-blocking subprocess/file-IO, failed-PDF cleanup, per-file `--file` processing
- [x] Contact rate-limiter unbounded-growth leak fixed (full sweep, key deletion)
- [x] Last Decimal→JSON-string leak (`GET /teams/` `goals_a`) + missing `scope='match'` filter (`/players/{id}/stats`) + dashboard 500s on empty DB → clean 404
- [x] N+1: `GET /matches/` (2N+1→2), `GET /teams/` (2N+1→3)
- [x] All TS `as`-casts out of template markup (SSR-breaker pattern); bits-ui v2 `asChild` leftovers removed; `MatchMeta` type synced (nullable scores + formations)
- [x] i18n: duplicate `finalThird` key (all 6 locales), 11 missing keys in 5 locales, `/admin` page (was hardcoded German), `/compare` match metrics + FloatingCompareBar (were hardcoded English), a11y labels — 29 new keys × 6 locales
- [x] RTL: TopBar active indicator + Footer dialogs converted to logical properties

**New technical debt identified (deferred):**

- [x] N+1 remainders RESOLVED (2026-07-11, 1.0.0 wave 2): `/teams/{id}/avg-stats`
  (6/match → 6 total), `/stats/leaderboards` team rankings (~190 → 3),
  `/teams/{id}/matches` (3/match → 2) — output byte-identical (hash-verified)
- [x] Legacy crawler modules REMOVED (2026-07-04): 9 crawler modules + `parse_efi_pdf.py` + 3 test files + fixtures + `scripts/crawl_efi.py` deleted; `make crawl` → `make ingest`; Dockerfile slimmed (no chromium/playwright); `requirements.txt` 15 → 6 deps (+ previously undeclared `python-dotenv`)
- [ ] Contact rate limiter is per-process and sees the proxy IP behind Passenger/reverse proxy (no `X-Forwarded-For` handling) — whole site shares one 3/h budget
- [ ] `watch_pdfs.py`: no lockfile against overlapping cron runs; permanently failing PDFs are retried every 5 min (no quarantine/dead-letter)
- [x] `_q()`/`_qs()` backslash escaping FIXED (2026-07-11, 1.0.0 wave 1) +
  `exec_driver_sql` so `:word` tokens aren't reinterpreted as bind params
- [x] Upload size RESOLVED (2026-07-11): rejects on declared `file.size` before
  reading the body into RAM
- [x] `is_featured` RESOLVED (2026-07-04): column wired into `get_featured_match_id()` (featured GER–CUR match actually featured again); dead query param removed from backend + frontend
- [x] Stale seeds RESOLVED (2026-07-04): `02_teams_ger_cur.sql` (empty stub) deleted. `05_final_third_entries.sql` turned out NOT to be a duplicate — it is the sole data source and was missing from the seed pipeline entirely (live DB had 0 rows, FinalThirdZones empty). Now mounted in initdb + `make seed`, idempotent via DELETE guard, applied live (400 rows)
- [x] Dead frontend code REMOVED (2026-07-04): `lib/api/{client,endpoints}.ts` (zero consumers), 5 unreferenced M8 modules (`EfficiencyMatrix`, `RiskReward`, `PressingEngine`, `PenetrationMap`, `ControlVsChaos`), 30 never-rendered `gk_*` fields in `KeyStatsTable` + the matching dead GK block (2 queries, 30 fields) in `GET /matches/{id}/key-stats`

## Feature Ideas (backlog)

### Full i18n Translation Coverage ✅ COMPLETE (Sessions 19–21 — 2026-07-03)

All hardcoded English strings across all route pages and viz components replaced with reactive `$t.*` keys. The dashboard is now fully translatable across EN/DE/ES/PT/FR/AR without any English fallback strings leaking through.

**Delivered (Session 19):**
- `teams/[id]` — Performance Trend, Top Performers, Match Stats grid (7 groups, 34 stat labels), Squad section, POS_LABEL, mode toggle, summary stats
- `matches/[id]` — Spatial "In/Out of Possession" section labels, line break labels
- `compare` — Full TEAM_METRICS (25 Avg… labels) and PLAYER_METRICS (33 player stat labels)
- `StatTable` — Head-to-head stat labels (Goals, xG, Possession, In Contest, Ball Recovery, xG/Shot, Efficiency, Out of Possession, HEAD-TO-HEAD)
- `CrossesDetail` — Delivery type labels (Inswing, Outswing, Driven, Lofted, Cut-back, Push Cross) + zone labels (Left, C-Left, C-Right, Right) + section titles
- `DefensiveDetail` — 14 stat row labels across Tackles, Blocks, Contests sections
- `PressureDetail` — 9 pressure stat labels including direction labels
- `OfferingsDetail` / `MovementDetail` — pitch zone and phase type labels
- `LineBreaksBars` — Defensive/Midfield/Attacking line labels
- `GkDetail` — 4 section headers + 20 goalkeeper stat row labels (Activity, Shot Stopping, Aerial Actions, Crosses Faced sections)
- 120 new i18n keys (32 `teams.*`, 53 `detail.*`, 35 `compare.*`) × 6 locales = 720 entries

**Delivered (Session 20):**
- `PhasesBar` — "IN POSSESSION" / "OUT OF POSSESSION" headers + all 17 tactical phase names via `PHASE_KEYS` lookup
- `PitchSpatial` + `SpatialMobilePicker` — block-type toggles, scenario tabs, KPI labels
- `ShotTimeline` — column headers (Min/Player/Body/Delivery/Outcome) + outcome chips
- `PhaseFingerprint` — radar spoke labels for 6 in-possession phases
- `teams/[id]` phase bars — phase names translated via `PHASE_KEYS`
- New `phases.*` namespace (19 keys) + 19 `detail.*` keys (shot/spatial/KPI) × 6 locales = 234 entries
- RTL fix: teams detail flag watermark now mirrors correctly in Arabic (`[dir='rtl']`)

**Delivered (Session 21):**
- `MovementDetail`, `OfferingsDetail`, `PressureDetail`, `DefensiveDetail`, `LineBreaksBars`, `FinalThirdZones` — all remaining hardcoded EN strings replaced with `$t.*` keys
- Fixed pre-existing duplicate `detail.finalThird` key in `en.ts`; added `detail.finalThirdEntries` and updated `matches/[id]` section label
- 20 new `detail.*` keys × 6 locales = 120 new entries

---

### PDF-Ingestion in Produktion ✅ COMPLETE

Automatisches Parsen und DB-Import von neu hochgeladenen EFI-PDFs unter Phusion Passenger.

**Geliefert:**
- `POST /api/v1/ingest/upload` — Bearer-Token-gesicherter Endpoint, nimmt PDF entgegen, triggert `watch_pdfs.py` als Subprocess
- `/admin/upload` — Admin-Formular im Frontend (nicht im Nav, Key-geschützt)
- Cron-basierter Fallback über bestehende `watch_pdfs.py` — via Hosting-Panel alle 5 Min. einrichten

**Deployment-Schritte (Produktion):**
1. `INGEST_SECRET_KEY` in `.env` setzen (`openssl rand -hex 32`)
2. `PDF_WATCH_DIR`, `INGESTION_PYTHON`, `INGESTION_MODULE_DIR` in `.env` setzen
3. Cron-Job im netcup/Plesk-Panel einrichten:
   `*/5 * * * * cd /pfad/projekt/ingestion && /pfad/.venv/bin/python -m ingestion.watch_pdfs >> /var/log/efi_watch.log 2>&1`

---


### Comparison view — teams & players side-by-side ✅ COMPLETE

All three sessions delivered. Full feature shipped in Sessions 25 A/B/C + Session 26 polish.

**Delivered:**
- Shared comparison store + URL param serialisation + checkbox/cmp-button UI on all three listing pages (teams, players, matches) with SVG checkmark
- `/compare` route — team, player, and match comparison with column layout + proportional bar charts + search/autocomplete
- Player entity header fix (API nesting `entity.player`), team name inline with flag+badge
- TEAM_METRICS: 22 rows across 5 groups; PLAYER_METRICS: 33 rows across 5 groups
- `MatchStatsSchema` extended to expose `shots_total` + `shots_on_target`
- Polish: empty/loading states, one-entity message, no-type landing with pick cards

**Remaining (future):**
- Match entity header improvements (team names as links)
- Shareable URL copies to clipboard (currently URLs are already shareable)

---

## Golden Plate V1

### M0 — Infra/Docker skeleton

- [x] `docker-compose.yml` (db + backend + frontend + ingestion profile + test profile)
- [x] `.env.example`
- [x] `Makefile` (up/down/reset/seed/crawl/test/contract/fmt/logs)
- [x] `README.md` (quickstart + verification)
- [x] `scripts/wait-healthy.sh`
- [x] `ROADMAP.md` + `CHANGELOG.md`
- [x] `.github/workflows/ci.yml` (lint + test stubs)

### M1 — DB schema

- [x] `db/init/01_schema.sql` — 11 tables, scope discriminator, match_key generated column

### M2 — Seed + Crawler

- [x] `db/seeds/02_match_10_ger_cur.sql` — GER/CUR anchor team inserts (IDs 1 & 2) + tournament placeholder
- [x] `db/seeds/03_team_aggregates.sql` — all 46 remaining WC2026 teams + aggregate stats
- [x] `db/seeds/04_all_matches.sql` — 36 matches from PDF parser (auto-generated by `pmsr_to_sql.py`)
- [x] `db/seeds/05_featured_match.sql` — marks GER 7–1 CUR as featured showcase match
- [x] `ingestion/ingestion/parse_pmsr.py` — FIFA PMSR PDF parser (PyMuPDF, 44-page coverage)
- [x] `ingestion/ingestion/pmsr_to_sql.py` — adapter: PDF → SQL for all 7 DB tables
- [x] All 36 available match PDFs processed and seeded into DB
- [x] ~~Full crawl verification in live Docker environment~~ — obsolete: web crawler removed 2026-07-04; PDF pipeline is the sole ingestion path

### M3 — FastAPI backend

- [x] `backend/app/main.py` — FastAPI app, CORS, all routers
- [x] `backend/app/models/` — SQLAlchemy 2.0 ORM (11 tables)
- [x] `backend/app/schemas/` — Pydantic v2 schemas
- [x] `backend/app/routers/` — health, matches, teams, dashboard, players, overview
- [x] `backend/app/services/match_service.py` — team→a/b transpose
- [x] `backend/tests/` — pytest + testcontainers

### M4 — Frontend scaffold + tokens + theme + primitives

- [x] SvelteKit, Svelte 5 runes, adapter-node, npm
- [x] `src/app.html` — no-flash theme, Lexend
- [x] `src/app.css` — all design tokens
- [x] `src/lib/types/efi.ts` — TypeScript contract
- [x] `src/lib/theme/theme.svelte.ts` — rune store
- [x] Primitive components (RainbowRail, SectionLabel, Badge, KpiStat, Card, StripeMotif)
- [x] Layout components (TopBar, NavTabs, ThemeSwitch, TermTooltip)

### M5 — Viz components

- [x] PossessionBar (3-seg + hatch)
- [x] StatTable (semantic table, team colours)
- [x] PitchSpatial (CSS pitch + ToggleGroup)
- [x] PhasesBar (stacked segmented bars)
- [x] LineBreaksBars (horizontal progress bars)
- [x] FinalThirdZones (5 vertical zone bars)

### M6 — Compose Übersicht page (fixtures)

- [x] `+layout.svelte` — RainbowRail + TopBar + NavTabs + Tooltip.Provider
- [x] `+page.svelte` — 6 sections, fixture data

### M7 — Wire live `load`

- [x] `+page.ts` — SvelteKit load → GET /api/v1/dashboard
- [x] `src/lib/api/client.ts` — env-aware (INTERNAL/PUBLIC)

### M8 — Analytical modules + full crawl

- [x] EfficiencyMatrix (xG vs Goals scatter)
- [x] RiskReward (quadrant scatter)
- [x] PressingEngine (turnovers vs recovery)
- [x] PhaseFingerprint (radar)
- [x] PenetrationMap (entry channel bars)
- [x] ControlVsChaos (possession vs in-contest)
- [x] ~~Full 48-team crawl integration~~ — obsolete: web crawler removed 2026-07-04; all 48 teams covered via PDF seeds

### M9 — Harden + verify

- [x] Vitest browser tests (viz components)
- [x] Playwright e2e (dashboard, theme, responsive)
- [x] axe a11y (zero violations, both themes)
- [x] Visual regression baselines
- [x] pytest backend suite (testcontainers)
- [x] CI full pipeline green
- [ ] Contract drift gate (openapi-typescript diff)

## Post-M9 — Data pipeline hardening

- [x] PDF ingestion pipeline: `parse_pmsr.py` (PyMuPDF) + `pmsr_to_sql.py` adapter
- [x] All 36 WC2026 group-stage match PDFs seeded; correct team/phase/spatial/line-break data
- [x] Phase names corrected in `PhaseFingerprint.svelte` to match real PDF values
- [x] Seed 02 cleaned — removed 46 wrong placeholder teams; real 48-team list authoritative
- [x] `.gitignore` hardened — env files, node_modules, PDF binaries, db_data excluded
- [x] Schema: `UNIQUE KEY uq_player (team_id, jersey_number)` added to `players` table
- [ ] `npm install` / `pip install` in CI (dependencies not yet verified in fresh container)
- [x] Live Docker run with fresh volume VERIFIED (2026-07-11): `down -v && up`
  loads seeds 01→05 clean — 48 teams · 96 matches · 1248 players · 192/192
  pressure directions non-null · AET match renders
- [x] `parse_efi_pdf.py` deprecation — `DeprecationWarning` added; docstring updated to redirect to `parse_pmsr.py + pmsr_to_sql.py`

## Post-M9 — Full dashboard build-out (Session 1)

- [x] English localisation: all German placeholder text replaced
- [x] Clickable match cards → `/matches/[id]` detail pages (7 EFI data sections per match)
- [x] Clickable team cards → `/teams/[id]` detail pages (stats + match history)
- [x] Player roster page `/players` — 1 248 players, search/filter, mobile-responsive
- [x] Tournament progress page `/tournament` — KPI strip + phase unlock cards
- [x] StatTable surfaced on every match detail page (was kitchen-sink only)
- [x] FinalThirdZones surfaced on every match detail page (was kitchen-sink only)
- [x] i18n system: EN · DE · ES · PT · FR · AR (6 locales, RTL Arabic)
- [x] Responsive design: hamburger nav, fluid grids, 400px floor
- [x] Vitest config fixed (happy-dom); all 10 frontend tests green
- [x] PDF drop-folder watcher (`watch_pdfs.py`): cron-based, `PDF_WATCH_DIR` env variable
- [x] 14 unit tests for PDF watcher (`test_watch_pdfs.py`)

## Post-M9 — Full dashboard build-out (Session 2)

- [x] Team detail page: phase profile section (avg % bars, in/out possession groups)
- [x] Team detail page: squad section (players grouped GK/DF/MF/FW with jersey numbers)
- [x] Team detail page: flag watermark in header, responsive CSS
- [x] Team cards: flag watermark (15% opacity, right side) via `flag-icons` v7.5.0
- [x] 48-team unique color assignment — no match-pair color collisions
- [x] Yellow/lime/lavender/pink contrast fix — `*-ink` variants for light mode
- [x] `teamTextColor()` applied to StatTable, PossessionBar, match/team detail pages
- [x] `tokens.ts` phase name map corrected to real DB values
- [x] `PhasesBar` redesigned: track background, segment labels, two-column legend
- [x] `final_third_entries` seeded for all 40 matches (5 zones × 2 teams × 40 = 400 rows)
- [x] `FinalThirdEntrySchema` serialises as `count` (was `entry_count`, breaking frontend)
- [x] 4 new match PDFs ingested (Matches 37–40); `04_all_matches.sql` now covers 40 matches
- [x] i18n error namespace added to all 6 locales; all raw `{data.error}` renders replaced
- [x] Goals `team_aggregate` now computed dynamically from actual match scores
- [x] Players page 500 fixed (`{@const}` placement)
- [x] "GER vs Germany" match history display fixed

## Post-M9 — Full dashboard build-out (Session 3)

- [x] `GET /api/v1/stats/leaderboards` — top scorers, most carded, full 48-team rankings
- [x] `GET /api/v1/stats/player-stats-summary` — aggregated stats for all 1 248 players
- [x] `PlayerStat` ORM model synced with DB schema (was missing goals/cards/minutes columns)
- [x] Player stats chips on every player card (goals, yellow/red, appearances)
- [x] Team rankings + group comparison section on teams page
- [x] Top scorers + position comparison sections on players page
- [x] i18n `stats` namespace (28 keys) added to all 6 locales
- [x] `nav.stats` removed — comparative stats live on teams/players pages, not separate route

## Post-M9 — Full dashboard build-out (Session 4)

- [x] Extended stats pipeline: parser → `pmsr_to_sql.py` → DB → ORM → API → frontend
- [x] 26 new `player_stats` columns (passing, offers, defensive, physical) from PDF pages 42–51
- [x] `match_gk_stats` table + ORM model (7 GK metrics from PDF pages 31–37)
- [x] `match_set_play_stats` table + ORM model (7 set play metrics from PDF pages 39–40)
- [x] `shots_total` / `shots_on_target` added to `match_stats` (PDF page 14/16)
- [x] `04_all_matches.sql` regenerated: 4 937 `UPDATE player_stats` statements, 80 GK rows, 80 set play rows
- [x] `GET /api/v1/matches/{id}/key-stats` — aggregates 36 metrics from 6 DB tables
- [x] `GET /api/v1/players/{player_id}` — full player profile with totals + per-match breakdown
- [x] `PhasesBar` completely rewritten with butterfly/mirror layout (matches PDF visual)
- [x] `/stats` route removed — per user request; stats live on teams/players pages
- [x] Stats nav item removed from TopBar

## Post-M9 — Full dashboard build-out (Session 5)

- [x] `KeyStatsTable` component: 36-metric grouped stats table replacing old 8-row StatTable
- [x] Match detail page now shows ALL key stats (goals, xG, shots, passes, line breaks, crosses, ball progressions, forced turnovers, tackles, interceptions, blocks, clearances, regains, pressing, duels, distance + GK section + Set Plays section)
- [x] `/players` redesigned as ranking landing: 5 position tabs, position-specific sort metrics
- [x] `/players/[id]` detail page: flag/badge header, tournament totals cards, match-by-match overview table, full per-match stat blocks with all 26 new stats
- [x] `/teams` redesigned: sortable comparison ranking table above team cards with CTA banner
- [x] Team names in ranking table link to `/teams/[id]`
- [x] `LineBreaksBars` rewritten with butterfly layout: completed/attempted + % + bars mirror view
- [x] `ball_progressions` added to `GET /api/v1/stats/player-stats-summary`

## Post-M9 — Full dashboard build-out (Session 6)

- [x] Parser bug: stoppage-time goals (e.g. "90+3'") now parsed as base+extra minutes, not just base
- [x] Parser bug: high-scoring matches (extra=1 shot-log pages) now include home team's page 2 in goal lookup
- [x] Seed SQL corrected: Undav 3 goals total (2 vs CIV + 1 vs CUR); Havertz 2 goals vs CUR; Brown 1 goal vs CUR
- [x] DB patched live: all wrong goal/card assignments corrected for GER matches 10 and 33
- [x] KeyStatsTable: double HR between sections removed (was border-bottom + border-top stacking)
- [x] Teams page: redundant team cards removed; ranking table with nation links is the entry point
- [x] PitchSpatial: team block region added (shaded defensive_line_height → +team_length); labels updated

## Post-M9 — Full dashboard build-out (Session 7)

- [x] Players page: "Top Scorers" → "Top Goals"; Assists column removed (not in PDF data)
- [x] Players page: sortable column headers on all 5 ranking tables (labels = sort buttons)
- [x] Players page: tab scrollbar hidden
- [x] Teams page: sort direction toggle (ASC/DESC) on ranking sort pills
- [x] Teams: avg xG fixed — now computed from per-match rows (team_aggregate had 0 xG for all teams)
- [x] Team detail: deep match stats section with all aggregated metrics + Avg/Total toggle
- [x] Team detail: match history xG/possession fix (always use `xg_a`/`possession_team_a`)
- [x] PitchSpatial: fully rewritten — two independent vertical pitches, each with own toggle
- [x] Player/squad appearances chip: guard on `minutes_played > 0` instead of `appearances > 0`
- [x] Reports badge: dynamic from `/api/v1/matches/` via `+layout.ts`; shows 40 not 36
- [x] i18n: players page tab labels wired to translation keys

## Post-M9 — Full dashboard build-out (Session 10)

- [x] 6 new DB tables: `shot_events`, `passing_connections`, `cross_stats`, `match_offering_stats`, `match_movement_stats`, `match_pressure_stats`
- [x] `defensive_actions` +13 columns; `match_set_play_stats` +13 corner columns; `player_stats` +15 columns
- [x] `pmsr_to_sql.py`: full ingestion for all 6 new tables + extended INSERT/UPDATE for existing tables
- [x] 40 PDFs re-ingested: 920 shot events, 396 passing connections, 80 rows each in new tables
- [x] Backend: 6 new ORM models, 6 new Pydantic schema files, 6 new API endpoints
- [x] Frontend: 6 new viz components — `ShotTimeline`, `PassingNetwork`, `CrossesDetail`, `OfferingsDetail`, `MovementDetail`, `PressureDetail` — wired into match detail page
- [x] Match detail page: 4 new layout sections (Shot Log, Passing Network + Pressure, Crosses + Offerings, Movement) with 14 parallel data fetches
- [x] Docker: frontend port changed to `5175` (avoids ddev-router conflict on 5173–5174)

## Post-M9 — Full dashboard build-out (Session 8)

- [x] Spatial Control: in-possession data (pages 6/7) now stored in DB and shown in UI — DB schema extended (block_type enum + width_m column); 240 rows backfilled for 40 matches — `GET /api/v1/matches/{id}/spatial` returns `{ defensive: [...], possession: [...] }` split — `PitchSpatial.svelte`: "Out of Possession" / "In Possession" scenario tabs; width shown on block
- [x] Overview API: now computes match count, goals, avg in-contest dynamically (was stale cache at 36) — Hero section and Tournament page now show correct count (40)
- [x] Badge component: lavender/pink now get dark text (`#0c1a10`) — was white-on-light (invisible)
- [x] Players/team detail: appearances chip guard changed to `minutes_played > 0`
- [x] i18n: 23 new keys in `players` namespace across all 6 locales; all 5 tables fully translated

## Next steps — Golden Plate V2

### Bug — Match detail page mobile layout ✓ fixed

- [x] **Two-column stat sections** — `.two-col` collapses to single column at 1024px; `.two-col__cell` padding drops to `var(--sp-4)` at 720px
- [x] **PitchSpatial** — desktop two-pitch layout hidden ≤600px; `SpatialMobilePicker` single-pitch shown on mobile (Session 21)
- [x] **ShotTimeline** — 4th column hidden at 720px; 3rd column hidden at 520px
- [x] **PassingNetwork** — `.pn` collapses to `grid-template-columns: 1fr` at 720px
- [x] **Score header** — `flex-wrap: wrap` on scoreline; team name hides at 480px; score font shrinks at 720px and 480px
- [x] **Section body padding** — drops from `var(--sp-8)` to `var(--sp-4)` on `.section-body`, `.match-header`, `.two-col__cell` at 720px

### Bug — Mobile navigation menu ✓ fixed

- [x] **Offcanvas overlay** — `.mobile-menu` converted to `position: fixed; top: 57px; left/right: 0; bottom: 0; z-index: 150; overflow-y: auto` with `animation: menu-in 0.18s ease` (fade + 6px translateY slide)
- [x] **Hamburger → X animation** — `.topbar__burger--open` class added when `menuOpen`; CSS transforms rotate bar 1 to +45°, fade+scale bar 2 to 0, rotate bar 3 to −45°; all bars use `transition: transform 0.22s ease, opacity 0.22s ease`

### Bug — TermTooltip / popover issues ✓ fixed

- [x] `avoidCollisions={true}` + `collisionPadding={12}` on `Tooltip.Content` — Bits UI/Floating UI now flips side at viewport edges
- [x] `white-space: normal; word-break: break-word; line-height: 1.45` added to tooltip CSS — no more truncation
- [x] `z-index` raised to 200 (above mobile menu at 150); `box-shadow` added for depth

### Feature — comparison mode (Session A complete)

- [x] Comparison store (`comparison.svelte.ts`) — module-level Svelte 5 `$state`; max 5 entities; type-homogeneous selection; URL serialisation `/compare?type=teams&ids=3,7,12`
- [x] Floating action bar (`FloatingCompareBar.svelte`) — fixed bottom-center, appears at ≥2 selected, slide-up animation, clear button
- [x] Checkbox UI on Teams ranking table (`cmp-check` button + `cmp-selected` row highlight)
- [x] Checkbox UI on Players ranking table (all 5 position tabs; GK + Discipline tabs excluded)
- [x] `/compare` route — team comparison with CSS Grid + proportional bar chart rows (3 metric groups); player comparison placeholder
- [x] Session B: full player stat comparison (4 metric groups + proportional bars); search/autocomplete to add entities; ✕ remove buttons on entity headers — Session 25b
- [x] Session C: type-pick landing, single-entity hint, search guard, responsive layout — Session 25c
- [x] Match comparison view: select 2–5 matches, compare head-to-head stats side by side — Session 25d

### Feature — missing visualizations

- [x] Player stats panel on match detail pages (starting XI + subs with goals/cards) — Session 25
- [x] Team aggregate trend chart: possession/xG per match sparklines on team detail page — Session 25
- [x] Phase fingerprint radar wired to real `match_phases` data (previously had hardcoded verdict text) — Session 25

### Work Stream D — Known limitations (deferred, documented)

- [ ] `final_third_entries`: no PDF source page exists; table populated from DB seed only. Do not attempt to add PDF ingestion — the data is not in the PMSR format.
- [x] GK goalkeeper name: `gk_name` column added to `match_gk_stats`; written by adapter (Session 13); shown in `GkDetail.svelte` (Session 14).
- [ ] Line break direction team totals (pages 8/9): through/around/over per team total; moderate effort for low display value — deferred.
- [ ] Passing matrix row totals (pages 12/13): full zone-to-zone matrix; requires new table; `PassingNetwork.svelte` already shows top connections — full matrix is deferred.
- [ ] Goal/card/substitution event minutes: would require a new `match_events` table; low value vs effort — deferred.

### Data pipeline — gaps identified by audit (Session 9)

- [ ] `final_third_entries`: no corresponding PDF page exists — this table is seeded only; ingestion via PDF not possible. Documented in WS-D; marked as "seeded only — no PDF source."
- [x] Pages 10/11 (line breaks per player): `player_line_breaks` table + `GET /api/v1/players/{id}/line-breaks` endpoint + scrollable table on `/players/[id]` with direction + unit breakdown (Session 12)
- [x] Pages 12/13 (passing network): `passing_connections` table + API endpoint + `PassingNetwork.svelte` (Session 10)
- [x] Pages 15/17 (shot log): `shot_events` table + API endpoint + `ShotTimeline.svelte` (Session 10)
- [x] Pages 18/19 (crosses): `cross_stats` table + API endpoint + `CrossesDetail.svelte` (Session 10); per-player cross type breakdown in `player_stats` + player detail page (Session 12)
- [x] Pages 20/21 (offerings to receive): `match_offering_stats` table + API endpoint + `OfferingsDetail.svelte` (Session 10)
- [x] Pages 22/23 (movement to receive): `match_movement_stats` table + API endpoint + `MovementDetail.svelte` (Session 10); by-pitch-third breakdown (15 cols) added to DB + API + component (Session 12)
- [x] Pages 25/26 (most possession regains): `most_regains_player/count` on `defensive_actions`; exposed in `DefensiveDetail.svelte` callout (Session 12)
- [x] Pages 36/37 (GK aerial breakdown): `punches/claims/tipped_palmed complete/incomplete` on `match_gk_stats`; shown in `KeyStatsTable.svelte` GK section (Session 12)
- [x] Page 2 (formations): `formation_a/formation_b` on `matches`; shown on match cards and detail header (Session 12)
- [x] 4 OOP player columns (`loose_ball_receptions`, `pushing_on`, `pushing_on_into_pressing`, `possession_interrupted`): added to `player_stats` UPDATE in `pmsr_to_sql.py` (Session 10)
- [x] Goalkeeper name: `gk_name` added to `match_gk_stats`, written by adapter, rendered in `GkDetail.svelte` (Session 13/14)

## Post-M9 — Full dashboard build-out (Session 11)

- [x] CORS: regex-based `allow_origin_regex` replaces explicit port list — any localhost port accepted
- [x] 14 new match PDFs ingested; `04_all_matches.sql` now covers 54 matches (1240 shot events)
- [x] Players page sort direction bug fixed (`dir * (av - bv)`, was `(bv - av)`)
- [x] Computed stats: `goals_per_shot`, `goals_per_game`, `pass_completion_pct`, `km_per_game`, `sprints_per_game` — all computed client-side in `computeDerived()` and sortable
- [x] Default sort per tab: Scorers→Goals, Defenders→Ballgewinne, Midfielders→Passquote, Forwards→Torquote, Physical→km/Game
- [x] 6 new i18n column keys in `players` namespace across all 6 locales
- [x] Tournament/Phases page: group stage corrected to 72 games; Round of 32 and 3rd Place added; total 104 matches; all unlock thresholds corrected
- [x] `tournament.roundOf32` + `tournament.thirdPlace` added to all 6 locales
- [x] `tournament.groupStageDetails` updated to "72 Matches" in all 6 locales

## Post-M9 — Full dashboard build-out (Session 12)

### Work Stream A — Frontend rendering gaps closed

- [x] `DefensiveDetail.svelte`: block + contest breakdown butterfly table; wired to match detail page
- [x] Player detail totals: 9 additional stat cards (tackles, blocks, regains, aerial/physical duels, pressing, HS runs, offers) — all from already-fetched player API data
- [x] Teams page: Top Scorers + Most Carded tables added below ranking table
- [x] Team detail: avg-stats mini strip (goals scored/conceded, possession, xG per match)

### Work Stream B — API extensions

- [x] `/key-stats` extended: 4 GK distribution fields + 15 corner breakdown fields
- [x] `KeyStatsTable.svelte`: GK distribution rows + 9 Set Play corner rows
- [x] Player API: 28 dark columns now exposed (switches_of_play, step_ins, lb totals, offer breakdown ×6, OOP detail ×4, distance zones ×5)
- [x] Player detail: all newly-exposed columns rendered in totals grid + per-match blocks

### Work Stream C — Full-stack additions (6 items)

- [x] C1 Formations (page 2): `formation_a/b` on matches; match cards + detail header
- [x] C2 Per-player crosses (pages 18/19): 6 cols on player_stats; cross type in player per-match blocks
- [x] C3 Player line breaks (pages 10/11): new `player_line_breaks` table; `/line-breaks` endpoint; table section on player detail page with direction + unit chip breakdown
- [x] C4 Movement by pitch third (pages 22/23): 15 cols on match_movement_stats; 3-column grid in `MovementDetail.svelte`
- [x] C5 GK aerial breakdown (pages 36/37): 6 cols on match_gk_stats; conditional rows in `KeyStatsTable.svelte`; `gkPunches/gkClaims/gkTipped` i18n in all 6 locales
- [x] C6 Most possession regains (pages 25/26): 2 cols on defensive_actions; callout in `DefensiveDetail.svelte`
- [x] All 54 PDFs re-ingested: 1 701 `player_line_breaks` rows, formations on all matches, pitch-third movement, GK aerial breakdown, possession regains callout data

### Work Stream E — Remaining parser gaps (Session 13)

- [x] E1 GK goal prevention detail (pages 34/35): 5 cols on match_gk_stats; adapter reads intervention_breakdown sub-fields; conditional rows in KeyStatsTable; i18n 5 keys × 6 locales
- [x] E2 GK crosses_faced delivery types (pages 36/37): 6 cols on match_gk_stats; adapter reads crosses_faced_delivery_types sub-fields; conditional rows in KeyStatsTable; i18n 6 keys × 6 locales
- [x] E3 GK name: gk_name VARCHAR(100) on match_gk_stats; adapter writes goalkeeper field; KeyStatsTable gkName row; i18n 1 key × 6 locales
- [x] E4 Player OOP fields (frontend only): pressing_indirect, possession_contests_won, pushing_on_into_pressing added to player detail totals + per-match blocks
- [x] All 72 match PDFs re-ingested; 144 match_gk_stats rows fully populated

### Data pipeline — deferred items (documented, will not implement)

- [ ] Pages 8/9 by_direction team totals (through/around/over): not stored; moderate effort for low display value
- [ ] Pages 20/21 per-player offering breakdown: would need new player_offering_stats table; unclear value
- [ ] Pages 22/23 top_ranked_players per movement type: not in any DB table; low priority
- [ ] Pages 25/26 per-player defensive table: 1 field only per player; not worth a new table
- [ ] `pressure_on_ball` column: schema column exists but adapter never writes it (no parser source); always NULL
- [ ] `player_stats.saves/goals_conceded/xg_faced`: columns exist but adapter never writes them; no per-player GK page source

## Post-M9 — Full dashboard build-out (Session 14)

### Bug fixes — data integrity

- [x] **Parser — extra shot-log page detection**: `_count_extra_shot_log_pages()` threshold `≥ 3` minute-words failed for low-shot matches; replaced with text-content check (`"Attempts at Goal" in doc[17].get_text()`). 5 affected matches re-ingested: Türkiye–USA, England–Ghana, Canada–Qatar, New Zealand–Egypt, Norway–France. `04_all_matches.sql` regenerated for all 72 matches.
- [x] **PressureDetail/DefensiveDetail Decimal crashes**: `avg_duration_s`, `ball_recovery_time_s`, `possession_actions_per_da`, `shot minute` changed from `Optional[Decimal]` → `Optional[float]` in backend schemas; `Number(v).toFixed()` in frontend components
- [x] **total_movements showing 2026**: `y > 50` filter added to movement total coordinate scan; page header year at `y≈13` now excluded

### GK redesign

- [x] `GkDetail.svelte` (new): dedicated GK stats section — Activity, Attempts Faced, Goal Interventions (+ 5-type breakdown), Aerial Interventions (+ punches/claims/tipped breakdown), Crosses Faced (+ 6 delivery types); rendered at bottom of match detail page
- [x] `GET /api/v1/matches/{id}/gk-stats`: new endpoint returning 29 GK fields per team; match `+page.ts` fetches as 15th parallel request
- [x] `GET /api/v1/stats/goalkeeper-rankings`: new endpoint aggregating `match_gk_stats` by `gk_name + team_id`; returns matches, attempts_faced, save_pct, goal_interventions, etc.
- [x] Players page: "Goalkeepers" tab (6th) with sortable ranking table (Apps, Attempts Faced, Save %, Goal Int., Aerial Int., Crosses Faced); data from new endpoint
- [x] `KeyStatsTable.svelte`: GK group removed — all GK detail now in `GkDetail.svelte`

### Maintenance

- [x] Full PDF data audit: 4-layer audit complete (Session 9)
- [x] PassingNetwork.svelte Decimal→string crash fixed (Session 13)
- [x] PressureDetail/DefensiveDetail Decimal crashes fixed (Session 14)
- [x] total_movements 2026 bug fixed (Session 14)
- [x] Extra shot-log page detection fixed for 5 affected matches (Session 14)
- [x] `parse_efi_pdf.py` deprecation — `DeprecationWarning` added; docstring updated to redirect to `parse_pmsr.py + pmsr_to_sql.py`
- [x] ~~Full crawl verification in live Docker container~~ — obsolete: web crawler removed 2026-07-04
- [ ] CI: `npm install` + `pip install` + fresh-volume seed test
- [ ] Contract drift gate (openapi-typescript diff on schema changes)
- [x] Missing tons of i18n translations in the whole app. (Session 26: playerDetail + compare namespaces, 70+25 keys × 6 locales)

## Post-M9 — Full dashboard build-out (Session 15)

### Bug fix — NewZealand-vs-Belgium.pdf (54 pages) page-shift

- [x] `_count_extra_shot_log_pages()` now iterates from `doc[17]` upward counting all consecutive "Attempts at Goal" pages — handles `extra=0/1/2/N` generically (not capped at 1)
- [x] NZL-BEL re-ingested with `extra=2`; NZL: 229 movements, BEL: 370 (both now correct)
- [x] Dataset audit: 48×52-page (extra=0), 23×53-page (extra=1), 1×54-page (extra=2) — all correct
- [x] `04_all_matches.sql` regenerated

## Post-M9 — Full dashboard build-out (Session 16)

### UI fixes

- [x] Double border fix — `GkDetail.svelte` `.gk__subheader`: `border-top` → `border-bottom`
- [x] Double border fix — `DefensiveDetail.svelte` `.dd__subheader`: same fix
- [x] Spatial panel null safety — `PitchSpatial.svelte`: `spatial_b` nullable; `hasSpatialB` guard shows "No spatial data" placeholder when team B has no rows
- [x] Team names clickable on match detail page (`/teams/{id}` links)

### Features

- [x] Matches page: group filter selectbox with "All Groups & Rounds" default; auto-populates knockout round labels once that data is ingested
- [x] Players page — ranking tables: sort applies to ALL eligible players; top 20 displayed
- [x] Players page — Discipline tab: 7th tab, sorted by total cards desc, includes yellow + red
- [x] Players page — browse section hidden until filter/search active (reduces initial load)
- [x] Players page — table styling: matches teams-page style (no border wrapper, simple hover)

## Post-M9 — Full dashboard build-out (Session 18)

### Style consistency sweep + UX improvements

- [x] Light mode a11y — `--muted` darkened (`#908a7c` → `#71685c`), passes WCAG AA 4.5:1
- [x] GK tab — `.slice(0, 20)` (was showing all 57 GKs)
- [x] Yellow card token — `var(--c-yellow)` replacing hardcoded `#d4a017`
- [x] Border-radius tokens — all hardcoded `8px`/`10px` → `var(--r-md)` across 4 files
- [x] Players detail section gap — `var(--sp-6)` → `var(--sp-5)`
- [x] StatTable hover — `tbody tr:hover { background: var(--border-soft); }`
- [x] Match card restructure — name below flag, formation below name, no ellipsis, team name links
- [x] Match card group badge — `<abbr>` tooltip ("Group A, Match 1")
- [x] Spatial control — empty right panel removed when `!hasSpatialB`
- [x] TermTooltip — "In Contest" (Teams), 9 stat column headers (Players)
- [x] Home page — removed xG/possession stats; match card clickable; CTA added
- [x] Player name links in shot log / passing network — `player-name-map` endpoint + ShotTimeline + PassingNetwork (Session 20)

## Post-M9 — Full dashboard build-out (Session 17)

### Bug fix — red cards missing from all player stats

- [x] `parse_pmsr.py` — `reclassify_red_cards()` post-processor: orphaned `COLOR_SUB_OFF` markers (no matching sub-on within ±2 min) reclassified as `{"type": "red"}` in player cards
- [x] 72-PDF scan detected 12 matches with red cards; all 12 re-ingested
- [x] DB now has 12 red card rows (was 0 before)
- [x] `04_all_matches.sql` regenerated
- [x] Second-yellow red cards distinguished from direct reds — `reclassify_red_cards()` reclassifies co-located yellows as `second_yellow` in-place (Session 25)

## Post-M9 — Full dashboard build-out (Session 25)

- [x] `parse_pmsr.py` — `reclassify_red_cards()` extended: co-located yellow card (±1 min of sub-off) reclassified as `second_yellow` in-place; direct red otherwise unchanged
- [x] `GET /api/v1/matches/{id}/lineup` — new endpoint; starting XI + subs with goals/cards per team; sorted by position group then jersey number
- [x] `LineupPanel.svelte` (new) — two-column team layout, position chips, event icons, player links; responsive single-column at 720px
- [x] Match detail page — Lineup section before Phases; PhaseFingerprint section after PhasesBar/LineBreaks
- [x] `PhaseFingerprint.svelte` — hardcoded verdict paragraph removed; component was already fully data-driven
- [x] `teams/[id]/+page.svelte` — "Performance Trend" section: possession % + xG sparkline cards with inline SVG polylines from match history
- [x] `comparison.svelte.ts` (new) — Svelte 5 module-level `$state` store; max 5; type-homogeneous; URL serialisation
- [x] `FloatingCompareBar.svelte` (new) — fixed bottom-center bar; slide-up animation; compare link + clear button
- [x] Teams + Players ranking pages — `cmp-check` toggle buttons + `cmp-selected` row highlight
- [x] `/compare` route — team comparison grid (3 metric groups, proportional bar charts); player placeholder

## Post-M9 — Full dashboard build-out (Session 25b/c)

- [x] `/compare` — full player comparison: 4 metric groups (General, Passing, Defensive, Physical) with proportional bars, position colour chips, team badges
- [x] Search/autocomplete: text input filters all teams or players client-side (≥2 chars); add by clicking option; navigates to updated URL
- [x] ✕ remove buttons on each entity column header; redirects to listing page if all removed
- [x] `safeColorVar()` — null-safe wrapper preventing crash on undefined team color
- [x] Empty state `/compare` with no type: pick cards for Teams and Players
- [x] Single-entity hint: "add at least one more" message when only 1 ID in URL
- [x] Search bar hidden until options loaded (no flash of disabled input)
- [x] Responsive: 140px metric column + minmax(100px, 1fr) at ≤720px; search full-width on mobile

## Post-M9 — Full dashboard build-out (Session 23)

- [x] `app.css` — `--accent-fg` token: `#fff` light / `#0b0b0f` dark; replaces `var(--bg)` on accent buttons
- [x] All accent-background buttons switched to `color: var(--accent-fg)` across 4 files
- [x] `SpatialMobilePicker.svelte` — `pill--team` active: `badgeTextColor()` → `--tc-text` CSS var → dark text on light team colors, white on dark team colors

## Post-M9 — Full dashboard build-out (Session 22)

- [x] `teams/+page.svelte` + `teams/[id]/+page.svelte` — accent active button: `color: #fff` → `color: var(--bg)` (dark-mode lime contrast fix)
- [x] `teams/[id]/+page.svelte` — mobile section-body padding shorthand; `performer-card` gets `min-width:0; overflow:hidden`
- [x] `TopBar.svelte` — brand div → `<a href="/">` so EFI logo navigates home

## Post-M9 — Full dashboard build-out (Session 21)

### Mobile UX polish & bug fixes

- [x] `ThemeSwitch.svelte` — replaced bits-ui Switch + label text with single 32×32 sun/moon icon button
- [x] `ShotTimeline.svelte` — `{@const}` crash fix (moved to direct `{#each}` children, not inside `<div>`)
- [x] `TopBar.svelte` — mobile lang switcher visibility: scoped selector `.topbar__right .lang-switcher { display: none }` so hamburger menu lang switcher stays visible
- [x] `+error.svelte` — "Back to Übersicht" → "Back to Home"
- [x] `SpatialMobilePicker.svelte` (new) — full-width single-pitch with nation/scenario/block pills
- [x] `matches/[id]/+page.svelte` — spatial split at page level: `.spatial-desktop` (two locked pitches, desktop) + `.spatial-mobile` (picker, mobile)
- [x] `matches/[id]/+page.svelte` — removed duplicate KPI row below PossessionBar
- [x] `matches/[id]/+page.svelte` — match header restructured: venue+date above scoreline; formation below team name
- [x] `SpatialMobilePicker.svelte` — pill modifier classes (`pill--scenario`, `pill--team`, `pill--block`) with correct contrast per type; `align-self: flex-start` on pill groups
- [x] `teams/+page.svelte` — sort pills converted to filled pill-group container pattern

## Post-M9 — Full dashboard build-out (Session 19)

### Footer — Impressum, Legal & Contact

- [x] `Footer.svelte`: centred ghost-text footer bar (Impressum · Privacy & Legal · Contact)
- [x] Impressum modal: § 5 DDG legal notice (Dustin Tramm, Hungen address, contact email)
- [x] Privacy & Legal modal: 2-col grid (privacy policy, FIFA data source, disclaimer, copyright)
- [x] Contact modal: form POSTing to `POST /api/v1/contact` with loading/error/success states
- [x] `backend/app/routers/contact.py`: SMTP email send via `smtplib` + STARTTLS in executor; in-memory rate limiter (3 req/IP/hour); Pydantic `EmailStr` validation
- [x] `backend/app/config.py`: SMTP settings (`smtp_host/port/user/pass`, `contact_to_email`, `allowed_origin`)
- [x] `backend/app/main.py`: contact router + `POST` in CORS methods
- [x] `.env.example`: all new env vars documented
- [x] i18n: 31-key `footer` namespace in all 6 locales (EN · DE · ES · PT · FR · AR)
- [x] Backdrop blur + dark mode border + SVG close icon — all dialog styling issues resolved
- [x] Company name purged from git history (3 commits squashed → 1 clean commit)

## Post-M9 — Session 26 (2026-06-29)

### i18n — full player detail + compare pages

- [x] `playerDetail` namespace: 70 keys × 6 locales — section labels, all stat card labels, table headers, status badges, zone distance labels, per-match mini labels
- [x] `compare` namespace: 25 keys × 6 locales — page titles, search placeholders, empty states, metric group names, match entity header
- [x] `players/[id]/+page.svelte`: fully i18n'd — `posLabel` map → `$derived` from `$t.players.*`; all stat labels use `$t.playerDetail.*` or reuse existing keyStats/players keys
- [x] `compare/+page.svelte`: fully i18n'd — `TEAM_METRICS`/`PLAYER_METRICS` → `$derived` so group names react to locale changes; all page UI strings use `$t.compare.*`; `t` variable shadowing eliminated
