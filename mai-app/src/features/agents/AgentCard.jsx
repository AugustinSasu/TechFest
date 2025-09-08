import React from 'react';
import { Avatar, Card, CardContent, Stack, Typography } from '@mui/material';

export default function AgentCard({ agent }) {
  const name = agent?.name || 'Unknown Agent';
  const initials = name.split(' ').map(s => s[0]).slice(0, 2).join('').toUpperCase();

  return (
    <Card>
      <CardContent>
        <Stack direction="row" spacing={2} alignItems="center">
          <Avatar>{initials}</Avatar>
          <Stack spacing={0.3}>
            <Typography fontWeight={600}>{name}</Typography>
            <Typography variant="body2" color="text.secondary">{agent?.region || '—'}</Typography>
            <Typography variant="caption" color="text.secondary">Revenue: {Intl.NumberFormat().format(agent?.revenue ?? 0)}</Typography>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
