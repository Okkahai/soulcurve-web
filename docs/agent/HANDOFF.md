# Handoff — soulcurve-web

Written 2026-11-06 for the migration from Claude Code Cloud Projects to a local
T3 Code / Claude Code / Codex CLI + git-worktree setup with independent reviewers
and GitHub CI. Read `docs/agent/PROJECT_STATE.md` and `docs/agent/TASK_REGISTRY.md`
first; this file is the narrative connective tissue between them.

## What a new coordinator needs to know immediately

1. **This repo is in good shape.** `main` is green on CI, 14 PRs merged cleanly, no
   open PRs, no open issues, no merge conflicts. There is nothing broken to fix
   before new work starts.
2. **The product is real-data-backed for most of its stats surface, but the model
   itself doesn't exist yet.** Anything touching win-probability, match analysis,
   net worth derived from the model, or the `/model` page is still mock and gated on
   `soulcurve-model`'s own validation. Don't "finish" those pages without checking
   that repo's state first.
3. **There is no issue tracker.** `CONTRIBUTING.md` describes one; it was never set
   up. All of the backlog/priority context lived in Cloud Projects' project memory
   and thread history, which is why this migration exists. `docs/agent/TASK_REGISTRY.md`
   is the best reconstruction available; treat gaps in it as real gaps, not as "it's
   probably fine."
4. **Two loose ends on GitHub, not on `main`, need a human decision:**
   - `experiment/bklit-charts` — explicitly rejected, must never be merged. Safe to
     delete once everyone building here knows not to revive it, but that's Gün's
     call, not an agent's.
   - `claude/zealous-dirac-ln9mg5` — a one-commit branch adding
     `.claude/settings.json` (plugin config for Cloud Projects sessions). Irrelevant
     once the migration completes; likely safe to delete, but again, confirm first.

## What this migration thread did and did not do

- Did: read every PR, branch, commit, and the live `docs/ARCHITECTURE.md` /
  `docs/DECISIONS.md` on `main`; cross-checked against Cloud Projects project memory;
  wrote the `docs/agent/` files and root `AGENTS.md`/`CLAUDE.md` you're reading.
- Did not: write, change, or delete any product code. Did not push to `main`. Did not
  merge, close, or cancel anything. Did not delete any branch, including the two
  flagged above.
- Could not: inspect any other Cloud Projects thread's live/internal state (no tool
  for that from here) — so "uncommitted work in another thread" is a structural gap
  this handoff cannot close, only flag. Based on the evidence gathered (clean `main`,
  no open PRs, no draft branches beyond the two named above), there's no sign of
  substantial unpushed work, but that is inference from absence of evidence, not
  direct confirmation.

## Recommended first actions for the new setup

1. Open this PR, read it, merge it (or ask for changes) — it's documentation only,
   zero behavior change.
2. Decide what to do with `experiment/bklit-charts` and `claude/zealous-dirac-ln9mg5`.
3. Decide whether to stand up GitHub Issues (or another tracker) using
   `docs/agent/TASK_REGISTRY.md` as the seed list — the current state (zero issues,
   memory-based backlog) won't survive the move to a setup with independent
   reviewers who need a shared, durable task list.
4. Re-verify the two "unverified" facts in `PROJECT_STATE.md` (Vercel git-link status
   for `apps/api`; whether group-D "small polish" items got done) by checking Vercel
   directly and by asking Gün, respectively — don't carry them forward as fact.
5. Only then pick up new feature work, respecting the Phase 1/Phase 2 gate on
   `soulcurve-model`.
