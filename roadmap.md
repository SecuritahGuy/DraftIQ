# DraftIQ - Fantasy Football Analytics Platform
## Progress Summary

**Current Status**: Phase 2 Complete ✅  
**Next Up**: Phase 3 (Scoring engine & projections)

---

Got it, Tim — let's reverse-engineer how FantasyPros hooks into **Yahoo Fantasy Football**, then lay down a clean build plan for a local, Python-backed clone you can run on your machine with SQLite.

# How FantasyPros actually integrates with Yahoo

## Draft phase (Draft Wizard + Browser Extension)

* **Draft Assistant w/ Sync** connects directly to Yahoo draft rooms and automatically crosses off taken players, shows expert ranks/ECR, and lets you make picks without leaving Yahoo’s UI. This is delivered by their **browser extension** (Chrome/Firefox/Edge) which injects a panel into the Yahoo draft page; third-party cookies must be enabled. ([FantasyPros][1], [Draft Wizard][2])
* **Mock drafts & live sync:** You can launch the assistant on **Yahoo live and mock drafts**; for mocks you paste the mock room URL and “Launch My Assistant.” ([FantasyPros][1])
* **Draft Intel:** After you sync a qualifying Yahoo league, FantasyPros mines up to **five years of draft history** to model leaguemate tendencies (e.g., how early they take QB/TE, RB-heavy starts) and feeds that back into the mock draft simulator. ([Draft Wizard][3], [FantasyPros][4], [FantasyPros Product Blog][5])

## In-season (My Playbook)

* **Start/Sit Assistant:** Computes an optimal lineup from expert rankings and supports **one-click lineup submission** back to supported hosts like Yahoo (premium tiers required for submit). ([FantasyPros][6])
* **Waiver Wire Assistant:** Evaluates adds/drops with weekly and ROS impact for your specific Yahoo roster. ([FantasyPros][7], [FantasyPros][8])
* **Trade Analyzer/Finder & League Analyzer:** Pulls your synced Yahoo league data and runs trade value and league-wide analysis. (Sync UI shows Yahoo among supported hosts.) ([FantasyPros][9])
* **Auto-Pilot:** Optional automation that can submit lineups for **inactive-only swaps** or a **full optimal lineup** before kickoff, powered by their rankings and connected to your league host. ([FantasyPros][10], [FantasyPros][11])
* **Extension overlay during season:** The extension can surface lineup advice directly on **Yahoo roster pages** as you view them. ([FantasyPros Product Blog][12])

## Under the hood (what they must be doing)

* **Yahoo OAuth + API:** Yahoo’s Fantasy Sports API exposes leagues/teams/players/draft results and supports authenticated **read and write** (e.g., set lineups, add/drop). OAuth is required; libraries and docs confirm endpoints for draft results, players, rosters, and more. ([developer.yahoo.com][13], [yahoo-fantasy-api.readthedocs.io][14])
* **Write operations are possible:** Community docs for the Yahoo API outline PUTs to edit lineups and POSTs for transactions, which is consistent with Auto-Pilot/one-click flows. ([Rdrr.io][15])

---

# Build a localized “FantasyPros-for-Yahoo” with Python + SQLite

Below is a pragmatic, step-by-step roadmap optimized for a **local FastAPI backend** + **SQLite**, pairing **Yahoo API** for league/roster control with **nfl\_data\_py** for historical stats, depth charts, injuries, and ID mappings.

## Tech choices (battle-tested & local-friendly)

* **Yahoo integration:** `yahoo-fantasy-api` (Python) gives you League/Team/Player/Draft abstractions on top of Yahoo OAuth. It’s active and documented. ([PyPI][16], [yahoo-fantasy-api.readthedocs.io][14])
* **On-field data:** `nfl_data_py` provides weekly/seasonal stats, play-by-play, **depth charts, injuries, snap counts, NGS**, schedules, and a **player IDs mapping** across major platforms (critical for joining Yahoo player\_ids to public data). ([GitHub][17])
* **Why not scrape projections?** Public projections are a licensing thicket; we’ll **compute projections** from nflverse stats, depth charts, usage, and Vegas lines (nfl\_data\_py has the pieces), plus allow **CSV import** for any proprietary projections you have rights to use. ([GitHub][17])

