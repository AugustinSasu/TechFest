import React from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Typography
} from '@mui/material';

export default function SalesTable({
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

  const fmtCurrency = (n) => Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(n || 0);
  const fmtDate = (iso) => (iso ? new Date(iso).toLocaleDateString() : '-');

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <TableContainer sx={{ maxHeight: 520 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Agent</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Product/Service</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Region</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((r) => (
              <TableRow
                key={r.id}
                hover
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
                onClick={() => onRowClick?.(r)}
              >
                <TableCell>{r.sale_id}</TableCell>
                <TableCell>{r.agent || r.agentId}</TableCell>
                <TableCell>{r.nume_locatie || r.dealership_id || '-'}</TableCell>
                <TableCell>{r.produs || r.serviceName || r.vehicleModel || '-'}</TableCell>
                <TableCell align="right">{fmtCurrency(r.pret)}</TableCell>
                <TableCell>{fmtDate(r.data_vanzare)}</TableCell>
                <TableCell>{r.regiune || '-'}</TableCell>
              </TableRow>
            ))}

            {empty && (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                    No sales found.
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
