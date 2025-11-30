import React from "react";
import ChatView from "../../features/chat/ChatView";
import SourcesPanel from "../../features/sources/SourcesPanel";
import SnippetsPanel from "../../features/sessions/SnippetsPanel";
import TopNav from "./TopNav";
import "../../styles/layout.css";
import { useSessions } from "../../contexts/SessionsContext";

const AppShell: React.FC = () => {
  const { leftCollapsed, rightCollapsed } = useSessions();
  const classes = ["app-shell", leftCollapsed ? "app-shell--left-collapsed" : "", rightCollapsed ? "app-shell--right-collapsed" : ""].join(" ");

  return (
    <>
      <TopNav />
      <div className={classes}>
        <aside className="app-shell__sidebar">
          <SnippetsPanel />
        </aside>
        <main className="app-shell__main">
          <ChatView />
        </main>
        <section className="app-shell__sources">
          <SourcesPanel />
        </section>
      </div>
    </>
  );
};

export default AppShell;
