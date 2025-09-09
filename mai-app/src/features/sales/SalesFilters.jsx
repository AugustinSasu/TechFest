import React from 'react';
import { Button, MenuItem, Stack, TextField } from '@mui/material';

/**
 * Controlled filters bar.
 * Props: value: { query, startDate, endDate, region }, onChange(next), onApply(), onReset()
 */
export default function SalesFilters({ value = {}, onChange, onApply, onReset, granularities = [] }) {
  const v = { "query": '', "start-date": '', "end-date": '', "granulatie": '', ...value };

  const update = (patch) => onChange?.({ ...v, ...patch });

  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center" sx={{ mb: 2 }}>
      <TextField
        label="Start date"
        type="date"
        size="small"
        value={v['start-date']}
        onChange={e => update({ 'start-date': e.target.value })}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="End date"
        type="date"
        size="small"
        value={v['end-date']}
        onChange={e => update({ 'end-date': e.target.value })}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="Granularity"
        size="small"
        select
        value={v['granulatie']}
        onChange={e => update({ 'granulatie': e.target.value })}
        sx={{ minWidth: 140 }}
      >
        <MenuItem value="">All</MenuItem>
        {granularities.map((r,i) => <MenuItem key={i+1} value={i+1}>{r}</MenuItem>)}
      </TextField>
    
      <Stack direction="row" spacing={1} sx={{ ml: 'auto' }}>
        <Button variant="outlined" onClick={onReset}>Reset</Button>
        <Button variant="contained" onClick={onApply}>Apply</Button>
      </Stack>
    </Stack>
  );
}
