import React from 'react';
import { Box, Container, Paper } from '@mui/material';
import Logo from '../components/common/Logo';

/**
 * Centers its children in the viewport. Useful for Login.
 * Not required by LoginPage right now, but available for reuse.
 */
export default function AuthLayout({ children, maxWidth = 'sm' }) {
  return (
    <Box sx={{ minHeight: '100%', display: 'grid', placeItems: 'center', py: 4 }}>
      <Container maxWidth={maxWidth}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <Logo size={36} />
        </Box>
        <Paper sx={{ p: 4, borderRadius: 3 }}>{children}</Paper>
      </Container>
    </Box>
  );
}
