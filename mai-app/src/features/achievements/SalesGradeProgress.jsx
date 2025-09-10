import React from 'react';
import { Box, LinearProgress, Stack, Typography } from '@mui/material';
import AchievementBadge from './AchievementBadge';

/**
 * Displays progress to next sales grade based on auto/service sales.
 * Grade rules (OR logic):
 *  - silver: auto >= 5 OR service >= 3
 *  - gold:   auto >=10 OR service >= 5
 *
 * Progress strategy: use the better (max) ratio toward the next tier.
 * Remaining hint chooses the smaller additional requirement (car vs service);
 * if both remaining > 0 for bronze -> show both; for silver -> show minimal path.
 */
export default function SalesGradeProgress({
  grade = 'bronze',
  autoSales = 0,
  serviceSales = 0,
  large = false,
  showCounts = true,
  halfWidth = false, // deprecated, kept for backward compatibility
  largeFont = false,
  widthPercent // number (e.g. 100) overrides halfWidth
}) {
  const normalized = (grade || '').toLowerCase();
  const thresholds = {
    silver: { auto: 5, service: 3 },
    gold: { auto: 10, service: 5 }
  };

  let current = normalized;
  if (!['bronze','silver','gold'].includes(current)) current = 'bronze';

  let nextTier = null;
  if (current === 'bronze') nextTier = 'silver';
  else if (current === 'silver') nextTier = 'gold';

  let pct = 100;
  let helper = 'Max level';

  if (nextTier) {
    const target = thresholds[nextTier];
    const ratioAuto = autoSales / target.auto;
    const ratioService = serviceSales / target.service;
    pct = Math.min(100, Math.round(Math.max(ratioAuto, ratioService) * 100));

    // Remaining calculations
    const remAuto = Math.max(0, target.auto - autoSales);
    const remService = Math.max(0, target.service - serviceSales);

    if (current === 'bronze') {
      if (remAuto === 0 || remService === 0) {
        helper = `Ready for ${nextTier} — refresh soon`;
      } else {
        helper = `Need ${remAuto} car sale${remAuto!==1?'s':''} OR ${remService} service sale${remService!==1?'s':''} to reach ${nextTier}`;
      }
    } else if (current === 'silver') {
      // choose minimal path
      if (remAuto === 0 || remService === 0) {
        helper = `Ready for ${nextTier} — refresh soon`;
      } else if (remAuto <= remService) {
        helper = `Need ${remAuto} more car sale${remAuto!==1?'s':''} to reach ${nextTier}`;
      } else {
        helper = `Need ${remService} more service sale${remService!==1?'s':''} to reach ${nextTier}`;
      }
    }
  }

  const containerSx = widthPercent
    ? { width: `${widthPercent}%`, minWidth: 260 }
    : (halfWidth ? { width: '50%', minWidth: 260 } : undefined);

  return (
    <Box sx={containerSx}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.75 }}>
        <AchievementBadge tier={current} size={large ? 'medium' : 'small'} sx={large ? { fontSize: 16, px: 1.5, py: 0.75 } : {}} />
        <Box sx={{ flexGrow: 1 }} />
        <Typography
          variant={largeFont ? 'h6' : 'body2'}
          color="text.secondary"
          fontWeight={600}
          sx={largeFont ? { fontSize: 24, lineHeight: 1 } : {}}
        >
          {nextTier ? `${pct}% to ${nextTier}` : 'Max level'}
        </Typography>
      </Stack>
      <LinearProgress
        variant="determinate"
        value={pct}
        sx={large ? { height: 20, borderRadius: 2, [`& .MuiLinearProgress-bar`]: { borderRadius: 2 } } : {}}
      />
      <Typography
        variant={largeFont ? 'body1' : 'caption'}
        color="text.secondary"
        sx={{ display: 'block', mt: 0.75, fontSize: largeFont ? 18 : undefined }}
      >
        {helper}
      </Typography>
      {showCounts && (
        <Typography
          variant={largeFont ? 'body2' : 'caption'}
          color="text.secondary"
          sx={{ display: 'block', fontSize: largeFont ? 16 : undefined }}
        >
          Car sales: {autoSales} · Service sales: {serviceSales}
        </Typography>
      )}
    </Box>
  );
}
