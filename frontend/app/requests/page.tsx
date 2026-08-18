"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { getSentApplications } from "@/lib/api";
import type { ApplicationListItemResponse } from "@/lib/types";

function formatDate(dateText: string): string {
  const date = new Date(dateText);
  if (Number.isNaN(date.getTime())) {
    return "Unknown time";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function RequestsPage() {
  const [requests, setRequests] = useState<ApplicationListItemResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  async function loadRequests() {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const sent = await getSentApplications();
      setRequests(sent);
      setSelectedId((previous) => {
        if (previous !== null && sent.some((item) => item.id === previous)) {
          return previous;
        }

        return sent[0]?.id ?? null;
      });
    } catch (error) {
      setRequests([]);
      setSelectedId(null);
      setErrorMessage(error instanceof Error ? error.message : "Unable to load sent requests.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadRequests();
  }, []);

  const selectedRequest = useMemo(() => {
    if (selectedId === null) {
      return null;
    }

    return requests.find((item) => item.id === selectedId) ?? null;
  }, [requests, selectedId]);

  return (
    <main className="h-screen overflow-hidden bg-background text-foreground">
      <section className="relative h-full overflow-hidden">
        <div className="pointer-events-none absolute -left-20 top-10 h-88 w-88 rounded-full bg-[radial-gradient(circle,rgba(0,82,255,0.18),transparent_72%)] blur-[70px]" />
        <div className="pointer-events-none absolute -right-16 bottom-8 h-72 w-72 rounded-full bg-[radial-gradient(circle,rgba(77,124,255,0.2),transparent_68%)] blur-[75px]" />

        <div className="mx-auto flex h-full w-full max-w-7xl flex-col px-6 py-5">
          <div className="mb-4 flex shrink-0 flex-wrap items-center justify-between gap-4">
            <div className="inline-flex items-center gap-3 rounded-full border border-accent/30 bg-accent/5 px-5 py-2">
              <span className="pulse-indicator h-2 w-2 rounded-full bg-accent" />
              <span className="font-mono text-xs uppercase tracking-[0.15em] text-accent">Sent Requests</span>
            </div>

            <div className="flex items-center gap-2">
              <Link className="inline-flex h-10 items-center rounded-xl border border-border bg-card px-4 text-sm font-medium text-foreground transition hover:border-accent/50 hover:text-accent" href="/">
                Back to Home
              </Link>

              <button
                className="h-10 rounded-xl border border-border bg-card px-4 text-sm font-medium text-foreground transition hover:border-accent/50 hover:text-accent"
                onClick={() => {
                  void loadRequests();
                }}
                type="button"
              >
                {isLoading ? "Refreshing..." : "Refresh"}
              </button>
            </div>
          </div>

          <h1 className="shrink-0 font-(--font-calistoga) text-3xl leading-tight tracking-[-0.01em] sm:text-4xl">All Sent Email Requests</h1>
          <p className="mt-2 shrink-0 max-w-2xl text-sm leading-relaxed text-muted-foreground sm:text-base">Browse every sent outreach on the left and inspect full details on the right preview panel.</p>

          <div className="mt-5 grid min-h-0 flex-1 gap-4 overflow-hidden grid-rows-[0.44fr_0.56fr] lg:grid-cols-[0.72fr_1.28fr] lg:grid-rows-1 lg:gap-6 xl:grid-cols-[0.64fr_1.36fr]">
            <div className="h-full overflow-hidden rounded-3xl border border-border bg-card shadow-lg">
              <div className="flex h-full flex-col">
                <div className="shrink-0 border-b border-border bg-muted/40 px-5 py-4">
                  <p className="font-mono text-xs uppercase tracking-[0.14em] text-muted-foreground">List View</p>
                </div>

                <div className="min-h-0 flex-1 overflow-y-auto p-4 scrollbar-none [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
                  {isLoading ? (
                    <p className="text-sm text-muted-foreground">Loading sent requests...</p>
                  ) : errorMessage ? (
                    <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</p>
                  ) : requests.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No requests found.</p>
                  ) : (
                    <ul className="space-y-3">
                      {requests.map((item) => {
                        const isSelected = item.id === selectedRequest?.id;

                        return (
                          <li key={item.id}>
                            <button
                              className={`w-full rounded-2xl border p-4 text-left transition ${isSelected ? "border-accent/40 bg-accent/5 shadow-accent" : "border-border bg-background hover:border-accent/30 hover:bg-accent/5"}`}
                              onClick={() => {
                                setSelectedId(item.id);
                              }}
                              type="button"
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <p className="text-sm font-semibold text-foreground">{item.company_name}</p>
                                  <p className="text-sm text-muted-foreground">{item.job_title}</p>
                                </div>
                                <span className="rounded-full bg-accent/15 px-2.5 py-1 font-mono text-[11px] uppercase tracking-[0.12em] text-accent">{item.status}</span>
                              </div>

                              <p className="mt-2 text-sm text-foreground/85">{item.recruiter_name}</p>
                              <p className="text-sm text-muted-foreground">{item.recruiter_email}</p>
                              <p className="mt-3 line-clamp-1 text-sm font-medium text-foreground">{item.subject}</p>
                              <p className="mt-2 text-xs uppercase tracking-[0.12em] text-muted-foreground">Sent {formatDate(item.sent_at)}</p>
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              </div>
            </div>

            <div className="h-full overflow-hidden rounded-3xl border border-accent/20 bg-linear-to-br from-accent/5 via-card to-card p-0.5 shadow-lg">
              <div className="flex h-full flex-col rounded-[calc(1.5rem-2px)] bg-card">
                <div className="shrink-0 border-b border-border px-6 py-4">
                  <p className="font-mono text-xs uppercase tracking-[0.14em] text-accent">Preview</p>
                </div>

                <div className="min-h-0 flex-1 overflow-y-auto px-6 py-5 scrollbar-none [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
                  {selectedRequest ? (
                    <div className="space-y-5">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h2 className="font-(--font-calistoga) text-3xl leading-tight">{selectedRequest.company_name}</h2>
                          <p className="mt-1 text-sm text-muted-foreground">{selectedRequest.job_title}</p>
                        </div>
                        <span className="rounded-full border border-accent/30 bg-accent/10 px-3 py-1 font-mono text-xs uppercase tracking-[0.12em] text-accent">{selectedRequest.status}</span>
                      </div>

                      <div className="grid gap-4 rounded-2xl border border-border bg-muted/35 p-4 sm:grid-cols-2">
                        <div>
                          <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">Recruiter</p>
                          <p className="mt-1 text-sm font-medium text-foreground">{selectedRequest.recruiter_name}</p>
                          <p className="text-sm text-muted-foreground">{selectedRequest.recruiter_email}</p>
                        </div>
                        <div>
                          <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">Sent Time</p>
                          <p className="mt-1 text-sm font-medium text-foreground">{formatDate(selectedRequest.sent_at)}</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <p className="font-mono text-xs uppercase tracking-[0.13em] text-muted-foreground">Subject</p>
                        <p className="wrap-break-word rounded-xl border border-border bg-background px-4 py-3 text-sm font-medium text-foreground">{selectedRequest.subject}</p>
                      </div>

                      <div className="space-y-2">
                        <p className="font-mono text-xs uppercase tracking-[0.13em] text-muted-foreground">Body</p>
                        <div className="rounded-2xl border border-border bg-background px-4 py-4 text-sm leading-relaxed text-muted-foreground">
                          <p className="whitespace-pre-wrap wrap-break-word">{selectedRequest.body}</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">Select a request from the list to view full details.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
