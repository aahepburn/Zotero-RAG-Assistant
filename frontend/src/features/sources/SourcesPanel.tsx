import React, { useState } from "react";
import { useSessions } from "../../contexts/SessionsContext";
import { useChatContext } from "../../contexts/ChatContext";

function buildZoteroSelectUri(itemKey?: string | number | null, groupId?: string | number | null) {
  if (!itemKey) return null;
  const key = encodeURIComponent(String(itemKey));
  if (groupId) {
    return `zotero://select/groups/${encodeURIComponent(String(groupId))}/items/${key}`;
  }
  return `zotero://select/library/items/${key}`;
}

function buildZoteroOpenPdfUri(itemKey?: string | number | null, page?: number | string | null, groupId?: string | number | null) {
  if (!itemKey) return null;
  const key = encodeURIComponent(String(itemKey));
  // Zotero 7 expects the newer form with /library/
  let uri = `zotero://open-pdf/library/items/${key}`;
  const params: string[] = [];
  if (page != null && String(page).trim() !== "") params.push(`page=${encodeURIComponent(String(page))}`);
  if (params.length) uri += `?${params.join("&")}`;
  return uri;
}

function tryOpenUri(uri: string | null) {
  if (!uri) return false;
  try {
    // Use location assign so the browser hands it off to the OS handler
    window.location.href = uri;
    return true;
  } catch (e) {
    try {
      window.open(uri, "_blank");
      return true;
    } catch (e2) {
      console.warn("Failed to open uri", uri, e2);
      return false;
    }
  }
}

