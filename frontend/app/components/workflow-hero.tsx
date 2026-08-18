import Link from "next/link";

export function WorkflowHero() {
  return (
    <section className="relative snap-start">
      <div className="pointer-events-none absolute -left-28 top-16 h-104 w-104 rounded-full bg-[radial-gradient(circle,rgba(0,82,255,0.16),transparent_72%)] blur-[70px]" />
      <div className="pointer-events-none absolute -right-32 top-112 h-96 w-96 rounded-full bg-[radial-gradient(circle,rgba(77,124,255,0.15),transparent_70%)] blur-[75px]" />

      <div className="mx-auto grid min-h-screen w-full max-w-7xl items-center gap-8 px-6 py-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-7">
          <div className="inline-flex items-center gap-3 rounded-full border border-accent/30 bg-accent/5 px-5 py-2">
            <span className="pulse-indicator h-2 w-2 rounded-full bg-accent" />
            <span className="font-mono text-xs uppercase tracking-[0.15em] text-accent">Recruiter Workflow</span>
          </div>

          <h1 className="font-(--font-calistoga) text-[2.8rem] leading-[1.06] tracking-[-0.02em] sm:text-6xl lg:text-[5.25rem]">
            Generate and Send with a
            <span className="relative ml-2 inline-block">
              <span className="gradient-text">Live Preview</span>
              <span className="absolute -bottom-1 left-0 h-3 w-full rounded-sm bg-linear-to-r from-accent/20 to-accent-secondary/10" />
            </span>
          </h1>

          <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">Scroll by screen: details, preview, and sent history. Every step fits the viewport and stays focused.</p>

          <div className="flex flex-wrap items-center gap-3">
            <Link className="inline-flex h-11 items-center justify-center rounded-xl border border-accent/40 bg-accent/10 px-5 text-sm font-semibold text-accent transition hover:bg-accent/15" href="/requests">
              View All Requests
            </Link>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {["Capture role details", "Generate and edit copy", "Send and track history"].map((step, index) => (
              <div className="rounded-2xl border border-border bg-card p-4 shadow-sm" key={step}>
                <p className="mb-2 text-4xl font-semibold text-accent">0{index + 1}</p>
                <p className="text-sm text-muted-foreground">{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative hidden h-120 lg:block">
          <div className="rotating-ring absolute left-1/2 top-1/2 h-92 w-92 -translate-x-1/2 -translate-y-1/2 rounded-full border border-dashed border-accent/40" />
          <div className="floating-soft glass-card absolute right-3 top-12 rounded-3xl border border-accent/30 p-5 shadow-xl">
            <p className="font-mono text-xs uppercase tracking-[0.15em] text-accent">Subject</p>
            <p className="mt-2 max-w-68 text-sm text-foreground">Application for Frontend Engineer at Bright Labs</p>
          </div>
          <div className="floating-soft-delay glass-card absolute bottom-14 left-0 rounded-3xl border border-border p-5 shadow-lg">
            <p className="font-mono text-xs uppercase tracking-[0.15em] text-accent">Preview</p>
            <p className="mt-2 max-w-68 text-sm text-muted-foreground">Hi Alex, I am excited to apply and share why this role aligns with my experience...</p>
          </div>
          <div className="absolute bottom-8 right-8 h-20 w-20 rounded-3xl bg-linear-to-br from-accent to-accent-secondary shadow-accent-lg" />
          <div className="absolute left-8 top-24 grid grid-cols-3 gap-2 opacity-40">
            {Array.from({ length: 9 }).map((_, idx) => (
              <span className="h-2 w-2 rounded-full bg-accent" key={idx} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
