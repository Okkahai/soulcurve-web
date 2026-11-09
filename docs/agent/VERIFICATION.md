# Verification — soulcurve-web

How this migration's claims were checked, as of 2026-11-06, so a new coordinator can
tell "I verified this" from "I was told this."

## Verified directly against GitHub (facts, not inference)

- `main` @ `cd8492c1`, CI green (run #69, 2026-11-04), 14 merged PRs (#1–#14), 0 open
  PRs, 0 open issues, 0 closed issues (issue tracker unused).
- Branches present beyond `main`: `docs/initial-scaffold` (pre-merge, superseded),
  `claude/project-thread-4id3sz` (the PR work branch, now merged, safe to consider
  stale), `claude/zealous-dirac-ln9mg5` (unmerged, 1 commit, Cloud-Projects-specific
  tooling config — not product code), `experiment/bklit-charts` (rejected spike, must
  never merge), and several `backup/main-*` snapshot branches (appear to be automatic
  pre-change backups from past sessions — not reviewed commit-by-commit, assumed
  redundant with `main`'s own history; verify before deleting if cleanup is wanted).
- `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` content quoted in
  `docs/agent/PROJECT_STATE.md` was read directly from `main` at the commit above,
  not reconstructed from memory.

## Taken from Cloud Projects project memory, not independently re-verified against code

- The free-vs-paid launch decision, the bklit.ui rejection, and the effects-lab
  rejection (all dated 2026-09-28). These are *decisions*, not claims about current
  code state, so "verifying" them would mean confirming they're still the team's
  position — not something checkable in the repo. Treated as current unless Gün says
  otherwise.
- The A5/B9 blockers (Following server-side storage; live overlay feasibility). B9's
  "infeasible as scoped" conclusion is a researched finding from memory, not
  re-derived here — if the new setup wants to re-confirm deadlock-api's live-data
  lag, that's new research, not verification of this doc.
- "Gün wants batched, autonomous progress with milestone-only check-ins" — a working-
  style preference from memory, not something a repo audit can confirm or deny.

## Explicitly NOT verified (flag, don't assume)

- Whether `apps/api`'s Vercel project is git-linked yet (`docs/DECISIONS.md` says no
  as of 2026-11-04; Vercel's dashboard was not checked from this session).
- Whether backlog group D ("small polish") items from the 2026-09-28 competitor-
  research backlog were ever completed — no corresponding PRs found, no memory record
  of completion either.
- Whether any other Cloud Projects thread has live, uncommitted work right now. No
  tool available from this session can enumerate or inspect other threads' state.
  This is the single largest hole in this verification pass — the absence of visible
  open PRs/branches is evidence of a clean state, not proof of one.
- Whether `CONTRIBUTING.md`'s "1 approval + green CI" merge rule has ever actually
  been enforced — all 14 PRs were opened and merged by the same account (Okkahai)
  with `DenizYalim` requested as reviewer; no review/approval record was checked
  (the PR list endpoint used here doesn't surface review state — would need a
  separate per-PR query to confirm either way).
