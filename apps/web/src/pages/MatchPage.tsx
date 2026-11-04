import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Pause, Play, RotateCcw } from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchBoxRoutes, fetchMatchMap, fetchNetWorth, fetchWinProbability } from "@/api";
import { CHART, axisProps, interpolate, percent } from "@/chartTheme";
import ChartTooltip from "@/components/ChartTooltip";
import MatchHeader from "@/components/site/MatchHeader";
import MatchMap from "@/components/site/MatchMap";
import { ErrorState, LoadingState, PageShell, Section, Stat, TeamLabel } from "@/components/site/primitives";
import { Button } from "@/components/ui/button";
import { useAsync } from "@/lib/useAsync";
import { cn } from "@/lib/utils";

// A full match replays in roughly 12 seconds regardless of its length.
const REPLAY_SECONDS = 12;
const TICK_MS = 50;

function clock(tMin: number) {
  const total = Math.round(tMin * 60);
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

function useReplay(duration: number) {
  // null = showing the finished match; a number = replay position in minutes.
  const [position, setT] = useState<number | null>(null);
  const [playing, setPlaying] = useState(false);
  const t = position ?? duration;

  useEffect(() => {
    if (!playing) return;
    const step = duration / ((REPLAY_SECONDS * 1000) / TICK_MS);
    const id = window.setInterval(() => {
      setT((prev) => {
        const next = Math.min(duration, (prev ?? 0) + step);
        if (next >= duration) {
          setPlaying(false);
          return null;
        }
        return next;
      });
    }, TICK_MS);
    return () => window.clearInterval(id);
  }, [playing, duration]);

  return {
    t,
    playing,
    toggle: () => {
      if (!playing && t >= duration) setT(0);
      setPlaying(!playing);
    },
    restart: () => {
      setT(0);
      setPlaying(true);
    },
    seek: (next: number) => {
      setPlaying(false);
      setT(next >= duration ? null : next);
    },
  };
}

function MatchPage() {
  const { matchId = "" } = useParams<{ matchId: string }>();
  const { data, error } = useAsync(() => fetchWinProbability(matchId), `wp-${matchId}`);
  const map = useAsync(() => fetchMatchMap(matchId), `map-${matchId}`);
  const boxRoutes = useAsync(fetchBoxRoutes, "box-routes");
  const netWorth = useAsync(() => fetchNetWorth(matchId), `nw-${matchId}`);

  const pWins = data?.points.map((p) => p.p_win) ?? [];
  const last = data?.points[data.points.length - 1];
  const duration = last?.t_min ?? 0;
  const replay = useReplay(duration);
  const replaying = replay.t < duration;
  const pNow = data ? interpolate(data.points, replay.t) : 0;
  const lastEvent = data?.events.filter((e) => e.t_min <= replay.t).at(-1);

  return (
    <PageShell>
      <MatchHeader matchId={matchId} />

      {error && <ErrorState message={`${error}. Check the match ID and try again.`} />}
      {!data && !error && <LoadingState label="Loading match…" />}

      {data && last && (
        <>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Stat label="Winner" value={<TeamLabel team={data.winner} />} />
            <Stat label="Duration" value={`${Math.round(last.t_min)} min`} />
            <Stat label="Lowest" value={percent(Math.min(...pWins))} hint={`${data.team_perspective} win chance`} />
            <Stat label="Highest" value={percent(Math.max(...pWins))} hint={`${data.team_perspective} win chance`} />
          </div>

          <Section
            title="Win Probability"
            description={`${data.team_perspective[0].toUpperCase()}${data.team_perspective.slice(1)} team’s chance to win · model ${data.model_version}`}
          >
            <div className="h-72">
              <ResponsiveContainer>
                <AreaChart data={data.points} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                  <defs>
                    <linearGradient id="wp-fill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0" stopColor={CHART.mark} stopOpacity={0.22} />
                      <stop offset="1" stopColor={CHART.mark} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke={CHART.grid} vertical={false} />
                  <XAxis dataKey="t_min" type="number" domain={["dataMin", "dataMax"]} unit="m" {...axisProps} />
                  <YAxis domain={[0, 1]} ticks={[0, 0.25, 0.5, 0.75, 1]} tickFormatter={percent} {...axisProps} axisLine={false} />
                  <ReferenceLine y={0.5} stroke={CHART.reference} strokeDasharray="3 3" />
                  {data.events.map((event) => (
                    <ReferenceDot
                      key={`${event.t_min}-${event.detail}-${event.team}`}
                      x={event.t_min}
                      y={interpolate(data.points, event.t_min)}
                      r={4}
                      fill={event.team === "amber" ? "var(--amber)" : "var(--sapphire)"}
                      fillOpacity={event.t_min <= replay.t ? 1 : 0.25}
                      stroke={CHART.surface}
                      strokeWidth={2}
                    />
                  ))}
                  {replaying && (
                    <>
                      <ReferenceArea x1={replay.t} x2={duration} fill={CHART.surface} fillOpacity={0.7} />
                      <ReferenceLine x={replay.t} stroke={CHART.mark} />
                      <ReferenceDot x={replay.t} y={pNow} r={5} fill={CHART.mark} stroke={CHART.surface} strokeWidth={2} />
                    </>
                  )}
                  <Tooltip
                    cursor={{ stroke: CHART.axis, strokeDasharray: "3 3" }}
                    content={({ active, payload, label }) =>
                      active && payload?.length ? (
                        <ChartTooltip>
                          <span className="font-mono tabular-nums">{label}m</span> ·{" "}
                          <span className="font-mono text-foreground tabular-nums">
                            {percent(Number(payload[0].value))}
                          </span>{" "}
                          to win
                        </ChartTooltip>
                      ) : null
                    }
                  />
                  <Area
                    type="monotone"
                    dataKey="p_win"
                    stroke={CHART.mark}
                    strokeWidth={2}
                    fill="url(#wp-fill)"
                    activeDot={{ r: 4, stroke: CHART.surface, strokeWidth: 2 }}
                    isAnimationActive={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <p className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              <span>Dots mark objectives:</span>
              <TeamLabel team="amber" />
              <TeamLabel team="sapphire" />
            </p>

            <div className="mt-5 flex flex-col gap-3 border-t pt-5 sm:flex-row sm:items-center sm:gap-4">
              <div className="flex items-center gap-2">
                <Button
                  size="icon"
                  onClick={replay.toggle}
                  aria-label={replay.playing ? "Pause replay" : "Play replay"}
                >
                  {replay.playing ? <Pause /> : <Play />}
                </Button>
                <Button size="icon" variant="outline" onClick={replay.restart} aria-label="Restart replay">
                  <RotateCcw />
                </Button>
                <span className="font-mono text-sm whitespace-nowrap tabular-nums">
                  {clock(replay.t)}
                  <span className="text-muted-foreground"> / {clock(duration)}</span>
                </span>
              </div>
              <input
                type="range"
                aria-label="Match time"
                min={0}
                max={duration}
                step={0.1}
                value={replay.t}
                onChange={(e) => replay.seek(Number(e.target.value))}
                className="h-1.5 flex-1 cursor-pointer accent-soul"
              />
              <div className="flex items-baseline gap-2 sm:w-56 sm:justify-end">
                <span className="font-mono text-lg text-foreground tabular-nums">{percent(pNow)}</span>
                <span className="truncate text-xs text-muted-foreground">
                  {lastEvent ? `after ${lastEvent.detail} (${lastEvent.team})` : "to win"}
                </span>
              </div>
            </div>
          </Section>

          {netWorth.data && (
            <Section title="Net Worth" description="Total souls per team · follows the replay above">
              <div className="h-56">
                <ResponsiveContainer>
                  <LineChart data={netWorth.data.points} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
                    <CartesianGrid stroke={CHART.grid} vertical={false} />
                    <XAxis dataKey="t_min" type="number" domain={["dataMin", "dataMax"]} unit="m" {...axisProps} />
                    <YAxis
                      tickFormatter={(v: number) => `${Math.round(v / 1000)}k`}
                      width={40}
                      {...axisProps}
                      axisLine={false}
                    />
                    {replaying && (
                      <>
                        <ReferenceArea x1={replay.t} x2={duration} fill={CHART.surface} fillOpacity={0.7} />
                        <ReferenceLine x={replay.t} stroke={CHART.mark} />
                      </>
                    )}
                    <Tooltip
                      cursor={{ stroke: CHART.axis, strokeDasharray: "3 3" }}
                      content={({ active, payload, label }) =>
                        active && payload?.length ? (
                          <ChartTooltip>
                            <span className="font-mono tabular-nums">{label}m</span>
                            {payload.map((entry) => (
                              <span key={String(entry.dataKey)} className="block capitalize">
                                {String(entry.dataKey)}{" "}
                                <span className="font-mono text-foreground tabular-nums">
                                  {Number(entry.value).toLocaleString("en-US")}
                                </span>
                              </span>
                            ))}
                          </ChartTooltip>
                        ) : null
                      }
                    />
                    <Line
                      type="monotone"
                      dataKey="amber"
                      stroke="var(--amber)"
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="sapphire"
                      stroke="var(--sapphire)"
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                <TeamLabel team="amber" />
                <TeamLabel team="sapphire" />
              </p>
            </Section>
          )}

          <div className="grid gap-6 lg:grid-cols-[3fr_2fr]">
            <Section
              title="Match Map"
              description="Real minimap, follows the replay above · drag to rotate · switch to the schematic to see a team's optimal box route"
            >
              {map.error && <ErrorState message={map.error} />}
              {!map.data && !map.error && <LoadingState label="Loading map…" variant="rows" />}
              {map.data && <MatchMap map={map.data} t={replay.t} boxRoutes={boxRoutes.data ?? undefined} />}
            </Section>

            <Section title="Objectives">
              <ol className="flex flex-col divide-y">
                {data.events.map((event) => (
                  <li
                    key={`${event.t_min}-${event.detail}-${event.team}`}
                    className={cn(
                      "grid grid-cols-[3.5rem_1fr_auto] items-center gap-3 py-3 text-sm transition-opacity first:pt-0 last:pb-0",
                      event.t_min > replay.t && "opacity-35",
                      event === lastEvent && replaying && "text-soul",
                    )}
                  >
                    <span className="font-mono text-muted-foreground tabular-nums">{event.t_min}m</span>
                    <span>{event.detail}</span>
                    <span className="text-muted-foreground">
                      <TeamLabel team={event.team} />
                    </span>
                  </li>
                ))}
              </ol>
            </Section>
          </div>
        </>
      )}
    </PageShell>
  );
}

export default MatchPage;
