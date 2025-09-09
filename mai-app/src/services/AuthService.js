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
  constructor(api) { this.api = api; }

  /** @param {{ db_username:string, password:string }} payload */
  signIn(payload) {
    // With base URL already including /api
    return this.api.post('/employees/sign-in', payload);
  }

  /** @param {number|string} employeeId */
  getEmployee(employeeId) {
    return this.api.get(`/employees/${encodeURIComponent(employeeId)}`);
  }
}

export function createAuthService(api) { return new AuthService(api); }
