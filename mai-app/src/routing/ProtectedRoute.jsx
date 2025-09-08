import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../providers/AuthProvider';
import { ROUTES } from './routePaths';
import LoadingOverlay from '../components/common/LoadingOverlay';

/**
 * Blocks unauthenticated access. Shows a loader while auth rehydrates.
 */
export function ProtectedRoute() {
  const { isAuthenticated, initializing } = useAuth() || {};
  const location = useLocation();

  if (initializing) return <LoadingOverlay open />;

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace state={{ from: location }} />;
  }

  return <Outlet />;
}
