// In Electron production, use the full backend URL
// In development (Vite dev server), use relative paths with proxy
const isElectron = navigator.userAgent.includes('Electron');
const BASE_URL = import.meta.env.VITE_API_BASE_URL || (isElectron ? "http://localhost:8000" : "");

// Log API client configuration for debugging
console.log('[API Client] Configuration:');
console.log('  - Electron mode:', isElectron);
console.log('  - BASE_URL:', BASE_URL);
console.log('  - User agent:', navigator.userAgent);

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const fullPath = BASE_URL + (path.startsWith("/") ? path : `/${path}`);
  const res = await fetch(fullPath, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    signal: options.signal,
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

/**
 * Configured fetch function that automatically prepends BASE_URL
 * Use this instead of direct fetch() calls to ensure proper URL resolution in Electron
 */
function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  const fullPath = BASE_URL + (path.startsWith("/") ? path : `/${path}`);
  console.log(`[API Fetch] ${options?.method || 'GET'} ${fullPath}`);
  return fetch(fullPath, options);
}

export { BASE_URL, request, apiFetch };
