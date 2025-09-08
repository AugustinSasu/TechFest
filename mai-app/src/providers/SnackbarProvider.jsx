import React, { createContext, useContext, useMemo, useState } from 'react';
import { Snackbar, Alert } from '@mui/material';

const SnackbarContext = createContext(null);

/**
 * Global Snackbar provider
 * usage: const { notify, success, error } = useSnackbar();
 */
export function SnackbarProvider({ children }) {
  const [snack, setSnack] = useState({
    open: false,
    message: '',
    severity: 'info',
    autoHideDuration: 3000
  });

  const notify = ({ message, severity = 'info', autoHideDuration = 3000 }) =>
    setSnack({ open: true, message, severity, autoHideDuration });

  const close = () => setSnack(s => ({ ...s, open: false }));

  const value = useMemo(
    () => ({
      notify,
      success: (m, d = 3000) => notify({ message: m, severity: 'success', autoHideDuration: d }),
      error: (m, d = 5000) => notify({ message: m, severity: 'error', autoHideDuration: d }),
      info: (m, d = 3000) => notify({ message: m, severity: 'info', autoHideDuration: d }),
      warning: (m, d = 4000) => notify({ message: m, severity: 'warning', autoHideDuration: d })
    }),
    []
  );

  return (
    <SnackbarContext.Provider value={value}>
      {children}
      <Snackbar
        open={snack.open}
        autoHideDuration={snack.autoHideDuration}
        onClose={close}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={close} severity={snack.severity} variant="filled" sx={{ width: '100%' }}>
          {snack.message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export const useSnackbar = () => useContext(SnackbarContext);
