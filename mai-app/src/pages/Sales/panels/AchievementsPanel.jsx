import React, { useEffect, useMemo, useState } from 'react';
import { Grid, Stack, Typography } from '@mui/material';
import { DailyRewardsCard, MonthlyRewardsCard, SideQuestsCard } from '../../../components/cards/RewardsCard';
import PageSection from '../../../components/common/PageSection';
import AchievementList from '../../../features/achievements/AchievementList';
import LevelProgress from '../../../features/achievements/LevelProgress';
import { useAuth } from '../../../hooks/useAuth';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';
import { ACHIEVEMENT_TIERS } from '../../../utils/constants';

export default function AchievementsPanel() {
  const { token } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient({ getToken: () => token }), [token]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [achievements, setAchievements] = useState([]);
  const [points, setPoints] = useState(0);

  useEffect(() => {
    sales.getAchievements()
      .then(list => {
        const items = Array.isArray(list) ? list : (list?.items || []);
        setAchievements(items);
        const pts = items.reduce((sum, a) => sum + (Number(a.points) || 0), 0);
        setPoints(pts);
      })
      .catch(e => {
        error?.(e.message || 'Failed to load achievements');
        setAchievements([]); setPoints(0);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Stack spacing={2}>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch" justifyContent="center">
        <DailyRewardsCard style={{ flex: 1, minWidth: 0 }} />
        <MonthlyRewardsCard style={{ flex: 1, minWidth: 0 }} />
        <SideQuestsCard style={{ flex: 1, minWidth: 0 }} />
      </Stack>
      <PageSection title="Your Achievements">
        <AchievementList items={achievements} />
      </PageSection>

      <PageSection title="Progress to next tier">
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <LevelProgress points={points} tiers={ACHIEVEMENT_TIERS} />
            <Typography variant="caption" color="text.secondary">
              Points: {points}
            </Typography>
          </Grid>
        </Grid>
      </PageSection>
    </Stack>
  );
}
