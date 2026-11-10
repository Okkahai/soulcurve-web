# CLAUDE.md — soulcurve-web

Claude-specific notes. The provider-neutral rules live in `AGENTS.md` — read that
first; this file only adds what's Claude-specific.

## Context

This repo was built almost entirely through Claude Code Cloud Projects (one
project, one long-running thread per feature batch, each producing a PR). That
setup is being migrated to local T3 Code / Claude Code / Codex CLI with git
worktrees and independent reviewers. `docs/agent/HANDOFF.md` has the full
migration context; `docs/agent/PROJECT_STATE.md` has current repo state.

## Attribution

Historical commits in this repo carry `Co-Authored-By: Claude ... <noreply@anthropic.com>`
and a `Claude-Session:` URL pointing at a Cloud Projects session — those sessions no
longer exist once the migration completes. Don't rely on a `Claude-Session` link in
an old commit message resolving to anything; treat the commit diff and message as
the record, not the link.

## Working style the owner (Gün) has stated

- Wants steady autonomous progress through an agreed backlog, not a "which feature
  next?" checkpoint every item. Surface results at milestones or blockers, not every
  small step.
- Wants visual proof (screenshot/demo) at real checkpoints, not after every change.
- Expects commands to actually be run and their output read before anything is
  called done.

These are working-style preferences recorded in the old Cloud Projects memory, not
enforced by anything in this repo. Confirm they still hold with Gün if the new setup
changes how often an agent reports in.
