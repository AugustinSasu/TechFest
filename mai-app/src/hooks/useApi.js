import { useMemo } from 'react';
import { useAuth } from './useAuth';

/**
 * Lightweight API helper based on fetch.
 * Later, you can swap this to use a dedicated ApiClient class without changing callers.
 */
export function useApi() {
  const { token } = useAuth() || {};
  const baseUrl = import.meta.env.VITE_API_BASE_URL;

  const makeUrl = (path, params) => {
    const q = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
    // allow path with or without leading slash
    const safePath = path.startsWith('/') ? path : `/${path}`;
    return `${baseUrl}${safePath}${q}`;
  };

  const request = async (path, { method = 'GET', params, body, headers } = {}) => {
    if (!baseUrl) throw new Error('VITE_API_BASE_URL is not defined.');
    const url = makeUrl(path, params);

    const isFormData = body instanceof FormData;
    const finalHeaders = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers || {})
    };

    const res = await fetch(url, {
      method,
      headers: finalHeaders,
      body: body ? (isFormData ? body : JSON.stringify(body)) : undefined
    });

    const contentType = res.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await res.json() : await res.text();

    if (!res.ok) {
      const message = typeof data === 'string' ? data : data?.message || `HTTP ${res.status}`;
      throw new Error(message);
    }

    return data;
  };

  return useMemo(
    () => ({
      baseUrl,
      request,
      get: (path, params, opts = {}) => request(path, { ...opts, method: 'GET', params }),
      post: (path, body, opts = {}) => request(path, { ...opts, method: 'POST', body }),
      put: (path, body, opts = {}) => request(path, { ...opts, method: 'PUT', body }),
      del: (path, opts = {}) => request(path, { ...opts, method: 'DELETE' })
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [baseUrl, token]
  );
}
