import React from 'react';
import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material';
import Logo from '../common/Logo';
import { useColorMode } from '../../providers/ThemeProvider';
import { useAuth } from '../../providers/AuthProvider';
import { getHomeForRole } from '../../routing/routePaths';
import { useNavigate } from 'react-router-dom';

export default function AppTopBar({ onMenuClick, showMenuButton = true }) {
  const { mode, toggleColorMode } = useColorMode();
  const { user, role, logout } = useAuth() || {};
  const navigate = useNavigate();
  const appName = import.meta.env.VITE_APP_NAME || 'SalesAI';

  const goHome = () => {
    if (role) navigate(getHomeForRole(role), { replace: true });
  };

  return (
    <AppBar position="sticky" color="default" elevation={0} sx={{ borderBottom: theme => `1px solid ${theme.palette.divider}` }}>
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ gap: 2 }}>
          <Box onClick={goHome} sx={{ cursor: 'pointer' }}>
            <Logo size={26} withText />
          </Box>

          <Box sx={{ flexGrow: 1 }} />

          <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
            {user ? `${user.name || 'User'} · ${role || ''}` : appName}
          </Typography>

          <Button onClick={toggleColorMode} color="inherit">
            {mode === 'light' ? 'Dark' : 'Light'}
          </Button>

          {user && (
            <Button onClick={logout} color="inherit">Logout</Button>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
}
