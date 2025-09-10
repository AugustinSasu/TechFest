import React, { useEffect, useMemo, useState } from 'react';
import PageSection from '../../../components/common/PageSection';
import FeedbackList from '../../../features/feedback/FeedbackList';
import { useAuth } from '../../../hooks/useAuth';
import { useSnackbar } from '../../../hooks/useSnackbar';
import { createApiClient } from '../../../services/ApiClient';
import { createSalesService } from '../../../services/SalesService';
import EmptyState from '../../../components/common/EmptyState';

export default function FeedbackPanel() {
  const { employeeId } = useAuth() || {};
  const { success, error } = useSnackbar() || {};
  const api = useMemo(() => createApiClient(), [employeeId]);
  const sales = useMemo(() => createSalesService(api), [api]);

  const [items, setItems] = useState([]);

  const load = async () => {
    try {
      if (!employeeId) return;
      const list = await sales.getReviews(employeeId);
      const arr = Array.isArray(list) ? list : (list?.items || []);
      // Map API review -> FeedbackItem shape
      const mapped = arr.map(r => ({
        id: r.review_id,
        title: `Manager Review #${r.review_id}`,
        body: r.review_text,
        createdAt: r.review_date,
        read: true // no ack mechanism provided in new API
      }));
      setItems(mapped);
    } catch (e) {
      error?.(e.message || 'Failed to load reviews');
      setItems([]);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const ack = () => {}; // Acknowledge disabled for new reviews API

  return (
  <PageSection title="Manager Reviews">
      {!items.length ? (
        <EmptyState title="No feedback yet" />
      ) : (
        <FeedbackList items={items} onAcknowledge={ack} />
      )}
    </PageSection>
  );
}
