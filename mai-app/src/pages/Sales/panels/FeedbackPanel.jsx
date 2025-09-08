import React, { useEffect, useMemo, useState } from 'react';
import PageSection from '../../../components/common/PageSection';
import FeedbackList from '../../../features/feedback/FeedbackList';
import { useAuth } from '../../../hooks/useAuth';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';
import EmptyState from '../../../components/common/EmptyState';

export default function FeedbackPanel() {
  const { token } = useAuth() || {};
  const { success, error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient({ getToken: () => token }), [token]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [items, setItems] = useState([]);

  const load = async () => {
    try {
      const list = await sales.getFeedback();
      setItems(Array.isArray(list) ? list : (list?.items || []));
    } catch (e) {
      error?.(e.message || 'Failed to load feedback');
      setItems([]);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const ack = async (item) => {
    try {
      await sales.ackFeedback(item.id);
      success?.('Acknowledged');
      setItems(prev => prev.map(x => (x.id === item.id ? { ...x, read: true } : x)));
    } catch (e) {
      error?.(e.message || 'Failed to acknowledge');
    }
  };

  return (
    <PageSection title="Feedback from Manager">
      {!items.length ? (
        <EmptyState title="No feedback yet" />
      ) : (
        <FeedbackList items={items} onAcknowledge={ack} />
      )}
    </PageSection>
  );
}
