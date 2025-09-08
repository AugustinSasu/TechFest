import React, { useMemo } from 'react';
import { Box, LinearProgress, Stack, Typography } from '@mui/material';

/**
 * Props:
 *  - points: number
 *  - tiers: [{id:'bronze'|'silver'|'gold', min:number}]
 */
export default function LevelProgress({ points = 0, tiers = [
  { id: 'bronze', min: 10000 },
  { id: 'silver', min: 25000 },
  { id: 'gold',   min: 50000 }
] }) {
  const { current, next, pct } = useMemo(() => {
    const ordered = [...tiers].sort((a, b) => a.min - b.min);
    let cur = ordered[0];
    for (const t of ordered) if (points >= t.min) cur = t;
    const idx = ordered.findIndex(t => t.id === cur.id);
    const nxt = ordered[idx + 1] || null;
    const base = cur?.min ?? 0;
    const cap = nxt?.min ?? Math.max(base, points);
    const percent = cap === base ? 100 : Math.round(((points - base) / (cap - base)) * 100);
    return { current: cur, next: nxt, pct: Math.max(0, Math.min(100, percent)) };
  }, [points, tiers]);

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
        <Typography variant="body2" fontWeight={600}>Level: {current?.id ?? '—'}</Typography>
        <Typography variant="body2" color="text.secondary">
          {next ? `${pct}% to ${next.id}` : 'Max level'}
        </Typography>
      </Stack>
      <LinearProgress variant="determinate" value={pct} />
    </Box>
  );
}
