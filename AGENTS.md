# AGENTS.md — soulcurve-web

Provider-neutral rules for any coding agent (Claude Code, Codex CLI, T3 Code, or a
human) working in this repo. Written 2026-11-06 as part of the migration off Claude
Code Cloud Projects to a local multi-agent setup. See `docs/agent/` for full state.

## What this repo is

Monorepo for SoulCurve's app side: `apps/api` (FastAPI, Python, uv) + `apps/web`
(React + Vite + TypeScript). Companion repo `soulcurve-model` (DuckDB + LightGBM/
XGBoost) owns the win-probability model; this repo consumes it, doesn't build it.

Read first, in order:
1. `docs/agent/PROJECT_STATE.md` — current reality, verified vs. assumed
2. `docs/agent/TASK_REGISTRY.md` — open work items
3. `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` — the pre-existing, still-authoritative
   architecture/decision log (not superseded by this migration, just indexed by it)
4. `CONTRIBUTING.md` — branch/PR/commit conventions

## Non-negotiable rules (from the project owner, Gün)

- **Don't write library APIs from memory.** Verify against current docs (Context7 or
  the library's own docs) before using an API you haven't checked this session.
- **Don't say "done" without having run it and read the output.** "Should work" is
  not done. This applies to tests, builds, and manual browser checks alike.
- **Full English only** in UI copy and user-facing text. No Turkish strings in
  `apps/web/src`.
- **Design bar:** premium, Statlocker/Leetify-level. Not a bare-bones dashboard.
- **Don't propose payment/subscription work.** The site launched free (2026-09-28
  decision); payments are explicitly deprioritized. See `docs/DECISIONS.md` D6 and
  `docs/agent/DECISIONS.md`.
- **Phase gate:** real win-probability/match-analysis features depend on
  `soulcurve-model` reaching its Phase 1 (M3) validation gate. Don't build match
  win-probability, net-worth-from-model, or the model page as if the model exists —
  it doesn't yet.
- **Rejected, do not re-propose:** `bklit.ui` for charts (keep Recharts — branch
  `experiment/bklit-charts` exists and must never be merged); the blob/data-mosh/
  1-bit-dither home-page background effects (all tried and reverted 2026-09-28).

## Working agreement

- CI: `.github/workflows/ci.yml` runs `uv sync --locked && ruff check && ruff format
  --check && pytest` for `apps/api`, and `npm ci && npm run lint && npm run build`
  for `apps/web`. Both must be green before merging.
- Tests mock `deadlock-api` calls via `respx` (see `apps/api/tests/conftest.py`'s
  `deadlock_api` fixture) rather than hitting the network.
- `CONTRIBUTING.md` describes an issue-tracked, two-reviewer workflow. **In practice,
  as of 2026-11-06, this repo has zero GitHub Issues** — all backlog, priorities and
  decisions lived in Claude Code Cloud Projects' memory and thread history instead.
  That history does not transfer automatically; `docs/agent/TASK_REGISTRY.md` is the
  best-effort reconstruction. Treat GitHub Issues as the task tracker going forward
  if the new orchestration setup needs one — nothing currently enforces that.
- Branch naming to date has been `claude/project-thread-<id>` (one long-lived branch
  per Cloud Projects thread, reused across many PRs) rather than the
  `<type>/<issue-no>-<description>` pattern `CONTRIBUTING.md` specifies. Follow
  `CONTRIBUTING.md`'s convention for new work under the new setup.

## Environment variables (names only — see `apps/api/.env.example`)

`MODEL_VERSION`, `DEADLOCK_API_BASE_URL` (defaults to `https://api.deadlock-api.com`),
`CACHE_DIR`. `apps/web/.env.example` has its own (check the file — not reproduced
here to avoid drift).

## Deploy

Both apps run on Vercel. `apps/web` is git-linked to `main` (auto-deploy). `apps/api`
was **not** git-linked as of the last verified doc update (2026-11-04) — see the open
item in `docs/DECISIONS.md`. Verify current Vercel project settings before assuming
either state; this is exactly the kind of fact that can silently drift.
