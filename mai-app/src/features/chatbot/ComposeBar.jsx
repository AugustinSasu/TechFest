import React, { useState } from 'react';
import { Box, Button, Stack, TextField } from '@mui/material';

/**
 * Props: disabled, onSend(text)
 */
export default function ComposeBar({ disabled = false, onSend }) {
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
        placeholder="Write a prompt…"
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        disabled={disabled}
        multiline
        minRows={1}
        maxRows={6}
        fullWidth
      />
      <Stack direction="row" spacing={1} sx={{ minWidth: 260 }}>
        <Button
          variant="contained"
          onClick={send}
          disabled={disabled || !value.trim()}
          sx={{ flex: 1, minWidth: 120, height: 40 }}
        >
          Send
        </Button>
        <Button
          variant="outlined"
          color="secondary"
          onClick={() => { if (value.trim()) { onRecommend?.(value.trim()); setValue(''); } }}
          disabled={disabled || !value.trim()}
          sx={{ flex: 1, minWidth: 120, height: 40 }}
        >
          Send Recommendation
        </Button>
      </Stack>
    </Stack>
  );
}
