# Pre-1.0 Audit — EFI World Cup 26 Data Engine

**Date:** 2026-07-11 · **Baseline commit:** `e7f289d` · **Scope:** full repo
(backend, ingestion, frontend, DB, Docker, CI, docs).

Five parallel audits were run — **Security**, **Backend/Ingestion correctness
("Fallstricke")**, **Frontend best-practices**, **Accessibility (BFSG → EN 301 549
→ WCAG 2.1 AA)**, and **Dependency currency/CVEs**. Every finding was verified by
reading the actual code; contrast ratios were computed from the real design tokens.

This document is the complete record: **what was fixed for 1.0** and **what is
deferred** as a tracked backlog. It is deliberately honest about the remaining
gaps — see [§7 Known limitations & conformance statement](#7-known-limitations--conformance-statement).

Verification after remediation: `svelte-check` 0 errors / 0 warnings · `npm run
build` green (adapter-node) · `npm run lint` green · backend pytest 10/10 ·
ingestion pytest 14/14 · live smoke test on the running Docker stack green.

---

## 1. Summary

| Area | Critical | High | Medium | Low/Info | Fixed for 1.0 | Deferred |
| --- | --- | --- | --- | --- | --- | --- |
| Security | 0 | 0 | 3 | 10 | 6 | 7 |
| Backend/Ingestion | 0 | 3 | 9 | 11 | 6 | 17 |
| Frontend | 1 | 2 | 6 | 11 | 6 | 14 |
| Accessibility | 2 | 7 | 14 | 10+ | 9 groups | long tail |
| Dependencies | — | — | — | — | 5 | rest documented |

No Critical **security** issues. The one **Critical frontend** issue (production
API base URL) and both **Critical accessibility** issues (keyboard operability)
were fixed.

---

## 2. Security audit

### Fixed for 1.0

| # | Sev | Finding | Fix |
| --- | --- | --- | --- |
| S1 | MED | SQL injection via crafted PDF — `_q`/`_qs` in `ingestion/ingestion/pmsr_to_sql.py` doubled `'` but not `\`; MySQL's default `sql_mode` has no `NO_BACKSLASH_ESCAPES`, so a PDF free-text field ending in `\` could break out of the string literal. | `_q`/`_qs` now escape `\` then `'`. `watch_pdfs._execute_sql` uses `exec_driver_sql` (no `:param` reinterpretation). |
| S2 | MED | docker-compose published MySQL on `0.0.0.0:3306` with weak default creds (`rootpw`/`wc26pass`). | Bound `db` and `backend` to `127.0.0.1`. |
| S3 | MED | `POST /ingest/upload` read the whole body into RAM before the 50 MB check. | Reject on declared `file.size` before `read()`. |
| S4 | LOW | Contact form 500'd on a name containing CR/LF (unhandled `ValueError` from `EmailMessage`). | Pydantic `field_validator` rejects control chars in `name` (also blocks header injection); length-capped. |
| S5 | LOW | `sa.text()` reinterpreted `:word` tokens in generated SQL as bind params. | Switched to `exec_driver_sql` (same fix as S1). |
| S6 | LOW | mysql:8.0 image past EOL. | Pinned `mysql:8.0.46` (8.4 LTS migration tracked post-1.0). |

### Deferred (documented, accepted or low-risk)

- **S-D1 (LOW)** Contact rate limiter is in-memory/per-process and keys on
  `request.client.host` — behind Passenger this is the proxy IP, so all clients
  share one 3/h budget (over-throttle, not a bypass). Needs a shared store +
  trusted-proxy `X-Forwarded-For` handling.
- **S-D2 (LOW)** CORS localhost regex (`main.py`) is always enabled, incl. in
  production. Not exploitable (`allow_credentials` false, data is public
  read-only, Starlette uses `fullmatch`), but should be dev-gated.
- **S-D3 (LOW)** Ingest bearer token stored in browser `localStorage` on the
  admin page when "remember" is checked. No XSS vector exists today (no `{@html}`
  anywhere; Svelte auto-escapes).
- **S-D4 (LOW)** Containers run as root (no `USER` in the three Dockerfiles).
- **S-D5 (LOW)** Weak hardcoded DB credential defaults in `config.py` /
  `watch_pdfs.py` (fail-open instead of fail-fast if env unset).
- **S-D6 (INFO)** FastAPI `/docs` `/redoc` `/openapi.json` public (reveal the
  token-protected ingest endpoint).
- **S-D7 (INFO)** Python deps are unpinned `>=` floors (no lockfile) — see §6.

### Checked and found OK

Ingest auth uses `secrets.compare_digest`, 503 when unconfigured (fails closed);
file validation covers extension + `%PDF-` magic bytes + path-traversal
(`Path(...).name`, `resolve()`, `dest.parent == watch_dir`); subprocess uses an
arg list with `shell=False`; email `To` fixed to owner (no open relay); all data
routers use SQLAlchemy ORM `select()` (no string-built SQL; repo-wide grep
clean); typed path/query params → 422; no `{@html}`/XSS; SSR fetch base URL is
fixed config (no SSRF); `.env*` gitignored, no real secrets committed; CI has no
`pull_request_target` / event-title injection; DB seeds contain no `GRANT`/`CREATE
USER`.

---

## 3. Backend & ingestion correctness ("Fallstricke")

### Fixed for 1.0

| # | Sev | Finding | Fix |
| --- | --- | --- | --- |
| B1 | HIGH | `make contract` ran `python app/export_openapi.py`, putting `backend/app` (not `backend`) on `sys.path` → `ModuleNotFoundError: app`. The stated contract-drift gate could never run. | Run as module: `python -m app.export_openapi`. |
| B2 | LOW→HIGH* | `parse_page1` parsed the date with `strptime("%d %B %Y")`, which depends on process `LC_TIME`. On a non-English host (the German cron/Passenger target) **every ingest would fail**. | Locale-independent English month map (`_parse_pmsr_date`). |
| B3 | MED | Contact SMTP had no socket timeout (a black-holed host hangs the worker) and only caught `SMTPException` — a DNS/refused `OSError` surfaced as 500. | `timeout=15`; `except OSError → 502`. |
| B4 | LOW | `_q`/`_qs` backslash escaping (same as S1). | Fixed. |
| B5 | LOW | `/health/db` returned a raw 500 with a stack trace on DB outage. | Returns 503 on `SQLAlchemyError`. |
| B6 | INFO | Upload memory (same as S3). | Fixed. |

\* Rated LOW by the auditor generically, but HIGH for **this** deployment
(documented German host).

### Deferred (tracked backlog)

- **B-D1 (HIGH)** `match_pressure_stats.direction_inside/outside` are NULL for
  all 192 rows — `_p29_val` looks up a stat name (`Direction - Inside`) that
  `parse_page29` never emits. Either extract the split or drop the two columns.
  Needs a parser change + re-ingest.
- **B-D2 (HIGH)** Extra shot-log page handling (`extra≥1`) can misattribute or
  drop the home team's page-2 shots (goal-minute map stays correct, masking the
  loss). Needs page-by-team classification + a per-team shot-count reconciliation
  check. **Action item:** confirm whether any current PDF actually spilled.
