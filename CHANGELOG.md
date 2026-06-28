# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]

### Added
- M0: Docker Compose infrastructure (db, backend, frontend, ingestion profile, test profile)
- M0: Makefile with up/down/reset/seed/crawl/test/contract/fmt/logs targets
- M0: `.env.example`, `scripts/wait-healthy.sh`, `ROADMAP.md`, `CHANGELOG.md`
- M0: GitHub Actions CI (lint, test stubs)
- M1: `db/init/01_schema.sql` — 11 EFI tables with scope discriminator and match_key generated column
- M2: `db/seeds/02_match_10_ger_cur.sql` — GER/CUR anchor team inserts + tournament placeholder
- M2: `db/seeds/03_team_aggregates.sql` — all 46 remaining WC2026 teams + aggregate stats
- M2: `ingestion/` — Python crawler pipeline (pd.read_html fast path + Playwright fallback)
- M3: FastAPI backend — async endpoints, SQLAlchemy 2.0 ORM, Pydantic v2 schemas
- M3: Dashboard composite endpoint `/api/v1/dashboard` (SSR single round-trip)
- M4: SvelteKit frontend scaffold — Svelte 5 runes, adapter-node, npm
- M4: Design system tokens — all colour, spacing, typography tokens in `app.css`
- M4: No-flash theme (inline `<head>` script + `theme.svelte.ts` rune store)
- M4: Primitive components — RainbowRail, SectionLabel, Badge, KpiStat, Card, StripeMotif
- M4: Layout components — TopBar, NavTabs, ThemeSwitch, TermTooltip
- M5: Viz components — PossessionBar, StatTable, PitchSpatial, PhasesBar, LineBreaksBars, FinalThirdZones
- M6: Übersicht dashboard page — 6 sections matching EFI Dashboard B design
- M7: Live data wiring — SvelteKit load → FastAPI dashboard endpoint
- M8: Analytical modules — EfficiencyMatrix, RiskReward, PressingEngine, PhaseFingerprint, PenetrationMap, ControlVsChaos
- M9: Test suite — Vitest browser, Playwright e2e, axe a11y, pytest testcontainers
- PDF ingestion pipeline: `ingestion/ingestion/parse_pmsr.py` (PyMuPDF, 2255 lines, 44 PMSR pages)
- PDF→SQL adapter: `ingestion/ingestion/pmsr_to_sql.py` — generates seed SQL from any FIFA PMSR PDF
- `db/seeds/04_all_matches.sql` — 36 group-stage matches from real PDF data
- `db/seeds/05_featured_match.sql` — marks GER 7–1 CUR as is_featured showcase match
- `.gitignore` — excludes env, node_modules, PDFs, db_data, editor artefacts

### Post-M9 — Full dashboard build-out (2026-06-22)

#### Navigation & routing
- All German placeholder text replaced with English throughout the UI
- Match cards clickable → `/matches/[id]` detail pages with all 7 EFI data sections
- Team cards clickable → `/teams/[id]` with aggregate summary stats and match history
- Player roster page `/players` — 1 248 real players, search/filter by name/team/position,
  colour-coded position badges, mobile-responsive grid
- Tournament progress page `/tournament` — KPI strip + phase unlock status + progress bars

#### Match detail pages
- StatTable (head-to-head stats: Goals, xG, Possession, In Contest, Ball Recovery,
  xG/Shot, Efficiency, Out Possession) now surfaces on every match detail page
- FinalThirdZones (5 attack-zone entry bars with team toggle) now surfaces on every
  match detail page — was previously only visible in the kitchen-sink dev route

#### i18n — Six-language support (EN · DE · ES · PT · FR · AR)
- Added German (DE) translations: `src/lib/i18n/de.ts` — full coverage of all UI strings
- Arabic (AR) RTL support: `setLocale` sets `dir="rtl"` on `<html>`;
  `app.css` adds `[dir='rtl']` overrides for font-family, text-alignment, stat-rows and back-links
- Language switcher in TopBar iterates `LOCALES` array — DE button appears automatically
- Locale persisted to `localStorage`; browser language auto-detected on first visit
- Added i18n keys `detail.finalThird` and `detail.headToHead` to all 6 locale files

#### Responsive design
- Mobile hamburger navigation at ≤960px breakpoint (TopBar)
- All page layouts use `auto-fill` / `minmax()` grids with media queries down to 400px
- Filters on players page collapse to full-width column on mobile

#### Test suite fixes
- Replaced broken `projects` workspace vitest config with single `happy-dom` environment
  so Svelte component tests run without Playwright
- Fixed `PossessionBar.svelte` — top-level `{@const}` moved to `$derived` in script block
  (Svelte 5 disallows `{@const}` at template root)
- Fixed `Team` mock objects in test files: added required `short_code` and `slug` fields
- Installed `happy-dom` and `@testing-library/jest-dom` dev dependencies
- All 10 frontend unit tests now pass

#### PDF drop-folder watcher
- Added `ingestion/ingestion/watch_pdfs.py` — cron-compatible PDF ingestion watcher
- Reads `PDF_WATCH_DIR` from `.env`; scans for new PMSR PDFs and ingests them
- Tracks processed files in `.processed_pdfs` log; idempotent and safe to re-run
- CLI flags: `--dry-run`, `--force`, `--dir <path>`
- Apache / Phusion Passenger: invoke as a cron job — no daemon or Passenger hooks needed
- `PDF_WATCH_DIR=./pdfs` added to `.env` and `.env.example` with inline deployment notes
- 14 unit tests in `ingestion/tests/test_watch_pdfs.py` — all passing

### Changed
- `db/seeds/02_match_10_ger_cur.sql` — stripped to GER/CUR team anchors only; wrong placeholder teams removed
- `db/init/01_schema.sql` — added `UNIQUE KEY uq_player (team_id, jersey_number)`
- `frontend/src/lib/components/modules/PhaseFingerprint.svelte` — IN_PHASES updated to real PDF names (Build Up Unopposed/Opposed, Final Third, Long Ball, Attacking Transition)
- `ingestion/requirements.txt` — added `pymupdf>=1.24.0`

### Fixed
- Phase names in seed data now match actual PDF values (old names like 'Build up', 'High press/block' were wrong)
- Line break values now derived from per-line aggregation across unit groups (old values were incorrect direction breakdowns from pdfplumber)
- Spatial stats (defensive_line_height, team_length) now from PDF parser; old values were manually estimated
- Ball recovery time now correctly sourced from page 29 of PMSR (GER: 11.42s, CUR: 18.09s)
- Team table now contains all 48 real WC2026 participants; 46 wrong placeholder teams removed

### Post-M9 — Session 5 (2026-06-23)

#### Match detail — full key-stats panel
- **`KeyStatsTable` component** (`src/lib/components/viz/KeyStatsTable.svelte`): replaces the old
  8-row `StatTable` with a comprehensive grouped stats table covering 36 metrics across 5 sections:
  Match Summary · In Possession (Passing) · Out of Possession (Defensive) · Goalkeeping · Set Plays
- `GET /api/v1/matches/{id}/key-stats` aggregates data from 6 DB tables: `match_stats`,
  `line_breaks`, `defensive_actions`, `player_stats`, `match_gk_stats`, `match_set_play_stats`
- Match detail `+page.ts` loads `key-stats` as 8th parallel request; standalone Defensive section
  removed (all defensive data now in KeyStatsTable)

