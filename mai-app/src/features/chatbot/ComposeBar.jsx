import React, { useState } from 'react';
import { Button, Stack, TextField } from '@mui/material';

/**
 * Props: disabled, onSend(text)
 */
export default function ComposeBar({ disabled = false, onSend, placeholder = 'Type here…' }) {
  const [value, setValue] = useState('');

  const send = () => {
    const v = value.trim();
    if (!v) return;
    onSend?.(v);
    setValue('');
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled) send();
    }
  };

  return (
    <Stack direction="row" spacing={1} sx={{ p: 1, borderTop: theme => `1px solid ${theme.palette.divider}` }}>
      <TextField
        placeholder={placeholder}
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        disabled={disabled}
        multiline
        minRows={1}
        maxRows={6}
        fullWidth
      />
      <Button
        variant="contained"
        onClick={send}
        disabled={disabled || !value.trim()}
        sx={{ minWidth: 120, height: 40 }}
      >
        Send
      </Button>
    </Stack>
  );
}
