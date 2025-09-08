import React from 'react';
import { Box, Divider, Drawer, Stack, Typography } from '@mui/material';
import AgentCard from './AgentCard';
import AchievementList from '../achievements/AchievementList';
import FeedbackList from '../feedback/FeedbackList';

export default function AgentDetailsDrawer({ open, onClose, agent, achievements = [], feedback = [] }) {
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: { xs: 360, sm: 420 }, p: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>Agent details</Typography>
        <AgentCard agent={agent} />

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" sx={{ mb: 1 }}>Achievements</Typography>
        <AchievementList items={achievements} dense />

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" sx={{ mb: 1 }}>Feedback</Typography>
        <FeedbackList items={feedback} />
      </Box>
    </Drawer>
  );
}