* **Frontend (React) stack:** React 18 + **TypeScript** + **Vite** (fast local dev), **React Router** for routing, **TanStack Query** for server cache & revalidation, **Zustand** for light client state (UI prefs, wizards), **Tailwind CSS** (utility-first) with **Radix UI** primitives for accessibility, **TanStack Table** for large sortable/filterable tables, **Recharts** for responsive charts/sparklines, **React Hook Form** + **Zod** for forms & validation, **date-fns** for time handling, **Lucide** icons, and **sonner** for toasts.
  * **Why this combo:** Query handles async/caching/invalidations; Zustand is minimal and local-only; Tailwind + Radix gives speed + a11y; Table/Charts are battle-tested and tree-shake well.
  * **Build output:** Static assets served by FastAPI (CORS enabled in dev), optional Nginx later for prod.

## Phase 1 — Scaffold & Auth (Yahoo read access)

1. ✅ **FastAPI app + SQLite** (SQLAlchemy 2.0). - **COMPLETED**
   - Basic FastAPI application structure with proper package organization
   - SQLAlchemy 2.0 async database setup with SQLite
   - Configuration management with Pydantic Settings
   - Health check and root endpoints
   - Auto-generated API documentation at `/docs`
   - Database connection pooling and session management

2. ✅ **OAuth flow** with Yahoo (3-legged). Store refreshable tokens encrypted in SQLite. - **COMPLETED**
   - Yahoo OAuth service with authorization URL generation
   - OAuth callback endpoint for token exchange
   - User and YahooToken models for database storage
   - Pydantic schemas for OAuth requests/responses
   - OAuth state management for security
   - Direct authorization redirect endpoint
3. ⏳ **Initial sync endpoints:** - **PENDING**

   * `/yahoo/leagues` – list user’s leagues.
   * `/yahoo/league/{league_key}/pull` – scoring, rosters, draft results, schedule, transactions.
   * `/yahoo/team/{team_key}/roster?week=` – current roster snapshot; cache weekly.

**Why this works:** Yahoo API exposes league metadata, scoring, draft\_results, players, and team rosters; the `yahoo-fantasy-api` shows methods like `draft_results()` and `player_details()` we can lean on. ([yahoo-fantasy-api.readthedocs.io][14])

## Phase 2 — Data model (SQLite first)

Core tables (minimal but extensible):

* `leagues(league_key, name, season, scoring_json, roster_slots_json)`
* `teams(team_key, league_key, manager, name)`
* `players(player_id_yahoo, gsis_id, pfr_id, full_name, pos, team)`
* `league_players(league_key, player_id_yahoo, status, percent_rostered, faab_cost_est)`
* `rosters(team_key, week, slot, player_id_yahoo)`
* `weekly_stats(gsis_id, season, week, stat_json)`
* `weekly_projections(gsis_id, season, week, proj_json, source, created_at)`
* `injuries(gsis_id, week, status, report)`
* `depth_charts(team, week, pos, gsis_id, order)`
* `draft_picks(league_key, round, pick, team_key, player_id_yahoo, cost)`
* `recommendations(team_key, week, lineup_json, delta_points)`

Use `nfl_data_py.import_ids()` to populate cross-walks between Yahoo and GSIS/PFR (we’ll persist a local mapping layer; some manual reconciliation may be required). ([GitHub][17])

## Phase 3 — Scoring engine & projections

1. **Ingest** weekly/seasonal data, injuries, snaps, depth charts (`nfl_data_py.import_weekly_data`, `import_injuries`, `import_snap_counts`, `import_depth_charts`). ([GitHub][17])
2. **Custom scoring compiler:** Parse Yahoo scoring into a dictionary, then compute fantasy points from weekly stats.
3. **Baseline projections:**

   * **Usage-driven** (depth chart order × recent snap share × matchup rate stats).
   * **QB/RB/WR/TE models:** regress last N games with opponent defensive splits; nudge by Vegas totals (available as “scoring lines/win totals” in nfl\_data\_py). ([GitHub][17])
   * Store into `weekly_projections`.
4. **Import projections via CSV** (optional) to override/ensemble.

## Phase 3.5 — React Web UI (Detailed)

