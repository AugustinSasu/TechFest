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
  disablePagination = false,
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
              <TableCell>Agent</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Product/Service / Status</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Region</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {rows.map((r, idx) => {
              // Compose a unique key from all possible id fields and index
              const key = [r.order_id, r.sale_id, r.id, idx].filter(Boolean).join('-');
              return (
                <TableRow
                  key={key}
                  hover
                  sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
                  onClick={() => onRowClick?.(r)}
                >
                  <TableCell>{r.full_name || r.agent || r.agentId || r.created_by || r.salesperson_id || '-'}</TableCell>
                  <TableCell>{r.location || r.nume_locatie || r.dealership_id || '-'}</TableCell>
                  <TableCell>{r.produs || r.serviceName || r.vehicleModel || r.status || '-'}</TableCell>
                  <TableCell align="right">{fmtCurrency(r.pret || r.total_amount)}</TableCell>
                  <TableCell>{fmtDate(r.data_vanzare || r.order_date)}</TableCell>
                  <TableCell>{r.region || r.regiune || '-'}</TableCell>
                </TableRow>
              );
            })}

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

      {!disablePagination && (onPageChange || onRowsPerPageChange) && (
        <TablePagination
          component="div"
          rowsPerPageOptions={[5, 10, 25]}
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_e, newPage) => onPageChange?.(newPage)}
          onRowsPerPageChange={(e) => onRowsPerPageChange?.(parseInt(e.target.value, 10))}
        />
      )}
    </Paper>
  );
}
