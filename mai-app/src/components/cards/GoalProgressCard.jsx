import React from 'react';
import { Card, CardContent, LinearProgress, Stack, Typography } from '@mui/material';

export default function GoalProgressCard({ title = 'Goal progress', value = 0, target = 100, sx }) {
  const pct = Math.max(0, Math.min(100, target ? Math.round((value / target) * 100) : 0));
  return (
    <Card sx={{ p: 1, ...sx }}>
      <CardContent>
        <Typography variant="overline" color="text.secondary">{title}</Typography>
        <Stack direction="row" alignItems="baseline" spacing={1} sx={{ mb: 1 }}>
          <Typography variant="h4">{value}</Typography>
          <Typography variant="body2" color="text.secondary">/ {target}</Typography>
          <Typography variant="body2" sx={{ ml: 'auto' }}>{pct}%</Typography>
        </Stack>
        <LinearProgress variant="determinate" value={pct} />
      </CardContent>
    </Card>
  );
}
