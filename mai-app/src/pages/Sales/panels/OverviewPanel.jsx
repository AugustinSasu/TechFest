import React, { useEffect, useMemo, useState } from 'react';
import { Button, Stack } from '@mui/material';
import PageSection from '../../../components/common/PageSection';
import SalesKPIs from '../../../features/sales/SalesKPIs';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { useAuth } from '../../../hooks/useAuth';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';

function lastNDaysRange(n = 30) {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - (n - 1));
  const toISO = d => d.toISOString().slice(0, 10);
  return { startDate: toISO(start), endDate: toISO(end) };
}

export default function OverviewPanel() {
  const { token } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient({ getToken: () => token }), [token]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [{ startDate, endDate }, setRange] = useState(lastNDaysRange(30));
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await sales.getMySummary({ startDate, endDate });
      setSummary(data || {});
    } catch (e) {
      error?.(e.message || 'Failed to load my summary');
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [startDate, endDate]);

  return (
    <Stack spacing={2}>
      <PageSection
        title="My KPI Overview"
        actions={
          <Stack direction="row" spacing={1}>
            <Button onClick={() => setRange(lastNDaysRange(7))} variant="outlined" size="small">Last 7d</Button>
            <Button onClick={() => setRange(lastNDaysRange(30))} variant="outlined" size="small">Last 30d</Button>
            <Button onClick={load} disabled={loading} variant="contained" size="small">{loading ? 'Refreshing…' : 'Refresh'}</Button>
          </Stack>
        }
      >
        <SalesKPIs summary={summary || {}} trend={summary?.trend || []} />
      </PageSection>
    </Stack>
  );
}
