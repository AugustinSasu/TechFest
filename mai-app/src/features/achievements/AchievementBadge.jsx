import React from 'react';
import { Chip } from '@mui/material';

const COLORS = {
  bronze: '#cd7f32',
  silver: '#c0c0c0',
  gold: '#ffd700'
};

export default function AchievementBadge({ tier = 'bronze', label, size = 'medium', sx }) {
  const text = label || tier.charAt(0).toUpperCase() + tier.slice(1);
  return (
    <Chip
      label={text}
      size={size}
      sx={{
        bgcolor: COLORS[tier] || 'action.selected',
        color: 'black',
        fontWeight: 600,
        ...sx
      }}
    />
  );
}
