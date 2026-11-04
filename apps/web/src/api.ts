// Kept in sync with the API contract in docs/ARCHITECTURE.md.

export interface WinProbabilityPoint {
  t_min: number;
  p_win: number;
}

export interface MatchEvent {
  t_min: number;
  type: string;
  detail: string;
  team: string;
}

export interface WinProbabilityResponse {
  match_id: number;
  model_version: string;
  team_perspective: "amber" | "sapphire";
  points: WinProbabilityPoint[];
  events: MatchEvent[];
  winner: "amber" | "sapphire";
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchWinProbability(matchId: string): Promise<WinProbabilityResponse> {
  const response = await fetch(`${API_BASE_URL}/api/matches/${matchId}/win-probability`);
  if (!response.ok) {
    throw new Error(`Match not found (${response.status})`);
  }
  return response.json();
}

export interface Me {
  steam_id: string | null;
}

export async function fetchMe(): Promise<Me> {
  const response = await fetch(`${API_BASE_URL}/api/me`, { credentials: "include" });
  return response.json();
}

export function steamLoginUrl(): string {
  return `${API_BASE_URL}/auth/steam/login`;
}

export async function logout(): Promise<void> {
  await fetch(`${API_BASE_URL}/auth/logout`, { method: "POST", credentials: "include" });
}

export interface HeroStat {
  hero_id: number;
  name: string;
  win_rate: number;
  pick_rate: number;
  matches: number;
}

export interface HeroStatsResponse {
  patch: string;
  rank: string | null;
  heroes: HeroStat[];
}

export interface ItemStat {
  item_id: number;
  name: string;
  win_rate: number;
  pick_rate: number;
  matches: number;
}

export interface HeroItemStatsResponse {
  patch: string;
  hero_id: number;
  hero_name: string;
  items: ItemStat[];
}

export interface ItemsResponse {
  patch: string;
  items: ItemStat[];
}

export async function fetchItemStats(): Promise<ItemsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats/items`);
  if (!response.ok) {
    throw new Error(`Failed to load item stats (${response.status})`);
  }
  return response.json();
}

export async function fetchHeroStats(rank?: string | null): Promise<HeroStatsResponse> {
  const query = rank ? `?rank=${encodeURIComponent(rank)}` : "";
  const response = await fetch(`${API_BASE_URL}/api/stats/heroes${query}`);
  if (!response.ok) {
    throw new Error(`Failed to load hero stats (${response.status})`);
  }
  return response.json();
}

export interface PatchChange {
  hero_id: number;
  name: string;
  win_rate: number;
  previous_win_rate: number;
  delta: number;
}

export interface PatchSummaryResponse {
  patch: string;
  previous_patch: string;
  winners: PatchChange[];
  losers: PatchChange[];
}

export async function fetchPatchSummary(): Promise<PatchSummaryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats/patch-summary`);
  if (!response.ok) {
    throw new Error(`Failed to load patch summary (${response.status})`);
  }
  return response.json();
}

export interface RankShare {
  rank: string;
  share: number;
}

export interface RankDistributionResponse {
  ranks: RankShare[];
}

export async function fetchRankDistribution(): Promise<RankDistributionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats/rank-distribution`);
  if (!response.ok) {
    throw new Error(`Failed to load rank distribution (${response.status})`);
  }
  return response.json();
}

export async function fetchRanks(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/stats/ranks`);
  if (!response.ok) {
    throw new Error(`Failed to load ranks (${response.status})`);
  }
  return response.json();
}

export async function fetchHeroItemStats(heroId: number, rank?: string | null): Promise<HeroItemStatsResponse> {
  const query = rank ? `?rank=${encodeURIComponent(rank)}` : "";
  const response = await fetch(`${API_BASE_URL}/api/stats/heroes/${heroId}/items${query}`);
  if (!response.ok) {
    throw new Error(`Failed to load item stats (${response.status})`);
  }
  return response.json();
}

export interface Build {
  build_id: number;
  name: string;
  author: string;
  items: string[];
  win_rate: number;
  games: number;
}

