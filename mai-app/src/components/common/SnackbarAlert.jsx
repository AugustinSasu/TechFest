import React from 'react';
import { Snackbar, Alert } from '@mui/material';

/**
 * Standalone Snackbar component.
 * Nota: e deja SnackbarProvider global; acesta e util pentru cazuri locale.
 */
export default function SnackbarAlert({ open, message, severity = 'info', autoHideDuration = 3000, onClose }) {
  return (
    <Snackbar
      open={open}
      onClose={onClose}
      autoHideDuration={autoHideDuration}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert onClose={onClose} severity={severity} variant="filled" sx={{ width: '100%' }}>
        {message}
      </Alert>
    </Snackbar>
  );
}
