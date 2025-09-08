// Centralized route & role constants
export const ROUTES = {
  LOGIN: '/login',
  MANAGER: '/manager',
  SALES: '/sales'
};

export const ROLES = {
  MANAGER: 'manager',
  SALESMAN: 'salesman'
};

// Tab keys used by the single-page dashboards (kept here for consistency)
export const MANAGER_TABS = ['overview', 'sales', 'agents', 'chat'];
export const SALESMAN_TABS = ['overview', 'mystats', 'improvements', 'achievements', 'feedback'];

export const getHomeForRole = (role) => {
  if (role === ROLES.MANAGER) return ROUTES.MANAGER;
  if (role === ROLES.SALESMAN) return ROUTES.SALES;
  return ROUTES.LOGIN;
};
