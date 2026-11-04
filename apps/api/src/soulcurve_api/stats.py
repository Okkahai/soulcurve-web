"""General stats endpoints (hero/item win rates, patch summary, rank distribution).

Hero, item and patch stats are live from deadlock-api.com, windowed to the
current gameplay patch. Only the rank distribution is still mock data.
"""

import asyncio

import httpx
from fastapi import APIRouter, HTTPException

from soulcurve_api import deadlock_client, patches
from soulcurve_api.models import (
    HeroItemStatsResponse,
    HeroStat,
    HeroStatsResponse,
    ItemsResponse,
    ItemStat,
    PatchChange,
    PatchSummaryResponse,
    RankDistributionResponse,
    RankShare,
)

router = APIRouter()

PATCH_SUMMARY_COUNT = 3
MIN_PATCH_COMPARE_MATCHES = 1000  # per patch window, so a lucky streak can't top the winners
ITEMS_OVERALL = 40

# Deadlock's ranked tiers (api.deadlock-api.com/v1/assets/ranks), low to high.
RANKS: list[str] = [
    "Obscurus",
    "Initiate",
    "Seeker",
    "Acolyte",
    "Sentinel",
    "Mystic",
    "Ritualist",
    "Emissary",
    "Oracle",
    "Phantom",
    "Ascendant",
    "Eternus",
]

# A rough bell curve over the 12 tiers, most players clustered in the middle
# ranks and long tails at Obscurus and Eternus, summing to 1.0.
_MOCK_RANK_SHARES: list[float] = [
    0.02,
    0.04,
    0.07,
    0.11,
    0.14,
    0.16,
    0.15,
    0.12,
    0.09,
    0.06,
    0.03,
    0.01,
]


async def _current_patch() -> tuple[str, int | None]:
    pair = await patches.latest_patches()
    return (pair[0].label, pair[0].start) if pair else ("All patches", None)


def _badge_range(rank: str | None) -> tuple[int | None, int | None]:
    """Rank name -> deadlock-api badge tier range (tier*10 .. tier*10+9)."""
    if rank is None:
        return None, None
    tier = RANKS.index(rank)
    return tier * 10, tier * 10 + 9


@router.get("/api/stats/ranks")
def ranks() -> list[str]:
    return RANKS


@router.get("/api/stats/heroes")
async def hero_stats(rank: str | None = None) -> HeroStatsResponse:
    if rank is not None and rank not in RANKS:
        raise HTTPException(status_code=422, detail="Unknown rank")

    min_badge, max_badge = _badge_range(rank)

    try:
        patch, since = await _current_patch()
        raw_stats, hero_names = await asyncio.gather(
            deadlock_client.fetch_hero_stats(min_badge, max_badge, since),
            deadlock_client.fetch_heroes(),
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="deadlock-api unavailable") from exc

    total_matches = sum(row["matches"] for row in raw_stats if row["hero_id"] in hero_names)
    heroes = [
        HeroStat(
            hero_id=row["hero_id"],
            name=hero_names[row["hero_id"]],
            win_rate=round(row["wins"] / row["matches"], 3),
            pick_rate=round(row["matches"] / total_matches, 3),
            matches=row["matches"],
        )
        for row in raw_stats
        if row["hero_id"] in hero_names and row["matches"] > 0
    ]
    return HeroStatsResponse(patch=patch, rank=rank, heroes=heroes)


