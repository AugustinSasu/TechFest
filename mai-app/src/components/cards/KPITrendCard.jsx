import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import LineChart from '../charts/LineChart';

export default function KPITrendCard({ title, value, data = [], height = 80, sx }) {
  return (
    <Card sx={{ p: 1, ...sx }}>
      <CardContent>
        <Typography variant="overline" color="text.secondary">{title}</Typography>
        <Typography variant="h4" sx={{ mb: 1 }}>{value}</Typography>
        <Box sx={{ height }}>
          <LineChart data={data} />
        </Box>
      </CardContent>
    </Card>
  );
}
