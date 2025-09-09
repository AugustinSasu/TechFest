import React, { useEffect, useMemo, useState } from 'react';
import { Stack } from '@mui/material';
import PageSection from '../../../components/common/PageSection';
import AgentsTable from '../../../components/tables/AgentsTable';
import AgentDetailsDrawer from '../../../features/agents/AgentDetailsDrawer';
import { useAuth } from '../../../hooks/useAuth';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { createApiClient } from '../../../services/ApiClient';
import { createManagerService } from '../../../services/ManagerService';

export default function AgentsPanel() {
  const { employeeId } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient(), [employeeId]);
  const manager = useMemo(() => createManagerService(api), [api]);

  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRpp] = useState(10);
  const [loading, setLoading] = useState(false);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentAchievements, setAgentAchievements] = useState([]);
  const [agentFeedback, setAgentFeedback] = useState([]);

  const load = async (opts = {}) => {
    setLoading(true);
    const { page: pg = page, pageSize = rowsPerPage } = opts;
    try {
      const list = await manager.getAgents({ page: pg, pageSize });
      setRows(list?.items || list || []);
      setTotal(list?.total ?? (list?.items?.length ?? 0));
      setPage(pg);
    } catch (e) {
      error?.(e.message || 'Failed to load agents');
      setRows([]); setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const openDetails = async (agent) => {
    setSelectedAgent(agent);
    setDrawerOpen(true);
    try {
      const details = await manager.getAgentDetails(agent.id);
      // Expecting { agent, achievements, feedback } but we handle generous shapes
      setAgentAchievements(details?.achievements || details?.agent?.achievements || []);
      setAgentFeedback(details?.feedback || details?.agent?.feedback || []);
    } catch (e) {
      error?.(e.message || 'Failed to load agent details');
      setAgentAchievements([]); setAgentFeedback([]);
    }
  };

  return (
    <Stack spacing={2}>
      <PageSection title="Agents">
        <AgentsTable
          rows={rows}
          total={total}
          page={page}
          rowsPerPage={rowsPerPage}
          loading={loading}
          onPageChange={(p) => load({ page: p })}
          onRowsPerPageChange={(n) => { setRpp(n); load({ pageSize: n, page: 0 }); }}
          onRowClick={openDetails}
        />
      </PageSection>

      <AgentDetailsDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        agent={selectedAgent}
        achievements={agentAchievements}
        feedback={agentFeedback}
      />
    </Stack>
  );
}
