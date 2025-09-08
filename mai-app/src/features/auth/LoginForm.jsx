import React, { useState } from 'react';
import { Button, Checkbox, FormControlLabel, Stack, TextField } from '@mui/material';
import PasswordField from './PasswordField';
import { useAuth } from '../../hooks/useAuth';
import { useSnackbar } from '../../hooks/useSnackbar';

/**
 * Optional abstraction over the login UI (LoginPage deja funcționează fără el).
 * Props: onSuccess(user)
 */
export default function LoginForm({ onSuccess }) {
  const { login, loading } = useAuth() || {};
  const { error, success } = useSnackbar() || {};
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return error?.('Please enter both email and password.');
    const res = await login({ email, password, remember });
    if (res.ok) {
      success?.('Welcome back!');
      onSuccess?.(res.user);
    } else {
      error?.(res.error || 'Login failed');
    }
  };

  return (
    <Stack component="form" onSubmit={onSubmit} spacing={2} noValidate>
      <TextField label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} fullWidth required />
      <PasswordField value={password} onChange={e => setPassword(e.target.value)} required />
      <FormControlLabel
        control={<Checkbox checked={remember} onChange={e => setRemember(e.target.checked)} />}
        label="Remember me"
      />
      <Button type="submit" variant="contained" size="large" disabled={loading}>
        {loading ? 'Signing in…' : 'Sign in'}
      </Button>
    </Stack>
  );
}
