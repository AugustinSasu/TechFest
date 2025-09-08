import React from 'react';
import { Box } from '@mui/material';
import SalesLayout from '../../layouts/SalesLayout';
import SectionNav from '../../components/layout/SectionNav';
import { SALESMAN_TABS } from '../../routing/routePaths';
import { useTabQuerySync } from '../../hooks/useTabQuerySync';

// Panels
// ...existing code...
import MyStatsPanel from './panels/MyStatsPanel';
import ImprovementsPanel from './panels/ImprovementsPanel';
import AchievementsPanel from './panels/AchievementsPanel';
import FeedbackPanel from './panels/FeedbackPanel';

export default function SalesDashboardPage() {
  const [tab] = useTabQuerySync(SALESMAN_TABS, SALESMAN_TABS[0]);

  return (
    <SalesLayout>
      <SectionNav tabs={SALESMAN_TABS} sx={{ mb: 2 }} />
      <Box sx={{ display: 'grid', gap: 2 }}>
        {tab === 'mystats' && <MyStatsPanel />}
        {tab === 'improvements' && <ImprovementsPanel />}
        {tab === 'achievements' && <AchievementsPanel />}
        {tab === 'feedback' && <FeedbackPanel />}
      </Box>
    </SalesLayout>
  );
}
