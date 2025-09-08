import React from 'react';
import { Box, Container, Typography } from '@mui/material';

export default function Footer() {
  const year = new Date().getFullYear();
  const appName = import.meta.env.VITE_APP_NAME || 'SalesAI';
  return (
    <Box component="footer" sx={{ borderTop: theme => `1px solid ${theme.palette.divider}`, mt: 4, py: 3 }}>
      <Container maxWidth="lg">
        <Typography variant="caption" color="text.secondary">
          © {year} {appName}. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
}
