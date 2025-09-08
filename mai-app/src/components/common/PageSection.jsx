import React from 'react';
import { Box, Paper, Stack, Typography } from '@mui/material';

export default function PageSection({ id, title, actions, children, noPaper = false, sx, contentSx }) {
  const Wrapper = noPaper ? Box : Paper;
  return (
    <Wrapper id={id} sx={{ p: noPaper ? 0 : 2, borderRadius: 2, ...sx }}>
      {(title || actions) && (
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
          {title && <Typography variant="subtitle1" fontWeight={600}>{title}</Typography>}
          {actions && <Box sx={{ display: 'flex', gap: 1 }}>{actions}</Box>}
        </Stack>
      )}
      <Box sx={{ ...contentSx }}>{children}</Box>
    </Wrapper>
  );
}
