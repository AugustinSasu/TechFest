import React, { useEffect, useMemo, useState } from 'react';
import PageSection from '../../../components/common/PageSection';
import ChatWindow from '../../../features/chatbot/ChatWindow';
import { useAuth } from '../../../hooks/useAuth';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { createApiClient } from '../../../services/ApiClient';
import { createManagerService } from '../../../services/ManagerService';
import { createChatService } from '../../../services/ChatService';

/**
 * Manager chatbot with presets. By default ChatWindow will call POST /chat.
 * Here we additionally show how to drive it via ChatService with a session.
 */
export default function ChatbotPanel() {
  const { employeeId } = useAuth() || {};
  const { error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient(), [employeeId]);
  const manager = useMemo(() => createManagerService(api), [api]);
  const chat = useMemo(() => createChatService(api), [api]);

  const [presets, setPresets] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    manager.getPresetPrompts().then(p => setPresets(p || [])).catch(() => setPresets([]));
    chat.startSession().then(s => setSessionId(s?.id)).catch(() => setSessionId(null));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSend = async (promptText) => {
    if (!sessionId) return; // fallback to ChatWindow internal POST /chat
    try {
      const r = await chat.sendMessage({ sessionId, prompt: promptText });
      // expect { content } or string
      return typeof r === 'string' ? r : (r?.content || r?.message || '');
    } catch (e) {
      error?.(e.message || 'Chat request failed');
      return 'Sorry, something went wrong.';
    }
  };

  return (
    <PageSection title="AI Assistant">
      <ChatWindow presets={presets} onSend={sessionId ? onSend : undefined} />
    </PageSection>
  );
}
