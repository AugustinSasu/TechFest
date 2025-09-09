import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  Container,
  FormControlLabel,
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
  const [remember, setRemember] = useState(true);
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
    const res = await login({ username, password, remember });
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
    <Container maxWidth="sm" sx={{ minHeight: '100%', display: 'grid', placeItems: 'center' }}>
      <Paper sx={{ p: 4, width: '100%', borderRadius: 3 }}>
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

          <FormControlLabel
            control={<Checkbox checked={remember} onChange={e => setRemember(e.target.checked)} />}
            label="Remember me"
          />

          <Button type="submit" variant="contained" size="large" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </Button>

          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center' }}>
            Tip: backend login endpoint must be <code>{import.meta.env.VITE_API_BASE_URL}/api/employees/sign-in</code>
          </Typography>

          <Box sx={{ textAlign: 'center' }}>
            <Typography
              component="button"
              onClick={() => navigate(ROUTES.LOGIN, { replace: true })}
              sx={{ background: 'none', border: 0, p: 0, m: 0, color: 'text.secondary', cursor: 'default' }}
            >
              Need a different role? The server should return <b>employee.role_code</b> as "MANAGER" sau "SALES".
            </Typography>
          </Box>
        </Stack>
      </Paper>
    </Container>
  );
}
