import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSessions } from "../../contexts/SessionsContext";
import { useChatContext } from "../../contexts/ChatContext";
import { apiFetch } from "../../api/client";

interface IndexProgress {
  processed_items?: number;
  total_items?: number;
  start_time?: number;
  elapsed_seconds?: number;
  eta_seconds?: number | null;
  skipped_items?: number;
  skip_reasons?: string[];
  mode?: 'incremental' | 'full';
}

interface IndexStatus {
  status: string;
  progress?: IndexProgress;
}

const IconPanel = ({ children }: { children: React.ReactNode }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    {children}
  </svg>
);

const OllamaStatus: React.FC = () => {
  const [status, setStatus] = useState<"checking" | "running" | "offline" | "error">("checking");
  const [models, setModels] = useState<string[]>([]);

  const check = async () => {
    try {
      const resp = await apiFetch("/api/ollama_status");
      const data = await resp.json();
      setStatus(data.status);
      setModels(data.models || []);
      return data.status;
    } catch (e) {
      setStatus("error");
      return "error";
    }
  };

  useEffect(() => {
    check();
  }, []);

  const statusColors = {
    checking: "#999",
    running: "#4caf50",
    offline: "#f44336",
    error: "#ff9800",
  };

  const statusLabels = {
    checking: "Checking...",
    running: "Ollama",
    offline: "Ollama Offline",
    error: "Ollama Error",
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "6px",
        fontSize: "12px",
        color: "var(--text-muted)",
      }}
    >
      <div
        style={{
          width: "8px",
          height: "8px",
          borderRadius: "50%",
          background: statusColors[status],
          boxShadow: status === "running" ? `0 0 8px ${statusColors[status]}` : "none",
        }}
      />
      <span>{statusLabels[status]}</span>
      <button
        className="btn"
        onClick={check}
        disabled={status === "checking"}
        style={{ padding: "2px 6px", fontSize: "11px", marginLeft: "2px" }}
        title={status === "running" && models.length > 0 ? `Models: ${models.join(", ")}\n\nClick to refresh` : "Refresh Ollama status"}
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0118.8-4.3M22 12.5a10 10 0 01-18.8 4.2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  );
};

