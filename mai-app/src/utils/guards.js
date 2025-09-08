import { ROLES, getHomeForRole } from '../routing/routePaths';

export { getHomeForRole } from '../routing/routePaths';

/**
 * Role helpers
 */
export function hasRole(user, role) {
  return !!user && user.role === role;
}

export function isManager(user) {
  return hasRole(user, ROLES.MANAGER);
}

export function isSalesman(user) {
  return hasRole(user, ROLES.SALESMAN);
}

/**
 * Auth helpers
 */
export function isAuthenticated(state) {
  return !!(state && (state.token || state.user));
}

/**
 * Returns true if current role is in allowed list
 * @param {UserRole|null|undefined} role
 * @param {UserRole[]} allowed
 */
export function roleAllowed(role, allowed = []) {
  return !!role && allowed.includes(role);
}

/**
 * Pick a safe home route for a role (fallback to login handled by routePaths)
 */
export function homeFor(user) {
  return getHomeForRole(user?.role);
}
