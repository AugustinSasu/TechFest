import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

/**
 * Single chat bubble.
 * message: { author: 'user'|'ai', content, createdAt }
 */
export default function MessageItem({ message }) {
  const isUser = message?.author === 'user';
  return (
    <Box sx={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', my: 0.5 }}>
      <Paper
        sx={{
          px: 1.5,
          py: 1,
          maxWidth: '75%',
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? 'primary.contrastText' : 'text.primary',
          borderRadius: 2
        }}
      >
        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{message?.content}</Typography>
        {message?.createdAt && (
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            {new Date(message.createdAt).toLocaleTimeString()}
          </Typography>
        )}
      </Paper>
    </Box>
  );
}
