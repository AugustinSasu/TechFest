import React from 'react';
import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material';
import Logo from '../common/Logo';
import { useColorMode } from '../../providers/ThemeProvider';
import { useAuth } from '../../providers/AuthProvider';
import { useEffect } from 'react';
import { getHomeForRole } from '../../routing/routePaths';
import { useNavigate } from 'react-router-dom';

export default function AppTopBar({ onMenuClick, showMenuButton = true }) {
  const { mode, toggleColorMode } = useColorMode();
  const { user, role, logout, refreshProfile, employeeId } = useAuth() || {};
  useEffect(() => { refreshProfile?.(); /* eslint-disable-next-line */ }, [employeeId]);
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
            {user
              ? (role === 'salesman'
                  ? (user.db_username || user.full_name || 'User')
                  : `${user.full_name || user.db_username || 'User'}${role ? ` · ${role}` : ''}`)
              : appName}
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