#### Players page — ranking & comparison landing
- `/players` redesigned as a ranking-first landing page with 5 position tabs:
  Top Scorers · Top Defenders · Top Midfielders · Top Forwards · Physical Leaders
- Each tab shows a sortable ranking table with position-specific key metrics:
  - Defenders ranked by `tackles_won + interceptions×1.5 + clearances×0.5`
  - Midfielders ranked by `passes_attempted`; shows `ball_progressions`, `take_ons`, `pressing`
  - Forwards ranked by `goals×3 + attempts_at_goal`; shows `take_ons`, `offers`
  - Physical by `total_distance_m`; shows `sprints`, `high_speed_runs`, `top_speed_kmh`
- All player names in ranking tables link to `/players/[id]`
- Full search/filter browse section kept below the ranking tabs
- `ball_progressions` added to `GET /api/v1/stats/player-stats-summary` response

#### Player detail page `/players/[id]`
- New route `src/routes/players/[id]/` (`+page.ts` + `+page.svelte`)
- Header: player name, position (colour-coded), jersey number, team badge + country flag
- Tournament totals section: stat cards for all categories (passing, defensive, physical)
- Match-by-match overview table: all matches with opponent link, status, key stats columns
- Per-match detail blocks: all available stats per match (passing, defensive, physical, offers)
- All opponent names link to `/teams/[id]`, back navigation to `/players` and `/teams/[id]`
- Uses existing `GET /api/v1/players/{player_id}` endpoint (totals + per_match breakdown)

#### Teams page — ranking table + CTA
- `/teams` now shows a sortable comparison table above the team cards with columns:
  Played · Goals · Goals Conceded · Goal Difference · Avg Possession · Avg xG · In Contest
- Sort pills: Goals (default) · Possession · xG · Goals Conceded ↑
- Nation names in table link to `/teams/[id]` detail pages
- CTA banner above the cards: "Want to look at a specific nation? Click on their card…"
- `teams/+page.ts` now loads `/api/v1/stats/leaderboards` in parallel

#### LineBreaksBars redesign
- `LineBreaksBars.svelte` rewritten with butterfly/mirror layout (same language as `PhasesBar`):
  team A numbers + bar on left, line name center, team B bar + numbers on right
- Each line shows: completed/attempted count + completion %, bar fills from outside in
- Cleaner than previous two-stacked-bars-per-row layout

### Post-M9 — Session 6 (2026-06-23)

#### Bug fixes — data integrity

- **Parser: stoppage-time goals** (`parse_pmsr.py`): minute markers like "90+3'" were being
  parsed as just 90, making `abs(90 - 93) = 3 > 2` tolerance fail. Fixed by parsing
  "90+3'" as 90+3=93. Affected: Deniz UNDAV's 90+3' goal in GER vs CIV was wrongly
  classified as a yellow card.

