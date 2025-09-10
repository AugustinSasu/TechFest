import React from 'react';
import { Box, Button, Paper, Stack, Typography, Divider } from '@mui/material';

/**
 * item: { id, title, body, createdAt, read }
 */
export default function FeedbackItem({ item, onAcknowledge }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Stack spacing={1}>
        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap', textAlign: 'center' }}>
          {item.body || '-'}
        </Typography>
        <Divider />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            {item.createdAt ? new Date(item.createdAt).toLocaleDateString() : ''}
          </Typography>
          {!item.read && (
            <Button size="small" onClick={() => onAcknowledge?.(item)} sx={{ ml: 'auto' }}>
              Acknowledge
            </Button>
          )}
        </Box>
      </Stack>
    </Paper>
  );
}
