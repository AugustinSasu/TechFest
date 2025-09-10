import React, { useEffect, useMemo, useState } from 'react';
import { Grid, Stack, Typography } from '@mui/material';
import { DailyRewardsCard, MonthlyRewardsCard, SideQuestsCard } from '../../../components/cards/RewardsCard';
import PageSection from '../../../components/common/PageSection';
import AchievementList from '../../../features/achievements/AchievementList';
import SalesGradeProgress from '../../../features/achievements/SalesGradeProgress';
import AchievementBadge from '../../../features/achievements/AchievementBadge';
import { useAuth } from '../../../hooks/useAuth';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';
// Removed ACHIEVEMENT_TIERS import – no longer using points-based tier bar

export default function AchievementsPanel() {
  const { employeeId } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient(), [employeeId]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [achievements, setAchievements] = useState([]);
  const [points, setPoints] = useState(0); // retained in case future UI needs it
  const [gradeData, setGradeData] = useState(null); // { grade, auto_sales, service_sales }
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!employeeId) return;
    // Load achievements (points) – legacy list
  setLoading(true);
    sales.getAchievements(employeeId)
      .then(list => {
        const items = Array.isArray(list) ? list : (list?.items || []);
        setAchievements(items);
        // still compute points silently (not shown) for potential later use
        const pts = items.reduce((sum, a) => sum + (Number(a.points) || 0), 0);
        setPoints(pts);
      })
      .catch(() => { // Suppress snackbar errors (e.g. 404) during placeholder
        setAchievements([]); setPoints(0);
      });

    // Load employee grade + raw sales counts from external (1919) service
    fetch(`http://127.0.0.1:1919/employee_grade_openai?employee_id=${employeeId}`)
      .then(r => r.json())
      .then(data => setGradeData(data))
      .catch(() => setGradeData(null))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [employeeId]);

  return (
    <Stack spacing={2}>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch" justifyContent="center">
        <DailyRewardsCard style={{ flex: 1, minWidth: 0 }} />
        <MonthlyRewardsCard style={{ flex: 1, minWidth: 0 }} />
        <SideQuestsCard style={{ flex: 1, minWidth: 0 }} />
      </Stack>
      <PageSection title="Your Achievements">
        {loading && (
          <Typography variant="body1" color="text.secondary" sx={{ mb:2 }}>Loading achievements…</Typography>
        )}
        <Stack spacing={2}>
          <AchievementList items={achievements} />
          {gradeData && (
            <Stack direction="row" spacing={3} alignItems="center">
              <AchievementBadge tier={(gradeData.grade || 'bronze').toLowerCase()} sx={{ transform: 'scale(1.3)' }} />
              <Typography variant="h5" fontWeight={600}>
                Car sales: {gradeData.auto_sales ?? 0} · Service sales: {gradeData.service_sales ?? 0}
              </Typography>
            </Stack>
          )}
        </Stack>
      </PageSection>

      <PageSection title="Progress to next tier">
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            {!loading && (
            <SalesGradeProgress
              grade={gradeData?.grade}
              autoSales={gradeData?.auto_sales || 0}
              serviceSales={gradeData?.service_sales || 0}
              large
              largeFont
              widthPercent={100}
              showCounts={false}
            />)}
          </Grid>
        </Grid>
      </PageSection>
    </Stack>
  );
}
