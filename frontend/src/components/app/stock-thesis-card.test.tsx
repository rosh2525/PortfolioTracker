import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { StockThesisCard } from "./stock-thesis-card";
import { demoStockAnalysis } from "@/demo/data/stock-analysis";

function renderCard() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <StockThesisCard assetId="1" />
    </QueryClientProvider>,
  );
}

describe("StockThesisCard", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("renders a completed signal and permanent disclaimer", async () => {
    const data = {
      ...demoStockAnalysis,
      demo: false,
      citations: [
        {
          id: "S1",
          url: "https://www.nseindia.com/filing",
          title: "NSE filing",
          domain: "nseindia.com",
          cited_text: "",
          published_at: "2026-08-20",
        },
      ],
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(data), { status: 200 })));
    renderCard();
    expect(await screen.findByText("Bullish")).toBeInTheDocument();
    expect(screen.getByText(/72/)).toBeInTheDocument();
    expect(screen.getByText(/not financial advice/i)).toBeInTheDocument();
    const source = screen.getByRole("link", { name: /NSE filing/i });
    expect(source).toHaveAttribute("target", "_blank");
    expect(source).toHaveAttribute("rel", expect.stringContaining("noopener"));
  });

  it("labels static demo analysis", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(demoStockAnalysis), { status: 200 })));
    renderCard();
    expect(await screen.findByText("Demo data — not live")).toBeInTheDocument();
  });

  it("shows quota-limited failures without exposing provider details", async () => {
    const failed = { ...demoStockAnalysis, demo: false, status: "FAILED", error_code: "AI_QUOTA_LIMITED" };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(failed), { status: 200 })));
    renderCard();
    expect(await screen.findByText(/free Gemini quota is currently exhausted/i)).toBeInTheDocument();
    expect(screen.getByText(/not financial advice/i)).toBeInTheDocument();
  });
});