- **B-D3 (MED)** Substitutes later subbed off get `final_whistle − sub_on`
  minutes instead of `sub_off − sub_on` (over-counts, esp. in AET matches).
- **B-D4 (MED)** A few raw `{leng}`/`{wid}`/`{ph.get(...)}` interpolations can
  emit Python `None` into SQL → whole-match rollback on a partial parse. Route
  through `_n()`.
- **B-D5 (MED)** N+1 query patterns in `/stats/leaderboards` (~190 sequential
  round-trips), `/teams/{id}/avg-stats`, `/teams/{id}/matches`. Performance, not
  correctness; batchable into grouped queries.
- **B-D6 (MED)** `matches` upsert never updates `group_letter`/team ids; a stage
  string not in `KNOCKOUT_LABELS` inserts `group_letter=NULL` silently and the
  match then matches neither `?stage=group` nor `knockout`. Raise on unmapped
  stage + add `group_letter=VALUES(group_letter)`.
- **B-D7 (MED)** Most list endpoints use `response_model=dict`/`list[dict]`, so
  the OpenAPI→TS contract gate is largely vacuous for the biggest responses.
- **B-D8 (MED)** Upload writes `dest.write_bytes` non-atomically; the 5-min cron
  can glob a half-written file. Write `.part` then `os.rename`.
- **B-D9 (MED)** Test coverage: `parse_pmsr.py`, `pdf_to_sql`, and most routers
  are untested; `backend/tests/factories.py` is broken-if-used dead scaffolding.
  Add a golden-file `pdf_to_sql` test + router 404/422 tests.
- **B-D10 (LOW)** Nullable DB columns vs non-Optional Pydantic fields
  (`line_break`, `spatial`, `phase`) → latent 500 on a NULL row.
