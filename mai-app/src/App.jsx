import React from 'react';
import './App.css';

import ErrorBoundary from './components/common/ErrorBoundary';
import { ThemeProvider } from './providers/ThemeProvider';
import { SnackbarProvider } from './providers/SnackbarProvider';
import { AuthProvider } from './providers/AuthProvider';
import { AppRoutes } from './routing/routes';

export default function App() {
  return (
    <ThemeProvider>
      <SnackbarProvider>
        <AuthProvider>
          <ErrorBoundary>
            <AppRoutes />
          </ErrorBoundary>
        </AuthProvider>
      </SnackbarProvider>
    </ThemeProvider>
  );
}
