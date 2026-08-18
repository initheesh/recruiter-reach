import type { FormEvent } from "react";

import type { FormState } from "@/app/components/workflow-types";

type ComposeScreenProps = {
  body: string;
  canGenerate: boolean;
  canSend: boolean;
  errorMessage: string;
  form: FormState;
  isGenerating: boolean;
  isSending: boolean;
  onGenerate: (event: FormEvent<HTMLFormElement>) => void;
  onSend: () => void;
  onUpdateForm: (key: keyof FormState, value: string) => void;
  setBody: (value: string) => void;
  setSubject: (value: string) => void;
  subject: string;
  successMessage: string;
};

export function ComposeScreen({ body, canGenerate, canSend, errorMessage, form, isGenerating, isSending, onGenerate, onSend, onUpdateForm, setBody, setSubject, subject, successMessage }: ComposeScreenProps) {
  return (
    <section className="snap-start">
      <div className="mx-auto min-h-screen w-full max-w-7xl px-6 py-5">
        <div className="grid h-[calc(100vh-2.5rem)] gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <form className="flex h-full flex-col overflow-hidden rounded-3xl border border-border bg-card p-4 shadow-lg sm:p-5" onSubmit={onGenerate}>
            <div className="min-h-0 flex-1 overflow-y-auto pb-4 scrollbar-none [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
              <div className="mb-6 flex items-center justify-between gap-4">
                <h2 className="font-(--font-calistoga) text-3xl">Generate Email</h2>
                <span className="rounded-full bg-muted px-3 py-1 font-mono text-xs uppercase tracking-[0.12em] text-muted-foreground">Step 1</span>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="space-y-2 text-sm font-medium text-foreground">
                  Recruiter Name
                  <input className="h-12 w-full rounded-xl border border-border bg-background px-4 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => onUpdateForm("recruiter_name", event.target.value)} placeholder="Alex Morgan" required type="text" value={form.recruiter_name} />
                </label>

                <label className="space-y-2 text-sm font-medium text-foreground">
                  Recruiter Email
                  <input className="h-12 w-full rounded-xl border border-border bg-background px-4 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => onUpdateForm("recruiter_email", event.target.value)} placeholder="alex@company.com" required type="email" value={form.recruiter_email} />
                </label>

                <label className="space-y-2 text-sm font-medium text-foreground">
                  Company Name
                  <input className="h-12 w-full rounded-xl border border-border bg-background px-4 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => onUpdateForm("company_name", event.target.value)} placeholder="Bright Labs" required type="text" value={form.company_name} />
                </label>

                <label className="space-y-2 text-sm font-medium text-foreground">
                  Job Title
                  <input className="h-12 w-full rounded-xl border border-border bg-background px-4 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => onUpdateForm("job_title", event.target.value)} placeholder="Frontend Engineer" required type="text" value={form.job_title} />
                </label>
              </div>

              <label className="mt-4 block space-y-2 text-sm font-medium text-foreground">
                Job Description
                <textarea className="min-h-40 w-full rounded-2xl border border-border bg-background px-4 py-3 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => onUpdateForm("job_description", event.target.value)} placeholder="Paste the job description here." required value={form.job_description} />
              </label>

              <label className="mt-4 block space-y-2 text-sm font-medium text-foreground">
                Additional Context (Optional)
                <textarea className="min-h-28 w-full rounded-2xl border border-border bg-background px-4 py-3 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => onUpdateForm("additional_context", event.target.value)} placeholder="Example: I already applied on careers portal. Job ID: TCS-4567. Reaching out for better visibility." value={form.additional_context} />
              </label>
            </div>

            <div className="shrink-0 border-t border-border/80 bg-card pt-4 pb-1.5">
              <button className="group inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-linear-to-r from-accent to-accent-secondary px-5 text-sm font-semibold text-accent-foreground shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:brightness-110 hover:shadow-accent disabled:cursor-not-allowed disabled:opacity-60" disabled={isGenerating || !canGenerate} type="submit">
                {isGenerating ? "Generating..." : "Generate Email"}
                <span className="transition-transform duration-200 group-hover:translate-x-1">&rarr;</span>
              </button>

              {errorMessage ? <p className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</p> : null}
              {successMessage ? <p className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{successMessage}</p> : null}
            </div>
          </form>

          <div className="h-full overflow-hidden rounded-3xl border border-accent/20 bg-linear-to-br from-accent/5 via-card to-card p-0.5 shadow-lg">
            <div className="flex h-full flex-col rounded-[calc(1.5rem-2px)] bg-card p-4 sm:p-5">
              <div className="min-h-0 flex-1 overflow-y-auto pb-4 scrollbar-none [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
                <div className="mb-6 flex items-center justify-between gap-4">
                  <h2 className="font-(--font-calistoga) text-3xl">Preview and Edit</h2>
                  <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 font-mono text-xs uppercase tracking-[0.12em] text-accent">Step 2</span>
                </div>

                <label className="mb-3 block space-y-2 text-sm font-medium text-foreground">
                  Subject
                  <input className="h-12 w-full rounded-xl border border-border bg-background px-4 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => setSubject(event.target.value)} placeholder="Generated subject appears here" value={subject} />
                </label>

                <label className="block space-y-2 text-sm font-medium text-foreground">
                  Body
                  <textarea className="min-h-56 w-full rounded-2xl border border-border bg-background px-4 py-3 text-sm leading-relaxed outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/25" onChange={(event) => setBody(event.target.value)} placeholder="Generated body appears here" value={body} />
                </label>

                <div className="mt-5 rounded-2xl border border-border bg-muted/40 p-4">
                  <p className="font-mono text-xs uppercase tracking-[0.14em] text-muted-foreground">Email Preview</p>
                  <div className="mt-3 space-y-3 text-sm leading-relaxed">
                    <p>
                      <span className="font-semibold text-foreground">To:</span> {form.recruiter_email || "(recruiter email)"}
                    </p>
                    <p>
                      <span className="font-semibold text-foreground">Subject:</span> {subject || "(subject)"}
                    </p>
                    <p className="whitespace-pre-wrap text-muted-foreground">{body || "(body)"}</p>
                  </div>
                </div>
              </div>

              <div className="shrink-0 border-t border-border/80 bg-card pt-4 pb-1.5">
                <button className="group inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-linear-to-r from-accent to-accent-secondary px-5 text-sm font-semibold text-accent-foreground shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:brightness-110 hover:shadow-accent disabled:cursor-not-allowed disabled:opacity-60" disabled={isSending || !canSend} onClick={onSend} type="button">
                  {isSending ? "Sending..." : "Send Email"}
                  <span className="transition-transform duration-200 group-hover:translate-x-1">&rarr;</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
