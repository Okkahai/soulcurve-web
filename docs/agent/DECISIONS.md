# Decisions (agent index) — soulcurve-web

The authoritative decision log is `docs/DECISIONS.md` at the repo root (D1–D6:
two-repo split, FastAPI backend, React+Vite frontend, model distribution via GitHub
Release, Vercel deploy, Phase-2 infra stack). Read it directly — not duplicated here.

This file adds decisions that were made (per Cloud Projects project memory) but never
written into that log, so a new coordinator doesn't lose them. Recommend folding
these into `docs/DECISIONS.md` as numbered entries in a follow-up PR; this migration
PR is additive/doc-only and deliberately doesn't touch that file.

## D7 (proposed numbering): Launch free, not paid
**Date:** 2026-09-28 · **Status:** accepted (per project memory; not yet in
`docs/DECISIONS.md`)

The site launches free rather than with a Polar.sh-based paid tier. Reasons recorded:
(1) removes the need to build payment infra before any other value is delivered,
(2) a free tool carries far less exposure to deadlock-api.com's still-unclarified
commercial ToS than a paid one would. Precedent cited: Leetify started free before
adding a freemium tier. Payments/subscription work should not be proposed
proactively until Gün revisits this.

## D8 (proposed numbering): Reject bklit.ui for charts
**Date:** 2026-09-28 · **Status:** accepted

Evaluated specifically against the win-probability chart: no fixed 0–100% y-axis, no
50% reference line, no objective-event markers, date-only x-axis (unusable for
match-minute data), and roughly +73KB gzip over keeping Recharts. Branch
`experiment/bklit-charts` (commit `40afa21` on GitHub) holds the spike; it must never
be merged. Recharts stays the charting library. bklit.ui might still fit a future
categorical chart (bar/radar) — that's an open option, not a rejection of the library
outright, only of this use.

## D9 (proposed numbering): Reject home-page visual effects lab experiments
**Date:** 2026-09-28 · **Status:** rejected

Tested on an unlisted `/lab/effects` route: blob tracking and data-mosh (rejected
outright — clashed with the premium/minimal analytics aesthetic) and a 1-bit ordered-
dither home-hero backdrop (tried, also reverted). Don't re-propose any of these
unless Gün raises it again himself.