- **B-D11 (LOW)** `pass_completion_pct` returns `null` when a side completed 0
  passes (guard tests `passes_comp` instead of only `passes_att`).
- **B-D12 (LOW)** `.processed_pdfs` grows unboundedly on forced re-uploads;
  stores absolute paths.
- **B-D13 (LOW)** Single-PDF CLI prints a human "Parsing…" line to stdout,
  polluting `> seed.sql`. Print progress to stderr.
- **B-D14 (LOW)** `process_all` moves PDFs to `done/` before the combined SQL is
  written.
- **B-D15 (LOW)** `players` uniqueness `(team_id, jersey_number)` allows dup rows
  when the number is NULL; name-based fallback subquery has no `ORDER BY`.
- **B-D16 (LOW)** `backend/Dockerfile` runs uvicorn `--reload` in the compose
  path; dev/test deps shipped in the prod image; `respx`/`testcontainers`
  unused.
- **B-D17 (INFO)** Trailing-slash 307s; unweighted stat averages;
  `/players/{id}/stats` is a subset of `/players/{id}`; `_i`/`_f` helper
  duplication; `player-name-map` collapses two same-named players;
  `final_third_entries` covers only 40/96 matches (seed-only, no PDF source) and
  its seed `DELETE`s globally.
- **B-D18 (MED)** `POST /ingest/upload` cannot work inside the compose **backend**
  container (no `ingestion` package / PyMuPDF there) — it targets the Passenger
  deploy. On failure it also unlinks the PDF. Documented deployment constraint;
  the cron watcher in the `ingestion` service is the compose ingestion path.

### Checked and found OK

`match_stats` team-perspective mirroring is consistent across all readers; every
`ON DUPLICATE KEY UPDATE` has a matching unique key incl. the `match_key`
generated column; ORM matches `01_schema.sql` across all 20 tables; shot minutes
integer-encoded (stoppage time preserved); async hygiene (blocking smtplib /
subprocess wrapped in `to_thread`); invalid ids → 404, bad `stage` → 422, empty
DB dashboard → clean 404; indexes cover the router query patterns; no
dead references to the removed `tournament_overview`/`is_featured`/legacy modules.

---

## 4. Frontend best-practices

### Fixed for 1.0

| # | Sev | Finding | Fix |
| --- | --- | --- | --- |
| F1 | **CRIT** | `import.meta.env.PUBLIC_API_URL` is always `undefined` in the browser bundle (Vite only exposes `VITE_`-prefixed vars). Client-side navigations fell back to `http://localhost:8000`, so in the split-origin Passenger deploy every page after the first — and the admin upload — broke. | New `$lib/api-base.ts` using `$env/dynamic/public`; all 11 loaders + admin use it. Verified: production build green. |
| F2 | HIGH | Lint gate dead — ESLint 9 had no flat config; `npm run lint` exited non-zero. | Added `eslint.config.js` + `.prettierrc`; `npm run lint` green (see §5 note). |
| F3 | MED | `phaseColor` fell back to undefined `--c-muted`. | → `--muted`. |
| F4 | LOW | Dead `NavTabs.svelte` residue partially cleaned (unused token imports removed across 5 files incl. dead `PhasesBar` import in teams/[id]). | Removed. |
| F5 | — | `+layout.svelte` typed `data` as `PageData` not `LayoutData`. | Fixed. |
| F6 | — | Several hardcoded strings wired to i18n (see §5 a11y — PossessionBar, matches group filter, skip link). | Fixed subset. |

### Deferred (tracked backlog)

- **F-D1 (HIGH)** Locale/RTL init is client-only (`onMount`), so SSR always
  ships `lang="en"` LTR → content/layout flash for DE/AR users, wrong `lang` for
  SEO/SR. Fix: persist locale in a cookie, set `lang`/`dir` in a server `handle`
  hook. (Also A11Y M2.)
- **F-D2 (MED)** ~20 hardcoded English strings/aria-labels remain despite a fully
  synced 632-key dictionary (`+error.svelte`, 5 route `<title>`s, TopBar/
  ThemeSwitch labels, compare empty-state, etc.). Dictionaries mostly already
  have the keys.
- **F-D3 (MED)** Date/number formatting hardcodes `en-GB`/`de-DE` regardless of
  active locale.
- **F-D4 (MED)** `+page.ts` dashboard returns `null as unknown as DashboardData`
  — type lie masking nullability (guard exists, only the type is wrong).
