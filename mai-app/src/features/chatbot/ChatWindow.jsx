import React, { useMemo, useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import MessageList from './MessageList';
import ComposeBar from './ComposeBar';
import PromptPresets from './PromptPresets';
import { useApi } from '../../hooks/useApi';
import { useSnackbar } from '../../hooks/useSnackbar';

const uid = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2));

/**
 * Simple chat window with optional backend hookup.
 * Props:
 *  - presets: [{id,label,prompt}]
 *  - initialMessages: [{id,author,content,createdAt}]
 *  - onSend(prompt) -> returns {content} or string (optional; if absent calls POST /chat)
 */
export default function ChatWindow({ presets = [], initialMessages = [], onSend }) {
  const { post } = useApi();
  const { error } = useSnackbar() || {};
  const [messages, setMessages] = useState(initialMessages);
  const [busy, setBusy] = useState(false);

  const add = (m) =>
    setMessages(prev => [...prev, { id: uid(), createdAt: new Date().toISOString(), ...m }]);

  const send = async (promptText) => {
    add({ author: 'user', content: promptText });
    setBusy(true);
    try {
      let reply;
      if (onSend) {
        const r = await onSend(promptText);
        reply = typeof r === 'string' ? r : (r?.content || r?.message || '');
      } else {
        // default backend: POST /chat  { prompt }
        const r = await post('/chat', { prompt: promptText });
        reply = typeof r === 'string' ? r : (r?.content || r?.message || JSON.stringify(r));
      }
      add({ author: 'ai', content: reply || '(no content)' });
    } catch (e) {
      error?.(e.message || 'Chat request failed');
      add({ author: 'ai', content: 'Sorry, something went wrong.' });
    } finally {
      setBusy(false);
    }
  };

  const sendRecommendation = async (recommendText) => {
    add({ author: 'manager', content: `Recommendation: ${recommendText}` });
    setBusy(true);
    try {
      if (onRecommend) {
        await onRecommend(recommendText);
      } else {
        await post('/chat/recommendation', { recommendation: recommendText });
      }
    } catch (e) {
      error?.(e.message || 'Failed to send recommendation');
    } finally {
      setBusy(false);
    }
  };

  const presetItems = useMemo(() => presets, [presets]);

  return (
    <Paper sx={{ display: 'flex', flexDirection: 'column', height: 480 }}>
      {presetItems?.length ? (
        <Box sx={{ p: 1 }}>
          <Typography variant="caption" color="text.secondary">Preset prompts</Typography>
          <PromptPresets presets={presetItems} onSelect={send} />
        </Box>
      ) : null}
      <MessageList messages={messages} />
  <ComposeBar disabled={busy} onSend={send} onRecommend={sendRecommendation} />
    </Paper>
  );
}
