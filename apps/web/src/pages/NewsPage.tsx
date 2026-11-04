import { useSearchParams } from "react-router-dom";
import { fetchNews, fetchPatchSummary } from "@/api";
import type { NewsItem, PatchChange } from "@/api";
import { percent } from "@/chartTheme";
import GameIcon from "@/components/GameIcon";
import { ErrorState, LoadingState, PageHeader, PageShell, Section } from "@/components/site/primitives";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAsync } from "@/lib/useAsync";
import { cn } from "@/lib/utils";

function PatchChangeRow({ change }: { change: PatchChange }) {
  const up = change.delta >= 0;
  return (
    <li className="flex items-center justify-between gap-3 py-2.5">
      <span className="flex items-center gap-2.5">
        <GameIcon name={change.name} kind="hero" />
        {change.name}
      </span>
      <span className={cn("font-mono text-sm tabular-nums", up ? "text-good" : "text-bad")}>
        {up ? "+" : "−"}
        {Math.abs(Math.round(change.delta * 100))}%{" "}
        <span className="text-muted-foreground">({percent(change.win_rate)})</span>
      </span>
    </li>
  );
}

const FILTERS = [
  { value: "all", label: "All" },
  { value: "patch-notes", label: "Patch Notes" },
  { value: "news", label: "News" },
] as const;

const TAG_LABELS: Record<NewsItem["tag"], string> = {
  "patch-notes": "Patch Notes",
  news: "News",
};

function NewsPage() {
  const [params, setParams] = useSearchParams();
  const filter = params.get("tag") ?? "all";
  const { data, error } = useAsync(fetchNews, "news");
  const items = data?.items.filter((item) => filter === "all" || item.tag === filter) ?? [];
  const patchSummary = useAsync(fetchPatchSummary, "patch-summary");

  return (
    <PageShell>
      <PageHeader
        title="Patch Notes & Updates"
        actions={
          <Tabs
            value={filter}
            onValueChange={(value) => setParams(value === "all" ? {} : { tag: String(value) }, { replace: true })}
          >
            <TabsList className="h-auto rounded-lg border bg-transparent p-1">
              {FILTERS.map((f) => (
                <TabsTrigger
                  key={f.value}
                  value={f.value}
                  className="rounded-md px-3 py-1.5 data-active:bg-soul! data-active:text-primary-foreground! data-active:border-transparent!"
                >
                  {f.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        }
      />

      {error && <ErrorState message={`${error}. Refresh to try again.`} />}
      {!data && !error && <LoadingState label="Loading news…" variant="list" />}

      {patchSummary.data && (
        <div className="grid gap-6 sm:grid-cols-2">
          <Section
            title="Patch Winners"
            description={`${patchSummary.data.previous_patch} → ${patchSummary.data.patch}`}
          >
            <ul className="flex flex-col divide-y">
              {patchSummary.data.winners.map((change) => (
                <PatchChangeRow key={change.hero_id} change={change} />
              ))}
            </ul>
          </Section>
          <Section
            title="Patch Losers"
            description={`${patchSummary.data.previous_patch} → ${patchSummary.data.patch}`}
          >
            <ul className="flex flex-col divide-y">
              {patchSummary.data.losers.map((change) => (
                <PatchChangeRow key={change.hero_id} change={change} />
              ))}
            </ul>
          </Section>
        </div>
      )}

      {data && items.length === 0 && (
        <p className="text-sm text-muted-foreground">Nothing here yet. Check back after the next patch.</p>
      )}

      {items.length > 0 && (
        <ol className="flex flex-col divide-y border-y">
          {items.map((item) => (
            <li key={item.id} className="grid gap-2 py-6 sm:grid-cols-[9rem_1fr] sm:gap-8">
              <div className="flex items-center gap-3 sm:flex-col sm:items-start">
                <time dateTime={item.date} className="font-mono text-sm text-muted-foreground tabular-nums">
                  {item.date}
                </time>
                <Badge variant={item.tag === "patch-notes" ? "default" : "outline"}>{TAG_LABELS[item.tag]}</Badge>
              </div>
              <div className="flex flex-col gap-1.5">
                <h2 className="text-lg font-medium text-balance">
                  {item.url ? (
                    <a href={item.url} target="_blank" rel="noreferrer" className="hover:text-soul hover:underline">
                      {item.title}
                    </a>
                  ) : (
                    item.title
                  )}
                </h2>
                <p className="text-sm text-pretty text-muted-foreground">{item.summary}</p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </PageShell>
  );
}

export default NewsPage;