- **F-D5 (MED)** `efi.ts` incomplete vs backend (`DefensiveAction` 2/17 fields,
  `MatchStats` missing `shots_*`), forcing `as`-casts in 8 components.
  `openapi-typescript` is installed but unused.
- **F-D6 (MED)** Compare load waterfall (`loadSearchOptions` before entity
  fetches); TermTooltip nests a second `Tooltip.Provider`.
- **F-D7 (LOW)** Deprecated `$app/stores` (use `$app/state`); `_kitchen-sink`
  route ships publicly; trailing-slash mismatch (`/matches` vs `/matches/`);
  layout fetches the full match list for a count; silent partial failures on
  match detail's 17 sub-fetches.

### Checked and found OK

Svelte 5 runes used correctly (only 2 intentional `$effect`s); all
`localStorage`/`window`/`document` access SSR-guarded; no memory leaks (no stray
intervals/listeners); every `+page.ts` catches fetch failures → friendly error
state (empty DB → 404 → error UI, no 500); **all six locale files have exactly
the same 632 keys** (verified by key-set diff); teardown residue gone (no refs to
the 5 removed modules or `$lib/api`); wire field names match FastAPI by-alias
serialization; adapter-node matches DEPLOY.md's Passenger setup.

---

## 5. Accessibility (BFSG → WCAG 2.1 AA)

Legal baseline: Barrierefreiheitsstärkungsgesetz → EN 301 549 → WCAG 2.1 AA.

### Fixed for 1.0

| Group | SC | Finding | Fix |
| --- | --- | --- | --- |
| A1 | 1.4.3 | **Contrast** — team-color text failed AA: teal/orange on light, red/blue/indigo on dark; `card-yellow` 1.29:1; position tags 1.3–2.0:1; `.positive` used an undefined var. | Added contrast-safe `-ink` variants (both themes) for teal/orange/red/blue/indigo; `teamTextColor` routes every spectrum color through its `-ink`; fixed card-yellow, GK/DF/MF/FW tags, `.positive`. All computed ≥4.5:1. |
| A2 | 1.4.3 | Local `badgeTextColor` override in `teams/[id]` produced failing white-on-light badges. | Deleted; imports the central (passing) `tokens.ts` version. |
| A3 | 2.1.1 | **Keyboard** — 41 sortable `/players` `<th>` were click-only. | `sortableHeader` action: focusable + Enter/Space, keeps `columnheader` role. |
| A4 | 2.1.1 / 4.1.2 | **Keyboard** — compare search dropdown was mouse-only (`onmousedown`, no combobox semantics). | Real ARIA combobox: arrow/Enter/Escape, `aria-expanded`/`-controls`/`-activedescendant`, accessible label, visible active option. |
| A5 | 1.1.1 / 4.1.2 | `role="img"` on text-bearing figures flattened live data and swallowed nested links/toggles (PossessionBar, PhasesBar, LineBreaksBars, FinalThirdZones). | Removed `role="img"`; content is real labeled text. |
| A6 | 4.1.2 | Toggle/filter groups exposed no state. | `aria-pressed` on matches stage pills, PitchSpatial scenario+block toggles, FinalThirdZones team toggle; `aria-current` on teams/players stage links. |
| A7 | 2.4.1 | No skip link. | Skip-to-content link → `<main id="main" tabindex="-1">`; `a11y.skipToContent` added to all 6 locales. |
| A8 | 3.1.2 | Hardcoded English in touched components. | Translated PossessionBar "In Contest" and the matches group-filter label. |
| A9 | 1.4.1 | `phaseColor` invisible fallback (also F3). | Fixed. |

### Deferred (tracked backlog — see §7)

- **A-D1 (MED, 3.1.1/1.3.2)** `<html lang>`/`dir` client-only (same as F-D1) —
  SSR ships `lang="en"` LTR for all locales.
- **A-D2 (MED, 4.1.3)** Async status/results not announced (contact & admin
  forms, filter/search counts) — need `role="status"`/`role="alert"`/`aria-live`.
  (FloatingCompareBar already does this correctly — copy the pattern.)
- **A-D3 (MED, 1.3.1)** Several stat blocks rendered as `<div>` grids rather than
  `<table>`/`<th scope>` (KeyStatsTable, ShotTimeline, GkDetail, Cross/Offer/
  Movement/Pressure/Defensive detail); `StatTable` uses `<table>` but no `<th>`.
