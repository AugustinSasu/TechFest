import React from 'react';
import { Box, Container } from '@mui/material';
import AppTopBar from '../components/layout/AppTopBar';
import Footer from '../components/layout/Footer';

/**
 * Manager shell layout: TopBar + SideNav + content.
 * Keeps the side nav permanent on md+ and temporary (drawer) on small screens.
 */
export default function ManagerLayout({ children }) {
  return (
    <Box sx={{ flex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ width: 900, alignSelf: 'center' }}>
        <AppTopBar />
      </Box>

      <Box sx={{ display: 'flex', flex: 1, justifyContent: 'center' }}>
        <Box
          component="main"
          sx={{
            width: 900,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            py: 3,
            flexGrow: 1
          }}
        >
          <Container maxWidth={false} sx={{ width: '100%', flexGrow: 1 }}>
            {children}
          </Container>
        </Box>
      </Box>

      <Footer />
    </Box>
  );
}
