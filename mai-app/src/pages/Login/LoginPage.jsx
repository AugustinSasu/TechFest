import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Container,
  InputAdornment,
  Paper,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import { useAuth } from '../../providers/AuthProvider';
import { useSnackbar } from '../../providers/SnackbarProvider';
import { useLocation, useNavigate } from 'react-router-dom';
import { getHomeForRole, ROUTES } from '../../routing/routePaths';

/**
 * One-file Login Page (no external LoginForm yet).
 * Calls AuthProvider.login → saves token+user → redirect by role.
 */
export default function LoginPage() {
  const { isAuthenticated, role, login, loading } = useAuth() || {};
  const { error, success } = useSnackbar() || {};
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname;

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  // Removed "remember me" feature per latest request
  const [showPassword, setShowPassword] = useState(false);

  // If already logged in, go home
  useEffect(() => {
    if (isAuthenticated && role) {
      navigate(from || getHomeForRole(role), { replace: true });
    }
  }, [isAuthenticated, role, from, navigate]);

  const onSubmit = async e => {
    e.preventDefault();
    if (!username || !password) {
      error?.('Please enter both username and password.');
      return;
    }
  const res = await login({ username, password });
    if (res.ok) {
      success?.('Welcome back!');
      // redirect imediat (în caz că efectul nu rulează suficient de repede)
      if (res.user?.role) {
        navigate(getHomeForRole(res.user.role), { replace: true });
      }
    } else {
      error?.(res.error || 'Login failed');
    }
  };

  return (
    <Container maxWidth="md" sx={{ minHeight: '100%', display: 'grid', placeItems: 'center' }}>
      <Paper
        sx={{
          p: { xs: 4, sm: 6 },
          width: '100%',
          maxWidth: 560,
          borderRadius: 4,
          mx: 'auto'
        }}
      >
        <Stack spacing={3} component="form" onSubmit={onSubmit} noValidate>
          <Box>
            <Typography variant="h4" fontWeight={700}>Sign in</Typography>
            <Typography variant="body2" color="text.secondary">
              Use your work credentials
            </Typography>
          </Box>

          <TextField
            label="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            autoComplete="username"
            fullWidth
            required
          />

          <TextField
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={e => setPassword(e.target.value)}
            autoComplete="current-password"
            fullWidth
            required
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <Button
                    size="small"
                    onClick={() => setShowPassword(s => !s)}
                    aria-label="toggle password visibility"
                    tabIndex={-1}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </Button>
                </InputAdornment>
              )
            }}
          />

          <Button type="submit" variant="contained" size="large" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </Button>
        </Stack>
      </Paper>
    </Container>
  );
}
