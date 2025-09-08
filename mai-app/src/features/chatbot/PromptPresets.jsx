import React from 'react';
import { Button, Stack } from '@mui/material';

/**
 * Props: presets = [{id, label, prompt}], onSelect(prompt)
 */
export default function PromptPresets({ presets = [], onSelect }) {
  if (!presets.length) return null;
  return (
    <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 1 }}>
      {presets.map(p => (
        <Button key={p.id || p.label} size="small" variant="outlined" onClick={() => onSelect?.(p.prompt || p.label)}>
          {p.label}
        </Button>
      ))}
    </Stack>
  );
}
