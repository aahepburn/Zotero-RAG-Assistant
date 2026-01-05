export type Snippet = {
  id: string;
  text: string;
  context: string;
  confidence: number;
  pageNumber?: number;
  section?: string;
  characterOffset?: number;
};

export type Source = {
  documentId: string;
  title: string;
  author: string;
  confidence: number;
  pageNumber?: number;
  section?: string;
  retrievalTimestamp: number;
  snippets: Snippet[];
  // Legacy fields for backward compatibility
  zoteroKey?: string;
  localPdfPath?: string;
};

// Legacy type alias for backward compatibility
export type SourceRef = Source;

export type Message = { 
  id: string; 
  role: "user" | "assistant"; 
  content: string; 
  createdAt: string;
  sources?: Source[];  // Response-scoped sources
  timestamp?: number;  // When response was generated
};

export type Session = {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
  snippets: Snippet[];
  sources: SourceRef[];
};
