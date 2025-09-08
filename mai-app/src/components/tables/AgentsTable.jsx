import React from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Typography
} from '@mui/material';

export default function AgentsTable({
  rows = [],
  page = 0,
  rowsPerPage = 10,
  total = rows.length,
  onPageChange,
  onRowsPerPageChange,
  onRowClick,
  loading = false,
}) {
  const empty = !loading && rows.length === 0;

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
                <TableCell>{r.name}</TableCell>
                <TableCell>{r.region || '-'}</TableCell>
                <TableCell align="right">{Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(r.revenue || 0)}</TableCell>
                <TableCell align="right">{r.achievementsCount ?? 0}</TableCell>
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

      <TablePagination
        component="div"
        rowsPerPageOptions={[5, 10, 25]}
        count={total}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={(_e, newPage) => onPageChange?.(newPage)}
        onRowsPerPageChange={(e) => onRowsPerPageChange?.(parseInt(e.target.value, 10))}
      />
    </Paper>
  );
}