export interface HeroBuildsResponse {
  patch: string;
  hero_id: number;
  hero_name: string;
  rank: string | null;
  builds: Build[];
}

export async function fetchHeroBuilds(heroId: number, rank?: string | null): Promise<HeroBuildsResponse> {
  const query = rank ? `?rank=${encodeURIComponent(rank)}` : "";
  const response = await fetch(`${API_BASE_URL}/api/stats/heroes/${heroId}/builds${query}`);
  if (!response.ok) {
    throw new Error(`Failed to load builds (${response.status})`);
  }
  return response.json();
}

export interface PlayerMoment {
  t_min: number;
  type: "death" | "objective_loss" | "objective_win" | "good_trade" | "rotation";
  description: string;
  wpa_delta: number;
}

export interface MatchAnalysisResponse {
  match_id: number;
  player_id: string;
  hero_name: string;
  score: number;
  summary: string;
  moments: PlayerMoment[];
}

export async function fetchMatchAnalysis(matchId: string): Promise<MatchAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/matches/${matchId}/analysis`);
  if (!response.ok) {
    throw new Error(`Match not found (${response.status})`);
  }
  return response.json();
}

export interface MatchSummary {
  match_id: number;
  hero_id: number;
  hero_name: string;
  result: "win" | "loss";
  kills: number;
  deaths: number;
  assists: number;
  duration_min: number;
  played_at: string;
}

export interface PlayerMatchesResponse {
  steam_id: string;
  name: string | null;
  matches: MatchSummary[];
}

export async function fetchPlayerMatches(steamId: string): Promise<PlayerMatchesResponse> {
  const response = await fetch(`${API_BASE_URL}/api/players/${encodeURIComponent(steamId)}/matches`);
  if (!response.ok) {
    throw new Error(`Failed to load match history (${response.status})`);
  }
  return response.json();
}

export interface ModelMetric {
  label: string;
  value: string;
  description: string;
}

export interface ModelInfoResponse {
  model_version: string;
  trained_at: string;
  training_matches: number;
  training_patch_range: string;
  algorithm: string;
  metrics: ModelMetric[];
  features: string[];
  summary: string;
}

export async function fetchModelInfo(): Promise<ModelInfoResponse> {
  const response = await fetch(`${API_BASE_URL}/api/model`);
  if (!response.ok) {
    throw new Error(`Failed to load model info (${response.status})`);
  }
  return response.json();
}

export interface NewsItem {
  id: number;
  title: string;
  date: string;
  tag: "patch-notes" | "news";
  summary: string;
  url: string | null;
}

export interface NewsResponse {
  items: NewsItem[];
}

export async function fetchNews(): Promise<NewsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/news`);
  if (!response.ok) {
    throw new Error(`Failed to load news (${response.status})`);
  }
  return response.json();
}

export interface BlogPostSummary {
  slug: string;
  title: string;
  date: string;
  author: string;
  excerpt: string;
}

export interface BlogPost extends BlogPostSummary {
  body: string;
}

export interface BlogListResponse {
  posts: BlogPostSummary[];
}

export async function fetchBlogList(): Promise<BlogListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/blog`);
  if (!response.ok) {
    throw new Error(`Failed to load blog posts (${response.status})`);
  }
  return response.json();
}

export async function fetchBlogPost(slug: string): Promise<BlogPost> {
  const response = await fetch(`${API_BASE_URL}/api/blog/${encodeURIComponent(slug)}`);
  if (!response.ok) {
    throw new Error(`Post not found (${response.status})`);
  }
  return response.json();
}

export interface TournamentSummary {
  slug: string;
  name: string;
  organizer: string;
  start_date: string;
  end_date: string;
  status: "upcoming" | "live" | "completed";
  prize_pool_usd: number;
  team_count: number;
}

export interface TournamentStanding {
  rank: number;
  team: string;
  wins: number;
  losses: number;
}

export interface TournamentMatch {
  id: number;
  round: string;
  date: string;
  team_a: string;
  team_b: string;
  score_a: number | null;
  score_b: number | null;
}

export interface Tournament extends TournamentSummary {
  standings: TournamentStanding[];
  matches: TournamentMatch[];
}

export interface TournamentListResponse {
  tournaments: TournamentSummary[];
}

export async function fetchTournaments(): Promise<TournamentListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tournaments`);
  if (!response.ok) {
    throw new Error(`Failed to load tournaments (${response.status})`);
  }
  return response.json();
}

