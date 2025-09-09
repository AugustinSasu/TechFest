import React, { useEffect, useMemo, useState } from 'react';
import { Box, Button, MenuItem, Stack, TextField, Typography } from '@mui/material';
import PageSection from '../../../components/common/PageSection';
import LineChart from '../../../components/charts/LineChart';
import BarChart from '../../../components/charts/BarChart';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { useAuth } from '../../../hooks/useAuth';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';

function initialFilters() {
  const end = new Date();
  const start = new Date();
  start.setMonth(end.getMonth() - 5); // ~6 months
  const toISO = d => d.toISOString().slice(0, 10);
  return { startDate: toISO(start), endDate: toISO(end), granularity: 'month' };
}

export default function MyStatsPanel() {
  const { employeeId } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient(), [employeeId]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [filters, setFilters] = useState(initialFilters());
  const [trend, setTrend] = useState([]);
  const [target, setTarget] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
  if (!employeeId) throw new Error('Missing employee id');
  const data = await sales.getStats(employeeId, filters);
      // Be generous with shape: accept { trend, target } or arrays directly
      setTrend(Array.isArray(data) ? data : (data?.trend || []));
      setTarget(Array.isArray(data?.target) ? data.target : []);
    } catch (e) {
      error?.(e.message || 'Failed to load stats');
      setTrend([]); setTarget([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const apply = () => load();

  return (
    <Stack spacing={2}>
      <PageSection title="Filters">
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
          <TextField
            label="Start date"
            type="date"
            size="small"
            value={filters.startDate}
            onChange={e => setFilters(f => ({ ...f, startDate: e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            label="End date"
            type="date"
            size="small"
            value={filters.endDate}
            onChange={e => setFilters(f => ({ ...f, endDate: e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            select
            size="small"
            label="Granularity"
            value={filters.granularity}
            onChange={e => setFilters(f => ({ ...f, granularity: e.target.value }))}
          >
            <MenuItem value="day">Day</MenuItem>
            <MenuItem value="week">Week</MenuItem>
            <MenuItem value="month">Month</MenuItem>
          </TextField>
          <Button onClick={apply} variant="contained" disabled={loading}>
            {loading ? 'Loading…' : 'Apply'}
          </Button>
        </Stack>
      </PageSection>

      <PageSection title="My Revenue Trend">
        <Box sx={{ height: 220 }}>
          {trend.length ? <LineChart data={trend} /> : <Typography variant="body2" color="text.secondary">No data</Typography>}
        </Box>
      </PageSection>

      {!!target.length && (
        <PageSection title="Target vs Actual">
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <Box sx={{ flex: 1, height: 200 }}>
              <Typography variant="caption" color="text.secondary">Actual</Typography>
              <BarChart data={trend} />
            </Box>
            <Box sx={{ flex: 1, height: 200 }}>
              <Typography variant="caption" color="text.secondary">Target</Typography>
              <BarChart data={target} />
            </Box>
          </Stack>
        </PageSection>
      )}
    </Stack>
  );
}
