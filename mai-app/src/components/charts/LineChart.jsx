import React, { useMemo } from 'react';
import { Box, useTheme } from '@mui/material';

/**
 * Tiny dependency-free line chart (sparkline) using SVG.
 * props: data:number[], strokeWidth, height (parent controls height), color
 */
export default function LineChart({ data = [], strokeWidth = 2, color }) {
  const theme = useTheme();
  const { d, minY, maxY } = useMemo(() => {
    const values = data.length ? data : [0, 0];
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const points = values.map((v, i) => {
      const x = (i / (values.length - 1 || 1)) * 100;
      const y = 100 - ((v - min) / range) * 100;
      return `${x},${y}`;
    });
    return { d: `M ${points.join(' L ')}`, minY: min, maxY: max };
  }, [data]);

  return (
    <Box component="svg" viewBox="0 0 100 100" preserveAspectRatio="none" sx={{ width: '100%', height: '100%' }}>
      {/* background grid (optional) */}
      <polyline fill="none" stroke={theme.palette.divider} strokeWidth="0.3" points="0,50 100,50" />
      <path d={d} fill="none" stroke={color || theme.palette.primary.main} strokeWidth={strokeWidth} />
      {/* min/max dots */}
      <circle cx="0" cy="100" r="0" data-min={minY} />
      <circle cx="0" cy="100" r="0" data-max={maxY} />
    </Box>
  );
}
