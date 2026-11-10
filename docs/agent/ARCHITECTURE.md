# Architecture (agent index) — soulcurve-web

This repo's architecture is documented in `docs/ARCHITECTURE.md` at the repo root,
which was already current as of this migration (last updated 2026-11-04, PR #14) —
it is **not** superseded or duplicated here. Read it directly.

This file exists only so `docs/agent/` is self-contained for an agent that starts
there: it points at the real doc and notes what, if anything, this migration found
that the real doc doesn't yet say.

## What to read

- `docs/ARCHITECTURE.md` — component diagram, full API contract, model-loading plan,
  data fetching/caching, frontend page list, env vars, deploy, CI. Treat it as
  authoritative; it's actively maintained by the same PRs that change the code.
- `docs/DECISIONS.md` — the decision log (D1–D6) behind the architecture above.

## What this migration added that wasn't in either doc

- The free-vs-paid launch decision (2026-09-28) isn't recorded in `docs/DECISIONS.md`
  itself, only in Cloud Projects memory. See `docs/agent/DECISIONS.md` for it written
  down properly. Consider folding it into `docs/DECISIONS.md` as a D7 in a follow-up
  PR — out of scope for this migration PR, which is additive-only.
