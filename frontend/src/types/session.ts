export type Snippet = {
  id: string;
  sourceId: string;
  text: string;
  locationHint?: string;
  page?: number | string;
  title?: string;
  authors?: string;
  year?: string | number;
};

export type SourceRef = {
  id: string;
  title: string;
  authors?: string;
  year?: string;
  zoteroKey?: string;
  localPdfPath?: string;
};

export type Message = { id: string; role: "user" | "assistant"; content: string; createdAt: string };

export type Session = {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
  snippets: Snippet[];
  sources: SourceRef[];
};
