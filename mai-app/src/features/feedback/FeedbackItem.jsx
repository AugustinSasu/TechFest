import React from 'react';
import { Box, Button, Paper, Stack, Typography } from '@mui/material';

/**
 * item: { id, title, body, createdAt, read }
 */
export default function FeedbackItem({ item, onAcknowledge }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Stack spacing={0.5}>
        <Typography variant="subtitle2" fontWeight={700}>
          {item.title || 'Feedback'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
          {item.body || '-'}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" color="text.secondary">
            {item.createdAt ? new Date(item.createdAt).toLocaleString() : ''}
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