export async function fetchTournament(slug: string): Promise<Tournament> {
  const response = await fetch(`${API_BASE_URL}/api/tournaments/${encodeURIComponent(slug)}`);
  if (!response.ok) {
    throw new Error(`Tournament not found (${response.status})`);
  }
  return response.json();
}

export interface MapKill {
  t_min: number;
  x: number;
  y: number;
  team: "amber" | "sapphire";
}

export interface MapObjective {
  name: string;
  lane: "left" | "middle" | "right";
  owner: "amber" | "sapphire";
  x: number;
  y: number;
  destroyed_at: number | null;
}

export interface MatchMapResponse {
  match_id: number;
  minimap_url: string | null;
  kills: MapKill[];
  objectives: MapObjective[];
}

export async function fetchMatchMap(matchId: string): Promise<MatchMapResponse> {
  const response = await fetch(`${API_BASE_URL}/api/matches/${encodeURIComponent(matchId)}/map`);
  if (!response.ok) {
    throw new Error(`Failed to load match map (${response.status})`);
  }
  return response.json();
}

export interface LeaderboardPlayer {
  position: number;
  steam_id: string;
  name: string;
  rank: string;
  rating: number;
  win_rate: number;
  matches: number;
  top_hero: string;
}

export interface LeaderboardResponse {
  region: string;
  players: LeaderboardPlayer[];
}

export async function fetchLeaderboard(): Promise<LeaderboardResponse> {
  const response = await fetch(`${API_BASE_URL}/api/leaderboard`);
  if (!response.ok) {
    throw new Error(`Failed to load leaderboard (${response.status})`);
  }
  return response.json();
}

export interface Crate {
  id: number;
  x: number;
  y: number;
  area: "alley" | "tunnel";
  spawn_min: number;
  respawn_min: number;
}

export interface BoxRouteStop {
  order: number;
  crate_id: number;
  x: number;
  y: number;
  arrive_s: number;
}

export interface BoxRoute {
  team: "amber" | "sapphire";
  stops: BoxRouteStop[];
  loop_seconds: number;
  naive_loop_seconds: number;
}

export interface BoxRouteResponse {
  crates: Crate[];
  routes: BoxRoute[];
}

export async function fetchBoxRoutes(): Promise<BoxRouteResponse> {
  const response = await fetch(`${API_BASE_URL}/api/map/box-routes`);
  if (!response.ok) {
    throw new Error(`Failed to load box routes (${response.status})`);
  }
  return response.json();
}

export interface PlayerGrade {
  category: string;
  letter: "S" | "A" | "B" | "C" | "D" | "F";
  score: number;
}

export interface PlayerTendency {
  label: string;
  detail: string;
  tone: "strength" | "weakness";
}

export interface PlayerProfileResponse {
  steam_id: string;
  skill_rating: number;
  skill_percentile: number;
  grades: PlayerGrade[];
  tendencies: PlayerTendency[];
}

export async function fetchPlayerProfile(steamId: string): Promise<PlayerProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/api/players/${encodeURIComponent(steamId)}/profile`);
  if (!response.ok) {
    throw new Error(`Failed to load player profile (${response.status})`);
  }
  return response.json();
}

export interface NetWorthPoint {
  t_min: number;
  amber: number;
  sapphire: number;
}

export interface NetWorthResponse {
  match_id: number;
  points: NetWorthPoint[];
}

export async function fetchNetWorth(matchId: string): Promise<NetWorthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/matches/${encodeURIComponent(matchId)}/net-worth`);
  if (!response.ok) {
    throw new Error(`Failed to load net worth (${response.status})`);
  }
  return response.json();
}
