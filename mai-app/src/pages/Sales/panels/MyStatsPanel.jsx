import React, { useEffect, useMemo, useState } from 'react';
import { Box, Button, MenuItem, Stack, TextField, Typography } from '@mui/material';
import PageSection from '../../../components/common/PageSection';
import LineChart from '../../../components/charts/LineChart';
import BarChart from '../../../components/charts/BarChart';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { useAuth } from '../../../hooks/useAuth';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';
import SalesTable from '../../../components/tables/SalesTable';
import EmptyState from '../../../components/common/EmptyState';

function initialFilters() {
  const end = new Date();
  const start = new Date();
  start.setMonth(end.getMonth() - 5); // ~6 months
  const toISO = d => d.toISOString().slice(0, 10);
  return { "start-date": toISO(start), "end-date": toISO(end), "granulatie": 1 };
}

export default function MyStatsPanel() {
  const { employeeId } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient(), [employeeId]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [filters, setFilters] = useState(initialFilters());
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
  if (!employeeId) throw new Error('Missing employee id');
  const data = await sales.getSales(employeeId, filters);
  // Always replace rows with the new array from the API
  const newRows = Array.isArray(data) ? data : (data?.items || []);
  setRows(newRows);
  console.log('MyStatsPanel.load: got rows', newRows.length);
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
            value={filters['start-date']}
            onChange={e => setFilters(f => ({ ...f, "start-date": e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            label="End date"
            type="date"
            size="small"
            value={filters['end-date']}
            onChange={e => setFilters(f => ({ ...f, "end-date": e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            select
            size="small"
            label="Granularity"
            value={filters['granulatie']}
            onChange={e => setFilters(f => ({ ...f, granulatie: e.target.value }))}
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

      <PageSection title="Sales">
              {rows.length === 0 && !loading ? (
                <EmptyState title="No sales found" description="Try adjusting the filters." />
              ) : (
                <SalesTable
                  rows={rows}
                  loading={loading}
                  disablePagination
                />
              )}
            </PageSection>
    </Stack>
  );
}
