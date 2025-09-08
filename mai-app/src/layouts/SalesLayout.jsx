import React, { useState } from 'react';
import { Box, Container, useMediaQuery, useTheme } from '@mui/material';
import AppTopBar from '../components/layout/AppTopBar';
import AppSideNav from '../components/layout/AppSideNav';
import Footer from '../components/layout/Footer';

/**
 * Sales shell layout: same structure as ManagerLayout.
 */
export default function SalesLayout({ children }) {
  const theme = useTheme();
  const mdUp = useMediaQuery(theme.breakpoints.up('md'));
  const [navOpen, setNavOpen] = useState(false);
  const drawerWidth = 240;

  return (
    <Box sx={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ width: 900, alignSelf: 'center' }}>
        <AppTopBar onMenuClick={() => setNavOpen(true)} showMenuButton={!mdUp} />
      </Box>

      <Box sx={{ display: 'flex', flex: 1, justifyContent: 'center' }}>
        <Box
          component="main"
          sx={{
            width: 900,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            py: 3
          }}
        >
          <Container maxWidth={false} sx={{ width: '100%' }}>{children}</Container>
        </Box>
      </Box>

      <Footer />
    </Box>
  );
}
