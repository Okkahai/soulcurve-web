"""Match map: where kills happened and which objectives fell when.

Coordinates are normalized to the map (0-1 on both axes): amber's base at the
bottom, sapphire's at the top. Objective positions and the minimap image are the
game's real ones from deadlock-api; if that asset is unreachable we fall back to
a schematic layout with three straight lanes at x = 0.2 / 0.5 / 0.8. Real kill
positions come from deadlock-api's match data in M4; until then kills are seeded
per match (placed along the real lanes), and objectives follow the same fixed
timeline as the mock win-probability curve so the two views agree.
"""

import hashlib

import httpx
from fastapi import APIRouter

from soulcurve_api import deadlock_client
from soulcurve_api.models import MapKill, MapObjective, MatchMapResponse

router = APIRouter()

MATCH_LENGTH_MIN = 29
KILL_COUNT = 36
LANE_X = {"left": 0.2, "middle": 0.5, "right": 0.8}

# (name, lane, owner, y, destroyed_at) -- matches the win-probability events.
_OBJECTIVES = [
    ("Guardian", "left", "amber", 0.62, 7.5),
    ("Guardian", "middle", "amber", 0.62, None),
    ("Guardian", "right", "amber", 0.62, None),
    ("Walker", "left", "amber", 0.78, None),
    ("Walker", "middle", "amber", 0.78, None),
    ("Walker", "right", "amber", 0.78, None),
    ("Patron", "middle", "amber", 0.92, None),
    ("Guardian", "left", "sapphire", 0.38, None),
    ("Guardian", "middle", "sapphire", 0.38, 18),
    ("Guardian", "right", "sapphire", 0.38, None),
    ("Walker", "left", "sapphire", 0.22, None),
    ("Walker", "middle", "sapphire", 0.22, 24),
    ("Walker", "right", "sapphire", 0.22, None),
    ("Patron", "middle", "sapphire", 0.08, MATCH_LENGTH_MIN),
]


# deadlock-api's objective_positions keys: team0 is amber, team1 sapphire.
_TEAM_KEY = {"amber": "team0", "sapphire": "team1"}
_TIER = {"Guardian": "tier1", "Walker": "tier2"}
_LANE_KEY = {"left": "1", "middle": "3", "right": "4"}


def _real_position(positions: dict, name: str, lane: str, owner: str) -> tuple[float, float] | None:
    team = _TEAM_KEY[owner]
    key = f"{team}_titan" if name == "Patron" else f"{team}_{_TIER[name]}_{_LANE_KEY[lane]}"
    point = positions.get(key)
    return (point["left_relative"], point["top_relative"]) if point else None


def _lane_x(positions: dict, lane: str, y: float) -> float:
    """x of a lane at height y, interpolated through its real objectives, base to base."""
    keys = [
        "team0_titan",
        f"team0_tier2_{_LANE_KEY[lane]}",
        f"team0_tier1_{_LANE_KEY[lane]}",
        f"team1_tier1_{_LANE_KEY[lane]}",
        f"team1_tier2_{_LANE_KEY[lane]}",
        "team1_titan",
    ]
    anchors = sorted(
        (
            (positions[k]["top_relative"], positions[k]["left_relative"])
            for k in keys
            if k in positions
        ),
        reverse=True,
    )
    if not anchors:
        return LANE_X[lane]
    for (y0, x0), (y1, x1) in zip(anchors, anchors[1:], strict=False):
        if y1 <= y <= y0:
            return x1 + (x0 - x1) * (y - y1) / (y0 - y1)
    return anchors[0][1] if y > anchors[0][0] else anchors[-1][1]


def _unit(seed: int, salt: int) -> float:
    return ((seed >> (salt * 12)) % 4096) / 4096


def _kills(match_id: int, positions: dict) -> list[MapKill]:
    kills = []
    for i in range(KILL_COUNT):
        seed = int(hashlib.sha256(f"map:{match_id}:{i}".encode()).hexdigest(), 16)
        t = round(MATCH_LENGTH_MIN * (i + _unit(seed, 0)) / KILL_COUNT, 2)
        lane = list(LANE_X)[seed % 3]
        # Fights drift toward sapphire's base as amber takes over the game.
        front = 0.5 - 0.3 * (t / MATCH_LENGTH_MIN)
        y = min(0.9, max(0.1, front + (_unit(seed, 1) - 0.5) * 0.35))
        x = min(0.95, max(0.05, _lane_x(positions, lane, y) + (_unit(seed, 2) - 0.5) * 0.08))
        team = "amber" if _unit(seed, 3) < 0.45 + 0.3 * (t / MATCH_LENGTH_MIN) else "sapphire"
        kills.append(MapKill(t_min=t, x=round(x, 3), y=round(y, 3), team=team))
    return kills


@router.get("/api/matches/{match_id}/map")
async def match_map(match_id: int) -> MatchMapResponse:
    try:
        asset = await deadlock_client.fetch_map()
    except httpx.HTTPError:
        asset = {}
    positions = asset.get("objective_positions", {})
    objectives = []
    for name, lane, owner, y, at in _OBJECTIVES:
        x, y = _real_position(positions, name, lane, owner) or (LANE_X[lane], y)
        objectives.append(
            MapObjective(name=name, lane=lane, owner=owner, x=x, y=y, destroyed_at=at)
        )
    return MatchMapResponse(
        match_id=match_id,
        minimap_url=asset.get("images", {}).get("minimap"),
        kills=_kills(match_id, positions),
        objectives=objectives,
    )
