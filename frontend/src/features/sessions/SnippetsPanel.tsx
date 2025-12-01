import React from "react";
import { useSessions } from "../../contexts/SessionsContext";
import { useChatContext } from "../../contexts/ChatContext";
import SnippetCard from "../../components/sources/SnippetCard";
import { Spinner } from "../../components/ui/Spinner";

/**
 * SnippetsPanel displays the evidence (snippets) that were used to generate
 * the most recent LLM answer. It shows the specific text chunks from PDFs
 * along with metadata and links to open items in Zotero or view the PDF.
 * 
 * This panel focuses on showing the provenance of answers, making the
 * assistant's responses transparent and trustworthy.
 */
const SnippetsPanel: React.FC = () => {
  const { currentSessionId, getSession, leftCollapsed, toggleLeft } = useSessions();
  const { loading } = useChatContext();
  const session = currentSessionId ? getSession(currentSessionId) : null;

  // Get snippets from the current session
  const snippets = session?.snippets || [];
  
  // Build a map of sourceId -> SourceRef for quick lookup
  const sourcesMap = new Map(
    (session?.sources || []).map((source) => [source.id, source])
  );

  return (
    <>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontFamily: "var(--font-serif)", fontSize: "20px", fontWeight: 600, color: "var(--text-main)", letterSpacing: "0.02em", marginBottom: "4px" }}>Evidence</div>
          <div className="muted">Source snippets for the latest answer</div>
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

        {/* Loading state */}
        {session && loading && snippets.length === 0 && (
          <div
            style={{
              padding: "40px 20px",
              textAlign: "center",
              color: "var(--text-muted)",
            }}
          >
            <Spinner />
            <div style={{ marginTop: "16px", fontSize: "14px" }}>
              Retrieving source snippets...
            </div>
          </div>
        )}

        {/* Empty state - no snippets yet */}
        {session && !loading && snippets.length === 0 && (
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
              No Source Snippets
            </div>
            <div style={{ fontSize: "13px" }}>
              No source snippets were found for this answer. This may occur if the answer
              was based on general knowledge rather than your library.
            </div>
          </div>
        )}

        {/* Snippets list */}
        {session && snippets.length > 0 && (
          <div style={{ padding: "8px 0" }}>
            <div
              style={{
                fontSize: "13px",
                marginBottom: "12px",
                color: "var(--text-muted)",
              }}
            >
              Showing {snippets.length} snippet{snippets.length !== 1 ? "s" : ""} in order of
              relevance:
            </div>
            {snippets.map((snippet, index) => {
              const source = sourcesMap.get(snippet.sourceId);
              return (
                <SnippetCard
                  key={snippet.id}
                  snippet={snippet}
                  source={source}
                  index={index}
                />
              );
            })}
          </div>
        )}
      </main>
    </>
  );
};

export default SnippetsPanel;
