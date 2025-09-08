import ApiClient from './ApiClient';

/**
 * Chat/AI endpoints.
 * Supports both session-based (/chat/sessions) and a simple fallback (/chat).
 */
export default class ChatService {
  /** @param {ApiClient} api */
  constructor(api) {
    this.api = api;
  }

  /** @param {{presetId?:string}} [opts] */
  startSession(opts = {}) {
    return this.api.post('/chat/sessions', opts);
  }

  /**
   * Send a message.
   * If sessionId is provided -> POST /chat/sessions/:id/messages
   * Otherwise falls back to POST /chat for simple “prompt -> response”.
   * @param {{sessionId?:string,prompt:string}} payload
   */
  sendMessage({ sessionId, prompt }) {
    if (sessionId) {
      return this.api.post(`/chat/sessions/${encodeURIComponent(sessionId)}/messages`, { prompt });
    }
    // fallback to simple endpoint used by ChatWindow by default
    return this.api.post('/chat', { prompt });
  }

  /** @param {string} sessionId */
  history(sessionId) {
    return this.api.get(`/chat/sessions/${encodeURIComponent(sessionId)}`);
  }
}

export function createChatService(api) {
  return new ChatService(api);
}
