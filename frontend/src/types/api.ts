export interface Citation {
  id: string;
  title: string;
  authors?: string;
  year?: number;
  pdf_path?: string;
}

export interface Snippet {
  id: string;
  citation_id?: number;
  item_id?: string;
  snippet: string; // The actual text chunk from the document
  text?: string; // Alias for backward compatibility
  title: string;
  authors?: string;
  year?: string | number;
  page?: number | string;
  zoteroKey?: string;
  pdf_path?: string;
}

export interface ChatResponse {
  summary: string;
  citations: Citation[];
  snippets: Snippet[];
  generated_title?: string;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
}
