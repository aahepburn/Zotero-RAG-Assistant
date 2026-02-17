import { request } from "./client";
import type { ChatRequest, ChatResponse } from "../types/api";

export async function chat(body: ChatRequest, signal?: AbortSignal): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify(body),
    signal,
  });
}
