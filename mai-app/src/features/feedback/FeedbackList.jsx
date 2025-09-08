import React from 'react';
import { Stack, Typography } from '@mui/material';
import FeedbackItem from './FeedbackItem';

export default function FeedbackList({ items = [], onAcknowledge }) {
  if (!items.length) {
    return <Typography variant="body2" color="text.secondary">No feedback available.</Typography>;
  }
  return (
    <Stack spacing={1.5}>
      {items.map(x => (
        <FeedbackItem key={x.id} item={x} onAcknowledge={onAcknowledge} />
      ))}
    </Stack>
  );
}