- **Parser: high-scoring matches with extra shot-log pages** (`parse_pmsr.py`): when a match
  has more than 52 PDF pages (extra=1), the home team's second shot log page (doc[15]) was
  not being included in the goal lookup map. All goals on that page were silently classified
  as yellow cards. Fixed: `p15_raw += _parse_shot_log(doc[15])` when `extra > 0`.
  Affected match: GER vs CUR (7–1) — HAVERTZ (2nd goal, 87'), BROWN (67'), UNDAV (77')
  were all showing as yellow cards.

- **Seed SQL corrected** (`04_all_matches.sql`):
  - GER vs CIV (match 33): Undav jersey 26 → 2 goals, 0 yellows (was 1 goal, 1 yellow)
  - GER vs CUR (match 10): Havertz jersey 7 → 2 goals, 0 yellows (was 0 goals, 2 yellows)
  - GER vs CUR (match 10): Brown jersey 18 → 1 goal, 0 yellows (was 0 goals, 1 yellow)
  - GER vs CUR (match 10): Undav jersey 26 → 1 goal, 0 yellows (was 0 goals, 1 yellow)
  - Deniz UNDAV total: now correctly 3 goals (2 vs CIV + 1 vs CUR)

#### Match detail page — double HR removed

- `KeyStatsTable.svelte`: removed `border-top` from `.kst__group-title` elements. The header's
  `border-bottom` already provides the separator; the group title's additional `border-top`
  created a double-HR between every section.

#### Teams page — cards removed

- `/teams` page: team cards below the ranking table removed entirely. Nation names in the
  comparison table already link to `/teams/[id]` detail pages, making the cards redundant.

#### Pitch spatial — team block visualization

- `PitchSpatial.svelte`: added team block region (shaded area from defensive line to
  defensive_line_height + team_length) for each team. Previously only showed a single
  defensive line per side. Toggle labels updated to "High Press / Mid Block / Low Block".
  Team direction labels (e.g. "GER →  ← RSA") added above the pitch.

### Post-M9 — Session 3 (2026-06-22)

#### Statistics page `/stats`
- New route `/stats` — sortable Team Rankings table, Top Scorers, Discipline, Best Forwards /
  Midfielders / Defenders, all with country flags and team badges
- Leaderboards API `GET /api/v1/stats/leaderboards` — top 50 scorers, top 30 carded players,
  full 48-team rankings (goals, xG, possession, in-contest, goal diff)
- Player stats summary API `GET /api/v1/stats/player-stats-summary` — aggregated appearances,
  goals, yellow/red cards, minutes for all 1 248 players with at least 1 appearance
- Stats nav item added to TopBar and mobile menu across all 6 locales

#### Player stats on players page
- Every player card now shows goals ⚽, yellow/red card counts, and match appearances
- `players/+page.ts` now loads player-stats-summary in parallel with the players list
- Stats chips styled per-type: goal (accent), yellow, red, apps (muted)

#### i18n — Stats namespace
- Added `stats` translation namespace to all 6 locales (EN/DE/ES/PT/FR/AR)
- 28 new keys covering: teamRankings, topScorers, mostCarded, groupComparison,
  bestForwards, bestDefenders, bestMidfielders, all table column headers
- `nav.stats` key added to all 6 locales

#### Backend — PlayerStat model fix
- `backend/app/models/player_stats.py` updated to add columns `goals`, `yellow_cards`,
  `red_cards`, `started`, `minutes_played` (were in DB schema but missing from ORM model)
- Fixes `AttributeError` crash on `GET /api/v1/stats/leaderboards`

### Post-M9 — Session 2 (2026-06-22)

#### Team detail page — full build-out
- Phase profile section: per-team average phase distribution across all matches, shown as
  horizontal bar rows grouped into "In Possession" and "Out of Possession" panels
- Squad section: all players grouped by position (GK/DF/MF/FW), jersey number + name cards
- Flag watermark in team detail header (country flag at 12% opacity, right-side positioning)
- CSS for `.phase-row`, `.squad__card`, `.team-header__flag` with responsive breakpoints
- `GET /api/v1/teams/{id}/players` — returns squad ordered by jersey number
- `GET /api/v1/teams/{id}/phases` — returns per-phase avg across all team matches

#### Flags (flag-icons v7.5.0)
- `flag-icons` npm package imported in `+layout.svelte`; FIFA → ISO2 map in `tokens.ts`
- Flags render on team cards (watermark, right side, 15% opacity) and team detail header
- 48-team FIFA code mapping including special cases: ENG→gb-eng, SCO→gb-sct, CPV→cv, CUR→cw

#### Color & contrast fixes
- 48 teams assigned unique colors — no two teams in the same match share a color
- `--c-yellow-ink` / `--c-lime-ink` / `--c-lavender-ink` / `--c-pink-ink` dark ink variants
  added to `app.css` for readable text on light backgrounds
- `teamTextColor()` in `tokens.ts` returns ink color for yellow/lime/lavender/pink,
  bright color for dark mode (via CSS vars); applied to StatTable, PossessionBar, match detail

#### Phase data
- `tokens.ts` phase name map corrected to real DB values (e.g. "Build Up Unopposed" not "Build up")
- `PhasesBar` fully redesigned: background track per group, segment % labels ≥8%, two-column legend
- `final_third_entries`: 400 rows seeded for all 40 matches (5 zones × 2 teams × 40 matches)
  via `db/seeds/05_final_third_entries.sql` (deterministic, seed=42)
- `FinalThirdEntrySchema`: changed `alias` → `validation_alias` so API serialises as `count`
  (matches the `FinalThirdEntry` TypeScript type and `FinalThirdZones` component)

#### 4 new match PDFs
- Match 37 (URU 2:2 CPV), Match 38 (ESP 4:0 KSA), Match 39 (BEL 0:0 IRN), Match 40 (NZL 1:3 EGY)
  processed via `python3 -m ingestion.pmsr_to_sql`; appended to `04_all_matches.sql`

#### i18n — error messages
- Added `error` namespace to all 6 locale files (EN/DE/ES/PT/FR/AR):
  `loadFailed`, `notFound`, `matchNotFound`, `teamNotFound`
- All `{data.error}` raw string renders replaced with translated messages across 7 pages:
  `/`, `/matches`, `/matches/[id]`, `/teams`, `/teams/[id]`, `/players`, `/phases`

#### Goals calculation
- `GET /api/v1/teams/` now computes `goals_a` dynamically from actual match scores
  via `func.sum(case(...))` — fixes stale aggregate values that missed late-seeded matches

#### Bug fixes
- Players page 500: `{@const}` must be immediate child of `{#each}`; moved before `<section>`
- "GER vs Germany" in match history: scoreline now shows both team badges side-by-side
- `03_team_aggregates.sql` changed from `INSERT IGNORE` to `ON DUPLICATE KEY UPDATE color=…`
  so color changes take effect on re-seed without full DB reset

### Post-M9 — Session 7 (2026-06-22)

#### Players page — Top Goals rename, sortable headers, tab scrollbar
- "Top Scorers" tab renamed to "Top Goals"; Assists column removed (not in PDF data)
- All 5 ranking tables now have fully sortable column headers (click to sort, click again to
  toggle ASC/DESC); direction shown with ↑/↓ indicator in the same header cell
- Merged two-row header into single row: labels ARE the sort buttons (no separate sorter row)
- Tab bar horizontal scrollbar hidden with `scrollbar-width: none` + webkit override

#### Teams page — sort direction toggle
- Team rankings sort pills now toggle ASC/DESC on repeated click (was silently staying DESC)
- Direction indicator (↓/↑) shown inline on the active sort pill
- "Goals Conceded" label shortened to "Conceded" (direction shown dynamically)

#### Avg xG fix — team rankings
- `GET /api/v1/stats/leaderboards`: avg xG was always 0.0 because it read from
  `team_aggregate` rows which contain no xG data; rewritten to compute `AVG(xg_a)` from
  per-match `scope='match'` rows (correct team-specific column)
- Korea now shows NULL avg possession / xG (no parsed PDFs for those matches — correct)

#### Team detail — deep match stats with Avg/Total toggle
- All averaged key stats from every parsed match shown in a new "Match Stats" section below
  the head-to-head history: Goals, xG, Possession, In Contest, Line Breaks (by type),
  Defensive Actions, GK stats, Set-play stats, Ball Recovery
- Avg/Total toggle button lets user switch between per-match average and tournament totals
- New `GET /api/v1/teams/{id}/avg-stats` endpoint aggregates all metrics with counts

#### Team detail match history — xG/possession fix
- Match history rows were applying an `isTeamA` flip to xG/possession, but the API already
  returns team-specific rows (xg_a = THIS team's xG always). Fixed: always use `ms.xg_a`
  and `ms.possession_team_a` directly

#### PitchSpatial — two independent vertical pitches
- `PitchSpatial.svelte` fully rewritten: two side-by-side vertical pitches (68:105 aspect),
  each with its own Low/Mid/High toggle (no shared state)
- Penalty boxes rendered as horizontal bands at top/bottom; center circle and center line shown
- Block rendered as horizontal band: `bottom: pct(def_line_height)`, `height: pct(team_length)`
- KPI row below each pitch shows Def. Line and Team Length values

#### Player/squad card appearances chip fix
- Appearances chip now hidden for players with `appearances > 0` but `minutes_played == 0`
  (players who were in the squad but never came on were incorrectly showing "Ng")

#### Reports badge — dynamic match count
- TopBar "Reports" pill now fetches actual match count from `/api/v1/matches/` via `+layout.ts`
  LayoutLoad; passed as prop through `+layout.svelte` → `TopBar`
- Hardcoded "36 Reports" replaced; now shows DB count (40)

#### i18n — players page stat naming (partial)
- Tab labels wired to i18n: `$t.players.tabTopGoals` / `tabTopDefenders` / etc.

### Post-M9 — Session 8 (2026-06-23)

#### Spatial Control — In Possession data (pages 6/7)
- DB: `team_spatial_stats.block_type` enum extended to include `build_up_low`,
  `build_up_mid`, `final_third_phase` (in-possession sections)
- DB: `team_spatial_stats.width_m DECIMAL(5,2)` column added
- SQLAlchemy model + Pydantic schema updated to reflect new columns
- `pmsr_to_sql.py`: now also generates INSERT statements for pages 6/7 in-possession
  spatial data (width_m, length_m, distance_to_goal_m per section)
- Backfill script run: 240 rows inserted for all 40 matches (2 teams × 3 sections × 40)
- `GET /api/v1/matches/{id}/spatial` response restructured: `{ team_a: { defensive: [...], possession: [...] }, team_b: ... }`
- `PitchSpatial.svelte` redesigned with scenario tabs ("Out of Possession" / "In Possession"):
  - Out of Possession: High/Mid/Low block toggle — existing defensive data
  - In Possession: Build-Up Low/Mid/Final Third toggle — new pages 6/7 data
  - In-possession block width (width_m) applied to the pitch block left/right margins
  - KPI row shows Distance, Length, Width (width only shown for in-possession)

#### Overview / Hero / Tournament — dynamic match count
- `GET /api/v1/overview` service rewritten to compute match count, goals, avg in-contest
  dynamically from `matches` and `match_stats` tables instead of stale `tournament_overview` cache
- Hero section and Tournament page now correctly show 40 (was hardcoded 36)
- Goals per match on Tournament page updates automatically

#### Badge component — contrast fix
- `Badge.svelte`: added `--c-lavender` and `--c-pink` to list of colors needing dark text
  (was rendering white text on light lavender/pink backgrounds — very poor contrast)
- Dark text color changed to `#0c1a10` (very dark green-black) for all light-background badges

#### Player appearances chip — minutes guard
- Players page and team detail page: appearances chip (`Ng`) now only shown when
  `minutes_played > 0`, not when `appearances > 0`; fixes all unused subs showing "2g"

#### i18n — players page fully wired
- 23 new keys added to `players` namespace in all 6 locale files (EN/DE/ES/PT/FR/AR):
  5 tab labels + 18 column header keys
- All 5 ranking table column headers now use `$t.players.col*` keys — fully translatable

### Post-M9 — Session 9 (2026-06-23)

#### Spatial Control — heading + layout fixes
- `PitchSpatial.svelte`: removed hardcoded `SPATIAL CONTROL` eyebrow — caused doubled heading
  (e.g. "RAUMKONTROLLE" + "SPATIAL CONTROL") when the parent already supplies a title.
  Section title is now entirely the calling component's responsibility.
- Added `initialScenario` prop (`'defensive' | 'possession'`, default `'defensive'`). Landing page
  now passes `initialScenario="possession"` so the spatial card opens on In Possession by default.
- `.compact .pitch-col` max-width increased 210px → 320px.

#### Match detail — Spatial + Final Third 50/50 grid
- Spatial Control and Final Third Entries are now side by side (50/50, one divider row) instead
  of stacked full-width sections. Collapses to single column at ≤900px.

#### i18n — KeyStatsTable fully wired to translations
- All 36 stat labels, 5 group titles, and the "MATCH STATS" centre header now use `$t.keyStats.*`
  keys. Previously the `keyStats` namespace existed in all 6 locales but the component still used
  hardcoded English strings.

#### Landing page — i18n cleanup
- `+page.svelte`: "Spatial Control" cell-eyebrow wired to `$t.detail.spatial`;
  "Key Statistics · Head-to-Head" wired to `$t.detail.headToHead`.

#### PDF data audit — full findings
- Comprehensive 4-layer audit: PDF extraction → DB storage → API exposure → frontend display.
- Key finding: **~70% of extracted PDF data never reaches the frontend.**
- Specific gaps (tracked in ROADMAP):
  - Pages 10/11, 12/13, 15/17, 18/19, 20/21, 22/23 data: parsed but never stored in DB.
  - `final_third_entries`: populated only via DB seeds; PDF ingestion does not insert this table.
  - 4 player OOP columns (`loose_ball_receptions`, `pushing_on`, `pushing_on_into_pressing`,
    `possession_interrupted`): extracted by parser, not present in seed SQL.
  - Comparison mode (country/player/match): not implemented.

### Post-M9 — Session 10 (2026-06-26)

#### Full-pipeline data expansion — 6 new tables, 41 new columns, 6 new frontend visualizations

All data that `parse_pmsr.py` extracted but `pmsr_to_sql.py` silently discarded is now stored,
exposed via API, and visualized in the match detail page.

##### DB schema (`db/init/01_schema.sql`)
- **6 new tables:** `shot_events`, `passing_connections`, `cross_stats`, `match_offering_stats`,
  `match_movement_stats`, `match_pressure_stats`
- **`defensive_actions` +13 columns:** `possession_regained`, `interceptions`, `tackles`,
  `possession_actions_per_da`, `blocks_total/passes/shots/crosses/clearances`,
  `contests_total/physical/aerial/duels`
- **`match_set_play_stats` +13 columns:** corner delivery breakdown — `corner_direct_area_left/right/total`,
  `corner_short_left/right/total`, `corner_edge_left/right/total`,
  `corner_inswing/outswing/driven/lofted`
- **`player_stats` +15 columns:** offer movement breakdown (`offers_in_front/in_between/out_to_in/
  in_to_out/in_behind/no_movement`), OOP stats (`loose_ball_receptions/pushing_on/
  pushing_on_into_pressing/possession_interrupted`), distance zones (`dist_zone1_m` – `dist_zone5_m`)

##### Ingestion (`ingestion/ingestion/pmsr_to_sql.py`)
- `_n()` promoted to module-level (was inner function at line ~741, causing `UnboundLocalError`
  for new sections that used it before that definition)
- **New sections:** shot_events (DELETE+INSERT per team), passing_connections (with garbage-row
  filter for `"% of Total"` header rows), cross_stats (pages 18/19), match_offering_stats (pages 20/21),
  match_movement_stats (pages 22/23), match_pressure_stats (page 29)
- **Extended sections:** defensive_actions (now 19 columns including blocks dict + contests dict),
  match_set_play_stats (now includes `corners_by_delivery_type` + `corners_by_delivery_style`),
  player_stats UPDATE for offers (6 breakdown columns), OOP (4 loose-ball columns),
  physical (5 distance-zone columns)
- All 40 match PDFs re-ingested: 920 shot events, 396 passing connections, 80 rows each in
  the 5 new aggregate tables

##### Backend
- **6 new ORM models:** `ShotEvent`, `PassingConnection`, `CrossStat`, `MatchOfferingStat`,
  `MatchMovementStat`, `MatchPressureStat`
- **6 new Pydantic schemas:** `ShotEventSchema`/`ShotLogSchema`, `PassingConnectionSchema`/
  `PassingNetworkSchema`, `CrossStatSchema`/`CrossStatsMatchSchema`, `OfferingStatSchema`/
  `OfferingStatsMatchSchema`, `MovementStatSchema`/`MovementStatsMatchSchema`,
  `PressureStatSchema`/`PressureStatsMatchSchema`
- **6 new endpoints** on `GET /api/v1/matches/{id}/`:
  - `shots` — shot log (minute, player, outcome, delivery, body part, distance, xG)
  - `passing-network` — top passing connections per team (rank, from→to, count, pct)
  - `crosses` — attempted/completed + delivery type + zone breakdown + most-active player
  - `offerings` — total offers made/received + pitch third + inside/outside shape
  - `movement` — total movements + game phase + movement type breakdown
  - `pressure` — 9 pressure metrics + most-direct-pressure player callout
- `backend/app/models/defensive.py`, `set_play_stats.py`, `player_stats.py`: extended to match new columns
- `backend/app/schemas/defensive.py`: 13 new `Optional` fields

##### Frontend
- **6 new Svelte 5 components:**
  - `ShotTimeline.svelte` — scrollable timeline table; goal/on-target/off-target/blocked color
    coding; responsive (drops delivery at 720px, body at 520px)
  - `PassingNetwork.svelte` — two-column home|away split; relative % bar; name abbreviation
    (e.g. "Jonathan TAH" → "J. TAH")
  - `CrossesDetail.svelte` — completion KPI row; butterfly bars for 6 delivery types +
    4 cross zones; most-active player callout
  - `OfferingsDetail.svelte` — KPI cards (total offers made/received + most player);
    butterfly bars for 3 pitch thirds; inside vs outside shape progress bar
  - `MovementDetail.svelte` — total movements KPI; butterfly bars for 3 game phases +
    5 movement types
  - `PressureDetail.svelte` — 9-row stat grid (team A | label | team B); callout cards
    for most-direct-pressure player per team
- `+page.ts` extended from 8 to 14 parallel requests (added shots, passingNetwork, crosses,
  offerings, movement, pressure)
- `+page.svelte` updated: 6 new `$derived` bindings; 4 new layout sections:
  - Shot Log (full width)
  - Passing Network + Pressure (two-column)
  - Crosses + Offerings (two-column)
  - Movement (full width)
- TypeScript: dynamic key access pattern `(stat as unknown as Record<string, T>)[key]` applied
  in all 4 butterfly-bar components (avoids TS2352 on generic key lookup)

##### Infrastructure
- `docker-compose.yml`: frontend port changed `5173→5175` (ddev-router binds 5173–5174 on host)

### Post-M9 — Session 11 (2026-06-26)

#### CORS — allow all localhost ports
- `backend/app/main.py`: replaced explicit `CORS_ORIGINS` allowlist with
  `allow_origin_regex=r"http://localhost(:\d+)?"` so any localhost port is accepted without
  code or env changes when the frontend port shifts.
- `backend/app/config.py`: `cors_origins` field removed (no longer used).
- `.env` / `.env.example`: `CORS_ORIGINS` line removed entirely.

#### PDF ingestion — 54 matches
- Re-ingested all 40 previously-done PDFs plus 14 new ones from `.claude/data/`:
  `04_all_matches.sql` now covers 54 matches (132 112 lines, ~5.9 MB).
- DB after apply: `matches=54`, `shot_events=1240`, `passing_connections=535`, all per-team
  aggregate tables at 108 rows each.

#### Players page — sort fixes and new computed columns
- **Sort direction bug fixed** (`reSort()`): `dir * (bv - av)` was inverted — `dir=-1` (DESC)
  produced ascending order. Fixed to `dir * (av - bv)`.
  Before: Messi (5 goals) shown at bottom, Munoz (2 goals) at top. After: Messi correctly #1.
- **New computed stats** added via `computeDerived()` (client-side):
  - `goals_per_shot` — shot conversion % (requires ≥1 attempt)
  - `goals_per_game` — goals divided by appearances
  - `pass_completion_pct` — passes completed / attempted % (requires ≥20 attempted)
  - `km_per_game` — total distance in km divided by appearances
  - `sprints_per_game` — sprints divided by appearances
- **Default sort per tab changed:**
  - Scorers → Goals (was goals, dir already correct)
  - Defenders → Ballgewinne / Ball Wins (`possession_regains`)
  - Midfielders → Passquote (`pass_completion_pct`; was raw `passes_completed` count)
  - Forwards → Torquote (`goals_per_shot`)
  - Physical → km/Game (`km_per_game`)
- **Tab pre-sort arrays updated:** Defenders filtered to DF+MF with `possession_regains > 0`;
  Midfielders filtered to MF with `passes_attempted ≥ 20`; Forwards filtered to FW with
  `attempts_at_goal ≥ 1`; Physical filtered to anyone with `km_per_game > 0`.
- All new columns added to their respective tables in HTML.

#### i18n — new column translations (all 6 locales)
- 6 new keys added to `players` namespace in EN/DE/ES/PT/FR/AR:
  `colGoalsPerShot`, `colGoalsPerGame`, `colBallRecoveries`, `colPassQuote`,
  `colKmPerGame`, `colSprintsPerGame`

#### Tournament / Phases page — WC2026 format corrected
- Group stage progress bar denominator changed 48 → 72 (12 groups × 4 teams × 6 matches = 72).
- Phase array corrected: old wrong entries (roundOf16 unlocks at 48, QF at 64, SF at 72,
  Final at 76) replaced with correct WC2026 bracket:
  - Round of 32 (1/16-Finale): 16 matches, unlocks at 72
  - Round of 16: 8 matches, unlocks at 88
  - Quarter-finals: 4 matches, unlocks at 96
  - Semi-finals: 2 matches, unlocks at 100
  - 3rd Place Play-off: 1 match, unlocks at 102
  - Final: 1 match, unlocks at 103
- Total: 104 tournament matches (correct).
- Two new i18n keys added to all 6 locales: `tournament.roundOf32`, `tournament.thirdPlace`.
- `tournament.groupStageDetails` updated from "48 Matches" to "72 Matches" in all 6 locales.
- `colGoalsPerShot` label clarified: DE "Torquote" → "Tore/Schuss", EN "Shot Conv." → "Goals/Shot"
  and equivalents in ES/PT/FR/AR — makes denominator explicit (per shot, not per game).

### Post-M9 — Session 12 (2026-06-28)

#### Work Stream A — Frontend rendering of already-fetched data

- **`DefensiveDetail.svelte`** (new component): two-column butterfly table for defensive actions —
  block breakdown (passes/shots/crosses/clearances vs total), contest breakdown
  (physical/aerial/duels vs total), `possession_actions_per_da` KPI row; wired into match
  detail `+page.svelte` as a new section
- **Player detail totals grid** (`/players/[id]`): 9 additional stat cards now shown when data
  present — `tackles_made`, `blocks`, `possession_regains`, `duels_won_aerial`,
  `duels_won_physical`, `pressing_direct`, `high_speed_runs`, `total_offers`, `offers_received`
- **Teams page** (`/teams`): Top Scorers and Most Carded leaderboard tables added below the
  comparison ranking table; data already loaded via `leaderboards` endpoint
- **Team detail page** (`/teams/[id]`): avg-stats mini strip shows avg goals scored/conceded,
  avg possession, avg xG per match from `GET /api/v1/teams/{id}/avg-stats`

#### Work Stream B — API extensions (no DB schema changes)

- **`GET /api/v1/matches/{id}/key-stats`** extended with:
  - 4 GK distribution fields: `gk_kick_from_feet`, `gk_kick_from_hands`,
    `gk_throw_distribution`, `gk_aerial_interventions`
  - 15 corner breakdown fields: `free_kicks_direct/indirect`, `corner_inswing/outswing/driven/lofted`,
    `corner_direct_area_left/right/total`, `corner_short_left/right/total`,
    `corner_edge_left/right/total`
- **`KeyStatsTable.svelte`**: GK group extended with Kick from Feet / Kick from Hands /
  Throw Distribution / Aerial Interventions rows; Set Plays section extended with 9 corner
  delivery and zone rows (inswing/outswing/driven/lofted, direct area/short/edge)
- **`GET /api/v1/players/{player_id}`** now exposes 28 previously dark columns:
  `switches_of_play`, `step_ins`, `lb_attempted`, `lb_completed`, offer breakdown
  (6 types), OOP stats (4 loose-ball columns), distance zones (`dist_zone1_m`–`dist_zone5_m`)
- **Player detail page** (`/players/[id]`): totals grid and per-match stat blocks extended to
  show all newly-exposed columns — switches of play, step-ins, line break totals, offer
  breakdown, OOP detail, and distance zone cards

#### Work Stream C — Full-stack additions (DB + ingestion + backend + frontend)

All 6 C-stream items required DB schema change, `pmsr_to_sql.py` adapter change, backend
model/schema/API, and frontend render. All 54 match PDFs re-ingested after schema changes.

- **C1 — Formations** (PDF page 2): `formation_a`/`formation_b` columns on `matches` table;
  adapter reads `formations.home_team`/`away_team` from page 2; `MatchMeta` schema extended;
  formations shown on match cards (e.g. "4-3-3 vs 4-2-3-1") and in match detail header
- **C2 — Per-player cross breakdown** (PDF pages 18/19): 6 columns added to `player_stats`
  (`crosses_inswing/outswing/driven/lofted/cutback/push_cross`); adapter UPDATE loop per
  player per team; cross type breakdown shown in per-match stat blocks on player detail page
- **C3 — Player line breaks table** (PDF pages 10/11): new `player_line_breaks` table with 21
  columns (attempted, completed, direction breakdown, distance type, 9 unit breakdown columns);
  adapter INSERT/ON DUPLICATE KEY per player; new `GET /api/v1/players/{id}/line-breaks`
  endpoint; `/players/[id]` page extended with a scrollable table (direction + distance cols)
  and unit chips per match row; `+page.ts` fetches line-breaks in parallel with player profile
- **C4 — Movement by pitch third** (PDF pages 22/23): 15 columns added to `match_movement_stats`
  (`ft/mid/def_in_front/in_between/out_to_in/in_to_out/in_behind`); `MovementDetail.svelte`
  extended with a 3-column "By Pitch Third" grid showing all 5 movement types per third
- **C5 — GK aerial breakdown** (PDF pages 36/37): 6 columns added to `match_gk_stats`
  (`punches_complete/incomplete`, `claims_complete/incomplete`, `tipped_palmed_complete/incomplete`);
  6 fields added to `/key-stats` response; `KeyStatsTable.svelte` extended with conditional
  Punches / Claims / Tipped rows (shown only when data present)
- **C6 — Most possession regains callout** (PDF pages 25/26): `most_regains_player` +
  `most_regains_count` columns added to `defensive_actions`; `DefensiveActionSchema` extended;
  `DefensiveDetail.svelte` shows callout card naming the player with most possession regains

#### Re-ingestion

- All 54 match PDFs re-ingested with the full C-stream additions; `04_all_matches.sql`
  regenerated — formations on all 54 matches, 1 701 `player_line_breaks` rows, pitch-third
  movement data, GK aerial breakdown, possession regains callout data

#### i18n — all 6 locales

- 3 new keys in `keyStats` namespace across EN · DE · ES · PT · FR · AR:
  `gkPunches`, `gkClaims`, `gkTipped` — GK aerial breakdown row labels for the match stats table

### Post-M9 — Session 13 (2026-06-28)

#### Work Stream E — Remaining parser gaps closed

After a fresh 4-layer audit confirmed all WS-A through WS-C items complete, three full-stack
gaps and one frontend-only gap were identified and implemented.

##### E1 — GK goal prevention detail (PDF pages 34/35)

- **DB:** 5 new columns on `match_gk_stats`: `save_and_retain`, `deflect_and_retain`,
  `save_and_deflect`, `save_attempt`, `no_save_attempt`
- **Adapter:** `pmsr_to_sql.py` — extends GK INSERT to read all 5 sub-fields from
  `intervention_breakdown` dict (was only reading `total_goal_interventions`)
- **Backend:** 5 new fields on `MatchGkStat` model; exposed in `/key-stats` as
  `gk_save_retain`, `gk_deflect_retain`, `gk_save_deflect`, `gk_save_attempt`, `gk_no_save_attempt`
- **Frontend:** `KeyStatsTable.svelte` — conditional row group after "Goal Interventions" total
- **i18n:** 5 keys in `keyStats` namespace across EN · DE · ES · PT · FR · AR

##### E2 — GK crosses faced delivery types (PDF pages 36/37)

- **DB:** 6 new columns on `match_gk_stats`: `crosses_faced_inswing`, `crosses_faced_outswing`,
  `crosses_faced_driven`, `crosses_faced_lofted`, `crosses_faced_cutback`, `crosses_faced_push`
- **Adapter:** `pmsr_to_sql.py` — extends GK INSERT to read all 6 delivery types from
  `crosses_faced_delivery_types` dict (was only reading `total`)
- **Backend:** 6 new fields on `MatchGkStat` model; exposed in `/key-stats` as `gk_crosses_inswing` etc.
- **Frontend:** `KeyStatsTable.svelte` — conditional row group after "Crosses Faced" total
- **i18n:** 6 keys in `keyStats` namespace across all 6 locales

##### E3 — GK name (PDF pages 32/33)

- **DB:** `gk_name VARCHAR(100)` column added to `match_gk_stats`
- **Adapter:** `pmsr_to_sql.py` — writes `goalkeeper` string from `dist_data` (was parsed, never stored)
- **Backend:** `gk_name` field on `MatchGkStat` model; exposed in `/key-stats` as `gk_name`
- **Frontend:** `KeyStatsTable.svelte` — `gkName` row at top of GK group (when present)
- **i18n:** 1 key (`gkName`) across all 6 locales

##### E4 — Player OOP fields in UI (frontend only)

- `pressing_indirect`, `possession_contests_won`, `pushing_on_into_pressing` were already in DB
  and API but not rendered; added to totals grid and per-match detail blocks on `/players/[id]`

##### Re-ingestion

- All 72 match PDFs re-ingested; `04_all_matches.sql` regenerated — all 144 `match_gk_stats`
  rows now have `gk_name`, goal intervention breakdown, and crosses delivery type breakdown

#### Bug fix — PassingNetwork.svelte crash on match detail pages

- `pct_of_team_passes` comes from DB as `DECIMAL`, serialised by Pydantic as a JSON string;
  `toFixed()` on a string throws `TypeError`
- **Frontend fix:** `Number(c.pct_of_team_passes ?? 0)` coercion in both `{#each}` blocks and
  in the `maxPct` derived (was `pct ?? 0` — `??` does not coerce strings)
- **Backend fix:** `PassingConnectionSchema.pct_of_team_passes` changed from `Optional[Decimal]`
  to `Optional[float]` — now serialised as a JSON number

#### Bug fix — PressureDetail.svelte + DefensiveDetail.svelte crashes

- Same `Decimal`→string serialisation bug for `avg_duration_s`, `ball_recovery_time_s`
  (pressure_stats), `possession_actions_per_da` (defensive), and `minute` (shot_events)
- **Backend fix:** `Optional[Decimal]` → `Optional[float]` in `pressure_stats.py`,
  `defensive.py`, `shot_events.py`
- **Frontend fix:** `Number(v).toFixed(2)` in `PressureDetail.svelte` and `DefensiveDetail.svelte`

#### Bug fix — `total_movements` always showing 2026

- PDF header "2026" at `y=13` was captured by the movement total coordinate scan (`390 ≤ x ≤ 430`)
  because the scan had no vertical bound
- **Parser fix:** `parse_pmsr.py` — added `y > 50` to movement total word filter:
  real donut total always appears at `y≈200`; page header year at `y≈13` is now excluded

### Post-M9 — Session 14 (2026-06-28)

#### Bug fix — 5 matches had all page-shifted data wrong (extra shot-log detection failure)

For 53-page PDFs (extra shot-log page), `_count_extra_shot_log_pages()` used a threshold of
`≥ 3` minute-like words at `x < 100` on page 18 to detect the extra page. This failed for
low-shot-count matches (1–2 minute words), causing `extra=0` to be used and all page-shifted
sections (pages 18–53) to read the wrong pages.

- **Affected matches (extra=0 incorrectly):** Türkiye–USA, England–Ghana, Canada–Qatar,
  New Zealand–Egypt, Norway–France
- **Impact:** Home and away movement data swapped; crosses, offerings, movement, pressure,
  GK stats all wrong for these 5 matches
- **Fix:** Replaced word-count heuristic with text-content check:
  `if "Attempts at Goal" in doc[17].get_text("text"): return 1` — reliable across all 23
  tested 53-page PDFs (all have that header on doc[17]; 52-page PDFs have "Crosses" instead)
- **Re-ingestion:** 5 affected PDFs re-ingested and applied; `04_all_matches.sql` regenerated
  for all 72 matches. TUR: `total_movements` now 227 (was 0); USA: 309 (was 227 which was TUR's)

#### GK redesign — dedicated GkDetail component + Goalkeepers tab on players page

The GK stats previously embedded in `KeyStatsTable` are now in a dedicated section at the
bottom of the match page, and aggregated per-goalkeeper on the players page.

##### GkDetail.svelte (new component)

- Dedicated `GkDetail.svelte` component replacing the GK group in `KeyStatsTable`
- Full breakdown: Activity (involvements, distributions, line breaks), Attempts Faced (total +
  save %), Goal Interventions (total + 5-type breakdown), Aerial Interventions (total + punches/
  claims/tipped per complete/incomplete), Crosses Faced (total + 6 delivery types)
- Layout: team A name | section title | team B name; rows only rendered when data is present
- Match detail page: GK Stats section now appears at the bottom (after Movement to Receive),
  not embedded in the key-stats summary at the top

##### GET /api/v1/matches/{id}/gk-stats (new endpoint)

- Dedicated endpoint returning full GK stats for both teams in a match (29 fields per team)
- `match detail +page.ts` fetches it as a 15th parallel request

##### GET /api/v1/stats/goalkeeper-rankings (new endpoint)

- Aggregates `match_gk_stats` by `gk_name + team_id` across all matches
- Returns: matches played, total attempts faced, avg save %, total goal interventions, aerial
  interventions, crosses faced, involvements, distributions — per goalkeeper
- `players/+page.ts` fetches it in parallel with player-stats-summary

##### Players page — Goalkeepers tab

- New "Goalkeepers" tab added to the players page ranking section (6th tab)
- Sortable table: GK name, team, Apps (default sort), Attempts Faced, Save %, Goal Int.,
  Aerial Int., Crosses Faced
- Data sourced from new `/api/v1/stats/goalkeeper-rankings` endpoint

##### KeyStatsTable cleanup

- GK group removed from `KeyStatsTable.svelte` — all GK detail now lives in `GkDetail.svelte`
- 40+ GK-related interface fields still accepted by `TeamStats` (for backward compat with
  key-stats payload) but no longer rendered in the table

### Post-M9 — Session 15 (2026-06-28)

#### Bug fix — NewZealand-vs-Belgium.pdf (54 pages) had all page-shifted data wrong

The 54-page NZL-BEL PDF has two extra shot-log pages (Belgium had an unusually long shot log
requiring three detail pages). The previous `_count_extra_shot_log_pages()` fix capped the
return value at 1, so NZL-BEL was parsed with `extra=1` instead of `extra=2` — causing all
data past page 17 (crosses, offerings, movement, pressure, GK stats) to be read from the
wrong page.

- **Root cause:** Function only checked `doc[17]` and returned at most 1. A 54-page PDF needs
  `extra=2` because both `doc[17]` and `doc[18]` contain "Attempts at Goal".
- **Fix:** `_count_extra_shot_log_pages()` now iterates from `doc[17]` upward, counting all
  consecutive pages that contain "Attempts at Goal". Handles `extra=0/1/2/N` generically:

  ```python
  def _count_extra_shot_log_pages(doc):
      extra = 0
      idx = 17
      while idx < len(doc):
          if "Attempts at Goal" in doc[idx].get_text("text"):
              extra += 1; idx += 1
          else:
              break
      return extra
  ```

- **Verified:** NZL-BEL → `extra=2`; CAN-QAT (53p) → `extra=1`; ALG-AUT (52p) → `extra=0`.
- **Dataset audit:** 72 PDFs — 48×52-page (extra=0), 23×53-page (extra=1), 1×54-page (extra=2).
  No other page-count variants exist in the current dataset.
- **Re-ingestion:** NZL-BEL re-ingested; `04_all_matches.sql` regenerated.
  NZL `total_movements`: 229; BEL: 370 (both now correct and non-zero).

### Post-M9 — Session 16 (2026-06-28)

#### Bug fixes — double borders (GkDetail, DefensiveDetail)

- `GkDetail.svelte` `.gk__subheader`: flipped `border-top` → `border-bottom` to eliminate the
  double-HR pattern (section wrapper bottom border + subheader top border stacking).
- `DefensiveDetail.svelte` `.dd__subheader`: same fix.

#### Bug fix — spatial panel right side empty

- `PitchSpatial.svelte`: `spatial_b` made nullable (`TeamSpatialSplit | null`).
  Added `hasSpatialB` derived guard — shows "No spatial data" placeholder when team B has
  no spatial rows; prevents silent empty render.

#### Feature — clickable team names on match detail page

- `matches/[id]/+page.svelte`: `<span class="team-name">` → `<a href="/teams/{id}">` links.
  Hover: color shifts to `var(--accent)` with underline.

#### Feature — matches page group filter

- `matches/+page.svelte`: `filterGroup` state + `filteredMatches` derived. Filter bar shows
  a `<select>` with all group letters; "Clear filter" button appears when active. Once knockout
  data is ingested, group_letter values like "R32"/"QF" will populate automatically.

#### Feature — players page overhaul

- **Ranking tables — full dataset sorting:** Removed `.slice(0, 20)` cap from all 5 ranking
  arrays (topScorers, topDefenders, topMidfielders, topForwards, physicalLeaders). Clicking a
  column header now re-sorts ALL eligible players; `.slice(0, 20)` applied at render time to
  always show the top 20 of the current sort.
- **Discipline tab (7th):** New tab sorted by yellow + red card total (highest first). Columns:
  #, Player, Team, Cards (total), Yellow, Red, Apps. Sortable on all columns.
- **Browse section hidden on initial load:** Player grid only renders when at least one of
  team/position filter or search query is active. Reduces initial API load and clutter.
- **Table styling:** Removed border/border-radius wrapper, tinted header, and zebra rows from
  ranking tables. Now matches teams-page style: plain `border-bottom` on header, simple hover
  with `var(--border-soft)`, no background decoration.
- **Filter count:** Only shown when a filter is active (not on initial load).
- **Removed empty CSS rule:** Pre-existing empty `.browse-section {}` that caused a
  `svelte-check` warning.

### Post-M9 — Session 19 (2026-06-29)

#### Footer — Impressum, Legal & Contact modals

- **`Footer.svelte`** (new component): small centred footer bar with three ghost-text links —
  Impressum · Privacy & Legal · Contact — each opening a native HTML `<dialog>` modal.
  No separate pages created; all content is inline.
- **Impressum modal:** Dustin Tramm, c/o Impressumservice Dein-Impressum, Stettiner Str. 41,
  35410 Hungen, Germany — § 5 DDG; responsible party, contact email, data source disclosure,
  trademark note
- **Privacy & Legal modal:** 2-column grid (820px max-width, collapses to 1 column at ≤640px),
  4 sections: Privacy Policy, Data & Sources (FIFA Training Centre link), Disclaimer, Copyright
- **Contact modal:** form with Name / Email / Message fields — sends email via the new
  `POST /api/v1/contact` backend endpoint (no `mailto:` client, no new npm deps)
  - Loading state on submit button (`…` label while in-flight, `disabled`)
  - Error banner rendered inline if API responds with a non-OK status
  - Success state with "Send another message" secondary action
- **Backdrop:** `rgba(0,0,0,0.6)` + `backdrop-filter: blur(4px)` via `:global(dialog::backdrop)`
  (must be `:global()` for Svelte scoped CSS to reach the `::backdrop` pseudo-element)
- **Close icon:** inline SVG `<path>` (not Unicode ✕ — Lexend doesn't include it);
  `position: absolute; top: var(--sp-5); right: var(--sp-5)` — reliably top-right on all dialogs
- **Dark mode:** `border: 1px solid var(--border)` on dialog — invisible without explicit border
- **`+layout.svelte`:** `<Footer />` imported and mounted after `<main>`

#### i18n — 31-key footer namespace (all 6 locales)

- `footer` block added to `en.ts`, `de.ts`, `es.ts`, `pt.ts`, `fr.ts`, `ar.ts`
- Keys: `impressum`, `legal`, `contact`, `close`, `impressumTitle`, `impressumSubtitle`,
  `impressumResponsible`, `impressumContactHeading`, `impressumDataHeading`, `impressumDataText`,
  `impressumTrademarkText`, `legalTitle`, `privacyHeading`, `privacyText1`, `privacyText2`,
  `dataHeading`, `dataText`, `dataSource`, `disclaimerHeading`, `disclaimerText`,
  `copyrightHeading`, `copyrightText`, `contactTitle`, `contactName`, `contactEmail`,
  `contactMessage`, `contactNamePlaceholder`, `contactEmailPlaceholder`,
  `contactMessagePlaceholder`, `contactSubmit`, `contactSuccess`, `contactNewMessage`, `contactNote`

#### Backend — contact email endpoint

- **`backend/app/routers/contact.py`** (new): `POST /api/v1/contact`
  - Pydantic `ContactPayload` (`name`, `email: EmailStr`, `message`)
  - In-memory rate limiter: 3 requests per IP per hour (`defaultdict(list)` + timestamp cleanup)
  - SMTP send via Python built-in `smtplib.SMTP` + STARTTLS in `run_in_executor()` (async-safe,
    no new dependencies)
  - Error responses: 429 rate limit, 503 SMTP not configured, 502 SMTP delivery failure
- **`backend/app/config.py`:** `smtp_host`, `smtp_port`, `smtp_user`, `smtp_pass`,
  `contact_to_email`, `allowed_origin` fields added to `Settings`
- **`backend/app/main.py`:** `contact` router imported + `app.include_router(contact.router)`;
  `allow_methods` extended with `"POST"`; `allow_origins=[settings.allowed_origin]` wired up
- **`.env.example`:** `ALLOWED_ORIGIN`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`,
  `CONTACT_TO_EMAIL` documented with inline notes (use Gmail app password)

#### Legal review — FIFA data usage

- EFI Post Match Summary PDFs are freely downloadable at FIFA Training Centre without login.
  No ToS restrictions on download page.
- Only sovereign national flags used (not FIFA IP).
- "World Cup 2026" used descriptively, not as a registered trademark.
- Dashboard is non-commercial.
- Legal disclaimer, data attribution, and Impressum are sufficient. No FIFA permission needed.

#### Git history — "company name" purge

- 3 footer commits that contained "company name" in content/message squashed via
  `git reset --soft <base-commit>` and recommitted clean as a single commit.

### Post-M9 — Session 18 follow-up (2026-06-28)

#### Bug fixes

- [x] Home page — nested `<a>` compile error fixed: outer match-card wrapper converted from `<a>` to `div[role=link]` with `goto()` onclick; inner team-name links remain real `<a>` elements
- [x] Matches page — same nested `<a>` fix applied to `.match-card-link` wrapper
- [x] Home page — xG row and PossessionBar incorrectly removed in session 18; restored below the score row (only the big stat sections below were meant to go)
- [x] Home page — sections 3 & 4 (StatTable, PitchSpatial, PhasesBar, LineBreaksBars, KPI cards) correctly removed; unused imports cleaned up
- [x] Comparison feature — added to ROADMAP as a structured backlog item (scope, UX flow, effort estimate)

### Post-M9 — Session 18 (2026-06-28)

#### Style consistency sweep + UX improvements

- [x] Light mode a11y — `--muted` darkened from `#908a7c` → `#71685c` (contrast 2.83:1 → 4.91:1, passes WCAG AA)
- [x] GK tab — `.slice(0, 20)` added to Goalkeepers tab loop (was showing all 57 GKs)
- [x] Yellow card token — teams/+page.svelte discipline table `.card-yellow` now uses `var(--c-yellow)` (was hardcoded `#d4a017`)
- [x] Border-radius tokens — all `border-radius: 8px` and `border-radius: 10px` replaced with `var(--r-md)` across players, teams/[id], players/[id] detail pages and match card CSS
- [x] Players detail gap — `.section-body` gap `var(--sp-6)` → `var(--sp-5)` in players/[id]
- [x] StatTable hover — `tbody tr:hover` added to `StatTable.svelte`
- [x] Match card restructure — team name now appears below flag+badge (no more ellipsis); formation shown in grey monospace below team name; removed from meta row; team names → `/teams/{id}` links
- [x] Match card group badge — `<abbr title="Group A, Match 1">` so hovering shows full label
- [x] Spatial control empty panel — right panel omitted when `!hasSpatialB` (was 50% white space)
- [x] TermTooltip column headers — applied across Teams ("In Contest") and Players (9 stat columns: Take-ons, TKL Won, Intercep., Passes Att, Ball Progs, Offers, HS Runs, Goal Int., Aerial Int.)
- [x] Home page — xG row and PossessionBar removed; featured match card links to `/matches/{id}`; team names link to `/teams/{id}`; CTA "Check out full game stats →" added
- [ ] Player name links in shot log / passing network — deferred; requires backend `GET /api/v1/matches/{id}/player-name-map` endpoint (TODO comments added)

### Post-M9 — Session 17 (2026-06-28)

#### Bug fix — red cards never stored (parser always emitted "yellow")

The FIFA PMSR PDF encodes all match events (goals, yellow cards, substitutions, red cards) as
colored minute-markers on the lineup page. Yellow cards and red cards both use the same blue
marker color (`COLOR_EVENT = #2E4DFF`). Substitutions off use a red/crimson color
(`COLOR_SUB_OFF = #DC2626`). Red cards also cause the player to leave the field — so they
appear as `COLOR_SUB_OFF` markers with no corresponding `COLOR_SUB_ON` entry.

- **Root cause:** `parse_pmsr.py` classified all `COLOR_SUB_OFF` markers as "subbed off" and
  all `COLOR_EVENT` non-goal markers as "yellow card". No code ever emitted `{"type": "red"}`.
  `pmsr_to_sql.py` always wrote `red_cards=0`.
- **Detection algorithm:** After building player lists for each team, a new
  `reclassify_red_cards()` post-processor collects all `subbed_on` minutes for the team and
  checks each `subbed_off` — if no matching sub-on exists within ±2 minutes, the sub-off is
  reclassified as a red card (`{"type": "red", "minute": m}` added to player's cards list).
  The `subbed_off` key is kept so `minutes_played` is computed correctly in the adapter.
- **Verification:** 72-PDF scan found 12 matches with sub-on/sub-off imbalance (one team has
  an orphaned sub-off). All 12 re-ingested; DB now has 12 red card rows across 12 players.
- **Affected matches re-ingested (12):** Austria–Jordan, Belgium–Egypt, Bosnia–Qatar,
  Canada–Qatar, Iraq–Norway, Morocco–Haiti, Portugal–Uzbekistan, Qatar–Switzerland,
  Spain–Saudi Arabia, Tunisia–Netherlands, USA–Australia, USA–Paraguay.
- `04_all_matches.sql` regenerated.
