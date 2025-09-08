import React from 'react';
import { Box, Typography } from '@mui/material';

export default function Logo({ size = 28, withText = true }) {
  const appName = import.meta.env.VITE_APP_NAME || 'SalesAI';
  return (
    <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
      {/* folosim vite.svg din public ca favicon/sigil */}
      <Box component="img" src="/vite.svg" alt="logo" sx={{ width: size, height: size }} />
      {withText && (
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: 0.2 }}>
          {appName}
        </Typography>
      )}
    </Box>
  );
}
