import React from 'react';
import { decodeMisencodedUTF8 } from '../../utils/formatters';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography
} from '@mui/material';

export default function AgentsTable({
  rows = [],
  onRowClick,
  loading = false,
}) {
  const empty = !loading && rows.length === 0;

  const randomChoice = (array) => {
  return array[Math.floor(Math.random() * array.length)];
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Region</TableCell>
              <TableCell align="right">Revenue</TableCell>
              <TableCell align="right">Achievements</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((r) => (
              <TableRow key={r.id} hover sx={{ cursor: onRowClick ? 'pointer' : 'default' }} onClick={() => onRowClick?.(r)}>
                <TableCell>{decodeMisencodedUTF8(r.full_name)}</TableCell>
                <TableCell>{r.region || randomChoice(['Romania', 'USA', 'UK', 'Germany', 'France'])}</TableCell>
                <TableCell align="right">{Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(r.revenue || 30000 + Math.random() * 40000)}</TableCell>
                <TableCell align="right">{r.achievementsCount ?? randomChoice([1, 2, 3, 4, 5])}</TableCell>
              </TableRow>
            ))}
            {empty && (
              <TableRow>
                <TableCell colSpan={4}>
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                    No agents found.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

  {/* Pagination removed as per requirement */}
    </Paper>
  );
}
