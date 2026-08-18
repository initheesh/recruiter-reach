import { NextResponse } from "next/server";

const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);

  if (!body) {
    return NextResponse.json({ detail: "Invalid JSON payload." }, { status: 400 });
  }

  try {
    const response = await fetch(`${BACKEND_BASE_URL}/applications/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const payload = await response.json().catch(() => ({}));

    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to reach backend generate endpoint." }, { status: 502 });
  }
}
