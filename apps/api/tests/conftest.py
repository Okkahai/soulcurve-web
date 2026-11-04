from datetime import datetime

import pytest
import respx
from httpx import Response

from soulcurve_api import deadlock_client

MOCK_DL_HEROES = [
    {"id": 1, "name": "Infernus", "player_selectable": True, "disabled": False},
    {"id": 2, "name": "Seven", "player_selectable": True, "disabled": False},
    {"id": 3, "name": "Vindicta", "player_selectable": True, "disabled": False},
]

MOCK_DL_HERO_STATS = [
    {"hero_id": 1, "wins": 520, "losses": 480, "matches": 1000},
    {"hero_id": 2, "wins": 450, "losses": 550, "matches": 1000},
    {"hero_id": 3, "wins": 600, "losses": 400, "matches": 1000},
]

# Same heroes the patch before the current one: Infernus up 4pp, Seven down 5pp, Vindicta flat.
MOCK_DL_HERO_STATS_PREVIOUS = [
    {"hero_id": 1, "wins": 480, "losses": 520, "matches": 1000},
    {"hero_id": 2, "wins": 500, "losses": 500, "matches": 1000},
    {"hero_id": 3, "wins": 600, "losses": 400, "matches": 1000},
]

CURRENT_PATCH_START = int(datetime.fromisoformat("2026-10-30T20:51:49Z").timestamp())


def _patch(title, pub_date, post_id, source="steam"):
    link = f"https://store.steampowered.com/news/app/1422450/view/{post_id}"
    return {
        "source": source,
        "title": title,
        "pub_date": pub_date,
        "link": link,
        "guid": {"is_perma_link": True, "text": link},
        "content": f'<p class="bb_paragraph">{title} &amp; <b>more</b> changes.</p>',
    }


MOCK_DL_PATCHES = [
    _patch("Big Gameplay Update", "2026-10-30T20:51:49Z", 300),
    _patch(" Minor Update - 10-14-2026", "2026-10-15T03:11:00Z", 200),
    _patch("Employee Spotlight", "2026-10-13T20:59:00Z", 100),
    _patch("09-29-2026", "2026-10-15T03:12:00Z", 150, source="forum"),
]

MOCK_DL_ITEMS = [
    {"id": 1001, "name": "Extra Health", "shopable": True},
    {"id": 1002, "name": "Extended Magazine", "shopable": True},
    {"id": 1003, "name": "Melee Lifesteal", "shopable": True},
    {"id": 1004, "name": "hidden_debug_item", "shopable": False},
]

MOCK_DL_ITEM_STATS = [
    {"item_id": 1001, "wins": 300, "losses": 200, "matches": 500},
    {"item_id": 1002, "wins": 150, "losses": 150, "matches": 300},
    {"item_id": 1003, "wins": 60, "losses": 40, "matches": 100},
    {"item_id": 1004, "wins": 5, "losses": 5, "matches": 10},
]

MOCK_DL_MATCH_HISTORY = [
    {
        "match_id": 111,
        "hero_id": 1,
        "player_team": 0,
        "match_result": 0,
        "player_kills": 10,
        "player_deaths": 2,
        "player_assists": 5,
        "match_duration_s": 1200,
        "start_time": 1700000000,
    },
    {
        "match_id": 112,
        "hero_id": 2,
        "player_team": 1,
        "match_result": 0,
        "player_kills": 3,
        "player_deaths": 8,
        "player_assists": 2,
        "match_duration_s": 1500,
        "start_time": 1700003600,
    },
]

MOCK_DL_RANK = {"badge": 93, "rank": 9, "subrank": 3, "last_match": None}

# Hero 1 builds: a 65% win rate over 100 games must rank below 60% over 2000 once Wilson-adjusted.
MOCK_DL_BUILD_STATS = [
    {"hero_id": 1, "hero_build_id": 10, "wins": 65, "losses": 35, "matches": 100},
    {"hero_id": 1, "hero_build_id": 11, "wins": 1200, "losses": 800, "matches": 2000},
    {"hero_id": 1, "hero_build_id": 12, "wins": 520, "losses": 480, "matches": 1000},
    {"hero_id": 1, "hero_build_id": 13, "wins": 400, "losses": 600, "matches": 1000},
]
MOCK_DL_BUILD_STATS_ETERNUS = [
    {"hero_id": 1, "hero_build_id": 12, "wins": 700, "losses": 300, "matches": 1000},
]

MOCK_DL_BUILD = {
    "hero_build": {
        "hero_id": 1,
        "hero_build_id": 11,
        "author_account_id": 777,
        "name": "Test Build",
        "details": {
            "mod_categories": [
                {"name": "Early", "mods": [{"ability_id": 1001}, {"ability_id": 1002}]},
                {"name": "Core", "mods": [{"ability_id": 1002}, {"ability_id": 424242}]},
            ]
        },
    }
}

