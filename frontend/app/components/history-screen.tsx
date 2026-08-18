import Link from "next/link";

import type { ApplicationListItemResponse } from "@/lib/types";

type HistoryScreenProps = {
  formatDate: (dateText: string) => string;
  history: ApplicationListItemResponse[];
  historyLoading: boolean;
  onRefresh: () => void;
};

export function HistoryScreen({ formatDate, history, historyLoading, onRefresh }: HistoryScreenProps) {
  return (
    <section className="relative snap-start bg-foreground text-background">
      <div className="dot-pattern pointer-events-none absolute inset-0" />
      <div className="pointer-events-none absolute -left-24 bottom-10 h-[18rem] w-[18rem] rounded-full bg-[radial-gradient(circle,_rgba(77,124,255,0.26),_transparent_72%)] blur-[100px]" />

      <div className="relative mx-auto min-h-screen w-full max-w-7xl px-6 py-5">
        <div className="h-[calc(100vh-2.5rem)] overflow-y-auto">
          <div className="mb-8 flex items-center justify-between gap-4">
            <div className="inline-flex items-center gap-3 rounded-full border border-white/20 bg-white/5 px-5 py-2">
              <span className="pulse-indicator h-2 w-2 rounded-full bg-accent-secondary" />
              <span className="font-mono text-xs uppercase tracking-[0.15em] text-white/80">Sent Applications</span>
            </div>
            <div className="flex items-center gap-2">
              <Link className="inline-flex h-10 items-center rounded-xl border border-white/25 px-4 text-sm font-medium text-white transition hover:border-accent-secondary/70 hover:bg-white/10" href="/requests">
                View All
              </Link>
              <button className="h-10 rounded-xl border border-white/25 px-4 text-sm font-medium text-white transition hover:border-accent-secondary/70 hover:bg-white/10" onClick={onRefresh} type="button">
                {historyLoading ? "Refreshing..." : "Refresh"}
              </button>
            </div>
          </div>

          <h2 className="font-[var(--font-calistoga)] text-4xl leading-tight tracking-[-0.01em] sm:text-5xl">Recently Sent Outreach</h2>

          {historyLoading ? (
            <p className="mt-8 text-white/70">Loading sent history...</p>
          ) : history.length === 0 ? (
            <p className="mt-8 text-white/70">No sent emails yet.</p>
          ) : (
            <div className="mt-8 grid gap-5 lg:grid-cols-2">
              {history.map((item) => (
                <article className="rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur" key={item.id}>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <p className="font-semibold text-white">{item.company_name}</p>
                    <span className="rounded-full bg-accent/20 px-3 py-1 text-xs uppercase tracking-[0.12em] text-blue-100">{item.status}</span>
                  </div>

                  <p className="text-sm text-white/80">{item.job_title}</p>
                  <p className="mt-2 text-sm text-white/90">{item.recruiter_name}</p>
                  <p className="text-sm text-white/70">{item.recruiter_email}</p>
                  <p className="mt-3 text-sm font-medium text-blue-100">{item.subject}</p>
                  <p className="mt-2 line-clamp-3 text-sm text-white/75">{item.body}</p>
                  <p className="mt-4 text-xs uppercase tracking-[0.12em] text-white/60">Sent {formatDate(item.sent_at)}</p>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
