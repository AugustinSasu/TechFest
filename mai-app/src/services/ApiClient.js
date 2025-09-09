/**
 * Small fetch wrapper with JSON handling and auth header.
 */
import { isMockEnabled, mockRequest } from './mock';

export class ApiError extends Error {
  constructor(message, { status, data, url, method } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.url = url;
    this.method = method;
  }
}

export default class ApiClient {
  /**
   * @param {{ baseUrl?: string, getToken?: ()=> (string|Promise<string>), onUnauthorized?: (res:any, data:any)=>void }} opts
   */
  constructor({ baseUrl } = {}) {
    this.baseUrl = baseUrl || import.meta.env.VITE_API_BASE_URL;
  }

  setBaseUrl(url) { this.baseUrl = url; return this; }

  buildUrl(path, params) {
    if (!this.baseUrl) throw new Error('Missing VITE_API_BASE_URL.');
    const safePath = path.startsWith('/') ? path : `/${path}`;
    const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
    return `${this.baseUrl}${safePath}${qs}`;
  }

  /**
   * @param {string} path
   * @param {{ method?:string, params?:Object, body?:any, headers?:Object, skipAuth?:boolean, signal?:AbortSignal }} opts
   */
  async request(path, { method = 'GET', params, body, headers, signal } = {}) {
    // MOCK SHORT-CIRCUIT
    if (isMockEnabled()) {
      const data = await mockRequest(path, { method, params, body });
      await new Promise(r => setTimeout(r, 200));
      return data;
    }

    const url = this.buildUrl(path, params);
    const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;

    const finalHeaders = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(headers || {})
    };

  // Authorization eliminat (folosim doar sesiune server-side sau alt mecanism)

    const res = await fetch(url, {
      method,
      headers: finalHeaders,
      body: body === undefined ? undefined : (isFormData ? body : JSON.stringify(body)),
      signal
    });

    const contentType = res.headers.get('content-type') || '';
    let data = null;
    if (res.status !== 204) {
      data = contentType.includes('application/json') ? await res.json() : await res.text();
    }

    if (!res.ok) {
  // 401 handling simplificat
      const message = (data && (data.message || data.error)) || `HTTP ${res.status}`;
      throw new ApiError(message, { status: res.status, data, url, method });
    }
    return data;
  }

  get(path, params, opts = {}) { return this.request(path, { ...opts, method: 'GET', params }); }
  post(path, body, opts = {}) { return this.request(path, { ...opts, method: 'POST', body }); }
  put(path, body, opts = {}) { return this.request(path, { ...opts, method: 'PUT', body }); }
  patch(path, body, opts = {}) { return this.request(path, { ...opts, method: 'PATCH', body }); }
  delete(path, opts = {}) { return this.request(path, { ...opts, method: 'DELETE' }); }
}

export function createApiClient() {
  return new ApiClient({ baseUrl: import.meta.env.VITE_API_BASE_URL });
}
