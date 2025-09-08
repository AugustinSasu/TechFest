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
      <Grid item xs={12} sm={6} md={3}><StatCard title="Revenue" value={Intl.NumberFormat().format(revenue)} delta={deltaRevenuePct} /></Grid>
      <Grid item xs={12} sm={6} md={3}><StatCard title="Deals" value={deals} /></Grid>
      <Grid item xs={12} sm={6} md={3}><StatCard title="Win Rate" value={`${winRatePct}%`} /></Grid>
      <Grid item xs={12} sm={6} md={3}><GoalProgressCard title="Quota" value={revenue} target={target} /></Grid>
      <Grid item xs={12}><KPITrendCard title="Revenue Trend" value={Intl.NumberFormat().format(revenue)} data={trend} /></Grid>
    </Grid>
  );
}
