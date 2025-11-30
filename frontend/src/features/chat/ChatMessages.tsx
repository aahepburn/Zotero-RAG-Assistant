import React from "react";
import type { ChatMessage } from "../../types/domain";
import { Spinner } from "../../components/ui/Spinner";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
}

function formatMessageWithCitations(content: string): React.ReactNode {
  // Replace citation numbers like [1] with styled spans
  const parts = content.split(/(\[\d+\])/g);
  return parts.map((part, i) => {
    if (/^\[\d+\]$/.test(part)) {
      return (
        <sup key={i} className="citation-ref">
          {part}
        </sup>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

const ChatMessages: React.FC<Props> = ({ messages, loading }) => {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleCopy = async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedId(messageId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="chat-view__messages">
      <div className="message-list">
        {messages.length === 0 && !loading && (
          <div className="message-list__empty">
            <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--muted)" }}>
              <div style={{ fontSize: "18px", fontWeight: 600, marginBottom: "8px" }}>Welcome to Zotero LLM Assistant</div>
              <div>Ask questions about your research library to get started.</div>
            </div>
          </div>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`message message--${m.role === "user" ? "user" : "assistant"}`}
          >
            <div className="message__avatar">
              {m.role === "user" ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
            <div className="message__content">
              <div className="message__role">
                {m.role === "user" ? "You" : "Assistant"}
              </div>
              <div className="message__body">{formatMessageWithCitations(m.content)}</div>
              {m.role === "assistant" && (
                <button
                  className="btn"
                  onClick={() => handleCopy(m.content, m.id)}
                  style={{
                    marginTop: "8px",
                    padding: "4px 10px",
                    fontSize: "11px",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px"
                  }}
                  title="Copy answer"
                >
                  {copiedId === m.id ? (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Copied
                    </>
                  ) : (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Copy
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message message--assistant">
            <div className="message__avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div className="message__content">
              <div className="message__role">Assistant</div>
              <div className="message__body" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Spinner size="sm" />
                <span>Analyzing your library...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatMessages;
