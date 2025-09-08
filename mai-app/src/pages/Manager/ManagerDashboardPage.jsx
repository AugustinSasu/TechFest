import React from 'react';
import { Box } from '@mui/material';
import ManagerLayout from '../../layouts/ManagerLayout';
import SectionNav from '../../components/layout/SectionNav';
import { MANAGER_TABS } from '../../routing/routePaths';
import { useTabQuerySync } from '../../hooks/useTabQuerySync';

// Panels
import OverviewPanel from './panels/OverviewPanel';
import SalesPanel from './panels/SalesPanel';
import AgentsPanel from './panels/AgentsPanel';
import ChatbotPanel from './panels/ChatbotPanel';

export default function ManagerDashboardPage() {
  const [tab] = useTabQuerySync(MANAGER_TABS, MANAGER_TABS[0]);

  return (
    <ManagerLayout>
      <SectionNav tabs={MANAGER_TABS} sx={{ mb: 2 }} />
      <Box sx={{ display: 'grid', gap: 2 }}>
        {tab === 'overview' && <OverviewPanel />}
        {tab === 'sales' && <SalesPanel />}
        {tab === 'agents' && <AgentsPanel />}
        {tab === 'chat' && <ChatbotPanel />}
      </Box>
    </ManagerLayout>
  );
}