**Goal:** A fast, local-first UI that overlays actionable insights on Yahoo or runs as a standalone dashboard. Ship core pages first (Connect → Dashboard → Weekly Lineup) and expand to Waivers/Trades.

### App architecture
* **Routing:** React Router with file-style routes.
* **Data fetching:** TanStack Query (staleTime tuned per endpoint; background refetch; retry/backoff sensible defaults).
* **Client state:** Zustand for ephemeral UI and cross-route prefs (theme, league/team selection, table filters).
* **Styling:** Tailwind CSS + Radix UI primitives (Dialog, Popover, Select, Tabs) for accessibility.
* **Charts/Tables:** Recharts (sparklines, bar/line, area) & TanStack Table (virtualized rows when >500).
* **Forms:** React Hook Form + Zod (schema-inferred types), optimistic UI where safe.

### Route map (v1)
- `/` — **Home/Connect**: show Yahoo auth state; list available leagues; CTA to connect/sync.
- `/auth/callback` — OAuth success/failure handling; redirects to `/leagues`.
- `/leagues` — League picker; recent sync times; per-league settings shortcut.
- `/league/:leagueKey` — **League dashboard**: standings, schedule, injuries, waiver budget, news pulse, scoring summary.
- `/team/:teamKey/week/:week` — **Weekly Lineup**: optimizer, projections vs actuals, lock status, submit lineup.
- `/waivers/:leagueKey` — **Waiver Center**: candidates, projected delta vs replacement, FAAB guidance, claim builder.
- `/trades/:leagueKey` — **Trade Lab**: build packages, team needs heatmap, delta ROS points.
- `/draft/:leagueKey` — **Draft Tools**: pick predictor, VOR board, roster build chart.
- `/settings` — Theme, data refresh cadence, CSV projection import, API base URL.

### Directory scaffold (suggested)
```text
/web
  ├─ index.html
  ├─ src/
  │  ├─ main.tsx
  │  ├─ app.css
  │  ├─ routes/
  │  │  ├─ Home.tsx               # `/`
  │  │  ├─ Leagues.tsx            # `/leagues`
  │  │  ├─ LeagueDashboard.tsx    # `/league/:leagueKey`
  │  │  ├─ Lineup.tsx             # `/team/:teamKey/week/:week`
  │  │  ├─ Waivers.tsx            # `/waivers/:leagueKey`
  │  │  ├─ Trades.tsx             # `/trades/:leagueKey`
  │  │  └─ Draft.tsx              # `/draft/:leagueKey`
  │  ├─ components/
  │  │  ├─ PlayerCard.tsx
  │  │  ├─ PositionSlot.tsx
  │  │  ├─ LineupOptimizerPanel.tsx
  │  │  ├─ ProjectionChart.tsx
  │  │  ├─ SnapShareSparkline.tsx
  │  │  ├─ InjuryBadge.tsx
  │  │  ├─ ByeWeekBadge.tsx
  │  │  ├─ WaiverCandidateRow.tsx
  │  │  ├─ TradePackageBuilder.tsx
  │  │  └─ DataTable.tsx
  │  ├─ stores/
  │  │  └─ useAppStore.ts         # theme, selected league/team, UI prefs
  │  ├─ hooks/
  │  │  ├─ useYahooAuth.ts        # reads auth status from backend
  │  │  ├─ useLeagues.ts          # TanStack Query wrappers
  │  │  ├─ useLineup.ts
  │  │  ├─ useWaivers.ts
  │  │  └─ useTrades.ts
  │  ├─ lib/
  │  │  ├─ api.ts                 # Axios/fetch client with interceptors
  │  │  ├─ queryClient.ts         # shared QueryClient
  │  │  └─ scoring.ts             # client-side helpers for point calc display
  │  └─ types/
  │     └─ api.d.ts               # shared types (OpenAPI-generated if available)
  └─ vite.config.ts
```

### Core screens & components (v1)
**Home/Connect**
- `ConnectYahooButton`: opens `/auth/yahoo/start` in new tab; shows spinner + error states.
- `TokenStatusCard`: indicates token freshness; CTA to re-auth.

**League Dashboard**
- `StandingsTable (DataTable)`: sortable, sticky header, virtualized rows.
- `NewsPulse`: merges injury/inactive headlines for your roster.
- `ScheduleMatrix`: week-by-week opponent view with projected totals.