MOCK_DL_MAP = {
    "images": {"minimap": "https://assets.example/minimap.png"},
    "objective_positions": {
        "team0_titan": {"left_relative": 0.3905, "top_relative": 0.8236},
        "team1_titan": {"left_relative": 0.5095, "top_relative": 0.0757},
        "team0_tier2_1": {"left_relative": 0.1583, "top_relative": 0.6702},
        "team0_tier2_3": {"left_relative": 0.3901, "top_relative": 0.6115},
        "team0_tier2_4": {"left_relative": 0.7117, "top_relative": 0.6853},
        "team1_tier2_1": {"left_relative": 0.1981, "top_relative": 0.2164},
        "team1_tier2_3": {"left_relative": 0.5099, "top_relative": 0.2885},
        "team1_tier2_4": {"left_relative": 0.7497, "top_relative": 0.2279},
        "team0_tier1_1": {"left_relative": 0.069, "top_relative": 0.5363},
        "team0_tier1_3": {"left_relative": 0.45, "top_relative": 0.5333},
        "team0_tier1_4": {"left_relative": 0.7774, "top_relative": 0.5423},
        "team1_tier1_1": {"left_relative": 0.1226, "top_relative": 0.3577},
        "team1_tier1_3": {"left_relative": 0.45, "top_relative": 0.3667},
        "team1_tier1_4": {"left_relative": 0.828, "top_relative": 0.3637},
    },
}

MOCK_DL_LEADERBOARD = [
    {
        "account_name": f"Player{i}",
        "possible_account_ids": [5000 + i],
        "rank": i + 1,
        "top_hero_ids": [1],
    }
    for i in range(9)
] + [
    {
        "account_name": "Ambiguous",
        "possible_account_ids": [9001, 9002],
        "rank": 10,
        "top_hero_ids": [2],
    }
]

MOCK_DL_STEAM_SEARCH = [
    {
        "account_id": 9002,
        "personaname": "Ambiguous",
        "last_team_avg_badge": 50,
        "matches_played_last_30d": 20,
    }
]


@pytest.fixture
def deadlock_api():
    """Mocks the deadlock-api.com endpoints stats/builds hit for hero data."""
    deadlock_client._cache.clear()
    with respx.mock(assert_all_called=False) as router:
        router.get("https://api.deadlock-api.com/v1/assets/heroes").mock(
            return_value=Response(200, json=MOCK_DL_HEROES)
        )
        router.get("https://api.deadlock-api.com/v1/assets/map").mock(
            return_value=Response(200, json=MOCK_DL_MAP)
        )
        router.get("https://api.deadlock-api.com/v2/patches").mock(
            return_value=Response(200, json=MOCK_DL_PATCHES)
        )
        router.get(
            "https://api.deadlock-api.com/v1/analytics/hero-stats",
            params={"max_unix_timestamp": str(CURRENT_PATCH_START)},
        ).mock(return_value=Response(200, json=MOCK_DL_HERO_STATS_PREVIOUS))
        router.get("https://api.deadlock-api.com/v1/analytics/hero-stats").mock(
            return_value=Response(200, json=MOCK_DL_HERO_STATS)
        )
        router.get(
            url__regex=r"https://api\.deadlock-api\.com/v1/analytics/hero-build-stats/\d+",
            params={"min_average_badge": "110"},
        ).mock(return_value=Response(200, json=MOCK_DL_BUILD_STATS_ETERNUS))
        router.get(
            url__regex=r"https://api\.deadlock-api\.com/v1/analytics/hero-build-stats/\d+"
        ).mock(return_value=Response(200, json=MOCK_DL_BUILD_STATS))
        router.get("https://api.deadlock-api.com/v1/builds").mock(
            return_value=Response(200, json=[MOCK_DL_BUILD])
        )
        router.get("https://api.deadlock-api.com/v1/players/steam").mock(
            return_value=Response(200, json=[{"account_id": 777, "personaname": "BuildAuthor"}])
        )
        router.get("https://api.deadlock-api.com/v1/assets/items/by-type/upgrade").mock(
            return_value=Response(200, json=MOCK_DL_ITEMS)
        )
        router.get("https://api.deadlock-api.com/v1/analytics/item-stats").mock(
            return_value=Response(200, json=MOCK_DL_ITEM_STATS)
        )
        router.get(url__regex=r"https://api\.deadlock-api\.com/v1/players/\d+/match-history").mock(
            return_value=Response(200, json=MOCK_DL_MATCH_HISTORY)
        )
        router.get(url__regex=r"https://api\.deadlock-api\.com/v1/players/\d+/rank").mock(
            return_value=Response(200, json=MOCK_DL_RANK)
        )
        router.get(url__regex=r"https://api\.deadlock-api\.com/v1/leaderboard/\w+").mock(
            return_value=Response(200, json={"entries": MOCK_DL_LEADERBOARD})
        )
        router.get(
            "https://api.deadlock-api.com/v1/players/steam-search",
            params={"search_query": "nonexistent-player", "limit": "15"},
        ).mock(
            return_value=Response(404, json={"status": 404, "error": "No Steam profiles found."})
        )
        router.get("https://api.deadlock-api.com/v1/players/steam-search").mock(
            return_value=Response(200, json=MOCK_DL_STEAM_SEARCH)
        )
        yield
    deadlock_client._cache.clear()
