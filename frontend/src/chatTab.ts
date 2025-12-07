// src/chatTab.ts

import { indexLibrary, chat, ChatResponse } from "./backendClient";

interface ChatTabState {
  loading: boolean;
  indexing: boolean;
  lastResponse: ChatResponse | null;
  lastError: string | null;
}

const state: ChatTabState = {
  loading: false,
  indexing: false,
  lastResponse: null,
  lastError: null,
};

export function registerChatTab() {
  // Using zotero-plugin-toolkit's helpers is recommended; this is conceptual.
  // In the real template, you'd import and call registerLibraryTabPanel(...)
  (Zotero as any).PaneManager.registerLibraryTabPanel({
    id: "zotero-llm-chat-tab",
    label: "Assistant",
    icon: "chrome://your-addon/content/icons/chat.svg",
    priority: 100,
    onRender: (_pane: unknown, _libraryID: number, container: HTMLElement) => {
      renderChatUI(container);
    },
  });
}

function renderChatUI(container: HTMLElement) {
  container.textContent = ""; // clear

  const root = container.ownerDocument.createElement("div");
  root.className = "zotero-llm-chat-root";

  const header = container.ownerDocument.createElement("h2");
  header.textContent = "Zotero RAG Assistant";

  const form = container.ownerDocument.createElement("div");
  form.className = "zotero-llm-chat-form";

  const textarea = container.ownerDocument.createElement("textarea");
  textarea.className = "zotero-llm-chat-input";
  textarea.rows = 3;
  textarea.placeholder = "Ask a question about your Zotero library…";

  const buttonsRow = container.ownerDocument.createElement("div");
  buttonsRow.className = "zotero-llm-chat-buttons";

  const askButton = container.ownerDocument.createElement("button");
  askButton.textContent = state.loading ? "Asking…" : "Ask";
  askButton.disabled = state.loading || state.indexing;

  const indexButton = container.ownerDocument.createElement("button");
  indexButton.textContent = state.indexing ? "Indexing…" : "Index library";
  indexButton.disabled = state.indexing || state.loading;

  const statusLine = container.ownerDocument.createElement("div");
  statusLine.className = "zotero-llm-chat-status";
  if (state.lastError) {
    statusLine.textContent = state.lastError;
  } else if (state.indexing) {
    statusLine.textContent = "Indexing library…";
  } else if (state.loading) {
    statusLine.textContent = "Generating answer…";
  } else {
    statusLine.textContent = "";
  }

  const resultBox = container.ownerDocument.createElement("div");
  resultBox.className = "zotero-llm-chat-result";

  // Wire handlers
  askButton.addEventListener("click", async () => {
    const question = textarea.value.trim();
    if (!question) return;
    await onAsk(question, container);
  });

  indexButton.addEventListener("click", async () => {
    await onIndex(container);
  });

  // Layout
  buttonsRow.appendChild(askButton);
  buttonsRow.appendChild(indexButton);

  form.appendChild(textarea);
  form.appendChild(buttonsRow);

  root.appendChild(header);
  root.appendChild(form);
  root.appendChild(statusLine);
  root.appendChild(resultBox);

  container.appendChild(root);

  // Render last response (if any)
  if (state.lastResponse) {
    renderResult(resultBox, state.lastResponse);
  }
}

async function onIndex(container: HTMLElement) {
  state.indexing = true;
  state.lastError = null;
  renderChatUI(container);

  try {
    await indexLibrary();
  } catch (e) {
    state.lastError =
      e instanceof Error ? e.message : "Failed to index library";
  } finally {
    state.indexing = false;
    renderChatUI(container);
  }
}

async function onAsk(question: string, container: HTMLElement) {
  state.loading = true;
  state.lastError = null;
  renderChatUI(container);

  try {
    // TODO: pass selected item IDs later
    const resp = await chat(question);
    state.lastResponse = resp;
  } catch (e) {
    state.lastError =
      e instanceof Error ? e.message : "Failed to contact assistant backend";
  } finally {
    state.loading = false;
    renderChatUI(container);
  }
}

function renderResult(root: HTMLElement, resp: ChatResponse) {
  root.textContent = "";

  const summaryEl = root.ownerDocument.createElement("div");
  summaryEl.className = "zotero-llm-chat-summary";
  summaryEl.textContent = resp.summary;

  const sourcesHeader = root.ownerDocument.createElement("h3");
  sourcesHeader.textContent = "Sources";

  const sourcesList = root.ownerDocument.createElement("ul");
  sourcesList.className = "zotero-llm-chat-sources";

  for (const c of resp.citations) {
    const li = root.ownerDocument.createElement("li");
    li.textContent = `${c.title} (${c.year ?? "n.d."}) [${c.item_id}]`;
    sourcesList.appendChild(li);
  }

  root.appendChild(summaryEl);
  root.appendChild(sourcesHeader);
  root.appendChild(sourcesList);
}
