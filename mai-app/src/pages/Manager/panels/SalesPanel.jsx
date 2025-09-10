import React, { useEffect, useMemo, useState } from 'react';
import { Box, Stack } from '@mui/material';
import PageSection from '../../../components/common/PageSection';
import SalesFilters from '../../../features/sales/SalesFilters';
import SalesKPIs from '../../../features/sales/SalesKPIs';
import SalesTable from '../../../components/tables/SalesTable';
import EmptyState from '../../../components/common/EmptyState';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { useAuth } from '../../../hooks/useAuth';
import { createApiClient } from '../../../services/ApiClient';
import { createManagerService } from '../../../services/ManagerService';

function defaultFilters() {
  // Fixed default end date requested: 01/01/2025 (dd/mm/yyyy) -> 2025-01-01 ISO
  const end_date = new Date('2025-01-01T00:00:00');
  const start_date = new Date(end_date);
  start_date.setDate(end_date.getDate() - 29); // keep 30-day window
  const toISO = d => d.toISOString().slice(0, 10);
  return { "granulatie": 1, "start-date": toISO(start_date), "end-date": toISO(end_date) };
}

export default function SalesPanel() {
  const { employeeId } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient(), [employeeId]);
  const manager = useMemo(() => createManagerService(api), [api]);

  const [filters, setFilters] = useState(defaultFilters());
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      // 1. KPI summary (păstrăm apelul existent)
      const summaryPromise = manager.getSalesSummary({ ...filters });
      // 2. Unic apel pentru tabel: /sale-orders/filter?start-date=...&end-date=...
      const list = await manager.getSalesList({ 'start-date': filters['start-date'], 'end-date': filters['end-date'] });
      const rows = Array.isArray(list) ? list : (list?.items || []);
      const sum = await summaryPromise;
      setSummary(sum || {});
      setTrend(sum?.trend || []);
      setRows(rows);
    } catch (e) {
      error?.(e.message || 'Failed to load sales');
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const apply = () => load();
  const reset = () => { setFilters(defaultFilters()); setTimeout(() => load(), 0); };

  return (
    <Stack spacing={2}>
      <PageSection title="Filters">
        <SalesFilters
          value={filters}
          onChange={setFilters}
          onApply={apply}
          onReset={reset}
          granularities={['week', 'month', 'year']} // renamed from RO to EN per request
        />
      </PageSection>

      <PageSection title="KPI Summary">
        <SalesKPIs summary={summary || {}} trend={trend} />
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

      <Box />
    </Stack>
  );
}
