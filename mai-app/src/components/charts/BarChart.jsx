import React, { useMemo } from 'react';
import { Box, useTheme } from '@mui/material';

/**
 * Simple dependency-free bar chart using SVG.
 * props: data:number[], barGap (0..1), color
 */
export default function BarChart({ data = [], barGap = 0.15, color }) {
  const theme = useTheme();
  const { rects } = useMemo(() => {
    const values = data.length ? data : [0];
    const min = Math.min(0, ...values);
    const max = Math.max(...values, 1);
    const range = max - min || 1;
    const n = values.length;
    const bw = 100 / n; // bar width in %
    const gap = bw * barGap;

    const rs = values.map((v, i) => {
      const h = ((v - min) / range) * 100;
      const x = i * bw + gap / 2;
      const y = 100 - h;
      const w = bw - gap;
      return { x, y, w, h };
    });
    return { rects: rs };
  }, [data]);

  return (
    <Box component="svg" viewBox="0 0 100 100" preserveAspectRatio="none" sx={{ width: '100%', height: '100%' }}>
      {rects.map((r, idx) => (
        <rect key={idx} x={r.x} y={r.y} width={r.w} height={r.h} fill={color || theme.palette.primary.main} />
      ))}
    </Box>
  );
}
