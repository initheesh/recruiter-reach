import { NextResponse } from "next/server";

const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE_URL}/applications`, {
      method: "GET",
      cache: "no-store",
    });

    const payload = await response.json().catch(() => []);

    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to reach backend applications endpoint." }, { status: 502 });
  }
}
