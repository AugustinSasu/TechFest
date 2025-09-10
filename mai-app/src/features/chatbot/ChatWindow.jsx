import React, { useEffect, useMemo, useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import MessageList from './MessageList';
import ComposeBar from './ComposeBar';
import PromptPresets from './PromptPresets';
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
export default function ChatWindow({ presets = [], initialMessages = [] }) {
  const { error } = useSnackbar() || {};
  // Init messages with welcome once (avoid StrictMode double effect duplication)
  const [messages, setMessages] = useState(() => {
    if (initialMessages.length) return initialMessages;
    return [{ id: uid(), author: 'ai', content: 'Welcome! Enter your business objective.', createdAt: new Date().toISOString() }];
  });
  const [busy, setBusy] = useState(false);

  // Secretary style multi-step state
  const [step, setStep] = useState('goal'); // goal -> recs -> style_perf -> review -> ids -> done
  const [goal, setGoal] = useState('');
  const [horizon, setHorizon] = useState(30);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedRecs, setSelectedRecs] = useState([]);
  const [style, setStyle] = useState('friendly');
  const [performanceLevel, setPerformanceLevel] = useState('medium'); // high | medium | low | all
  const [teamMessage, setTeamMessage] = useState('');
  const [managerId, setManagerId] = useState('');
  const [salespersonId, setSalespersonId] = useState('');
  const [lastGroupShown, setLastGroupShown] = useState('');

  const add = (m) =>
    setMessages(prev => [...prev, { id: uid(), createdAt: new Date().toISOString(), ...m }]);

  const apiBase = 'http://127.0.0.1:1919';

  const jsonPost = async (path, body) => {
    const res = await fetch(apiBase + path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!res.ok) throw new Error(`${res.status}`);
    return res.json();
  };

  const showGroupMembers = async (group) => {
    add({ author: 'ai', content: `Loading ${group} group members…` });
    try {
      const res = await jsonPost('/send_group_review', { group, review_text: '[preview only]' });
      const list = res?.results || [];
      if (!list.length) {
        add({ author: 'ai', content: 'No members found for this group.' });
      } else {
        const formatted = list.map(e => `${e.name || ''} (ID: ${e.salesperson_id})`).join('\n');
        add({ author: 'ai', content: `Members in group ${group}:\n${formatted}` });
      }
    } catch {
      add({ author: 'ai', content: 'Failed to load group members.' });
    }
  };

  const resetConversation = () => {
    setMessages([]);
    setGoal('');
    setRecommendations([]);
    setSelectedRecs([]);
    setStyle('friendly');
    setPerformanceLevel('medium');
    setTeamMessage('');
    setManagerId('');
    setSalespersonId('');
    setStep('goal');
    add({ author: 'ai', content: 'Welcome! Enter your business objective.' });
  };

  const handleInput = async (text) => {
    const t = text.trim();
    if (!t) return;
    add({ author: 'user', content: t });
    setBusy(true);
    try {
      if (step === 'goal') {
        setGoal(t);
        add({ author: 'ai', content: 'Loading business data summary…' });
        try {
          const summary = await jsonPost('/data_summary', { goal: t, horizon });
          if (summary?.ai_summary) add({ author: 'ai', content: `Business Data Summary:\n${summary.ai_summary}` });
        } catch {
          add({ author: 'ai', content: 'No summary available.' });
        }
        add({ author: 'ai', content: 'Generating recommendations…' });
        const recRes = await jsonPost('/recommendations', { goal: t, horizon });
        const recs = recRes?.recommendations || [];
        setRecommendations(recs);
        if (!recs.length) {
          add({ author: 'ai', content: 'No recommendations found. Enter another objective.' });
          setStep('goal');
        } else {
          const list = recs.map((r,i) => `${i+1}. ${r.title}\n${r.explanation}`).join('\n\n');
          add({ author: 'ai', content: `Available recommendations (reply numbers, e.g. 1,3):\n\n${list}` });
          setStep('recs');
        }
        return;
      }
      if (step === 'recs') {
        const nums = t.split(',').map(x => parseInt(x.trim(),10)-1).filter(x => !isNaN(x) && x>=0 && x<recommendations.length);
        if (!nums.length) {
          add({ author: 'ai', content: 'Please reply with valid numbers (e.g. 1,2).'});
          return;
        }
        setSelectedRecs(nums);
        add({ author: 'ai', content: 'Specify style and performance, e.g.: style: motivational, performance: high (performance can be high, medium, low, all)' });
        setStep('style_perf');
        return;
      }
      if (step === 'style_perf') {
        const styleMatch = t.match(/style\s*:\s*(friendly|professional|motivational)/i);
        const perfMatch = t.match(/performance\s*:\s*(high|medium|low|all)/i);
        if (styleMatch) setStyle(styleMatch[1].toLowerCase());
        if (perfMatch) setPerformanceLevel(perfMatch[1].toLowerCase());
        if (!styleMatch || !perfMatch) {
          add({ author: 'ai', content: 'Need both style and performance (e.g. style: friendly, performance: medium).'});
          return;
        }
        add({ author: 'ai', content: 'Composing team message…' });
        const msgRes = await jsonPost('/compose_message', { goal, horizon, selected: selectedRecs, style: styleMatch[1].toLowerCase(), performance_level: perfMatch[1].toLowerCase() });
        setTeamMessage(msgRes?.message || '');
        add({ author: 'ai', content: `Team Message:\n${msgRes?.message || '(empty)'}` });
        add({ author: 'ai', content: 'Type "accept" to approve, "accept group" to send to the performance group, "redo" to regenerate, "manual" for custom text, or "show group high" (low/medium/all) to list members. Use "back" to adjust style/performance again.' });
        setStep('review');
        return;
      }
      if (step === 'review') {
        const lower = t.toLowerCase();
        if (lower === 'back' || lower === 'restart message') {
          add({ author: 'ai', content: 'Re-enter style & performance (style: friendly, performance: medium).'});
          setStep('style_perf');
          return;
        }
        if (lower === 'accept') {
          add({ author: 'ai', content: 'Enter manager ID and salesperson ID (e.g. 1,2):' });
          setStep('ids');
          return;
        }
        if (lower.startsWith('accept group')) {
          const group = performanceLevel || 'high';
            add({ author: 'ai', content: `Sending message to ${group} group…` });
            try {
              const res = await jsonPost('/send_group_review', { group, review_text: teamMessage });
              const list = res?.results || [];
              add({ author: 'ai', content: 'Group message sent!' });
              if (list.length) {
                const formatted = list.map(e => `${e.name || ''} (ID: ${e.salesperson_id})`).join('\n');
                add({ author: 'ai', content: `Members in group ${group}:\n${formatted}` });
              }
              add({ author: 'ai', content: 'Type "back" to generate a new message or "restart" to begin a new conversation.' });
              setStep('done');
            } catch {
              add({ author: 'ai', content: 'Failed to send group message.' });
            }
            return;
        }
        if (lower.startsWith('show group')) {
          const match = lower.match(/show group\s+(low|medium|high|all)/i);
          const group = match ? match[1] : 'high';
          setLastGroupShown(group);
          await showGroupMembers(group);
          return;
        }
        if (lower === 'redo') {
          add({ author: 'ai', content: 'Re-enter style & performance (style: friendly, performance: medium).' });
          setStep('style_perf');
          return;
        }
        if (lower === 'manual') {
          add({ author: 'ai', content: 'Write your custom message.' });
          setStep('manual');
          return;
        }
        add({ author: 'ai', content: 'Use accept / accept group / redo / manual / show group <group> / back.' });
        return;
      }
      if (step === 'manual') {
        setTeamMessage(t);
        add({ author: 'ai', content: 'Custom message set. Type "accept" (single), "accept group" (group send), or "back" to regenerate style/performance.' });
        setStep('review');
        return;
      }
      if (step === 'ids') {
        const ids = t.split(',').map(x => parseInt(x.trim(),10));
        if (ids.length !== 2 || ids.some(isNaN)) {
          add({ author: 'ai', content: 'Please enter two numbers separated by comma.' });
          return;
        }
        setManagerId(ids[0]);
        setSalespersonId(ids[1]);
        add({ author: 'ai', content: 'Sending review…' });
        await jsonPost('/send_review', { manager_id: ids[0], salesperson_id: ids[1], review_text: teamMessage });
        add({ author: 'ai', content: 'Review sent! Type "restart" to start over.' });
        setStep('done');
        return;
      }
      if (step === 'done') {
        const lower = t.toLowerCase();
        if (lower === 'restart') {
          resetConversation();
          return;
        }
        if (lower === 'back' || lower === 'restart message') {
          add({ author: 'ai', content: 'Re-enter style & performance (style: friendly, performance: medium).'});
          setStep('style_perf');
          return;
        }
        add({ author: 'ai', content: 'Type "restart" to begin again or "back" to tweak style/performance.' });
        return;
      }
    } catch (e) {
      error?.(e.message || 'Operation failed');
      add({ author: 'ai', content: 'Something went wrong.' });
    } finally {
      setBusy(false);
    }
  };

  // Removed effect that added welcome message (caused duplication in React StrictMode)

  const presetItems = useMemo(() => presets, [presets]);

  return (
    <Paper sx={{ display: 'flex', flexDirection: 'column', height: 480 }}>
      {presetItems?.length ? (
        <Box sx={{ p: 1 }}>
          <Typography variant="caption" color="text.secondary">Preset prompts</Typography>
          <PromptPresets presets={presetItems} onSelect={handleInput} />
        </Box>
      ) : null}
      <MessageList messages={messages} />
      <ComposeBar
        disabled={busy}
        onSend={handleInput}
        placeholder={
          step === 'goal' ? 'Enter business objective…' :
          step === 'recs' ? 'Select recommendations (e.g. 1,2)' :
          step === 'style_perf' ? 'style: friendly, performance: medium' :
          step === 'review' ? 'accept | accept group | redo | manual | show group high' :
          step === 'manual' ? 'Write custom message…' :
          step === 'ids' ? 'managerId,salespersonId' :
          'restart | back'
        }
      />
    </Paper>
  );
}