**Weekly Lineup**
- `LineupOptimizerPanel`: shows current lineup vs **Optimal**; `Apply` button triggers PUT to `/yahoo/lineup/{team_key}`.
- `PositionSlot`: droppable slots; drag players between slots (with rules awareness).
- `ProjectionChart`: area chart of projected vs actual per slot; confidence bands.
- `SnapShareSparkline` + `InjuryBadge` + `ByeWeekBadge` on `PlayerCard`.

**Waiver Center**
- `CandidateFilters`: position, roster %, weeks to playoffs, volatility.
- `WaiverCandidateRow`: delta points vs current worst starter; FAAB guidance; `Add Claim`.

**Trade Lab**
- `TeamNeedsHeatmap`: positional needs across league.
- `TradePackageBuilder`: drag players to My/Their panes; compute delta weekly/ROS.

### Data flow & cache strategy
- **Query keys:** `['leagues']`, `['league', leagueKey]`, `['team', teamKey, week]`, `['waivers', leagueKey]`, `['trades', leagueKey]`.
- **Stale times:** leagues (1h), league meta (30m), lineup (30s during game windows, 5m otherwise), waivers (15m), trades (15m).
- **Invalidations:** after lineup submit → invalidate `team` and `league` queries; after CSV import → invalidate `projections`.
- **Optimistic updates:** lineup assignment (UI reflects change immediately; rollback on error). Disable optimistic for transactions that may fail (waiver claims) and show server result instead.

### API client & typing
- Generate TypeScript types from FastAPI OpenAPI: `openapi-typescript http://localhost:8000/openapi.json -o web/src/types/api.d.ts`.
- Centralized `api.ts` with auth-aware fetch/axios, error normalization, and retry policy.

### Performance & UX
- Route-level **code splitting**; keep above-the-fold first paint < 1s on dev.
- Virtualize large tables; memoize heavy rows (e.g., waiver lists).
- Persist UI prefs in `localStorage` via Zustand middleware.
- **Dark mode** and compact density toggle.

### Accessibility
- Radix components; focus traps on dialogs; color-contrast validated; keyboard nav on tables (arrow keys) and grids (lineup slots).

### Testing
- **Unit/Component:** Vitest + React Testing Library.
- **E2E:** Playwright smoke flows (connect → league → set lineup → submit).

### Local dev & security
- Frontend on `http://localhost:5173`, backend FastAPI on `http://localhost:8000` (CORS allowed in dev).
- No secrets in the client; Yahoo tokens remain server-side; session via HTTP-only cookie or JWT with short TTL.

### Milestones
1. **M1:** Home/Connect + Leagues (auth wired, list leagues).
2. **M2:** League Dashboard (standings, injuries, schedule, scoring summary).
3. **M3:** Weekly Lineup (optimizer + submit lineup).
4. **M4:** Waiver Center (delta calc + claim builder; submit optional).
5. **M5:** Trade Lab (delta & finder MVP).
6. **M6 (optional):** Draft Tools overlay & browser extension bridge (content script calls local API; Shadow DOM to isolate styles).

## Phase 4 — Start/Sit Assistant (with one-click submit)

* **Algorithm:** Evaluate all legal lineup permutations; choose the max projected point lineup (with tie-breakers: volatility, floor, correlation).
* **“One-click” submit:** Call Yahoo roster PUT to apply positions for the week (respect lock times). Community docs show this pattern is supported. ([Rdrr.io][15])
* **UI:** Minimal web UI (React or simple HTMX) + a **browser extension option** to overlay suggestions inside the Yahoo roster page (content script fetches `http://localhost:PORT/recommendation?team_key=...`).

## Phase 5 — Waiver Assistant

* **Add/Drop delta:** For every candidate FA, compute team ROS/weekly delta vs current worst starter (positional replacement).
* **FAAB guidance:** Heuristic based on league scarcity (percent-rostered, expected starts, weeks to playoff).
* **Submit claim** (optional): POST a waiver transaction to Yahoo (respect FAAB or priority rules). Yahoo supports transactions via API. ([Rdrr.io][15])

## Phase 6 — Trade Analyzer

