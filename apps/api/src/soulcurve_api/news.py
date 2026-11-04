"""News / patch notes feed.

Valve's Steam announcements come live from deadlock-api's patch feed; SoulCurve's
own announcements are fixed entries. Newest first.
"""

import html
import re

import httpx
from fastapi import APIRouter

from soulcurve_api import deadlock_client
from soulcurve_api.models import NewsItem, NewsResponse

router = APIRouter()

NEWS_COUNT = 15
SUMMARY_CHARS = 220

_SOULCURVE_NEWS: list[NewsItem] = [
    NewsItem(
        id=2,
        title="SoulCurve match analysis is live",
        date="2026-09-27",
        tag="news",
        summary="See your win-probability curve and a 10-point mistake score for any match.",
    ),
    NewsItem(
        id=1,
        title="SoulCurve general stats page is live",
        date="2026-09-14",
        tag="news",
        summary="Browse hero win rates and drill into the most popular items per hero.",
    ),
]


def _summary(content: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", content))
    text = " ".join(text.split())
    return text if len(text) <= SUMMARY_CHARS else text[:SUMMARY_CHARS].rsplit(" ", 1)[0] + "…"


@router.get("/api/news")
async def news() -> NewsResponse:
    try:
        entries = await deadlock_client.fetch_patches()
    except httpx.HTTPError:
        entries = []
    valve = [
        NewsItem(
            id=int(e["guid"]["text"].rsplit("/", 1)[-1]) % 2**31,
            title=e["title"].strip(),
            date=e["pub_date"][:10],
            tag="patch-notes" if "update" in e["title"].lower() else "news",
            summary=_summary(e["content"]),
            url=e["link"],
        )
        for e in entries
        if e["source"] == "steam"
    ][:NEWS_COUNT]
    items = sorted(valve + _SOULCURVE_NEWS, key=lambda n: n.date, reverse=True)
    return NewsResponse(items=items)
