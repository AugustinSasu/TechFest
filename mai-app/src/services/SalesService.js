import ApiClient from './ApiClient';

/**
 * Sales (self) endpoints for the logged-in agent.
 */
export default class SalesService {
  /** @param {ApiClient} api */
  constructor(api) {
    this.api = api;
  }

  /** @param {{startDate?:string,endDate?:string}} params */
  getMySummary(params) {
    return this.api.get('/sales/me/summary', params);
  }

  /** @param {{startDate?:string,endDate?:string,granularity?:'day'|'week'|'month'}} params */
  getMyStats(params) {
    return this.api.get('/sales/me/stats', params);
  }

  getAchievements() {
    return this.api.get('/sales/me/achievements');
  }

  getFeedback() {
    return this.api.get('/sales/me/feedback');
  }

  /** @param {string} id */
  ackFeedback(id) {
    return this.api.post(`/sales/me/feedback/${encodeURIComponent(id)}/ack`, null);
  }
}

export function createSalesService(api) {
  return new SalesService(api);
}
