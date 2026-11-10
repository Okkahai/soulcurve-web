# Project State — soulcurve-web

Last verified: 2026-11-06, against live GitHub state (`SoulCurve/soulcurve-web`,
branch `main` @ `cd8492c1`) and this repo's own `docs/ARCHITECTURE.md` /
`docs/DECISIONS.md` (themselves last updated 2026-11-04 by PR #14). Mark anything
below unverifiable from here as such — don't upgrade it to "verified" on faith.

## Goals, scope, non-goals

- **Goal:** a Deadlock (Valve game) stats/analysis site — Statlocker/Leetify-tier
  design — that eventually surfaces a per-match win-probability curve and WPA-style
  "where you played badly" coaching, built on a model owned by `soulcurve-model`.
- **Launch model:** free, not paid (decided 2026-09-28 — removes the need for Polar.sh
  payment infra now, and sidesteps deadlock-api's unclear commercial ToS for a
  non-commercial tool). Payments are **not** a current goal.
- **Non-goal (explicit):** a desktop companion app (would need local game-file access,
  a separate Electron/Tauri product) — out of scope for this repo.
- **Non-goal (for now):** anything gated on `soulcurve-model`'s Phase 1 validation —
  see "Blocked / gated" below.

## Architecture — verified facts

Source of truth is `docs/ARCHITECTURE.md` (updated 2026-11-04) and `docs/DECISIONS.md`
in this repo's `main` branch. Don't duplicate their content here; it drifts. Summary
of what they say as of this writing:

- `apps/web` (React + Vite + TS, Recharts for charts) talks to `apps/api` (FastAPI,
  Python 3.12, managed with `uv`).
- Real (live, from `api.deadlock-api.com`) as of PR #14 (merged 2026-11-04): hero/item
  stats and tier list (windowed to the current patch), patch summary, community
  builds (ranked by Wilson-score lower bound), news (Valve's own Steam feed), the
  leaderboard, player match history + skill rating, and the match map's minimap
  image + real objective positions.
- Still mock: the win-probability model itself and everything built on it (match
  analysis / mistake score, net-worth chart, kill positions on the map), per-category
  player grades (deadlock-api's role-stats endpoint is Patreon-only), rank
  distribution, tournaments, and the `/model` transparency page.
- Auth: Steam OpenID 2.0, implemented directly in FastAPI (no OAuth2, no third-party
  auth service).
- Hosting: Vercel for both apps. `apps/web` git-linked to `main` (auto-deploy);
  `apps/api` **not** git-linked as of the 2026-11-04 doc update — redeployed
  manually. This is a known open item (`docs/DECISIONS.md` "Open decisions"). Verify
  current Vercel state before assuming either way.
- DB/cache for Phase 2 (Neon Postgres, Upstash Redis): decided, **not provisioned**,
  not wired into code.

## Decisions and rejected approaches

Full log: `docs/DECISIONS.md` (D1–D6, in this repo). Not reproduced here. Additional
decisions recorded only in Cloud Projects memory (not in that file):
- Monetization: free launch over paid, 2026-09-28 (see "Goals" above). This predates
  and motivates D6's payments item but isn't written into `docs/DECISIONS.md` itself —
  worth adding there or to `docs/agent/DECISIONS.md` (done, see that file) so it isn't
  lost again.
- Charting: `bklit.ui` evaluated 2026-09-28 against the win-probability chart
  specifically (no fixed 0–100% axis, no 50% reference line, no objective markers,
  +73KB gzip) and rejected. Keep Recharts. Branch `experiment/bklit-charts` exists on
  GitHub and must never be merged.
- Visual effects lab (`/lab/effects`, unlisted route added on the old `docs/initial-
  scaffold` branch pre-main-merge): blob tracking and data-mosh rejected outright
  (clashed with the premium/minimal look); a 1-bit ordered-dither home-hero backdrop
  was tried and also reverted. Don't re-propose any of these unless Gün raises it
  again.

## Completed work (verified via merged PRs, all on `main`, CI green)

PR #1 (2026-09-27/28): initial scaffold, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`,
`CONTRIBUTING.md`, CI, `apps/api` + `apps/web` skeletons.
PR #2 (2026-09-28): home Top Players + Blog cards, match-map optimal box routes.
PR #3 (2026-09-28): API moved to Python 3.12 (Vercel build fix).
PR #4 (2026-09-28): 404 page, leaderboard-sourced player names.
PR #5 (2026-09-28): fixed two mock item icons, named build authors, mobile-nav scroll
hint.
PR #6 (2026-09-28): player skill grades, match net-worth chart, rank-scoped item
stats (all still mock at this point).
PR #7 (2026-09-28): fixed unstyled `<select>` options on Windows.
PR #8 (2026-09-28): hero stats wired to real deadlock-api data (first live-data PR;
added `deadlock_client.py`).
PR #9 (2026-09-28): player match history + skill rating wired to real deadlock-api
data.
PR #10 (2026-09-28): leaderboard wired to real deadlock-api data (via steam-search
identity resolution).
PR #11 (2026-09-28): fixed invalid-Steam-ID crash (unhandled `ValueError` → clean 422).
PR #12 (2026-09-28): player search resolves by name, not just numeric Steam ID.
PR #13 (2026-09-28): fixed `skill_percentile` (was badge/MAX, assumed uniform rank
distribution — now a proper CDF-based percentile) and hero/item tier-list ranking
(was raw win_rate with no sample-size adjustment — now Wilson-score lower bound).
PR #14 (2026-11-04): patch-aware stats (current vs. previous patch only, not all-time),
live builds, live patch summary, live news, real minimap/objective positions on the
match map (schematic kept as a toggle).

