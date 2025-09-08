import React from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Typography } from '@mui/material';

export default function ConfirmDialog({
  open,
  title = 'Are you sure?',
  content,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  destructive = false,
  onClose,
  onConfirm,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{title}</DialogTitle>
      {content && (
        <DialogContent>
          {typeof content === 'string'
            ? <Typography variant="body2">{content}</Typography>
            : content}
        </DialogContent>
      )}
      <DialogActions>
        <Button onClick={onClose} color="inherit">{cancelText}</Button>
        <Button onClick={onConfirm} variant="contained" color={destructive ? 'error' : 'primary'}>
          {confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
