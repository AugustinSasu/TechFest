import React from 'react';
import { Box, Tab, Tabs } from '@mui/material';
import { useSearchParams } from 'react-router-dom';

/**
 * Tabs control that syncs with the ?tab= query param.
 * props.tabs: string[] or {key,label}[]
 */
export default function SectionNav({ tabs = [], sx }) {
  const [params, setParams] = useSearchParams();

  const normalized = tabs.map(t => (typeof t === 'string' ? { key: t, label: t } : t));
  const defaultKey = normalized[0]?.key || 'overview';
  const value = params.get('tab') || defaultKey;

  const handleChange = (_e, newVal) => {
    const next = new URLSearchParams(params);
    next.set('tab', newVal);
    setParams(next, { replace: true });
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', ...sx }}>
      <Tabs value={value} onChange={handleChange}>
        {normalized.map(t => (
          <Tab key={t.key} value={t.key} label={t.label.charAt(0).toUpperCase() + t.label.slice(1)} />
        ))}
      </Tabs>
    </Box>
  );
}