- **A-D4 (MED, 1.3.1)** Match detail page has no headings (`SectionLabel`
  renders `<p>`); add a heading level prop + an `<h1>`.
- **A-D5 (MED, 4.1.2)** `role="tablist"` on players ranking tabs without
  panels/arrow-key model; `aria-sort` not yet set on the (now keyboard-operable)
  sortable headers.
- **A-D6 (MED, 2.4.3)** Mobile menu: no Escape, no focus trap, page behind stays
  tabbable; native `<dialog>`s lack `aria-labelledby`.
- **A-D7 (MED, 1.4.1)** Shot log encodes team by color only — add a short-code
  column/prefix.
- **A-D8 (MED, 3.3.2)** ~20 placeholder-only/English-only control labels (same
  set as F-D2).
- **A-D9 (LOW)** `abbr title` hover-only; emoji event icons; `html,body{font-size:16px}`
  overriding user prefs; small touch targets (WCAG 2.2 2.5.8, not 2.1);
  accent-on-`--bg` marginal 4.45:1; cryptic zone abbreviations.

### What passes (verified)

Global `:focus-visible` ring; `prefers-reduced-motion` kill-switch; zoom/reflow
(tables in `overflow-x:auto`, no orientation lock); landmarks present & singular;
top-nav `aria-current` + burger `aria-expanded`; FloatingCompareBar is a correct
live region; native `<dialog>` focus-trap+Escape; flags `aria-hidden` with
adjacent text; central `badgeTextColor` ≥4.97:1; core `--ink`/`--muted`/accent
contrast passes both themes; no keyboard traps.

---

## 6. Dependency currency & CVEs (as of 2026-07-11)

### Fixed for 1.0

- `pymysql>=1.1.1` (was `>=1.1.0`, admitted CVE-2024-36039 SQLi).
- `python-multipart>=0.0.32` (was `>=0.0.9`, admitted several CVEs — parses
  untrusted form data).
- `cryptography>=44.0.0` (was `>=42.0.0`).
- `mysql:8.0` → `mysql:8.0.46` (8.0 major EOL 2026-04-30).
- Test container + CI Node 20 (EOL) → 24.

### Deferred / documented

- **Accepted risk:** `asyncmy` CVE-2025-65896 (SQLi via dict keys, CVSS 9.8) has
  **no fixed release**. Practical exposure is low — SQLAlchemy generates its own
  bind keys; no raw dict-key interpolation reaches query params in this codebase.
  Watch for a fix or consider `aiomysql`.
- **Accepted risk:** `cookie <0.7.0` low-sev advisory via `@sveltejs/kit` — no
  upstream fix; `npm audit fix --force` would destructively downgrade kit. Do not.
- **Post-1.0, prioritized:** mysql 8.4 LTS migration (8.0 EOL); vite 8 + vitest 4
  batch (clears 2 critical + 1 high **dev-only** advisories — not in the
  adapter-node prod bundle); eslint 10 / TS 7 / pytest 9 majors.
- **Recommended before publish:** `npm update` (safe minors: kit 2.69.2, svelte
  5.56.4, adapter-node 5.5.7, etc.) + `npm audit fix` (js-yaml, dev-only). Pin
  Python deps to exact tested versions (currently `>=` floors, no lockfile).

Docker base images otherwise fine: `python:3.11-slim` (security support to
2027-10), `node:24-slim` (LTS). No `:latest` tags. GitHub Actions are 1–3 majors
behind (CI-only, no runtime risk).

---

## 7. Known limitations & conformance statement

**This 1.0 does not claim full WCAG 2.1 AA / BFSG conformance.** The two Critical
keyboard blockers, the systemic contrast failures, the worst `role="img"` data
loss, and state-exposure on the primary filters were fixed and verified. A
**tracked backlog remains** (§3–§5 "Deferred"), most notably:

1. **SSR locale/`lang`/`dir`** (A-D1/F-D1) — the largest single a11y+i18n gap.
2. **Async status announcements** & **table semantics** for the stat grids
   (A-D2/A-D3).
3. **Remaining hardcoded control labels** (A-D8/F-D2).
4. **Backend data-integrity re-ingest items** — pressure-direction NULLs (B-D1)
   and extra-shot-log attribution (B-D2) require a parser fix + full re-ingest.

None of the deferred items block a portfolio/soft launch, but the a11y backlog
should be closed before the product is marketed as BFSG-conformant. This
document, `CHANGELOG.md`, and `ROADMAP.md` track every item.
