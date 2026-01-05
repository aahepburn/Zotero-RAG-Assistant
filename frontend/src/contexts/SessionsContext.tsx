import React, { createContext, useContext, useState, useEffect } from "react";
import type { Session, Snippet, Source, Message } from "../types/session";

// Legacy type alias for backward compatibility
type SourceRef = Source;

type SessionsShape = {
  sessions: Record<string, Session>;
  currentSessionId: string | null;
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  createSession: (
    initialUserQuestion: string,
    initialAnswer?: string,
    responseSources?: Source[],
    initialSources?: Source[],
    initialSnippets?: Snippet[],
    customTitle?: string,
    userMessageId?: string,
    assistantMessageId?: string,
  ) => { sessionId: string; assistantMessageId: string };
  appendMessage: (sessionId: string, message: Message) => void;
  updateSessionTitle: (sessionId: string, newTitle: string) => void;
  addSnippet: (sessionId: string, snippet: Snippet) => void;
  upsertSource: (sessionId: string, source: Source) => void;
  setCurrentSession: (id: string | null) => void;
  deleteSession: (id: string) => void;
  toggleLeft: () => void;
  toggleRight: () => void;
  getSession: (id: string) => Session | null;
};

const SessionsContext = createContext<SessionsShape | null>(null);

function nowISO() {
  return new Date().toISOString();
}

export const SessionsProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [sessions, setSessions] = useState<Record<string, Session>>({});
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [leftCollapsed, setLeftCollapsed] = useState<boolean>(false);
  const [rightCollapsed, setRightCollapsed] = useState<boolean>(false);

  const STORAGE_KEY = "zotero_llm_sessions_v1";

  // Load persisted state on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed.sessions) setSessions(parsed.sessions);
      // Validate that the currentSessionId exists in sessions
      if (parsed.currentSessionId && parsed.sessions && parsed.sessions[parsed.currentSessionId]) {
        setCurrentSessionId(parsed.currentSessionId);
      } else {
        // Clear invalid session ID
        setCurrentSessionId(null);
      }
      if (typeof parsed.leftCollapsed === "boolean") setLeftCollapsed(parsed.leftCollapsed);
      if (typeof parsed.rightCollapsed === "boolean") setRightCollapsed(parsed.rightCollapsed);
    } catch (e) {
      // ignore parse errors
      console.warn("Failed to load sessions from localStorage", e);
    }
  }, []);

  // Persist when sessions or selection/collapsed state changes
  useEffect(() => {
    try {
      const payload = JSON.stringify({ sessions, currentSessionId, leftCollapsed, rightCollapsed });
      localStorage.setItem(STORAGE_KEY, payload);
    } catch (e) {
      console.warn("Failed to persist sessions to localStorage", e);
    }
  }, [sessions, currentSessionId, leftCollapsed, rightCollapsed]);

  function createSession(
    initialUserQuestion: string, 
    initialAnswer = "", 
    responseSources: Source[] = [],
    initialSources: Source[] = [], 
    initialSnippets: Snippet[] = [], 
    customTitle?: string,
    userMessageId?: string,
    assistantMessageId?: string,
  ): { sessionId: string; assistantMessageId: string } {
    const id = crypto.randomUUID();
    const createdAt = nowISO();
    const userMsgId = userMessageId ?? crypto.randomUUID();
    const assistantMsgId = assistantMessageId ?? crypto.randomUUID();
    const userMsg: Message = { 
      id: userMsgId, 
      role: "user", 
      content: initialUserQuestion, 
      createdAt 
    };
    const assistantMsg: Message = { 
      id: assistantMsgId, 
      role: "assistant", 
      content: initialAnswer, 
      createdAt,
      sources: responseSources,  // Attach sources to assistant message
      timestamp: Date.now()
    };
    console.log("[SessionsContext] Creating assistant message with sources:", responseSources);
    console.log("[SessionsContext] Assistant message ID:", assistantMsgId);
    const title = customTitle || (initialUserQuestion || "New session").slice(0, 80);
    const s: Session = {
      id,
      title,
      createdAt,
      updatedAt: createdAt,
      messages: [userMsg, assistantMsg].filter(Boolean),
      snippets: initialSnippets || [],
      sources: initialSources || [],
    };
    setSessions((prev) => ({ ...prev, [id]: s }));
    setCurrentSessionId(id);
    return { sessionId: id, assistantMessageId: assistantMsgId };
  }

  function appendMessage(sessionId: string, message: Message) {
    setSessions((prev) => {
      const s = prev[sessionId];
      if (!s) return prev;
      const updated = { ...s, messages: [...s.messages, message], updatedAt: nowISO() };
      return { ...prev, [sessionId]: updated };
    });
  }

  function updateSessionTitle(sessionId: string, newTitle: string) {
    setSessions((prev) => {
      const s = prev[sessionId];
      if (!s) return prev;
      const updated = { ...s, title: newTitle, updatedAt: nowISO() };
      return { ...prev, [sessionId]: updated };
    });
  }

  function addSnippet(sessionId: string, snippet: Snippet) {
    setSessions((prev) => {
      const s = prev[sessionId];
      if (!s) return prev;
      const exists = s.snippets.find((x) => x.id === snippet.id);
      const updated = {
        ...s,
        snippets: exists ? s.snippets.map((x) => (x.id === snippet.id ? snippet : x)) : [...s.snippets, snippet],
        updatedAt: nowISO(),
      };
      return { ...prev, [sessionId]: updated };
    });
  }

  function upsertSource(sessionId: string, source: Source) {
    setSessions((prev) => {
      const s = prev[sessionId];
      if (!s) return prev;
      const exists = s.sources.find((x) => x.documentId === source.documentId);
      const updated = {
        ...s,
        sources: exists ? s.sources.map((x) => (x.documentId === source.documentId ? { ...x, ...source } : x)) : [...s.sources, source],
        updatedAt: nowISO(),
      };
      return { ...prev, [sessionId]: updated };
    });
  }

  function setCurrentSession(id: string | null) {
    setCurrentSessionId(id);
  }

  function toggleLeft() {
    setLeftCollapsed((p) => !p);
  }

  function toggleRight() {
    setRightCollapsed((p) => !p);
  }

  function getSession(id: string) {
    return sessions[id] ?? null;
  }

  function deleteSession(id: string) {
    setSessions((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    // If deleting current session, clear it
    if (currentSessionId === id) {
      setCurrentSessionId(null);
    }
  }

  return (
    <SessionsContext.Provider
      value={{
        sessions,
        currentSessionId,
        leftCollapsed,
        rightCollapsed,
        createSession,
        appendMessage,
        updateSessionTitle,
        addSnippet,
        upsertSource,
        setCurrentSession,
        deleteSession,
        toggleLeft,
        toggleRight,
        getSession,
      }}
    >
      {children}
    </SessionsContext.Provider>
  );
};

export function useSessions() {
  const ctx = useContext(SessionsContext);
  if (!ctx) throw new Error("useSessions must be used within SessionsProvider");
  return ctx;
}

export default SessionsContext;
