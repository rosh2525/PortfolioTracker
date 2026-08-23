"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ExternalLink, Sparkles } from "lucide-react";
import { api, ApiClientError, extractApiErrorMessage, pollTask } from "@/lib/api-client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { StockAnalysis, StockAnalysisPost } from "@/types";

const labels: Record<string, string> = {
  VERY_BEARISH: "Very Bearish",
  BEARISH: "Bearish",
  NEUTRAL: "Neutral",
  BULLISH: "Bullish",
  VERY_BULLISH: "Very Bullish",
  fundamentals: "Fundamentals",
  valuation: "Valuation",
  earnings: "Earnings",
  momentum: "Momentum",
  news: "News",
};

function List({ title, items }: { title: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div>
      <h4 className="text-sm font-semibold mb-1">{title}</h4>
      <ul className="list-disc pl-5 space-y-1 text-sm text-muted-foreground">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export function StockThesisCard({ assetId }: { assetId: string }) {
  const queryClient = useQueryClient();
  const queryKey = ["stock-analysis", assetId];
  const query = useQuery({
    queryKey,
    queryFn: () => api.get<StockAnalysis | null>(`/assets/${assetId}/stock-analysis/`),
    retry: (count, error) => !(error instanceof ApiClientError && error.status === 400) && count < 2,
    refetchInterval: (state) => (["PENDING", "RUNNING"].includes(state.state.data?.status ?? "") ? 2000 : false),
  });
  const generate = useMutation({
    mutationFn: () => api.post<StockAnalysisPost>(`/assets/${assetId}/stock-analysis/`),
    onSuccess: async (data) => {
      if (data.cached) queryClient.setQueryData(queryKey, data.analysis);
      else {
        await queryClient.invalidateQueries({ queryKey });
        await pollTask(data.task_id).catch(() => undefined);
        await queryClient.invalidateQueries({ queryKey });
      }
    },
  });
  if (query.error instanceof ApiClientError && query.error.status === 400) return null;
  const analysis = query.data;
  const earnings =
    analysis?.metrics_snapshot.earnings && typeof analysis.metrics_snapshot.earnings === "object"
      ? (analysis.metrics_snapshot.earnings as Record<string, unknown>)
      : null;
  const error = generate.error ? extractApiErrorMessage(generate.error, "Analysis could not be started.") : null;
  const running = analysis && ["PENDING", "RUNNING"].includes(analysis.status);

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Stock Thesis
          </CardTitle>
          {analysis?.demo && <Badge variant="outline">Demo data — not live</Badge>}
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        {query.isLoading && <p className="text-sm text-muted-foreground">Loading analysis…</p>}
        {!query.isLoading && !analysis && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Generate an evidence-grounded signal from public fundamentals, price momentum, earnings and recent cited
              news.
            </p>
            <Button onClick={() => generate.mutate()} disabled={generate.isPending}>
              {generate.isPending ? "Starting…" : "Generate analysis"}
            </Button>
          </div>
        )}
        {running && (
          <div className="rounded-md border p-4">
            <p className="font-medium">Analysis in progress</p>
            <p className="text-sm text-muted-foreground mt-1">
              Collecting public evidence and validating cited sources. This page updates automatically.
            </p>
          </div>
        )}
        {analysis?.status === "FAILED" && (
          <div className="rounded-md border border-destructive/40 p-4">
            <p className="font-medium text-destructive">Analysis unavailable</p>
            <p className="text-sm text-muted-foreground mt-1">
              {analysis.error_code === "AI_QUOTA_LIMITED"
                ? "The free Gemini quota is currently exhausted. Try again later."
                : "The analysis provider could not produce a safe result."}
            </p>
          </div>
        )}
        {analysis?.status === "INSUFFICIENT_DATA" && (
          <div className="rounded-md border p-4">
            <p className="font-medium">Insufficient data</p>
            <p className="text-sm text-muted-foreground mt-1">
              A signal is withheld because coverage or independent cited evidence did not meet the minimum threshold.
            </p>
            <p className="text-sm mt-2">Data coverage: {analysis.data_coverage}%</p>
          </div>
        )}
        {analysis?.status === "COMPLETED" && (
          <>
            <div className="flex flex-wrap items-end gap-4">
              <div>
                <Badge className="text-sm">{labels[analysis.rating ?? ""]}</Badge>
                <p className="mt-2 text-4xl font-bold tabular-nums">
                  {analysis.signal_score}
                  <span className="text-base font-normal text-muted-foreground"> / 100 signal score</span>
                </p>
              </div>
              <div className="text-sm text-muted-foreground">Data coverage: {analysis.data_coverage}%</div>
            </div>
            {earnings && (
              <div className="grid gap-3 rounded-md border p-3 sm:grid-cols-4">
                <div>
                  <p className="text-xs text-muted-foreground">Latest earnings</p>
                  <p className="text-sm font-medium">{String(earnings.latest_reported_at ?? "Not available")}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">EPS estimate</p>
                  <p className="text-sm font-medium">{String(earnings.eps_estimate ?? "Not available")}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">EPS actual</p>
                  <p className="text-sm font-medium">{String(earnings.eps_actual ?? "Not available")}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Next earnings</p>
                  <p className="text-sm font-medium">{String(earnings.next_earnings_date ?? "Not announced")}</p>
                </div>
              </div>
            )}
            <p className="text-sm leading-6">{analysis.summary}</p>
            <div>
              <h4 className="text-sm font-semibold mb-2">Key metrics</h4>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {Object.entries(analysis.metrics_snapshot)
                  .filter(([, value]) => typeof value === "number")
                  .slice(0, 8)
                  .map(([name, value]) => (
                    <div key={name} className="rounded-md bg-muted/50 p-2">
                      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">
                        {name.replaceAll("_", " ")}
                      </p>
                      <p className="text-sm font-medium tabular-nums">
                        {Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              {Object.entries(analysis.factors).map(([name, factor]) => (
                <div key={name} className="rounded-md border p-3">
                  <div className="flex justify-between text-sm font-medium">
                    <span>{labels[name] ?? name}</span>
                    <span>{factor.score}</span>
                  </div>
                  <div className="mt-2 h-2 rounded bg-muted">
                    <div className="h-2 rounded bg-primary" style={{ width: `${factor.score}%` }} />
                  </div>
                  <p className="mt-2 text-xs leading-5 text-muted-foreground">{factor.explanation}</p>
                </div>
              ))}
            </div>
            <div className="grid gap-5 md:grid-cols-2">
              <List title="Bull case" items={analysis.bull_case} />
              <List title="Bear case" items={analysis.bear_case} />
              <List title="Catalysts" items={analysis.catalysts} />
              <List title="Risks" items={analysis.risks} />
            </div>
            {analysis.citations.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold mb-2">Sources</h4>
                <div className="space-y-2">
                  {analysis.citations.map((source) => (
                    <a
                      key={source.id}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer nofollow"
                      className="flex items-start gap-2 text-sm text-primary hover:underline"
                    >
                      <ExternalLink className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      <span>
                        {source.title}
                        <span className="block text-xs text-muted-foreground">
                          {source.domain}
                          {source.published_at ? ` · ${source.published_at}` : ""}
                        </span>
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              Data as of{" "}
              {analysis.data_timestamp ? new Date(analysis.data_timestamp).toLocaleString("en-IN") : "unknown"} · Model:{" "}
              {analysis.gemini_model}
            </p>
          </>
        )}
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="border-t pt-3 text-xs text-muted-foreground">
          AI-generated educational analysis—not financial advice. The signal score is not a probability, price target or
          trading instruction.
        </div>
      </CardContent>
    </Card>
  );
}
