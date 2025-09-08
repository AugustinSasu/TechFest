import React from 'react';
import { Box, Stack, Typography } from '@mui/material';

export default function PageHeader({ title, subtitle, actions, sx }) {
  return (
    <Stack
      direction="row"
      alignItems={{ xs: 'stretch', sm: 'center' }}
      justifyContent="space-between"
      spacing={2}
      sx={{ mb: 2, flexWrap: 'wrap', ...sx }}
    >
      <Box>
        <Typography variant="h5" fontWeight={700}>{title}</Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">{subtitle}</Typography>
        )}
      </Box>
      {actions && <Box sx={{ display: 'flex', gap: 1 }}>{actions}</Box>}
    </Stack>
  );
}
