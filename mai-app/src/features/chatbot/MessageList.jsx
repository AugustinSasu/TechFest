import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import MessageItem from './MessageItem';

export default function MessageList({ messages = [] }) {
  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Box sx={{ overflowY: 'auto', flex: 1, p: 1 }}>
      {messages.map(m => <MessageItem key={m.id} message={m} />)}
      <div ref={endRef} />
    </Box>
  );
}