const TopNav: React.FC = () => {
  const navigate = useNavigate();
  const { sessions, currentSessionId, getSession, updateSessionTitle, leftCollapsed, rightCollapsed, toggleLeft, toggleRight, createSession, setCurrentSession, deleteSession } = useSessions();
  const session = currentSessionId ? getSession(currentSessionId) : null;
  const [editing, setEditing] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [indexStatus, setIndexStatus] = useState<IndexStatus | null>(null);
  const [indexStats, setIndexStats] = useState<any>(null);
  const pollRef = React.useRef<number | null>(null);
  const [title, setTitle] = useState(session?.title ?? "Zotero RAG Assistant");
  const [menuOpen, setMenuOpen] = useState(false);
  const [showIndexMenu, setShowIndexMenu] = useState(false);
  const [skipWarningsDismissed, setSkipWarningsDismissed] = useState(false);

  useEffect(() => {
    setTitle(session?.title ?? "Zotero RAG Assistant");
  }, [session]);

  // Fetch index stats periodically
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const resp = await apiFetch('/api/index_stats');
        const data = await resp.json();
        setIndexStats(data);
      } catch (err) {
        console.error('Failed to fetch index stats', err);
      }
    };
    
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const startIndexing = async (incremental: boolean) => {
    if (reindexing) return;
    try {
      setReindexing(true);
      setSkipWarningsDismissed(false); // Reset warnings on new index
      setShowIndexMenu(false);
      const resp = await apiFetch("/api/index_library", { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ incremental })
      });
      const data = await resp.json();
      
      // Start polling status
      const poll = async () => {
        try {
          const r = await apiFetch('/api/index_status');
          const js = await r.json();
          setIndexStatus(js);
          if (js?.status === 'indexing') {
            return false;
          }
          // Refresh stats after indexing completes
          const statsResp = await apiFetch('/api/index_stats');
          const statsData = await statsResp.json();
          setIndexStats(statsData);
          return true;
        } catch (err) {
          console.error('Failed to fetch index_status', err);
          return true;
        }
      };
      
      const done = await poll();
      if (!done) {
        pollRef.current = window.setInterval(async () => {
          const finished = await poll();
          if (finished) {
            if (pollRef.current) { 
              window.clearInterval(pollRef.current); 
              pollRef.current = null; 
            }
            setReindexing(false);
          }
        }, 1500) as unknown as number;
      } else {
        setReindexing(false);
      }
    } catch (e: any) {
      console.error("Indexing request failed", e);
      setReindexing(false);
      setIndexStatus({ status: 'error', progress: undefined });
    }
  };

  function save() {
    if (!currentSessionId) return setEditing(false);
    updateSessionTitle(currentSessionId, title.trim() || "Untitled session");
    setEditing(false);
  }

  const chat = useChatContext();

  function handleCreateNew() {
    // Clear current session so the next message will create a new one
    setCurrentSession(null);
    chat.clearMessages();
    setMenuOpen(false);
  }

  function handleDeleteSession(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    if (confirm("Delete this session? This cannot be undone.")) {
      deleteSession(id);
    }
  }

  const sessionsList = Object.values(sessions).sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));

  return (
    <nav className="top-nav">
      <div className="top-nav__left">
        <button className="btn" onClick={toggleLeft} title={leftCollapsed ? "Show snippets" : "Hide snippets"}>
          <IconPanel>
            {leftCollapsed ? <path d="M9 18l6-6-6-6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/> : <path d="M15 18l-6-6 6-6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>}
          </IconPanel>
        </button>
        <div style={{ width: 8 }} />
        <button 
          className="btn" 
          onClick={() => {
            if (!session || session.messages.length === 0) {
              alert('No chat to copy');
              return;
            }
            const chatText = session.messages.map(m => 
              `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`
            ).join('\n\n');
            navigator.clipboard.writeText(chatText).then(() => {
              alert('Chat copied to clipboard!');
            }).catch(err => {
              console.error('Failed to copy:', err);
              alert('Failed to copy chat');
            });
          }}
          disabled={!session || session.messages.length === 0}
          title="Copy entire chat to clipboard"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <div style={{ width: 8 }} />
        <div style={{ position: 'relative' }}>
          <button className="btn" onClick={() => setMenuOpen((s) => !s)} title="Sessions">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: "4px" }}>
              <path d="M3 9h18M3 15h18M9 3v18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Sessions {sessionsList.length > 0 && `(${sessionsList.length})`}
          </button>
          {menuOpen && (
            <>
              <div style={{ position: 'fixed', inset: 0, zIndex: 79 }} onClick={() => setMenuOpen(false)} />
              <div className="sessions-menu" style={{ 
                position: 'absolute', 
                top: '40px', 
                left: 0, 
                background: 'var(--bg-panel)', 
                border: '1px solid var(--border-subtle)', 
                borderRadius: 8, 
                padding: 0,
                boxShadow: '0 4px 16px rgba(0,0,0,0.15)', 
                minWidth: 360, 
                maxWidth: 480,
                zIndex: 80 
              }}>
                <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>Sessions</div>
                  <button className="btn btn--primary" onClick={handleCreateNew} style={{ padding: '4px 12px', fontSize: '12px' }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: "4px" }}>
                      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    New
                  </button>
                </div>
                <div style={{ maxHeight: 400, overflow: 'auto' }}>
                  {sessionsList.length === 0 && (
                    <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      <div style={{ fontSize: '13px' }}>No sessions yet.</div>
                      <div style={{ fontSize: '12px', marginTop: '4px' }}>Start a new conversation to create one.</div>
                    </div>
                  )}
                  {sessionsList.map((s) => (
                    <div 
                      key={s.id} 
                      style={{ 
                        padding: '12px 16px',
                        borderBottom: '1px solid var(--border-subtle)',
                        background: s.id === currentSessionId ? 'rgba(214, 178, 106, 0.1)' : 'transparent',
                        cursor: 'pointer',
                        transition: 'background 0.15s ease'
                      }}
                      onClick={() => { setCurrentSession(s.id); setMenuOpen(false); }}
                      onMouseEnter={(e) => { if (s.id !== currentSessionId) e.currentTarget.style.background = 'rgba(0,0,0,0.02)'; }}
                      onMouseLeave={(e) => { if (s.id !== currentSessionId) e.currentTarget.style.background = 'transparent'; }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: 500, fontSize: '13px', marginBottom: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {s.title}
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            {new Date(s.updatedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} · {s.messages.length} messages
                          </div>
                        </div>
                        <button 
                          className="btn" 
                          onClick={(e) => handleDeleteSession(s.id, e)}
                          style={{ padding: '4px 8px', fontSize: '11px', opacity: 0.7 }}
                          title="Delete session"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="top-nav__center">
        {editing ? (
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input className="top-nav__title-input" value={title} onChange={(e) => setTitle(e.target.value)} />
            <button className="btn" onClick={save}>Save</button>
            <button className="btn" onClick={() => { setEditing(false); setTitle(session?.title ?? ""); }}>Cancel</button>
          </div>
        ) : (
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div className="top-nav__title" onDoubleClick={() => setEditing(true)}>{session?.title ?? "Zotero RAG Assistant"}</div>
            {session && <button className="btn" onClick={() => setEditing(true)} title="Edit session title">Edit</button>}
          </div>
        )}
      </div>

      <div className="top-nav__right">
        <OllamaStatus />
        <div style={{ width: 8 }} />
        <button className="btn" onClick={() => navigate('/settings')} title="Settings">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <div style={{ width: 8 }} />
        <button className="btn" onClick={toggleRight} title={rightCollapsed ? "Show sources" : "Hide sources"}>
          <IconPanel>
            {rightCollapsed ? <path d="M15 6l-6 6 6 6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/> : <path d="M9 6l6 6-6 6" stroke="#5b4632" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>}
          </IconPanel>
        </button>
        <div style={{ width: 8 }} />
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', position: 'relative' }}>
          <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
            <button
              className="btn"
              onClick={() => startIndexing(true)}
              disabled={reindexing}
              title={indexStats?.new_items > 0 ? `Sync ${indexStats.new_items} new item${indexStats.new_items !== 1 ? 's' : ''}` : "Sync new items"}
            >
              {reindexing ? "Indexing…" : indexStats?.new_items > 0 ? `Sync (${indexStats.new_items})` : "Sync"}
            </button>
            <button
              className="btn"
              onClick={() => setShowIndexMenu(!showIndexMenu)}
              disabled={reindexing}
              title="Index options"
              style={{ padding: '4px 8px' }}
            >
              ▾
            </button>
          </div>
          
          {showIndexMenu && (
            <>
              <div 
                style={{ position: 'fixed', inset: 0, zIndex: 79 }} 
                onClick={() => setShowIndexMenu(false)} 
              />
              <div style={{
                position: 'absolute',
                top: '40px',
                right: 0,
                background: 'var(--bg-panel)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 8,
                boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
                minWidth: 200,
                zIndex: 80,
                overflow: 'hidden'
              }}>
                <button
                  onClick={() => startIndexing(true)}
                  style={{
                    width: '100%',
                    padding: '10px 16px',
                    border: 'none',
                    background: 'transparent',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: 14
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--surface-hover)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <div style={{ fontWeight: 500 }}>Sync New Items</div>
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
                    {indexStats?.new_items > 0 
                      ? `Index ${indexStats.new_items} new item${indexStats.new_items !== 1 ? 's' : ''}`
                      : 'Only index items not yet in database'}
                  </div>
                </button>
                <div style={{ height: 1, background: 'var(--border)' }} />
                <button
                  onClick={() => startIndexing(false)}
                  style={{
                    width: '100%',
                    padding: '10px 16px',
                    border: 'none',
                    background: 'transparent',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: 14
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--surface-hover)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <div style={{ fontWeight: 500 }}>Full Reindex</div>
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
                    Rebuild entire index from scratch
                  </div>
                </button>
                {indexStats && (
                  <>
                    <div style={{ height: 1, background: 'var(--border)' }} />
                    <div style={{ padding: '10px 16px', fontSize: 12, color: 'var(--muted)' }}>
                      <div>Indexed: {indexStats.indexed_items} items</div>
                      <div>Chunks: {indexStats.total_chunks}</div>
                      <div>Library: {indexStats.zotero_items} items</div>
                    </div>
                    {indexStats.new_items > 0 && (
                      <>
                        <div style={{ height: 1, background: 'var(--border)' }} />
                        <button
                          onClick={async () => {
                            try {
                              const resp = await apiFetch('/api/diagnose_unindexed');
                              const data = await resp.json();
                              console.log('Unindexed items diagnostics:', data);
                              alert(`Diagnostics found ${data.unindexed_count} unindexed items. Check console for details.`);
                            } catch (err) {
                              console.error('Failed to fetch diagnostics', err);
                              alert('Failed to fetch diagnostics. Check console.');
                            }
                          }}
                          style={{
                            width: '100%',
                            padding: '10px 16px',
                            border: 'none',
                            background: 'transparent',
                            textAlign: 'left',
                            cursor: 'pointer',
                            fontSize: 14
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.background = 'var(--surface-hover)'}
                          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                        >
                          <div style={{ fontWeight: 500 }}>Diagnose Sync Issues</div>
                          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
                            Check why {indexStats.new_items} item{indexStats.new_items !== 1 ? 's' : ''} aren't indexed
                          </div>
                        </button>
                      </>
                    )}
                  </>
                )}
              </div>
            </>
          )}


          {/* Progress bar + status */}
          {indexStatus && (
            <div style={{ width: 220, marginTop: 6 }}>
              <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>
                  {indexStatus.status === 'indexing' ? 'Indexing…' : indexStatus.status === 'idle' ? 'Index idle' : indexStatus.status}
                </span>
                {indexStatus.status === 'indexing' && indexStatus.progress?.eta_seconds != null && indexStatus.progress.eta_seconds > 0 && (
                  <span style={{ fontSize: 11 }}>
                    {indexStatus.progress.eta_seconds < 60 
                      ? `~${indexStatus.progress.eta_seconds}s`
                      : `~${Math.ceil(indexStatus.progress.eta_seconds / 60)}m`}
                  </span>
                )}
              </div>
              <div style={{ height: 8, background: 'var(--border-subtle)', borderRadius: 4, overflow: 'hidden' }}>
                {indexStatus.progress && indexStatus.progress.total_items ? (
                  <div style={{ height: '100%', background: 'linear-gradient(90deg,var(--accent) 0%, var(--accent-2) 100%)', width: `${Math.min(100, Math.round((100 * (indexStatus.progress.processed_items ?? 0) / (indexStatus.progress.total_items ?? 1))))}%`, transition: 'width 300ms ease' }} />
                ) : (
                  // indeterminate bar
                  <div style={{ height: '100%', width: '100%', background: 'repeating-linear-gradient(-45deg, rgba(0,0,0,0.08) 0, rgba(0,0,0,0.02) 10px)' }} />
                )}
              </div>
              {indexStatus.status === 'indexing' && indexStatus.progress && (
                <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
                  {indexStatus.progress.processed_items ?? 0} / {indexStatus.progress.total_items ?? 0} items
                  {indexStatus.progress.mode === 'incremental' && (indexStatus.progress.skipped_items ?? 0) > 0 && (
                    <span style={{ marginLeft: 8 }}>
                      ({indexStatus.progress.skipped_items} already indexed)
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default TopNav;
