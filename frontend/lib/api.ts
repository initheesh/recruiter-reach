import type { ApplicationListItemResponse, GenerateApplicationRequest, GenerateApplicationResponse, SendApplicationRequest, SendApplicationResponse } from "@/lib/types";

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = typeof payload?.detail === "string" ? payload.detail : "Request failed. Please try again.";
    throw new Error(message);
  }

  return payload as T;
}

export async function generateEmail(input: GenerateApplicationRequest): Promise<GenerateApplicationResponse> {
  const response = await fetch("/api/applications/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  return parseResponse<GenerateApplicationResponse>(response);
}

export async function sendEmail(input: SendApplicationRequest): Promise<SendApplicationResponse> {
  const response = await fetch("/api/applications/send", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  return parseResponse<SendApplicationResponse>(response);
}

export async function getSentApplications(): Promise<ApplicationListItemResponse[]> {
  const response = await fetch("/api/applications", {
    method: "GET",
    cache: "no-store",
  });

  return parseResponse<ApplicationListItemResponse[]>(response);
}
