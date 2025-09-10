import React from 'react';
import { Grid } from '@mui/material';
import StatCard from '../../components/cards/StatCard';
import KPITrendCard from '../../components/cards/KPITrendCard';
import GoalProgressCard from '../../components/cards/GoalProgressCard';

export default function SalesKPIs({ summary = {}, trend = [] }) {
  const {
    revenue = 0,
    target = 0,
    winRatePct = 0,
    deals = 0,
    deltaRevenuePct = 0
  } = summary;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}><StatCard title="Revenue" value={Intl.NumberFormat().format(summary.venit)} delta={deltaRevenuePct} /></Grid>
      <Grid item xs={12} sm={6} md={3}><StatCard title="Deals" value={summary.vanzari_incheiate} /></Grid>
      <Grid item xs={12}><KPITrendCard title="Revenue Trend" value={Intl.NumberFormat().format(summary.venit)} data={trend} /></Grid>
    </Grid>
  );
}
