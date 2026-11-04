import { useSearchParams } from "react-router-dom";
import { ChevronDown } from "lucide-react";
import { fetchHeroBuilds, fetchHeroStats } from "@/api";
import { percent } from "@/chartTheme";
import GameIcon from "@/components/GameIcon";
import { ErrorState, LoadingState, PageHeader, PageShell, RankSelect, Section } from "@/components/site/primitives";
import { useAsync } from "@/lib/useAsync";

function HeroSelect({ value, onChange }: { value: number | null; onChange: (heroId: number) => void }) {
  const heroes = useAsync(() => fetchHeroStats(), "builds-heroes");
  return (
    <div className="relative w-full sm:w-56">
      <select
        aria-label="Select hero"
        value={value ?? ""}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-9 w-full cursor-pointer appearance-none rounded-md border bg-card py-1.5 pr-8 pl-3 text-sm outline-none focus-visible:border-soul/60"
      >
        {heroes.data?.heroes.map((hero) => (
          <option key={hero.hero_id} value={hero.hero_id} className="bg-card text-foreground">
            {hero.name}
          </option>
        ))}
      </select>
      <ChevronDown
        className="pointer-events-none absolute top-1/2 right-2.5 size-3.5 -translate-y-1/2 text-muted-foreground"
        aria-hidden="true"
      />
    </div>
  );
}

function BuildsPage() {
  const [params, setParams] = useSearchParams();
  const heroId = params.get("hero") ? Number(params.get("hero")) : 1;
  const rank = params.get("rank") ?? "";
  const builds = useAsync(() => fetchHeroBuilds(heroId, rank || null), `builds-${heroId}-${rank}`);

  return (
    <PageShell>
      <PageHeader
        title="Builds"
        description={`The highest win-rate item builds from top players, per hero${rank ? ` · ${rank} rank` : ""}.`}
        actions={
          <div className="flex gap-2">
            <RankSelect
              value={rank}
              onChange={(next) => {
                const nextParams = new URLSearchParams(params);
                if (next) nextParams.set("rank", next);
                else nextParams.delete("rank");
                setParams(nextParams, { replace: true });
              }}
            />
            <HeroSelect
              value={heroId}
              onChange={(next) => {
                const nextParams = new URLSearchParams(params);
                nextParams.set("hero", String(next));
                setParams(nextParams, { replace: true });
              }}
            />
          </div>
        }
      />

      {builds.error && <ErrorState message={`${builds.error}. Try another hero.`} />}
      {!builds.data && !builds.error && <LoadingState label="Loading builds…" variant="list" />}

      {builds.data && (
        <Section
          title={`${builds.data.hero_name} · Top Builds`}
          description={`Community builds ranked by confidence-adjusted win rate · patch ${builds.data.patch}`}
        >
          <ol className="flex flex-col divide-y">
            {builds.data.builds.map((build, i) => (
              <li
                key={build.build_id}
                className="flex flex-col gap-3 py-4 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="flex flex-col gap-2">
                  <span className="flex items-center gap-2 text-sm">
                    <span className="font-mono text-muted-foreground tabular-nums">#{i + 1}</span>
                    <span className="font-medium">{build.name}</span>
                    <span className="text-xs text-muted-foreground">
                      by {build.author} · {build.games.toLocaleString()} games
                    </span>
                  </span>
                  <div className="flex flex-wrap items-center gap-2">
                    {build.items.map((item) => (
                      <span
                        key={item}
                        className="flex items-center gap-1.5 rounded-md border bg-card px-2 py-1 text-xs"
                      >
                        <GameIcon name={item} kind="item" className="size-5" />
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
                <span className="font-mono text-lg font-medium text-soul tabular-nums">
                  {percent(build.win_rate)}
                </span>
              </li>
            ))}
          </ol>
        </Section>
      )}
    </PageShell>
  );
}

export default BuildsPage;
