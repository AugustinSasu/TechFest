import React from 'react';
import { Backdrop, CircularProgress } from '@mui/material';

export default function LoadingOverlay({ open = false }) {
  return (
    <Backdrop open={open} sx={{ zIndex: theme => theme.zIndex.modal + 1 }}>
      <CircularProgress />
    </Backdrop>
  );
}
