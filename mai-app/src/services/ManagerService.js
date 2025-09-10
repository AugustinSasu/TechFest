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
    return this.api.get('/sale-orders/trends', params);
  }

  /** @param {{page?:number,pageSize?:number,query?:string,startDate?:string,endDate?:string,region?:string}} params */
  getSalesList(params) {
    // Nou requirement corectat: pentru tabel folosim endpoint:
    //   GET /sale-orders/filter?start-date=YYYY-MM-DD&end-date=YYYY-MM-DD
    // și NU trimitem granularitatea (rămâne doar pentru summary/trends).
    // Păstrăm fallback la vechiul endpoint dacă lipsesc datele.
    const p = params || {};
    const startDate = p['start_date'] || p.startDate;
    const endDate = p['end_date'] || p.endDate;
    if (startDate && endDate) {
      // Excludem duplicatele și granularitatea din query (nu e nevoie pentru listă)
      const { ['start-date']: _sd, ['end-date']: _ed, startDate: _sds, endDate: _eds, granulatie, granularity, ...rest } = p;
      return this.api.get('/sale-orders/filter', { 'start-date': startDate, 'end-date': endDate, ...rest });
    }
    // fallback vechi comportament
    return this.api.get('/sale-orders/stats', params);
  }

  /** Get single sale order detail by id */
  // Detaliile individuale / dealership / employee nu mai sunt necesare pentru tabelul simplificat.

  /** @param {{page?:number,pageSize?:number,region?:string}} params */
  getAgents(params) {
    return this.api.get('/employees', params);
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
