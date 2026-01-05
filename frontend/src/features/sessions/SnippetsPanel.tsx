import React, { useEffect, useState } from "react";
import { useSessions } from "../../contexts/SessionsContext";
import { useResponseSelection } from "../../contexts/ResponseSelectionContext";
import type { Source, Snippet } from "../../types/session";

/**
 * SnippetsPanel displays snippet evidence specific to the selected response.
 * Snippets are grouped by source document and sorted by confidence within each group.
 * Shows the exact quote with full context highlighting.
 */
const SnippetsPanel: React.FC = () => {
  const { currentSessionId, getSession, leftCollapsed, toggleLeft } = useSessions();
  const { selectedResponseId } = useResponseSelection();
  const session = currentSessionId ? getSession(currentSessionId) : null;
  const [groupedSnippets, setGroupedSnippets] = useState<Map<string, { source: Source, snippets: Snippet[] }>>(new Map());

  // Update snippets when selected response changes
  useEffect(() => {
    if (!session || !selectedResponseId) {
      setGroupedSnippets(new Map());
      return;
    }

    // Find the selected message
    const selectedMessage = session.messages.find(m => m.id === selectedResponseId);
    if (selectedMessage && selectedMessage.role === "assistant" && selectedMessage.sources) {
      // Group snippets by source
      const grouped = new Map<string, { source: Source, snippets: Snippet[] }>();
      
      selectedMessage.sources.forEach(source => {
        if (source.snippets && source.snippets.length > 0) {
          // Sort snippets by confidence (highest first)
          const sortedSnippets = [...source.snippets].sort((a, b) => b.confidence - a.confidence);
          grouped.set(source.documentId, { source, snippets: sortedSnippets });
        }
      });
      
      setGroupedSnippets(grouped);
    } else {
      setGroupedSnippets(new Map());
    }
  }, [session, selectedResponseId]);

  return (
    <>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontFamily: "var(--font-serif)", fontSize: "20px", fontWeight: 600, color: "var(--text-main)", letterSpacing: "0.02em", marginBottom: "4px" }}>Evidence</div>
          <div className="muted">Source snippets for selected response</div>
        </div>
        <div>
          <button
            className="btn"
            onClick={toggleLeft}
            title={leftCollapsed ? "Show evidence panel" : "Hide evidence panel"}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              {leftCollapsed ? (
                <path
                  d="M9 18l6-6-6-6"
                  stroke="#5b4632"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              ) : (
                <path
                  d="M15 18l-6-6 6-6"
                  stroke="#5b4632"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              )}
            </svg>
          </button>
        </div>
      </header>

      <main>
        {/* No session state */}
        {!session && (
          <div
            style={{
              padding: "40px 20px",
              textAlign: "center",
              color: "var(--text-muted)",
            }}
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{ margin: "0 auto 16px", opacity: 0.3 }}
            >
              <path
                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M14 2v6h6M16 13H8M16 17H8M10 9H8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div style={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>
              No Active Session
            </div>
            <div style={{ fontSize: "13px" }}>
              Ask a question to see the evidence and source snippets used in the answer.
            </div>
          </div>
        )}

        {/* No response selected */}
        {session && !selectedResponseId && (
          <div
            style={{
              padding: "40px 20px",
              textAlign: "center",
              color: "var(--text-muted)",
            }}
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{ margin: "0 auto 16px", opacity: 0.3 }}
            >
              <path
                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M14 2v6h6M16 13H8M16 17H8M10 9H8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div style={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>
              No Response Selected
            </div>
            <div style={{ fontSize: "13px" }}>
              Click on an assistant response to view its snippet evidence.
            </div>
          </div>
        )}

        {/* Empty state - no snippets yet */}
        {session && selectedResponseId && groupedSnippets.size === 0 && (
          <div
            style={{
              padding: "40px 20px",
              textAlign: "center",
              color: "var(--text-muted)",
            }}
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{ margin: "0 auto 16px", opacity: 0.3 }}
            >
              <path
                d="M9 11l3 3L22 4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div style={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>
              No Snippet Evidence
            </div>
            <div style={{ fontSize: "13px" }}>
              This response has no snippet evidence from source documents.
            </div>
          </div>
        )}

        {/* Snippets list grouped by source */}
        {session && groupedSnippets.size > 0 && (
          <div style={{ padding: "8px 0" }}>
            <div
              style={{
                fontSize: "13px",
                marginBottom: "12px",
                color: "var(--text-muted)",
              }}
            >
              Showing snippets from {groupedSnippets.size} source{groupedSnippets.size !== 1 ? "s" : ""}:
            </div>
            {Array.from(groupedSnippets.values()).map(({ source, snippets }, sourceIndex) => (
              <div
                key={source.documentId}
                style={{
                  marginBottom: "16px",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "4px",
                  overflow: "hidden",
                }}
              >
                {/* Source header */}
                <div
                  style={{
                    padding: "12px",
                    background: "var(--bg-panel-alt, #fafafa)",
                    borderBottom: "1px solid var(--border-subtle)",
                  }}
                >
                  <div style={{ fontWeight: 600, marginBottom: "4px" }}>
                    {source.title}
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "8px" }}>
                    <span>{source.author}</span>
                    <div style={{ 
                      display: "inline-block", 
                      background: source.confidence >= 0.9 ? "#e8f5e9" : source.confidence >= 0.8 ? "#fff3e0" : "#fce4ec",
                      color: source.confidence >= 0.9 ? "#2e7d32" : source.confidence >= 0.8 ? "#e65100" : "#c2185b",
                      padding: "2px 6px", 
                      borderRadius: "10px", 
                      fontSize: "10px",
                      fontWeight: 600
                    }}>
                      {(source.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
                {/* Snippets for this source */}
                <div>
                  {snippets.map((snippet, snippetIndex) => (
                    <div
                      key={snippet.id}
                      style={{
                        padding: "12px",
                        borderBottom: snippetIndex < snippets.length - 1 ? "1px solid var(--border-subtle)" : "none",
                      }}
                    >
                      <div style={{ marginBottom: "8px" }}>
                        <div
                          style={{
                            fontWeight: 700,
                            fontSize: "13px",
                            marginBottom: "6px",
                            color: "var(--text-main)",
                          }}
                        >
                          "{snippet.text.slice(0, 150)}{snippet.text.length > 150 ? "..." : ""}"
                        </div>
                        <div
                          style={{
                            fontSize: "12px",
                            color: "var(--text-muted)",
                            lineHeight: "1.6",
                          }}
                        >
                          {snippet.context && snippet.context !== snippet.text ? (
                            <span
                              dangerouslySetInnerHTML={{
                                __html: highlightTextInContext(snippet.text, snippet.context),
                              }}
                            />
                          ) : (
                            snippet.text
                          )}
                        </div>
                      </div>
                      <div
                        style={{
                          fontSize: "11px",
                          color: "var(--text-muted)",
                          display: "flex",
                          gap: "12px",
                          alignItems: "center",
                        }}
                      >
                        {snippet.pageNumber && <span>Page {snippet.pageNumber}</span>}
                        {snippet.section && <span>• {snippet.section}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
};

/**
 * Highlight the quote text within the full context paragraph
 */
function highlightTextInContext(quote: string, context: string): string {
  // Find the quote in the context (case-insensitive)
  const quoteIndex = context.toLowerCase().indexOf(quote.toLowerCase());
  if (quoteIndex === -1) {
    return context;
  }
  
  const before = context.slice(0, quoteIndex);
  const highlighted = context.slice(quoteIndex, quoteIndex + quote.length);
  const after = context.slice(quoteIndex + quote.length);
  
  return `${before}<mark style="background: #fff3cd; font-weight: 600;">${highlighted}</mark>${after}`;
}

export default SnippetsPanel;