const SourcesPanel: React.FC = () => {
  const { currentSessionId, getSession, rightCollapsed, toggleRight } = useSessions();
  const session = currentSessionId ? getSession(currentSessionId) : null;
  const chat = useChatContext();
  const [searchResults, setSearchResults] = useState<Record<string, any[]>>({});
  const [searchLoading, setSearchLoading] = useState<Record<string, boolean>>({});
  const [showDebug, setShowDebug] = useState(false);

  if (!session) {
    return (
      <>
        <header>
          <div className="app-heading">Sources</div>
          <div className="muted">Cited items and snippets.</div>
        </header>
        <main>
          <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ margin: "0 auto 16px", opacity: 0.3 }}>
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <div style={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>No Active Session</div>
            <div style={{ fontSize: "13px" }}>Ask a question to see cited sources from your library.</div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div className="app-heading">Sources</div>
          <div className="muted">Cited items and snippets for this session</div>
        </div>
        <div>
          <button className="btn" onClick={toggleRight} title={rightCollapsed ? "Show sources" : "Hide sources"}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              {rightCollapsed ? <path d="M15 6l-6 6 6 6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/> : <path d="M9 6l6 6-6 6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>}
            </svg>
          </button>
        </div>
      </header>
      <main>
        <div style={{ marginBottom: 8 }} className="muted">Showing sources for this session.</div>

        <div style={{ marginTop: 8 }}>
          {session.sources.length === 0 && <div className="muted">No sources yet in session; checking latest response...</div>}
          {session.sources.length === 0 && (chat?.lastResponse?.citations ?? []).length > 0 && (
            <div style={{ marginBottom: 8 }} className="muted">Showing sources from latest response (session not populated)</div>
          )}
          {(session.sources.length > 0 ? session.sources : (chat?.lastResponse?.citations ?? []).map((c: any) => ({ id: String(c.id), title: c.title, authors: c.authors, year: c.year ? String(c.year) : undefined, zoteroKey: c.zoteroKey, localPdfPath: c.pdf_path }))).map((s: any, index: number) => (
            <div key={s.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
              {/* Top section: metadata */}
              <div style={{ padding: 12, display: "flex", alignItems: "flex-start", gap: "12px" }}>
                <div style={{ 
                  minWidth: "28px", 
                  height: "28px", 
                  borderRadius: "50%", 
                  background: "var(--accent)", 
                  color: "white", 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  fontSize: "14px", 
                  fontWeight: 600,
                  flexShrink: 0
                }}>
                  {s.id || index + 1}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, marginBottom: "4px" }}>{s.title}</div>
                  <div className="muted" style={{ fontSize: 12 }}>
                    {s.authors ? s.authors.split(",")[0].trim() + (s.authors.split(",").length > 1 ? " et al." : "") : "Unknown author"}
                    {s.year ? ` • ${s.year}` : ""}
                  </div>
                </div>
              </div>
              {/* Bottom section: action buttons */}
              <div style={{ padding: "8px 12px", borderTop: "1px solid var(--border-subtle)", background: "var(--bg-panel-alt, #fafafa)", display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
                <button
                  className="btn"
                  title="Open PDF"
                  onClick={async () => {
                    // Open PDF via backend endpoint that uses system default viewer
                    if (s.localPdfPath) {
                      const fp = String(s.localPdfPath);
                      console.log("Opening PDF:", fp);
                      try {
                        const resp = await fetch("/open_pdf", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ pdf_path: fp }),
                        });
                        const data = await resp.json();
                        if (data.error) {
                          alert(`Failed to open PDF: ${data.error}`);
                        }
                      } catch (e) {
                        console.error("Failed to open PDF:", e);
                        alert("Failed to open PDF. Check console for details.");
                      }
                    } else {
                      alert("No local PDF path available for this source");
                    }
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M14 2v6h6M9 13h6M9 17h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>

                <a title="Google Scholar" className="btn" href={`https://scholar.google.com/scholar?q=${encodeURIComponent(s.title)}`} target="_blank" rel="noreferrer">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M7.5 4.21l4.5 2.6 4.5-2.6M12 22v-10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </a>
                
                <a title="Google Books" className="btn" href={`https://www.google.com/search?tbm=bks&q=${encodeURIComponent(s.title)}`} target="_blank" rel="noreferrer">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </a>
              </div>
            </div>
          ))}
          {/* Inline search results popovers */}
          {session.sources.map((s) => {
            const results = searchResults[s.id] ?? null;
            if (!results) return null;
            return (
              <div key={`search-${s.id}`} style={{ padding: 8, borderBottom: "1px solid var(--border-subtle)", background: "rgba(0,0,0,0.02)" }}>
                <div style={{ fontSize: 13, marginBottom: 8 }}><strong>Search results for “{s.title}”</strong></div>
                {searchLoading[s.id] && <div className="muted">Searching…</div>}
                {!searchLoading[s.id] && results.length === 0 && <div className="muted">No matches found.</div>}
                {!searchLoading[s.id] && results.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {results.map((r: any) => (
                      <div key={r.id ?? r.key ?? JSON.stringify(r)} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'center' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 600 }}>{r.title ?? r.itemTitle ?? "(no title)"}</div>
                          <div className="muted" style={{ fontSize: 12 }}>{r.author ?? r.creators ?? ''} {r.date ? ` • ${r.date}` : ''}</div>
                        </div>
                        <div style={{ display: 'flex', gap: 6 }}>
                          <button className='btn' title="Open PDF" onClick={async () => {
                            const key = r.key ?? r.zoteroKey ?? null;
                            const page = r.page ?? null;
                            const groupId = r.groupID ?? r.groupId ?? r.group?.id ?? null;
                            const zuri = buildZoteroOpenPdfUri(key, page, groupId);
                            console.log('openPdfUri (result)', zuri);
                            if (zuri) {
                              if (tryOpenUri(zuri)) return;
                            }
                            const fp = r.pdf_path ?? r.filePath ?? null;
                            if (fp) {
                              console.log('Opening PDF:', fp);
                              try {
                                const resp = await fetch('/open_pdf', {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  body: JSON.stringify({ pdf_path: fp }),
                                });
                                const data = await resp.json();
                                if (data.error) {
                                  alert(`Failed to open PDF: ${data.error}`);
                                }
                              } catch (e) {
                                console.error('Failed to open PDF:', e);
                                alert('Failed to open PDF. Check console for details.');
                              }
                            } else {
                              alert('No PDF path available for this result');
                            }
                          }}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                              <path d="M14 2v6h6M9 13h6M9 17h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}


        </div>
      </main>
    </>
  );
};

export default SourcesPanel;
