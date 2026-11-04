from fastapi.testclient import TestClient

from soulcurve_api.main import app

client = TestClient(app)


def test_hero_builds_shape(deadlock_api):
    response = client.get("/api/stats/heroes/1/builds")
    assert response.status_code == 200
    body = response.json()
    assert body["hero_id"] == 1
    assert body["patch"] == "Big Gameplay Update"
    assert len(body["builds"]) == 3
    for build in body["builds"]:
        assert build["name"] == "Test Build"
        assert build["author"] == "BuildAuthor"
        # duplicate and non-shop picks are dropped
        assert build["items"] == ["Extra Health", "Extended Magazine"]
        assert 0.0 <= build["win_rate"] <= 1.0


def test_hero_builds_ranked_by_confidence_not_raw_win_rate(deadlock_api):
    builds = client.get("/api/stats/heroes/1/builds").json()["builds"]
    # 65/100 beats 60% raw, but 1200/2000 is the safer pick; the 40% build is cut
    assert [b["build_id"] for b in builds] == [11, 10, 12]
    assert builds[0]["games"] == 2000


def test_hero_builds_404_for_unknown_hero(deadlock_api):
    response = client.get("/api/stats/heroes/999999/builds")
    assert response.status_code == 404


def test_hero_builds_rank_filter(deadlock_api):
    ranked = client.get("/api/stats/heroes/1/builds", params={"rank": "Eternus"}).json()
    assert ranked["rank"] == "Eternus"
    assert [b["build_id"] for b in ranked["builds"]] == [12]
    assert ranked["builds"][0]["win_rate"] == 0.7

    bad = client.get("/api/stats/heroes/1/builds", params={"rank": "Nope"})
    assert bad.status_code == 422
