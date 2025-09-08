import React from 'react';
import { Button, MenuItem, Stack, TextField } from '@mui/material';

/**
 * Controlled filters bar.
 * Props: value: { query, startDate, endDate, region }, onChange(next), onApply(), onReset()
 */
export default function SalesFilters({ value = {}, onChange, onApply, onReset, regions = [] }) {
  const v = { query: '', startDate: '', endDate: '', region: '', ...value };

  const update = (patch) => onChange?.({ ...v, ...patch });

  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center" sx={{ mb: 2 }}>
      <TextField
        label="Search"
        size="small"
        value={v.query}
        onChange={e => update({ query: e.target.value })}
        sx={{ minWidth: 160 }}
      />
      <TextField
        label="Start date"
        type="date"
        size="small"
        value={v.startDate}
        onChange={e => update({ startDate: e.target.value })}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="End date"
        type="date"
        size="small"
        value={v.endDate}
        onChange={e => update({ endDate: e.target.value })}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="Region"
        size="small"
        select
        value={v.region}
        onChange={e => update({ region: e.target.value })}
        sx={{ minWidth: 140 }}
      >
        <MenuItem value="">All</MenuItem>
        {regions.map(r => <MenuItem key={r} value={r}>{r}</MenuItem>)}
      </TextField>

      <Stack direction="row" spacing={1} sx={{ ml: 'auto' }}>
        <Button variant="outlined" onClick={onReset}>Reset</Button>
        <Button variant="contained" onClick={onApply}>Apply</Button>
      </Stack>
    </Stack>
  );
}
