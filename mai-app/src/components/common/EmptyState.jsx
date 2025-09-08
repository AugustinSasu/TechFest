import React from 'react';
import { Box, Button, Typography } from '@mui/material';

export default function EmptyState({ title = 'Nothing here', description, actionLabel, onAction }) {
  return (
    <Box sx={{ textAlign: 'center', py: 6 }}>
      <Box sx={{ fontSize: 44, lineHeight: 1, mb: 2 }}>🗂️</Box>
      <Typography variant="h6" gutterBottom>{title}</Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {description}
        </Typography>
      )}
      {actionLabel && <Button variant="contained" onClick={onAction}>{actionLabel}</Button>}
    </Box>
  );
}
