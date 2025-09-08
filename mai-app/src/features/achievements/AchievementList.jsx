import React from 'react';
import { Grid } from '@mui/material';
import AchievementBadge from './AchievementBadge';

/**
 * items: [{ id, tier: 'bronze'|'silver'|'gold', label? }]
 * dense: grid compacter
 */
export default function AchievementList({ items = [], dense = false }) {
  if (!items.length) return null;
  return (
    <Grid container spacing={dense ? 1 : 2}>
      {items.map((a, idx) => (
        <Grid key={a.id ?? `${a.tier}-${idx}`} item>
          <AchievementBadge tier={a.tier} label={a.label} />
        </Grid>
      ))}
    </Grid>
  );
}
