"use client";

import { useMemo, useState } from "react";

import { ComposeScreen } from "@/app/components/compose-screen";
import type { FormState } from "@/app/components/workflow-types";
import { WorkflowHero } from "@/app/components/workflow-hero";
import { generateEmail, sendEmail } from "@/lib/api";
import type { GenerateApplicationRequest, SendApplicationRequest } from "@/lib/types";

const INITIAL_FORM: FormState = {
  recruiter_name: "",
  recruiter_email: "",
  company_name: "",
  job_title: "",
  job_description: "",
  additional_context: "",
};

export default function Home() {
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const canGenerate = useMemo(() => {
    return Boolean(form.recruiter_name.trim() && form.recruiter_email.trim() && form.company_name.trim() && form.job_title.trim() && form.job_description.trim());
  }, [form]);

  const canSend = useMemo(() => {
    return canGenerate && Boolean(subject.trim() && body.trim());
  }, [body, canGenerate, subject]);

  function updateForm<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((previous) => ({ ...previous, [key]: value }));
  }

  async function onGenerate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setIsGenerating(true);

    const payload: GenerateApplicationRequest = {
      recruiter_name: form.recruiter_name.trim(),
      recruiter_email: form.recruiter_email.trim(),
      company_name: form.company_name.trim(),
      job_title: form.job_title.trim(),
      job_description: form.job_description.trim(),
      additional_context: form.additional_context.trim(),
    };

    try {
      const generated = await generateEmail(payload);
      setSubject(generated.subject);
      setBody(generated.body);
      setSuccessMessage("Email generated. Review and edit before sending.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Generation failed.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function onSend() {
    setErrorMessage("");
    setSuccessMessage("");
    setIsSending(true);

    const payload: SendApplicationRequest = {
      recruiter_name: form.recruiter_name.trim(),
      recruiter_email: form.recruiter_email.trim(),
      company_name: form.company_name.trim(),
      job_title: form.job_title.trim(),
      subject: subject.trim(),
      body: body.trim(),
    };

    try {
      const response = await sendEmail(payload);
      setSuccessMessage(`${response.message} Message ID: ${response.gmail_message_id}`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Send failed.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="h-screen snap-y snap-mandatory overflow-y-auto overflow-x-clip bg-background text-foreground scroll-smooth">
      <WorkflowHero />

      <ComposeScreen body={body} canGenerate={canGenerate} canSend={canSend} errorMessage={errorMessage} form={form} isGenerating={isGenerating} isSending={isSending} onGenerate={onGenerate} onSend={onSend} onUpdateForm={updateForm} setBody={setBody} setSubject={setSubject} subject={subject} successMessage={successMessage} />
    </main>
  );
}
