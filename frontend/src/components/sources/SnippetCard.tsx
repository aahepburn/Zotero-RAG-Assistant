import React, { useState } from "react";
import { buildZoteroSelectUri, tryOpenZoteroUri, openLocalPdf } from "../../utils/zotero";
import type { Snippet } from "../../types/session";
import type { SourceRef } from "../../types/session";

interface SnippetCardProps {
  snippet: Snippet;
  source?: SourceRef;
  index: number;
}

const MAX_SNIPPET_LENGTH = 350;

const SnippetCard: React.FC<SnippetCardProps> = ({ snippet, source, index }) => {
  const [expanded, setExpanded] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const snippetText = snippet.text || "";
  const needsTruncation = snippetText.length > MAX_SNIPPET_LENGTH;
  const displayText = expanded || !needsTruncation
    ? snippetText
    : snippetText.slice(0, MAX_SNIPPET_LENGTH) + "...";

  // Use snippet metadata first, fallback to source metadata
  const title = snippet.title || source?.title || "Unknown Source";
  const authors = snippet.authors || source?.authors;
  const year = snippet.year || source?.year;
  const page = snippet.page;
  
  // Build metadata line
  const authorDisplay = authors
    ? authors.split(",")[0].trim() + (authors.split(",").length > 1 ? " et al." : "")
    : null;
  
  const metadataLine = [
    authorDisplay,
    year ? `(${year})` : null,
    page ? `p. ${page}` : null,
  ].filter(Boolean).join(" ");

  // Get Zotero key and PDF path from source
  const zoteroKey = source?.zoteroKey;
  const pdfPath = source?.localPdfPath;

  const handleOpenInZotero = () => {
    setActionError(null);
    const uri = buildZoteroSelectUri(zoteroKey);
    if (!uri) {
      setActionError("No Zotero key available for this item");
      return;
    }
    if (!tryOpenZoteroUri(uri)) {
      setActionError("Failed to open Zotero. Is the Zotero app running?");
    }
  };

  const handleOpenPdf = async () => {
    setActionError(null);
    if (!pdfPath) {
      setActionError("No PDF path available for this item");
      return;
    }
    try {
      await openLocalPdf(pdfPath);
    } catch (e: any) {
      setActionError(e.message || "Failed to open PDF");
    }
  };

  return (
    <div
      style={{
        border: "1px solid var(--border-subtle)",
        borderRadius: "8px",
        background: "var(--bg-panel)",
        marginBottom: "12px",
        overflow: "hidden",
      }}
    >
      {/* TOP SECTION: All metadata */}
      <div style={{ padding: "16px" }}>
        {/* Header with index badge */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: "12px", marginBottom: "12px" }}>
          <div
            style={{
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
              flexShrink: 0,
            }}
          >
            {index + 1}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "4px" }}>
              {title}
            </div>
            {metadataLine && (
              <div className="muted" style={{ fontSize: "12px" }}>
                {metadataLine}
              </div>
            )}
          </div>
        </div>

        {/* Snippet text */}
        <div
          style={{
            padding: "12px",
            background: "var(--bg-panel-alt, #f8f8f8)",
            borderRadius: "6px",
            fontFamily: "var(--font-mono, monospace)",
            fontSize: "13px",
            lineHeight: "1.6",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {displayText}
        </div>

        {/* Truncation toggle */}
        {needsTruncation && (
          <button
            className="btn"
            onClick={() => setExpanded(!expanded)}
            style={{
              fontSize: "12px",
              padding: "4px 8px",
              marginTop: "8px",
            }}
          >
            {expanded ? "Show less" : "Show more"}
          </button>
        )}
      </div>

      {/* BOTTOM SECTION: Action buttons */}
      <div
        style={{
          padding: "12px 16px",
          borderTop: "1px solid var(--border-subtle)",
          background: "var(--bg-panel-alt, #fafafa)",
          display: "flex",
          flexWrap: "wrap",
          gap: "8px",
          alignItems: "center",
          justifyContent: "flex-start",
        }}
      >
        {zoteroKey && (
          <button
            className="btn"
            onClick={handleOpenInZotero}
            title="Open this item in Zotero"
            style={{ fontSize: "12px", padding: "6px 12px", display: "flex", alignItems: "center", gap: "6px" }}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Open in Zotero
          </button>
        )}
        {pdfPath && (
          <button
            className="btn"
            onClick={handleOpenPdf}
            title="Open the PDF file"
            style={{ fontSize: "12px", padding: "6px 12px", display: "flex", alignItems: "center", gap: "6px" }}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M14 2v6h6M9 13h6M9 17h6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Open PDF
          </button>
        )}
      </div>

      {/* Error display */}
      {actionError && (
        <div
          style={{
            margin: "0 16px 12px 16px",
            padding: "8px",
            background: "#fee",
            border: "1px solid #fcc",
            borderRadius: "4px",
            fontSize: "12px",
            color: "#c33",
          }}
        >
          {actionError}
        </div>
      )}
    </div>
  );
};

export default SnippetCard;
