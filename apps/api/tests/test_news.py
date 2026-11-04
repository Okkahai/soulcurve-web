from fastapi.testclient import TestClient

from soulcurve_api.main import app

client = TestClient(app)


def test_news_shape(deadlock_api):
    response = client.get("/api/news")
    assert response.status_code == 200
    items = response.json()["items"]
    for item in items:
        assert item["tag"] in {"patch-notes", "news"}

    by_title = {item["title"]: item for item in items}
    update = by_title["Big Gameplay Update"]
    assert update["tag"] == "patch-notes"
    assert update["url"].startswith("https://store.steampowered.com/")
    # markup and entities are stripped from the summary
    assert update["summary"] == "Big Gameplay Update & more changes."
    assert by_title["Employee Spotlight"]["tag"] == "news"
    # forum changelog mirrors are skipped; SoulCurve's own announcements are kept
    assert "09-29-2026" not in by_title
    assert "SoulCurve match analysis is live" in by_title


def test_news_newest_first(deadlock_api):
    dates = [item["date"] for item in client.get("/api/news").json()["items"]]
    assert dates == sorted(dates, reverse=True)
