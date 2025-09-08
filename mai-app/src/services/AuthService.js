import ApiClient from './ApiClient';

/**
 * Auth API wrapper.
 * Expected backend:
 *  - POST /auth/login       -> { token, user }
 *  - POST /auth/logout
 *  - GET  /auth/me          -> { user }
 *  - POST /auth/refresh     -> { token }
 */
export default class AuthService {
  /** @param {ApiClient} api */
  constructor(api) {
    this.api = api;
  }

  /** @param {{email:string,password:string}} payload */
  login(payload) {
    return this.api.post('/auth/login', payload, { skipAuth: true });
  }

  logout() {
    return this.api.post('/auth/logout', null).catch(() => ({}));
  }

  getProfile() {
    return this.api.get('/auth/me');
  }

  refreshToken() {
    return this.api.post('/auth/refresh', null, { skipAuth: true });
  }
}

export function createAuthService(api) {
  return new AuthService(api);
}
