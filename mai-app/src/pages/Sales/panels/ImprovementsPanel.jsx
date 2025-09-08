import React, { useEffect, useMemo, useState } from 'react';
import { Box, Button, Paper, Stack, Typography } from '@mui/material';
import PageSection from '../../../components/common/PageSection';
import EmptyState from '../../../components/common/EmptyState';
import { useAuth } from '../../../hooks/useAuth';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';

export default function ImprovementsPanel() {
  const { token } = useAuth() || {};
  const { success, error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient({ getToken: () => token }), [token]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [items, setItems] = useState([]);
  const [busyId, setBusyId] = useState(null);

  const load = async () => {
    try {
      const list = await sales.getImprovements();
      setItems(Array.isArray(list) ? list : (list?.items || []));
    } catch (e) {
      error?.(e.message || 'Failed to load improvements');
      setItems([]);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const markDone = async (id) => {
    setBusyId(id);
    try {
      await sales.completeImprovement(id);
      success?.('Marked as done');
      setItems(prev => prev.map(it => (it.id === id ? { ...it, done: true } : it)));
    } catch (e) {
      error?.(e.message || 'Failed to update improvement');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <PageSection title="AI Improvements">
      {!items.length ? (
        <EmptyState title="No improvements" description="You're all caught up!" />
      ) : (
        <Stack spacing={1.5}>
          {items.map(it => (
            <Paper key={it.id} sx={{ p: 2 }}>
              <Stack spacing={0.5}>
                <Typography variant="subtitle2" fontWeight={700}>{it.title || 'Improvement'}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                  {it.description || it.body || '-'}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    {it.createdAt ? new Date(it.createdAt).toLocaleString() : ''}
                  </Typography>
                  <Box sx={{ flex: 1 }} />
                  <Button
                    size="small"
                    variant="contained"
                    disabled={!!it.done || busyId === it.id}
                    onClick={() => markDone(it.id)}
                  >
                    {it.done ? 'Done' : (busyId === it.id ? 'Working…' : 'Mark done')}
                  </Button>
                </Box>
              </Stack>
            </Paper>
          ))}
        </Stack>
      )}
    </PageSection>
  );
}
