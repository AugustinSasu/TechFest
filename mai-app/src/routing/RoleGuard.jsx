import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../providers/AuthProvider';
import { ROUTES, getHomeForRole } from './routePaths';

/**
 * Ensures the current user has an allowed role for this branch.
 * Usage: <Route element={<RoleGuard allowed={['manager']} />}> ... </Route>
 */
export function RoleGuard({ allowed = [] }) {
  const { isAuthenticated, role } = useAuth() || {};

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  if (allowed.includes(role)) {
    return <Outlet />;
  }

  // Logged-in but wrong role → send to their home
  return <Navigate to={getHomeForRole(role)} replace />;
}
