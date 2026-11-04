import httpx
import pytest
from fastapi.testclient import TestClient

from soulcurve_api import deadlock_client
from soulcurve_api.main import app
from soulcurve_api.match_map import _lane_x

client = TestClient(app)


def test_match_map_shape(deadlock_api):
    body = client.get("/api/matches/12345678/map").json()
    assert body["match_id"] == 12345678
    assert body["minimap_url"] == "https://assets.example/minimap.png"
    assert body["kills"]
    for kill in body["kills"]:
        assert 0 <= kill["x"] <= 1
        assert 0 <= kill["y"] <= 1
    times = [k["t_min"] for k in body["kills"]]
    assert times == sorted(times)
    assert client.get("/api/matches/12345678/map").json() == body


def test_objectives_use_real_map_positions(deadlock_api):
    objectives = client.get("/api/matches/12345678/map").json()["objectives"]
    amber_mid_guardian = next(
        o
        for o in objectives
        if o["owner"] == "amber" and o["name"] == "Guardian" and o["lane"] == "middle"
    )
    assert (amber_mid_guardian["x"], amber_mid_guardian["y"]) == (0.45, 0.5333)
    sapphire_patron = next(
        o for o in objectives if o["owner"] == "sapphire" and o["name"] == "Patron"
    )
    assert (sapphire_patron["x"], sapphire_patron["y"]) == (0.5095, 0.0757)


def test_lane_x_interpolates_through_real_objectives():
    positions = {
        "team0_tier1_1": {"left_relative": 0.069, "top_relative": 0.5363},
        "team1_tier1_1": {"left_relative": 0.1226, "top_relative": 0.3577},
    }
    assert _lane_x(positions, "left", 0.5363) == pytest.approx(0.069)
    assert _lane_x(positions, "left", (0.5363 + 0.3577) / 2) == pytest.approx((0.069 + 0.1226) / 2)
    # beyond the outermost objectives it holds the nearest lane x; with no data, the schematic lane
    assert _lane_x(positions, "left", 0.95) == pytest.approx(0.069)
    assert _lane_x({}, "right", 0.5) == 0.8


def test_match_map_falls_back_to_schematic_when_map_asset_is_down(deadlock_api, monkeypatch):
    async def down():
        raise httpx.ConnectError("asset api down")

    monkeypatch.setattr(deadlock_client, "fetch_map", down)
    body = client.get("/api/matches/12345678/map").json()
    assert body["minimap_url"] is None
    assert {o["x"] for o in body["objectives"]} == {0.2, 0.5, 0.8}
    assert len(body["objectives"]) == 14


def test_objectives_agree_with_win_probability_events(deadlock_api):
    events = client.get("/api/matches/12345678/win-probability").json()["events"]
    objectives = client.get("/api/matches/12345678/map").json()["objectives"]
    for event in events:
        # The team in an event is the one that took the objective, so the owner is the other side.
        assert any(
            o["name"] == event["detail"]
            and o["destroyed_at"] == event["t_min"]
            and o["owner"] != event["team"]
            for o in objectives
        )
