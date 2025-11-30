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
  text: string;
  title?: string;
  pdf_path?: string;
}

export interface ChatResponse {
  summary: string;
  citations: Citation[];
  snippets: Snippet[];
}

export interface ChatRequest {
  query: string;
}