All 14 PRs were opened and merged by Okkahai (Gün); `DenizYalim` was requested as
reviewer on each but no review/approval is visible in the PR list fetched — if
`CONTRIBUTING.md`'s "every PR needs 1 approval" rule matters to the new setup,
note that it has not been enforced in practice so far.

## Blocked / gated (explicit, from memory — not GitHub state)

- **Real win-probability / match-analysis / net-worth-from-model / model page:**
  blocked on `soulcurve-model` reaching its own Phase 1 (M3) validation gate. See
  `soulcurve-model`'s `docs/agent/PROJECT_STATE.md` for that repo's status — as of
  2026-11-06 it has not started model code yet (planning only).
- **A5 (move the Following feature's storage server-side):** blocked on Neon being
  provisioned (Vercel serverless has no persistent storage of its own).
- **B9 (live in-match overlay):** investigated and found currently infeasible —
  deadlock-api's live/spectate data lags real game time by 60–90s, and a usable
  overlay would need a separate desktop app (same out-of-scope category as the
  companion app). This is a researched conclusion, not an open question — don't
  re-investigate without new information.

## Tests, CI, verification

- CI (`.github/workflows/ci.yml`): `api` job runs `uv sync --locked`, `ruff check`,
  `ruff format --check`, `pytest`; `web` job runs `npm ci`, `npm run lint`,
  `npm run build`. Latest run on `main` (run #69, commit `cd8492c1`, 2026-11-04):
  **success**.
- No GitHub Issues exist in this repo (0 open, 0 closed, checked 2026-11-06) despite
  `CONTRIBUTING.md` describing an issue-tracked workflow. Work tracking has lived
  entirely in Cloud Projects' project memory/thread history, which does not carry
  over automatically — see `docs/agent/TASK_REGISTRY.md` for the reconstruction and
  its gaps.

## Open questions / unresolved

- Is `apps/api`'s Vercel project git-linked yet? (`docs/DECISIONS.md` says not, as of
  2026-11-04 — reverify, since a manual redeploy habit is easy to silently fix without
  updating the doc.)
- Cache layer for Phase 2 (file/SQLite vs. something else) — open per
  `docs/DECISIONS.md`.
- Branch `claude/zealous-dirac-ln9mg5` (single commit, 2026-09-28, "chore: declare
  plugins in repo settings for cloud sessions," adds `.claude/settings.json`) exists
  on GitHub, unmerged, with no associated PR. It's Claude-Code-Cloud-Projects-
  specific tooling config, not product code — likely safe to delete once the
  migration is live, but confirm with Gün before deleting any branch.
