"""Top community item builds per hero, ranked over the current patch.

Live from deadlock-api.com: hero-build-stats gives each build's win/loss record,
and the builds endpoint gives its name, author and item picks.
"""

import asyncio
import math

import httpx
from fastapi import APIRouter, HTTPException

from soulcurve_api import deadlock_client
from soulcurve_api.models import Build, HeroBuildsResponse
from soulcurve_api.stats import RANKS, _badge_range, _current_patch

router = APIRouter()

BUILDS_PER_HERO = 3
BUILD_ITEM_COUNT = 12  # a build lists ~40 items across options; show the opening and core picks
MIN_BUILD_MATCHES = 300


def _wilson_lower_bound(wins: int, matches: int, z: float = 1.96) -> float:
    """Confidence-adjusted win rate, so a small lucky sample can't out-rank a proven build."""
    p = wins / matches
    denom = 1 + z * z / matches
    centre = p + z * z / (2 * matches)
    margin = z * math.sqrt(p * (1 - p) / matches + z * z / (4 * matches * matches))
    return (centre - margin) / denom


@router.get("/api/stats/heroes/{hero_id}/builds")
async def hero_builds(hero_id: int, rank: str | None = None) -> HeroBuildsResponse:
    if rank is not None and rank not in RANKS:
        raise HTTPException(status_code=422, detail="Unknown rank")
    min_badge, max_badge = _badge_range(rank)
    try:
        hero_names = await deadlock_client.fetch_heroes()
        hero_name = hero_names.get(hero_id)
        if hero_name is None:
            raise HTTPException(status_code=404, detail="Hero not found")
        patch, since = await _current_patch()
        stats, item_names = await asyncio.gather(
            deadlock_client.fetch_hero_build_stats(
                hero_id, min_badge, max_badge, since, MIN_BUILD_MATCHES
            ),
            deadlock_client.fetch_items(),
        )
        top = sorted(
            stats, key=lambda r: _wilson_lower_bound(r["wins"], r["matches"]), reverse=True
        )
        top = top[:BUILDS_PER_HERO]
        details = await asyncio.gather(
            *(deadlock_client.fetch_build(hero_id, r["hero_build_id"]) for r in top)
        )
        found = [(r, d) for r, d in zip(top, details, strict=True) if d is not None]
        authors = (
            await deadlock_client.fetch_steam_names([d["author_account_id"] for _, d in found])
            if found
            else {}
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="deadlock-api unavailable") from exc

    builds = []
    for row, detail in found:
        picks = (m["ability_id"] for c in detail["details"]["mod_categories"] for m in c["mods"])
        items = list(dict.fromkeys(item_names[i] for i in picks if i in item_names))
        builds.append(
            Build(
                build_id=row["hero_build_id"],
                name=detail["name"],
                author=authors.get(detail["author_account_id"], "Unknown"),
                items=items[:BUILD_ITEM_COUNT],
                win_rate=round(row["wins"] / row["matches"], 3),
                games=row["matches"],
            )
        )
    return HeroBuildsResponse(
        patch=patch, hero_id=hero_id, hero_name=hero_name, rank=rank, builds=builds
    )
