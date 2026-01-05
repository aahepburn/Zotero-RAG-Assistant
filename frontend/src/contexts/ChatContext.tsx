import React, { createContext, useContext } from "react";
import type { ChatResponse } from "../types/api";
import type { ChatMessage } from "../types/domain";
import { useChat as useChatHook } from "../hooks/useChat";
import { useSessions } from "./SessionsContext";
import { useResponseSelection } from "./ResponseSelectionContext";
import type { Snippet as SessionSnippet, Source, Message as SessionMessage } from "../types/session";

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

/**
 * Convert backend citations and snippets to response-scoped Source format.
 * Groups snippets by citation and calculates confidence scores.
 */
function convertToResponseScopedSources(citations: any[], snippets: any[]): Source[] {
  const sources: Source[] = [];
  const retrievalTimestamp = Date.now();
  
  // Create a map of citation_id to snippets
  const snippetsBySourceId = new Map<string, any[]>();
  snippets.forEach(snippet => {
    const sourceId = String(snippet.citation_id ?? snippet.citationId ?? snippet.item_id ?? snippet.itemId ?? "");
    if (!snippetsBySourceId.has(sourceId)) {
      snippetsBySourceId.set(sourceId, []);
    }
    snippetsBySourceId.get(sourceId)!.push(snippet);
  });
  
  // Convert each citation to a Source with its snippets
  citations.forEach((citation, index) => {
    const citationId = String(citation.id ?? citation.key ?? index + 1);
    const citationSnippets = snippetsBySourceId.get(citationId) || [];
    
    // Calculate confidence based on snippet count and order (earlier = higher confidence)
    const baseConfidence = 0.95 - (index * 0.05);
    const confidence = Math.max(0.5, Math.min(1.0, baseConfidence));
    
    const source: Source = {
      documentId: citationId,
      title: citation.title ?? citation.itemTitle ?? "(no title)",
      author: citation.authors ?? citation.creators ?? "Unknown",
      confidence: confidence,
      pageNumber: citation.page ?? undefined,
      section: citation.section ?? undefined,
      retrievalTimestamp: retrievalTimestamp,
      zoteroKey: citation.zotero_key ?? citation.key ?? citation.itemKey ?? undefined,
      localPdfPath: citation.pdf_path ?? citation.filePath ?? undefined,
      snippets: citationSnippets.map((s, sIndex) => ({
        id: String(s.id ?? s.snippet_id ?? crypto.randomUUID()),
        text: s.snippet ?? s.text ?? s.content ?? "",
        context: s.context ?? s.snippet ?? s.text ?? "", // Use snippet as context if no separate context
        confidence: Math.max(0.5, 0.95 - (sIndex * 0.03)),
        pageNumber: s.page ?? undefined,
        section: s.section ?? undefined,
        characterOffset: s.characterOffset ?? undefined,
      }))
    };
    
    sources.push(source);
  });
  
  return sources;
}

