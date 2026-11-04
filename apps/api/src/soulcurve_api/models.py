"""Response schemas.

Kept in sync with the API contract in docs/ARCHITECTURE.md.
"""

from typing import Literal

from pydantic import BaseModel


class WinProbabilityPoint(BaseModel):
    t_min: float
    p_win: float


class MatchEvent(BaseModel):
    t_min: float
    type: str
    detail: str
    team: str


class WinProbabilityResponse(BaseModel):
    match_id: int
    model_version: str
    team_perspective: Literal["amber", "sapphire"]
    points: list[WinProbabilityPoint]
    events: list[MatchEvent]
    winner: Literal["amber", "sapphire"]


class HeroStat(BaseModel):
    hero_id: int
    name: str
    win_rate: float
    pick_rate: float
    matches: int


class HeroStatsResponse(BaseModel):
    patch: str
    rank: str | None = None
    heroes: list[HeroStat]


class ItemStat(BaseModel):
    item_id: int
    name: str
    win_rate: float
    pick_rate: float
    matches: int


class HeroItemStatsResponse(BaseModel):
    patch: str
    hero_id: int
    hero_name: str
    items: list[ItemStat]


class ItemsResponse(BaseModel):
    patch: str
    items: list[ItemStat]


class Build(BaseModel):
    build_id: int
    name: str
    author: str
    items: list[str]
    win_rate: float
    games: int


class HeroBuildsResponse(BaseModel):
    patch: str
    hero_id: int
    hero_name: str
    rank: str | None = None
    builds: list[Build]


class PlayerMoment(BaseModel):
    t_min: float
    type: Literal["death", "objective_loss", "objective_win", "good_trade", "rotation"]
    description: str
    wpa_delta: float


class MatchAnalysisResponse(BaseModel):
    match_id: int
    player_id: str
    hero_name: str
    score: float
    summary: str
    moments: list[PlayerMoment]


class MatchSummary(BaseModel):
    match_id: int
    hero_id: int
    hero_name: str
    result: Literal["win", "loss"]
    kills: int
    deaths: int
    assists: int
    duration_min: int
    played_at: str


class PlayerMatchesResponse(BaseModel):
    steam_id: str
    name: str | None = None
    matches: list[MatchSummary]


class ModelMetric(BaseModel):
    label: str
    value: str
    description: str


class ModelInfoResponse(BaseModel):
    model_version: str
    trained_at: str
    training_matches: int
    training_patch_range: str
    algorithm: str
    metrics: list[ModelMetric]
    features: list[str]
    summary: str


class NewsItem(BaseModel):
    id: int
    title: str
    date: str
    tag: Literal["patch-notes", "news"]
    summary: str
    url: str | None = None


class NewsResponse(BaseModel):
    items: list[NewsItem]


class BlogPostSummary(BaseModel):
    slug: str
    title: str
    date: str
    author: str
    excerpt: str


class BlogPost(BlogPostSummary):
    body: str


class BlogListResponse(BaseModel):
    posts: list[BlogPostSummary]


class PatchChange(BaseModel):
    hero_id: int
    name: str
    win_rate: float
    previous_win_rate: float
    delta: float


class PatchSummaryResponse(BaseModel):
    patch: str
    previous_patch: str
    winners: list[PatchChange]
    losers: list[PatchChange]


class RankShare(BaseModel):
    rank: str
    share: float


class RankDistributionResponse(BaseModel):
    ranks: list[RankShare]


class MapKill(BaseModel):
    t_min: float
    x: float
    y: float
    team: Literal["amber", "sapphire"]


class MapObjective(BaseModel):
    name: str
    lane: Literal["left", "middle", "right"]
    owner: Literal["amber", "sapphire"]
    x: float
    y: float
    destroyed_at: float | None


class MatchMapResponse(BaseModel):
    match_id: int
    minimap_url: str | None = None
    kills: list[MapKill]
    objectives: list[MapObjective]


class TournamentSummary(BaseModel):
    slug: str
    name: str
    organizer: str
    start_date: str
    end_date: str
    status: Literal["upcoming", "live", "completed"]
    prize_pool_usd: int
    team_count: int


class TournamentStanding(BaseModel):
    rank: int
    team: str
    wins: int
    losses: int


class TournamentMatch(BaseModel):
    id: int
    round: str
    date: str
    team_a: str
    team_b: str
    score_a: int | None
    score_b: int | None


class Tournament(TournamentSummary):
    standings: list[TournamentStanding]
    matches: list[TournamentMatch]


class TournamentListResponse(BaseModel):
    tournaments: list[TournamentSummary]


class LeaderboardPlayer(BaseModel):
    position: int
    steam_id: str
    name: str
    rank: str
    rating: int
    win_rate: float
    matches: int
    top_hero: str


class LeaderboardResponse(BaseModel):
    region: str
    players: list[LeaderboardPlayer]


class Crate(BaseModel):
    id: int
    x: float
    y: float
    area: Literal["alley", "tunnel"]
    spawn_min: float
    respawn_min: float


class BoxRouteStop(BaseModel):
    order: int
    crate_id: int
    x: float
    y: float
    arrive_s: int


class BoxRoute(BaseModel):
    team: Literal["amber", "sapphire"]
    stops: list[BoxRouteStop]
    loop_seconds: int
    naive_loop_seconds: int


class BoxRouteResponse(BaseModel):
    crates: list[Crate]
    routes: list[BoxRoute]


class PlayerGrade(BaseModel):
    category: str
    letter: Literal["S", "A", "B", "C", "D", "F"]
    score: float


class PlayerTendency(BaseModel):
    label: str
    detail: str
    tone: Literal["strength", "weakness"]


class PlayerProfileResponse(BaseModel):
    steam_id: str
    skill_rating: int
    skill_percentile: float
    grades: list[PlayerGrade]
    tendencies: list[PlayerTendency]


class NetWorthPoint(BaseModel):
    t_min: float
    amber: int
    sapphire: int


class NetWorthResponse(BaseModel):
    match_id: int
    points: list[NetWorthPoint]