* **Trade impact:** Recalculate weekly and ROS points for both teams under their league scoring; show playoff odds delta if you add a simple Monte Carlo schedule sim.
* **Finder:** Scan the league for Pareto-improving swaps given roster needs.

## Phase 7 — Draft tools (pre-season)

* **League-aware mocks:** Pull **draft\_results** for past seasons to compute league-mate tendencies (“Draft Intel-lite”). ([yahoo-fantasy-api.readthedocs.io][14])
* **Live Draft Assistant:**

  * Sidecar web app with **Pick Predictor** (who’s likely to go before your pick based on ADP & team needs).
  * Optional browser extension overlay during Yahoo drafts, mirroring FantasyPros’ sync experience.
* **Salary-cap/auction mode:** Show budget left, value-over-replacement, and bid curve.

## Phase 8 — Auto-Pilot (opt-in)

* **Policies:** (1) **Inactive-only** swaps 30–60 min before kickoff; (2) **Full optimal** lineup; (3) Position-specific rules (never bench Studs).
* **Execution:** Cron/APScheduler tasks check injuries/inactives and **PUT** new lineups via Yahoo API when a policy triggers. This mirrors the FantasyPros options. ([FantasyPros][10])

---

## Minimal implementation blueprint (copy-paste ready outline)

**FastAPI endpoints**

* `POST /auth/yahoo/start` → redirect to Yahoo OAuth
* `GET /auth/yahoo/callback` → store tokens (encrypted)
* `POST /sync/league/{league_key}` → pulls league meta, teams, rosters, draft\_results (cache)
* `POST /etl/weekly?season=&week=` → imports weekly stats, injuries, depth charts (nfl\_data\_py) ([GitHub][17])
* `POST /score/lineup/{team_key}?week=` → returns optimal lineup JSON
* `POST /yahoo/lineup/{team_key}?week=` → **applies** lineup via Yahoo API (write) ([Rdrr.io][15])
* `POST /waivers/{league_key}` → recommend N targets with projected deltas; optionally submit claim
* `POST /trades/{league_key}/analyze` → trade impact delta

**Key library calls (documented)**

* Yahoo: `lg = yahoo_fantasy_api.League(sc, league_id); lg.draft_results(); lg.players(); lg.team_roster(team_key)` (examples & behavior in docs). ([yahoo-fantasy-api.readthedocs.io][14])
* NFL data: `nfl.import_weekly_data`, `import_injuries`, `import_depth_charts`, `import_snap_counts`, `import_ids` (all listed in README). ([GitHub][17])

**ID Mapping**

* Use `nfl_data_py.import_ids()` to map names/IDs; persist your own `player_id_map` table to bridge **Yahoo player\_id ⇄ GSIS/PFR** reliably. ([GitHub][17])

**SQLite schemas** (abridged)

```sql
CREATE TABLE leagues(
  league_key TEXT PRIMARY KEY, name TEXT, season INT,
  scoring_json TEXT, roster_slots_json TEXT
);
CREATE TABLE players(
  player_id_yahoo TEXT PRIMARY KEY, gsis_id TEXT, pfr_id TEXT,
  full_name TEXT, pos TEXT, team TEXT
);
CREATE TABLE weekly_stats(
  gsis_id TEXT, season INT, week INT, stat_json TEXT,
  PRIMARY KEY(gsis_id, season, week)
);
CREATE TABLE weekly_projections(
  gsis_id TEXT, season INT, week INT, proj_json TEXT, source TEXT,
  created_at TEXT, PRIMARY KEY(gsis_id, season, week, source)
);
```

---

## Practical notes & gotchas

* **Yahoo auth can be finicky** (token refresh, occasional auth changes); lean on maintained wrappers and persist refresh tokens carefully. Community threads reflect auth quirks. ([Stack Overflow][18])
* **Write operations:** Respect lineup lock times & host rules. The API supports PUT for lineups and POST for transactions. ([Rdrr.io][15])
* **Data freshness:** nfl\_data\_py pulls from nflverse; in season, cache weekly and refresh after games/injury reports. The library explicitly supports caching PBP and has weekly/NGS/injury/depth chart imports. ([GitHub][17])

---

## What you’ll have at the end

