const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(path.startsWith("/") ? path : `/${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed: ${res.status} ${text}`);
  }

  const data = (await res.json()) as any;
  
  // Check if the response contains an error field (backend error responses)
  if (data && typeof data === 'object' && 'error' in data) {
    throw new Error(data.error || 'An error occurred');
  }

  return data as T;
}

export { BASE_URL, request };
