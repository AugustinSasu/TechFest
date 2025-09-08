import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

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
  const [token, setToken] = useState(null);

  // Rehydrate from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(AUTH_STORAGE_KEY);
      if (raw) {
        const saved = JSON.parse(raw);
        setUser(saved.user || null);
        setToken(saved.token || null);
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

  const login = async ({ email, password }) => {
    setLoading(true);
    try {
      // ---------------- MOCK MODE ----------------
      if (USE_MOCKS) {
        const role = (email || '').toLowerCase().includes('manager') ? 'manager' : 'salesman';
        const mockUser = {
          id: 'u-' + role,
          name: role === 'manager' ? 'Manager Mia' : 'Sales Sam',
          email: email || `${role}@example.com`,
          role
        };
        const mockToken = 'mock-token-' + role;
        setUser(mockUser);
        setToken(mockToken);
        saveAuth({ user: mockUser, token: mockToken });
        return { ok: true, user: mockUser };
      }

      // --------------- REAL BACKEND ---------------
      if (!API_BASE_URL) throw new Error('Missing VITE_API_BASE_URL.');
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        let msg = `Login failed (${res.status})`;
        try {
          const err = await res.json();
          if (err?.message) msg = err.message;
        } catch {}
        throw new Error(msg);
      }
      const data = await res.json();
      if (!data?.token || !data?.user) throw new Error('Invalid login response (expected { token, user }).');

      setUser(data.user);
      setToken(data.token);
      saveAuth({ user: data.user, token: data.token });
      return { ok: true, user: data.user };
    } catch (err) {
      console.error(err);
      setUser(null);
      setToken(null);
      saveAuth(null);
      return { ok: false, error: err.message || 'Login failed' };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (!USE_MOCKS && API_BASE_URL && token) {
        // best-effort; backend poate ignora lipsa endpoint-ului
        fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` }
        }).catch(() => {});
      }
    } finally {
      setUser(null);
      setToken(null);
      saveAuth(null);
    }
  };

  const value = useMemo(
    () => ({
      initializing,
      loading,
      isAuthenticated: !!token,
      user,
      token,
      role: user?.role ?? null, // 'manager' | 'salesman'
      login,
      logout
    }),
    [initializing, loading, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
