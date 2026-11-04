import httpx
from fastapi.testclient import TestClient

from soulcurve_api import deadlock_client
from soulcurve_api.main import app

client = TestClient(app)


def test_hero_stats_shape(deadlock_api):
    response = client.get("/api/stats/heroes")
    assert response.status_code == 200
    body = response.json()
    assert body["patch"] == "Big Gameplay Update"
    assert len(body["heroes"]) == 3
    for hero in body["heroes"]:
        assert 0.0 <= hero["win_rate"] <= 1.0
        assert 0.0 <= hero["pick_rate"] <= 1.0
    assert abs(sum(h["pick_rate"] for h in body["heroes"]) - 1.0) < 0.001


def test_hero_item_stats_shape(deadlock_api):
    heroes = client.get("/api/stats/heroes").json()["heroes"]
    hero_id = heroes[0]["hero_id"]

    response = client.get(f"/api/stats/heroes/{hero_id}/items")
    assert response.status_code == 200
    body = response.json()
    assert body["hero_id"] == hero_id
    assert len(body["items"]) == 3  # the 4th mock item is unshopable and filtered out
    for item in body["items"]:
        assert 0.0 <= item["win_rate"] <= 1.0
        assert 0.0 <= item["pick_rate"] <= 1.0
    # sorted by pick rate, highest first
    pick_rates = [i["pick_rate"] for i in body["items"]]
    assert pick_rates == sorted(pick_rates, reverse=True)


def test_hero_item_stats_404_for_unknown_hero(deadlock_api):
    response = client.get("/api/stats/heroes/999999/items")
    assert response.status_code == 404


def test_ranks_list():
    response = client.get("/api/stats/ranks")
    assert response.status_code == 200
    ranks = response.json()
    assert "Eternus" in ranks
    assert "Obscurus" in ranks


def test_hero_stats_filtered_by_rank(deadlock_api):
    response = client.get("/api/stats/heroes", params={"rank": "Eternus"})
    assert response.status_code == 200
    body = response.json()
    assert body["rank"] == "Eternus"
    assert len(body["heroes"]) == 3
    for hero in body["heroes"]:
        assert 0.0 <= hero["win_rate"] <= 1.0
        assert 0.0 <= hero["pick_rate"] <= 1.0


def test_item_stats_shape(deadlock_api):
    response = client.get("/api/stats/items")
    assert response.status_code == 200
    body = response.json()
    assert body["patch"] == "Big Gameplay Update"
    assert len(body["items"]) == 3  # the unshopable mock item is filtered out
    for item in body["items"]:
        assert 0.0 <= item["win_rate"] <= 1.0
        assert 0.0 <= item["pick_rate"] <= 1.0
        assert item["matches"] > 0
    pick_rates = [i["pick_rate"] for i in body["items"]]
    assert pick_rates == sorted(pick_rates, reverse=True)


def test_hero_stats_rejects_unknown_rank(deadlock_api):
    response = client.get("/api/stats/heroes", params={"rank": "Legendary"})
    assert response.status_code == 422


def test_rank_distribution_shape():
    response = client.get("/api/stats/rank-distribution")
    assert response.status_code == 200
    body = response.json()
    assert len(body["ranks"]) == 12
    assert body["ranks"][0]["rank"] == "Obscurus"
    assert abs(sum(r["share"] for r in body["ranks"]) - 1.0) < 0.001


def test_patch_summary_compares_current_patch_to_previous(deadlock_api):
    response = client.get("/api/stats/patch-summary")
    assert response.status_code == 200
    body = response.json()
    assert body["patch"] == "Big Gameplay Update"
    assert body["previous_patch"] == "Minor Update - 10-14-2026"
    # Infernus 48% -> 52%, Seven 50% -> 45%, Vindicta unchanged
    assert [(c["name"], c["delta"]) for c in body["winners"]] == [
        ("Infernus", 0.04),
        ("Vindicta", 0.0),
        ("Seven", -0.05),
    ]
    assert body["losers"][0]["name"] == "Seven"
    assert body["winners"][0]["previous_win_rate"] == 0.48


def test_hero_items_rank_filter(deadlock_api):
    ranked = client.get("/api/stats/heroes/1/items?rank=Eternus")
    assert ranked.status_code == 200
    assert len(ranked.json()["items"]) == 3

    assert client.get("/api/stats/heroes/1/items?rank=Nope").status_code == 422


def test_hero_stats_fall_back_to_all_patches_when_patch_feed_is_down(deadlock_api, monkeypatch):
    async def down():
        raise httpx.ConnectError("patch feed down")

    monkeypatch.setattr(deadlock_client, "fetch_patches", down)
    response = client.get("/api/stats/heroes")
    assert response.status_code == 200
    assert response.json()["patch"] == "All patches"
