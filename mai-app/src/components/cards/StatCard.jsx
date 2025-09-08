import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

export default function StatCard({ title, value, delta, footer, sx }) {
  const deltaColor = typeof delta === 'number' ? (delta >= 0 ? 'success.main' : 'error.main') : 'text.secondary';
  const deltaText = typeof delta === 'number' ? `${delta >= 0 ? '+' : ''}${delta}%` : delta;

  return (
    <Card sx={{ p: 1, ...sx }}>
      <CardContent>
        <Typography variant="overline" color="text.secondary">{title}</Typography>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
          <Typography variant="h4">{value}</Typography>
          {deltaText && (
            <Typography variant="body2" sx={{ color: deltaColor }}>{deltaText}</Typography>
          )}
        </Box>
        {footer && (
          <Typography variant="caption" color="text.secondary">{footer}</Typography>
        )}
      </CardContent>
    </Card>
  );
}