@router.get("/api/stats/patch-summary")
async def patch_summary() -> PatchSummaryResponse:
    pair = await patches.latest_patches()
    if pair is None:
        raise HTTPException(status_code=503, detail="Patch feed unavailable")
    current, previous = pair
    try:
        now_rows, before_rows, hero_names = await asyncio.gather(
            deadlock_client.fetch_hero_stats(since=current.start),
            deadlock_client.fetch_hero_stats(since=previous.start, until=current.start),
            deadlock_client.fetch_heroes(),
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="deadlock-api unavailable") from exc

    before = {r["hero_id"]: r for r in before_rows if r["matches"] >= MIN_PATCH_COMPARE_MATCHES}
    changes = []
    for row in now_rows:
        old = before.get(row["hero_id"])
        if (
            old is None
            or row["hero_id"] not in hero_names
            or row["matches"] < MIN_PATCH_COMPARE_MATCHES
        ):
            continue
        win_rate = row["wins"] / row["matches"]
        previous_win_rate = old["wins"] / old["matches"]
        changes.append(
            PatchChange(
                hero_id=row["hero_id"],
                name=hero_names[row["hero_id"]],
                win_rate=round(win_rate, 3),
                previous_win_rate=round(previous_win_rate, 3),
                delta=round(win_rate - previous_win_rate, 3),
            )
        )
    ranked = sorted(changes, key=lambda c: c.delta, reverse=True)
    return PatchSummaryResponse(
        patch=current.label,
        previous_patch=previous.label,
        winners=ranked[:PATCH_SUMMARY_COUNT],
        losers=ranked[-PATCH_SUMMARY_COUNT:][::-1],
    )


@router.get("/api/stats/rank-distribution")
def rank_distribution() -> RankDistributionResponse:
    return RankDistributionResponse(
        ranks=[
            RankShare(rank=rank, share=share)
            for rank, share in zip(RANKS, _MOCK_RANK_SHARES, strict=True)
        ]
    )


@router.get("/api/stats/items")
async def item_stats() -> ItemsResponse:
    try:
        patch, since = await _current_patch()
        item_names, item_rows, hero_rows = await asyncio.gather(
            deadlock_client.fetch_items(),
            deadlock_client.fetch_item_stats(since=since),
            deadlock_client.fetch_hero_stats(since=since),
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="deadlock-api unavailable") from exc

    total_matches = sum(row["matches"] for row in hero_rows)
    items = [
        ItemStat(
            item_id=row["item_id"],
            name=item_names[row["item_id"]],
            win_rate=round(row["wins"] / row["matches"], 3),
            pick_rate=round(min(1.0, row["matches"] / total_matches), 3),
            matches=row["matches"],
        )
        for row in item_rows
        if row["item_id"] in item_names and row["matches"] > 0 and total_matches
    ]
    items.sort(key=lambda i: i.pick_rate, reverse=True)
    return ItemsResponse(patch=patch, items=items[:ITEMS_OVERALL])


ITEMS_PER_HERO = 12


@router.get("/api/stats/heroes/{hero_id}/items")
async def hero_item_stats(hero_id: int, rank: str | None = None) -> HeroItemStatsResponse:
    if rank is not None and rank not in RANKS:
        raise HTTPException(status_code=422, detail="Unknown rank")

    min_badge, max_badge = _badge_range(rank)

    try:
        patch, since = await _current_patch()
        hero_names, item_names, item_rows, hero_rows = await asyncio.gather(
            deadlock_client.fetch_heroes(),
            deadlock_client.fetch_items(),
            deadlock_client.fetch_item_stats(hero_id, min_badge, max_badge, since),
            deadlock_client.fetch_hero_stats(min_badge, max_badge, since),
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="deadlock-api unavailable") from exc

    hero_name = hero_names.get(hero_id)
    if hero_name is None:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_matches = next((row["matches"] for row in hero_rows if row["hero_id"] == hero_id), 0)
    items = [
        ItemStat(
            item_id=row["item_id"],
            name=item_names[row["item_id"]],
            win_rate=round(row["wins"] / row["matches"], 3),
            pick_rate=round(min(1.0, row["matches"] / hero_matches), 3),
            matches=row["matches"],
        )
        for row in item_rows
        if row["item_id"] in item_names and row["matches"] > 0 and hero_matches
    ]
    items.sort(key=lambda i: i.pick_rate, reverse=True)
    return HeroItemStatsResponse(
        patch=patch,
        hero_id=hero_id,
        hero_name=hero_name,
        items=items[:ITEMS_PER_HERO],
    )