export const ChatProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const { messages, loading, error, lastResponse, sendMessage: rawSendMessage, loadThread, clearMessages } = useChatHook();
  const sessions = useSessions();
  const { setSelectedResponseId } = useResponseSelection();

  async function sendMessage(content: string) {
    // Get current session ID to enable stateful conversation
    let sessionId = sessions.currentSessionId;
    
    // send via the chat hook, which returns created messages and the response
    const result = await rawSendMessage(content, sessionId || undefined);
    if (!result) return;

    const { userMessage, assistantMessage, response } = result;

    // Ensure there is a session: if not, create one using the initial user question
    // Normalize possible backend shapes (some backends may use `sources` instead of `citations`)
    console.debug("chat response:", response);
    console.log("response.summary:", response.summary);
    console.log("assistantMessage.content:", assistantMessage.content);
    const citations = (response as any).citations ?? (response as any).sources ?? [];
    const snippets = (response as any).snippets ?? (response as any).results ?? [];
    const generatedTitle = (response as any).generated_title;
    console.log("Extracted generatedTitle from response:", generatedTitle);
    
    // Convert citations and snippets to response-scoped Source format
    const responseSources = convertToResponseScopedSources(citations, snippets);
    console.log("Response-scoped sources:", responseSources);
    console.log("Citations count:", citations.length, "Snippets count:", snippets.length);

    if (!sessionId) {
      // Legacy compatibility: still create session-level sources for old panel code
      const initialSources = (citations || []).map((c: any) => ({
        id: String(c.id ?? c.key ?? c.zoteroKey ?? c.itemKey ?? c.item_id ?? c.key ?? c.UUID ?? ""),
        documentId: String(c.id ?? c.key ?? c.zoteroKey ?? c.itemKey ?? c.item_id ?? c.key ?? c.UUID ?? ""),
        title: c.title ?? c.itemTitle ?? c.name ?? "(no title)",
        author: c.authors ?? c.creators ?? "Unknown",
        authors: c.authors ?? c.creators ?? undefined,
        year: c.year ? String(c.year) : c.date ? String(c.date) : undefined,
        zoteroKey: c.zotero_key ?? c.key ?? c.itemKey ?? undefined,
        localPdfPath: c.pdf_path ?? c.filePath ?? c.local_path ?? undefined,
        confidence: 0.9,
        retrievalTimestamp: Date.now(),
        snippets: []
      } as Source));
      const initialSnippets = (snippets || []).map((s: any) => ({
        id: String(s.id ?? s.snippet_id ?? s.key ?? crypto.randomUUID()),
        text: s.snippet ?? s.text ?? s.content ?? "",
        context: s.context ?? s.snippet ?? s.text ?? s.content ?? "", // Use snippet as context if no separate context
        confidence: 0.8, // Default confidence for legacy snippets
        pageNumber: s.page ?? undefined,
        section: s.section ?? s.location ?? undefined,
        characterOffset: s.characterOffset ?? undefined,
      } as SessionSnippet));
      
      // Use generated title if available, otherwise use first part of user message
      const { sessionId: newSessionId, assistantMessageId } = sessions.createSession(
        userMessage.content, 
        response.summary,
        responseSources,  // Pass response-scoped sources
        initialSources, 
        initialSnippets,
        generatedTitle,  // Custom title from LLM
        userMessage.id,  // Use existing user message ID from useChat
        assistantMessage.id  // Use existing assistant message ID from useChat
      );
      
      sessionId = newSessionId;
      
      // Directly select the assistant message - no timeout or getSession needed
      // This eliminates the race condition with state updates
      setSelectedResponseId(assistantMessageId);
      console.log("[ChatContext] Auto-selected initial response (no race):", assistantMessageId);
    } else {
      // convert to session Message shape and append to existing session
      const u: SessionMessage = { 
        id: userMessage.id, 
        role: "user", 
        content: userMessage.content, 
        createdAt: new Date().toISOString() 
      };
      const a: SessionMessage = { 
        id: assistantMessage.id, 
        role: "assistant", 
        content: response.summary || assistantMessage.content,  // Use response.summary (actual LLM response)
        createdAt: new Date().toISOString(),
        sources: responseSources,  // Attach sources to assistant message
        timestamp: Date.now()
      };
      sessions.appendMessage(sessionId, u);
      sessions.appendMessage(sessionId, a);

      // Auto-select the new assistant response
      // We know a.id immediately, no need for setTimeout or state checking
      setSelectedResponseId(a.id);
      console.log("[ChatContext] Auto-selected follow-up response (no race):", a.id);

      // Update session title if LLM generated one (first message in session)
      if (generatedTitle) {
        sessions.updateSessionTitle(sessionId, generatedTitle);
      }

      // upsert sources (robust mapping) - legacy for session-level sources
      (citations || []).forEach((c: any) => {
        const src: Source = {
          documentId: String(c.id ?? c.key ?? c.zoteroKey ?? c.itemKey ?? c.UUID ?? ""),
          title: c.title ?? c.itemTitle ?? c.name ?? "(no title)",
          author: c.authors ?? c.creators ?? "Unknown",
          confidence: 0.9,
          retrievalTimestamp: Date.now(),
          authors: c.authors ?? c.creators ?? undefined,
          year: c.year ? String(c.year) : c.date ? String(c.date) : undefined,
          zoteroKey: c.zotero_key ?? c.key ?? c.itemKey ?? undefined,
          localPdfPath: c.pdf_path ?? c.filePath ?? c.local_path ?? undefined,
          snippets: []
        } as Source;
        sessions.upsertSource(sessionId!, src);
      });

      // add snippets (robust mapping with all metadata fields)
      (snippets || []).forEach((s: any) => {
        const sn: SessionSnippet = {
          id: String(s.id ?? s.snippet_id ?? crypto.randomUUID()),
          text: s.snippet ?? s.text ?? s.content ?? "",
          context: s.context ?? s.snippet ?? s.text ?? s.content ?? "", // Use snippet as context if no separate context
          confidence: 0.8, // Default confidence for legacy snippets
          pageNumber: s.page ?? undefined,
          section: s.section ?? s.location ?? undefined,
          characterOffset: s.characterOffset ?? undefined,
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
