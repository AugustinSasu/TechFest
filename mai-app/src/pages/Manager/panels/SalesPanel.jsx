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
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - 29);
  const toISO = d => d.toISOString().slice(0, 10);
  return { query: '', startDate: toISO(start), endDate: toISO(end), region: '' };
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
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRpp] = useState(10);
  const [loading, setLoading] = useState(false);

  const load = async (opts = {}) => {
    setLoading(true);
    const { page: pg = page, pageSize = rowsPerPage } = opts;
    try {
      const [sum, list] = await Promise.all([
        manager.getSalesSummary({ ...filters }),
        manager.getSalesList({ ...filters, page: pg, pageSize })
      ]);
      setSummary(sum || {});
      setTrend(sum?.trend || []);
      setRows(list?.items || list || []);
      setTotal(list?.total ?? (list?.items?.length ?? 0));
      setPage(pg);
    } catch (e) {
      error?.(e.message || 'Failed to load sales');
      setRows([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const apply = () => load({ page: 0 });
  const reset = () => { setFilters(defaultFilters()); setTimeout(() => load({ page: 0 }), 0); };

  return (
    <Stack spacing={2}>
      <PageSection title="Filters">
        <SalesFilters
          value={filters}
          onChange={setFilters}
          onApply={apply}
          onReset={reset}
          regions={[]} // optionally populate from backend
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
            total={total}
            page={page}
            rowsPerPage={rowsPerPage}
            loading={loading}
            onPageChange={(p) => load({ page: p })}
            onRowsPerPageChange={(n) => { setRpp(n); load({ pageSize: n, page: 0 }); }}
          />
        )}
      </PageSection>

      <Box />
    </Stack>
  );
}
