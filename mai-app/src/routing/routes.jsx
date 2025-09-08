import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleGuard } from './RoleGuard';
import { ROUTES, ROLES } from './routePaths';

import LoginPage from '../pages/Login/LoginPage';
import ManagerDashboardPage from '../pages/Manager/ManagerDashboardPage';
import SalesDashboardPage from '../pages/Sales/SalesDashboardPage';

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to={ROUTES.LOGIN} replace />} />
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<RoleGuard allowed={[ROLES.MANAGER]} />}>
            <Route path={ROUTES.MANAGER} element={<ManagerDashboardPage />} />
          </Route>

          <Route element={<RoleGuard allowed={[ROLES.SALESMAN]} />}>
            <Route path={ROUTES.SALES} element={<SalesDashboardPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to={ROUTES.LOGIN} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
