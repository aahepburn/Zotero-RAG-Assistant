import React, { createContext, useContext } from "react";
import type { ChatResponse } from "../types/api";
import type { ChatMessage } from "../types/domain";
import { useChat as useChatHook } from "../hooks/useChat";
import { useSessions } from "./SessionsContext";
import type { Snippet as SessionSnippet, SourceRef as SessionSource, Message as SessionMessage } from "../types/session";

type ChatContextShape = {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  lastResponse: ChatResponse | null;
  sendMessage: (content: string) => Promise<void>;
  loadThread: (thread: { id: string; title?: string; messages: ChatMessage[]; lastResponse?: ChatResponse }) => void;
  clearMessages: () => void;
};

const ChatContext = createContext<ChatContextShape | null>(null);

export const ChatProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const { messages, loading, error, lastResponse, sendMessage: rawSendMessage, loadThread, clearMessages } = useChatHook();
  const sessions = useSessions();

  async function sendMessage(content: string) {
    // send via the chat hook, which returns created messages and the response
    const result = await rawSendMessage(content);
    if (!result) return;

    const { userMessage, assistantMessage, response } = result;

    // Ensure there is a session: if not, create one using the initial user question
    // Normalize possible backend shapes (some backends may use `sources` instead of `citations`)
    console.debug("chat response:", response);
    const citations = (response as any).citations ?? (response as any).sources ?? [];
    const snippets = (response as any).snippets ?? (response as any).results ?? [];

    let sessionId = sessions.currentSessionId;
    if (!sessionId) {
      const initialSources = (citations || []).map((c: any) => ({
        id: String(c.id ?? c.key ?? c.zoteroKey ?? c.itemKey ?? c.item_id ?? c.key ?? c.UUID ?? ""),
        title: c.title ?? c.itemTitle ?? c.name ?? "(no title)",
        authors: c.authors ?? c.creators ?? undefined,
        year: c.year ? String(c.year) : c.date ? String(c.date) : undefined,
        zoteroKey: c.zotero_key ?? c.key ?? c.itemKey ?? undefined,
        localPdfPath: c.pdf_path ?? c.filePath ?? c.local_path ?? undefined,
      } as SessionSource));
      const initialSnippets = (snippets || []).map((s: any) => ({
        id: String(s.id ?? s.snippet_id ?? s.key ?? crypto.randomUUID()),
        sourceId: String(s.citation_id ?? s.citationId ?? s.item_id ?? s.itemId ?? s.source_id ?? ""),
        text: s.snippet ?? s.text ?? s.content ?? "",
        locationHint: s.location ?? undefined,
        page: s.page ?? undefined,
        title: s.title ?? undefined,
        authors: s.authors ?? undefined,
        year: s.year ?? undefined,
      } as SessionSnippet));
      sessionId = sessions.createSession(userMessage.content, response.summary, initialSources, initialSnippets);
    } else {
      // convert to session Message shape and append to existing session
      const u: SessionMessage = { id: userMessage.id, role: "user", content: userMessage.content, createdAt: new Date().toISOString() };
      const a: SessionMessage = { id: assistantMessage.id, role: "assistant", content: assistantMessage.content, createdAt: new Date().toISOString() };
      sessions.appendMessage(sessionId, u);
      sessions.appendMessage(sessionId, a);

      // upsert sources (robust mapping)
      (citations || []).forEach((c: any) => {
        const src: SessionSource = {
          id: String(c.id ?? c.key ?? c.zoteroKey ?? c.itemKey ?? c.UUID ?? ""),
          title: c.title ?? c.itemTitle ?? c.name ?? "(no title)",
          authors: c.authors ?? c.creators ?? undefined,
          year: c.year ? String(c.year) : c.date ? String(c.date) : undefined,
          zoteroKey: c.zotero_key ?? c.key ?? c.itemKey ?? undefined,
          localPdfPath: c.pdf_path ?? c.filePath ?? c.local_path ?? undefined,
        } as SessionSource;
        sessions.upsertSource(sessionId!, src);
      });

      // add snippets (robust mapping with all metadata fields)
      (snippets || []).forEach((s: any) => {
        const sn: SessionSnippet = {
          id: String(s.id ?? s.snippet_id ?? crypto.randomUUID()),
          sourceId: String(s.citation_id ?? s.citationId ?? s.item_id ?? s.itemId ?? s.source_id ?? ""),
          text: s.snippet ?? s.text ?? s.content ?? "",
          locationHint: s.location ?? undefined,
          page: s.page ?? undefined,
          title: s.title ?? undefined,
          authors: s.authors ?? undefined,
          year: s.year ?? undefined,
        } as SessionSnippet;
        sessions.addSnippet(sessionId!, sn);
      });
    }
  }

  return (
    <ChatContext.Provider value={{ messages, loading, error, lastResponse, sendMessage, loadThread, clearMessages }}>
      {children}
    </ChatContext.Provider>
  );
};

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChatContext must be used within ChatProvider");
  return ctx;
}

export default ChatContext;
