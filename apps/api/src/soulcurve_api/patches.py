"""Deadlock gameplay patches, from deadlock-api's patch feed.

Stats are windowed to the current patch so balance changes show up right away
instead of being averaged with every earlier patch.
"""

from dataclasses import dataclass
from datetime import datetime

import httpx

from soulcurve_api import deadlock_client


@dataclass(frozen=True)
class Patch:
    label: str
    start: int  # unix seconds


async def latest_patches() -> tuple[Patch, Patch] | None:
    """(current, previous) gameplay patch, or None if the feed is unreachable or too short."""
    try:
        entries = await deadlock_client.fetch_patches()
    except httpx.HTTPError:
        return None
    patches = sorted(
        (
            Patch(e["title"].strip(), int(datetime.fromisoformat(e["pub_date"]).timestamp()))
            for e in entries
            if e["source"] == "steam" and "update" in e["title"].lower()
        ),
        key=lambda p: p.start,
        reverse=True,
    )
    return (patches[0], patches[1]) if len(patches) >= 2 else None
