import ApiClient from './ApiClient';

/**
 * Manager endpoints (team-wide data).
 * All methods return JSON as provided by your backend.
 */
export default class ManagerService {
  /** @param {ApiClient} api */
  constructor(api) {
    this.api = api;
  }

  /** @param {{startDate?:string,endDate?:string,region?:string}} params */
  getSalesSummary(params) {
    return this.api.get('/manager/sales/summary', params);
  }

  /** @param {{page?:number,pageSize?:number,query?:string,startDate?:string,endDate?:string,region?:string}} params */
  getSalesList(params) {
    return this.api.get('/manager/sales', params);
  }

  /** @param {{page?:number,pageSize?:number,region?:string}} params */
  getAgents(params) {
    return this.api.get('/manager/agents', params);
  }

  /** @param {string} agentId */
  getAgentDetails(agentId) {
    return this.api.get(`/manager/agents/${encodeURIComponent(agentId)}`);
  }

  getPresetPrompts() {
    return this.api.get('/manager/prompts');
  }

  /** @param {{agentId:string,title:string,body:string}} payload */
  createFeedback(payload) {
    return this.api.post('/manager/feedback', payload);
  }
}

export function createManagerService(api) {
  return new ManagerService(api);
}
