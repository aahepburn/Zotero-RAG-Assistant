import React, { useMemo, useState } from "react";
import { useSessions } from "../../contexts/SessionsContext";

const SnippetsPanel: React.FC = () => {
  const { currentSessionId, getSession, leftCollapsed, toggleLeft } = useSessions();
  const session = currentSessionId ? getSession(currentSessionId) : null;
  const [starred, setStarred] = useState<Record<string, boolean>>({});

  const grouped = useMemo(() => {
    if (!session) return {} as Record<string, any[]>;
    const out: Record<string, any[]> = {};
    for (const s of session.snippets || []) {
      if (!s) continue;
      const key = s.sourceId ?? "unknown";
      out[key] = out[key] || [];
      out[key].push(s);
    }
    return out;
  }, [session]);

  function handleInsert(snippetText: string) {
    // Emit a DOM event other components can listen to (ChatInput can subscribe later)
    window.dispatchEvent(new CustomEvent("zotero:insert-snippet", { detail: { text: snippetText } }));
  }

  if (!session) {
    return (
      <>
        <header>
          <div className="app-heading">Snippets</div>
          <div className="muted">Saved highlights for this session</div>
        </header>
        <main>
          <div className="muted">No session selected. Start a session to collect snippets.</div>
        </main>
      </>
    );
  }

  return (
    <>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div className="app-heading">Snippets</div>
          <div className="muted">Promoted highlights for this session</div>
        </div>
        <div>
          <button className="btn" onClick={toggleLeft} title={leftCollapsed ? "Show snippets" : "Hide snippets"}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              {leftCollapsed ? <path d="M9 18l6-6-6-6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/> : <path d="M15 18l-6-6 6-6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>}
            </svg>
          </button>
        </div>
      </header>
      <main>
        {Object.keys(grouped).length === 0 && <div className="muted">No snippets yet for this session.</div>}
        {Object.entries(grouped).map(([sourceId, snippets]) => (
          <div key={sourceId} style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>{session.sources.find((x) => x.id === sourceId)?.title ?? `Source ${sourceId}`}</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {snippets.map((sn: any, idx: number) => {
                const text = typeof sn?.text === "string" ? sn.text : "";
                const display = text.length > 160 ? text.slice(0, 157) + "…" : text;
                const key = sn?.id ?? `${sourceId}-${idx}`;
                return (
                  <div key={key} style={{ padding: 8, border: "1px solid var(--border-subtle)", borderRadius: 6, background: "var(--bg-panel-alt)" }}>
                    <div style={{ fontSize: 13, marginBottom: 6 }}>{display || <span className="muted">(empty snippet)</span>}</div>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button className="btn" onClick={() => handleInsert(text)}>Insert</button>
                      <button
                        className="btn"
                        onClick={() => setStarred((p) => ({ ...p, [key]: !p[key] }))}
                      >
                        {starred[key] ? "★" : "☆"}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </main>
    </>
  );
};

export default SnippetsPanel;