* A **local Start/Sit assistant** that can **submit** lineups to Yahoo. (FantasyPros equivalent: Start/Sit with one-click submit.) ([FantasyPros][6])
* A **Waiver assistant** that quantifies pickup deltas and can post claims. ([FantasyPros][7])
* A **Draft sidecar** with league-aware mocks and live pick recommendations based on your league’s history (Draft Intel-lite). ([Draft Wizard][3])
* Optional **Auto-Pilot** that enforces your policies before kickoff. ([FantasyPros][10])

If you want, I can spin up a starter FastAPI repo skeleton (auth flow, SQLite models, `nfl_data_py` ETL stubs, and a “set optimal lineup” endpoint) so you can plug it straight into your Sports-Edge workflow.

[1]: https://support.fantasypros.com/hc/en-us/articles/360034462253-How-do-I-use-the-FantasyPros-Browser-Extension-with-my-Yahoo-live-and-mock-drafts?utm_source=chatgpt.com "How do I use the FantasyPros Browser Extension with my ..."
[2]: https://draftwizard.fantasypros.com/football/draft-assistant/?utm_source=chatgpt.com "2025 Fantasy Football Draft Assistant for Yahoo, Sleeper, CBS ..."
[3]: https://draftwizard.fantasypros.com/football/draft-intel/?utm_source=chatgpt.com "2025 Fantasy Football Draft Intel"
[4]: https://support.fantasypros.com/hc/en-us/articles/7844305180187-What-is-Draft-Intel?utm_source=chatgpt.com "What is Draft Intel?"
[5]: https://blog.fantasypros.com/08-22-2023-making-the-most-of-the-mock-draft-simulator/?utm_source=chatgpt.com "Making the Most of the Mock Draft Simulator"
[6]: https://support.fantasypros.com/hc/en-us/articles/115001316467--How-does-the-Start-Sit-Assistant-work?utm_source=chatgpt.com "How does the Start/Sit Assistant work?"
[7]: https://support.fantasypros.com/hc/en-us/articles/115001363868-How-does-the-Waiver-Wire-Assistant-work?utm_source=chatgpt.com "How does the Waiver Wire Assistant work?"
[8]: https://www.fantasypros.com/nfl/myplaybook/waiver-wire-assistant.php?utm_source=chatgpt.com "My Playbook - Waiver Wire Assistant"
[9]: https://www.fantasypros.com/nfl/myplaybook/trade-analyzer.php?utm_source=chatgpt.com "Fantasy Football Trade Analyzer | Trade Calculator"
[10]: https://support.fantasypros.com/hc/en-us/articles/115001832073-What-is-My-Playbook-Auto-Pilot-and-how-does-it-work-NFL?utm_source=chatgpt.com "What is My Playbook Auto-Pilot and how does it work? (NFL)"
[11]: https://www.fantasypros.com/2017/09/my-playbook-auto-pilot-fantasy-football/?utm_source=chatgpt.com "My Playbook Auto-Pilot: The easy, automated way to ..."
[12]: https://blog.fantasypros.com/10-02-2020-setting-your-optimal-lineups-with-the-start-sit-assistant/?utm_source=chatgpt.com "[10/02/2020] Setting your Optimal Lineups with the Start-Sit ..."
[13]: https://developer.yahoo.com/fantasysports/guide/?utm_source=chatgpt.com "Fantasy Sports API - Yahoo Developer Network"
[14]: https://yahoo-fantasy-api.readthedocs.io/en/latest/yahoo_fantasy_api.html?utm_source=chatgpt.com "yahoo_fantasy_api documentation - Read the Docs"
[15]: https://rdrr.io/github/macraesdirtysocks/YFAR/f/vignettes/Yahoo_API_Guide.Rmd?utm_source=chatgpt.com "macraesdirtysocks/YFAR: vignettes/Yahoo_API_Guide.Rmd"
[16]: https://pypi.org/project/yahoo-fantasy-api/?utm_source=chatgpt.com "yahoo-fantasy-api"
[17]: https://github.com/nflverse/nfl_data_py "GitHub - nflverse/nfl_data_py: Python code for working with NFL play by play data."
[18]: https://stackoverflow.com/questions/78894970/yahoo-fantasy-api-oauth2-not-authenticating-some-users?utm_source=chatgpt.com "Yahoo fantasy API oAuth2 not authenticating some users"
