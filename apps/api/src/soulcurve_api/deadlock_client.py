"""Thin client for api.deadlock-api.com, with a small in-process TTL cache.

No API key needed (public tier, 200 req/min per IP). Cache keeps repeat
requests for the same query well under that.
"""

import time
from typing import Any

import httpx

BASE_URL = "https://api.deadlock-api.com"
_HERO_STATS_TTL_S = 300
_HEROES_TTL_S = 3600

_cache: dict[tuple, tuple[float, Any]] = {}


async def _get(path: str, params: dict, ttl_s: float) -> Any:
    key = (path, tuple(sorted(params.items())))
    cached = _cache.get(key)
    if cached and cached[0] > time.monotonic():
        return cached[1]
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.get(path, params=params)
        response.raise_for_status()
        data = response.json()
    _cache[key] = (time.monotonic() + ttl_s, data)
    return data


def _filters(min_badge: int | None, max_badge: int | None, since: int | None, until: int | None):
    """Analytics query params: average-badge range and a unix-time window, skipping unset ones."""
    candidates = {
        "min_average_badge": min_badge,
        "max_average_badge": max_badge,
        "min_unix_timestamp": since,
        "max_unix_timestamp": until,
    }
    return {k: v for k, v in candidates.items() if v is not None}


async def fetch_hero_stats(
    min_badge: int | None = None,
    max_badge: int | None = None,
    since: int | None = None,
    until: int | None = None,
) -> list[dict]:
    params = _filters(min_badge, max_badge, since, until)
    return await _get("/v1/analytics/hero-stats", params, _HERO_STATS_TTL_S)


async def fetch_map() -> dict:
    """The game map: minimap image URLs and real objective positions."""
    return await _get("/v1/assets/map", {}, _HEROES_TTL_S)


async def fetch_patches() -> list[dict]:
    return await _get("/v2/patches", {}, _HEROES_TTL_S)


async def fetch_heroes() -> dict[int, str]:
    """Active, player-selectable heroes, keyed by hero_id."""
    heroes = await _get("/v1/assets/heroes", {"only_active": "true"}, _HEROES_TTL_S)
    return {
        h["id"]: h["name"] for h in heroes if h.get("player_selectable") and not h.get("disabled")
    }


async def fetch_items() -> dict[int, str]:
    """Purchasable shop upgrade items (weapon/vitality/spirit), keyed by item_id."""
    items = await _get("/v1/assets/items/by-type/upgrade", {}, _HEROES_TTL_S)
    return {i["id"]: i["name"] for i in items if i.get("shopable")}


async def fetch_match_history(account_id: int) -> list[dict]:
    return await _get(f"/v1/players/{account_id}/match-history", {}, _HERO_STATS_TTL_S)


async def fetch_rank(account_id: int) -> dict:
    return await _get(f"/v1/players/{account_id}/rank", {}, _HERO_STATS_TTL_S)


async def fetch_item_stats(
    hero_id: int | None = None,
    min_badge: int | None = None,
    max_badge: int | None = None,
    since: int | None = None,
) -> list[dict]:
    """Item win/purchase counts; across all heroes when hero_id is omitted."""
    params = _filters(min_badge, max_badge, since, None)
    if hero_id is not None:
        params["hero_id"] = hero_id
    return await _get("/v1/analytics/item-stats", params, _HERO_STATS_TTL_S)


async def fetch_hero_build_stats(
    hero_id: int,
    min_badge: int | None,
    max_badge: int | None,
    since: int | None,
    min_matches: int,
) -> list[dict]:
    params = _filters(min_badge, max_badge, since, None) | {"min_matches": min_matches}
    return await _get(f"/v1/analytics/hero-build-stats/{hero_id}", params, _HERO_STATS_TTL_S)


async def fetch_build(hero_id: int, build_id: int) -> dict | None:
    """A community build's latest version (name, author, item mods), or None if it's gone."""
    params = {"hero_id": hero_id, "build_id": build_id, "only_latest": "true", "limit": 1}
    rows = await _get("/v1/builds", params, _HEROES_TTL_S)
    return rows[0]["hero_build"] if rows else None


async def fetch_steam_names(account_ids: list[int]) -> dict[int, str]:
    rows = await _get(
        "/v1/players/steam", {"account_ids": ",".join(map(str, account_ids))}, _HEROES_TTL_S
    )
    return {r["account_id"]: r["personaname"] for r in rows}


async def fetch_leaderboard(region: str) -> list[dict]:
    return (await _get(f"/v1/leaderboard/{region}", {}, _HERO_STATS_TTL_S))["entries"]


async def steam_search(name: str, limit: int = 15) -> list[dict]:
    """Resolve a persona name to Steam profiles, best match first."""
    try:
        return await _get(
            "/v1/players/steam-search", {"search_query": name, "limit": limit}, _HERO_STATS_TTL_S
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return []
        raise
