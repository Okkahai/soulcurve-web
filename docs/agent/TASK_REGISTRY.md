# Task Registry — soulcurve-web

Reconstructed 2026-11-06 from Cloud Projects memory + GitHub state, for a migration
to local multi-agent orchestration. **This repo has no GitHub Issues**, so there is
no authoritative task tracker to cross-check against — everything below is a
best-effort reconstruction from thread/memory records this session could read. Any
task here could be stale, already done, or already abandoned by work this session
had no visibility into (other Cloud Projects threads' internal state is not
accessible from here — flagged explicitly rather than assumed fine).

Status legend: DONE (verified via merged PR + CI), BLOCKED (named blocker, not
actionable yet), OPEN (actionable, not started or not finished), UNVERIFIED
(claimed done somewhere in memory, not confirmed against the repo).

## DONE

| ID | Title | Evidence |
|---|---|---|
| T-W1 | Initial scaffold + architecture/decision docs | PR #1, merged |
| T-W2 | Home Top Players + Blog cards; map box routes | PR #2, merged |
| T-W3 | API → Python 3.12 (Vercel build fix) | PR #3, merged |
| T-W4 | 404 page + leaderboard player names | PR #4, merged |
| T-W5 | Item icon fixes, build authors, mobile nav hint | PR #5, merged |
| T-W6 | Player skill grades, net-worth chart, rank-scoped items (mock) | PR #6, merged |
| T-W7 | Fix unstyled `<select>` on Windows | PR #7, merged |
| T-W8 | Hero stats → real deadlock-api data | PR #8, merged |
| T-W9 | Player match history + skill rating → real data | PR #9, merged |
| T-W10 | Leaderboard → real data | PR #10, merged |
| T-W11 | Fix invalid-Steam-ID crash (422 instead of 500) | PR #11, merged |
| T-W12 | Player search by name, not just Steam ID | PR #12, merged |
| T-W13 | Fix skill-percentile + tier-list methodology (CDF, Wilson score) | PR #13, merged |
| T-W14 | Patch-aware stats, live builds/patch-summary/news, real map | PR #14, merged |

## BLOCKED

| ID | Title | Blocked on | Owner's call needed |
|---|---|---|---|
| T-W15 | Real win-probability / match-analysis / net-worth-from-model / `/model` page | `soulcurve-model` Phase 1 (M3) validation gate — see that repo's state | No — just wait on the model |
| T-W16 (memory: "A5") | Move Following storage server-side (off `localStorage`) | Neon not provisioned | Yes — when to provision Neon |
| T-W17 (memory: "B9") | Live in-match overlay | Investigated, found infeasible as scoped (deadlock-api live data lags 60–90s; needs a separate desktop app) | Yes — only if Gün wants to revisit the premise |

## OPEN / UNVERIFIED (from memory, no corresponding PR found)

| ID | Title | Status | Note |
|---|---|---|---|
| T-W18 | Git-link `apps/api`'s Vercel project | UNVERIFIED | Listed as an open item in `docs/DECISIONS.md` as of 2026-11-04; may have been done manually in the Vercel dashboard without a repo change — check Vercel directly, don't assume from this repo alone |
| T-W19 | Choose cache layer for Phase 2 (file/SQLite vs. other) | OPEN | Listed as open in `docs/DECISIONS.md`; owner "A" (Gün) per that doc |
| T-W20 | Server-side Following storage once Neon exists | OPEN | Same as T-W16; separate line because it needs product work beyond just provisioning |
| T-W21 | Backlog groups B (minus #9, see T-W17), C (infra/real-data beyond what's in T-W8–14), D (small polish) from the 2026-09-28 competitor-research backlog | UNVERIFIED | Memory records an explicit execution order "A then D, then B#9" but has no record of D's items being started; D's exact item list is not in any memory file this session could read — likely sitting only in that thread's own context, which Phase 1 of this migration flagged as an inherent access gap |

## Gaps in this registry (be explicit, don't guess)

- No way to confirm whether any Cloud Projects thread beyond the ones referenced in
  project memory is **currently running** with uncommitted work. This session has no
  API to list or inspect other threads' live state.
- Group D ("small polish") from the 2026-09-28 backlog was never itemized in memory
  beyond "builds rank-bracket filter, Following empty-state message, consistent
  loading/skeleton states, and more" — the full list, if it still exists, is probably
  only visible inside that specific thread's own transcript.
- `CONTRIBUTING.md` implies a milestone/label system (`M0-M5`, labels like `data`,
  `model`, `api`, `web`, `infra`, `docs`, `bug`, `phase-2`) that was never actually
  set up in this repo (0 issues, unchecked whether labels exist). If the new
  orchestration setup wants GitHub Issues as its tracker, this registry is the
  seed list to turn into real issues — it is not a substitute for them.
