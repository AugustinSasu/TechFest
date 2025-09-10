import ApiClient from './ApiClient';

/**
 * Sales (self) endpoints for the logged-in agent.
 */
export default class SalesService {
  /** @param {ApiClient} api */
  constructor(api) { this.api = api; }

  /** All endpoints now require employeeId */
  getSummary(employeeId, params) {
    return this.api.get(`/employees/${encodeURIComponent(employeeId)}/summary`, params);
  }

  getSales(employeeId, params) {
    return this.api.get(`/sale-orders/filter`, {...params, "employee_id": employeeId});
  }

  getAchievements(employeeId) {
    return this.api.get(`/employees/${encodeURIComponent(employeeId)}/achievements`);
  }

  getFeedback(employeeId) {
    return this.api.get(`/employees/${encodeURIComponent(employeeId)}/feedback`);
  }

  ackFeedback(employeeId, id) {
    return this.api.post(`/employees/${encodeURIComponent(employeeId)}/feedback/${encodeURIComponent(id)}/ack`);
  }
}

export function createSalesService(api) {
  return new SalesService(api);
}
