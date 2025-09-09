import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { createApiClient } from '../services/ApiClient';
import { createAuthService } from '../services/AuthService';

const AuthContext = createContext(null);

const AUTH_STORAGE_KEY = 'mai.auth';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

/**
 * AuthProvider
 * - Ține user, token, role
 * - login/logout
 * - rehidratează din localStorage
 * - dacă VITE_USE_MOCKS=true → generează user/token local
 */
export function AuthProvider({ children }) {
  const [initializing, setInitializing] = useState(true);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  // In noul flux nu mai folosim token, ci id-ul angajatului (employee_id)
  const [employeeId, setEmployeeId] = useState(null);

  // Rehydrate from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(AUTH_STORAGE_KEY);
      if (raw) {
        const saved = JSON.parse(raw);
        setUser(saved.user || null);
  setEmployeeId(saved.employeeId || null);
      }
    } catch (e) {
      console.warn('Failed to parse saved auth', e);
    } finally {
      setInitializing(false);
    }
  }, []);

  const saveAuth = (next) => {
    if (!next) localStorage.removeItem(AUTH_STORAGE_KEY);
    else localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(next));
  };

  const api = useMemo(() => createApiClient(), []);
  const authService = useMemo(() => createAuthService(api), [api]);

  const login = async ({ username, password }) => {
    setLoading(true);
    try {
      // ---------------- MOCK MODE ----------------
      if (USE_MOCKS) {
        const role = (username || '').toLowerCase().includes('manager') ? 'manager' : 'salesman';
        const mockUser = {
          employee_id: 'u-' + role,
          full_name: role === 'manager' ? 'Manager Mia' : 'Sales Sam',
          db_username: username || role,
          role_code: role === 'manager' ? 'MANAGER' : 'SALES'
        };
        setUser(mockUser);
        setEmployeeId(mockUser.employee_id);
        saveAuth({ user: mockUser, employeeId: mockUser.employee_id });
        return { ok: true, user: mockUser };
      }

      // --------------- REAL BACKEND ---------------
  if (!API_BASE_URL) throw new Error('Missing VITE_API_BASE_URL.');
  const data = await authService.signIn({ db_username: username, password });
      // Asteptam forma:
      // { authenticated: true, employee: { employee_id, db_username, full_name, role_code, dealership_id } }
      if (!data?.authenticated || !data?.employee) throw new Error('Invalid login response');
      const emp = data.employee;
      // Mapăm role_code -> rol intern (manager/salesman)
      const mappedRole = emp.role_code === 'MANAGER' ? 'manager' : 'salesman';
      const userObj = { ...emp, role: mappedRole };
      setUser(userObj);
      setEmployeeId(emp.employee_id);
      saveAuth({ user: userObj, employeeId: emp.employee_id });
      return { ok: true, user: userObj };
    } catch (err) {
      console.error(err);
      setUser(null);
      setEmployeeId(null);
      saveAuth(null);
      return { ok: false, error: err.message || 'Login failed' };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (!USE_MOCKS && API_BASE_URL && employeeId) {
        // best-effort; backend poate ignora lipsa endpoint-ului
        // Daca exista un endpoint de logout il poți adăuga aici
        // fetch(`${API_BASE_URL}/api/employees/logout`, { method: 'POST' }).catch(() => {});
      }
    } finally {
      setUser(null);
      setEmployeeId(null);
      saveAuth(null);
    }
  };

  const value = useMemo(
    () => ({
      initializing,
      loading,
      isAuthenticated: !!employeeId,
      user,
      employeeId,
      role: user?.role ?? null, // 'manager' | 'salesman' (derivat din role_code)
      refreshProfile: async () => {
        if (!API_BASE_URL || !employeeId) return;
        try {
          const emp = await authService.getEmployee(employeeId);
          const mappedRole = emp.role_code === 'MANAGER' ? 'manager' : 'salesman';
          const userObj = { ...emp, role: mappedRole };
          setUser(userObj);
          saveAuth({ user: userObj, employeeId });
        } catch {}
      },
      login,
      logout
    }),
    [initializing, loading, employeeId, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
