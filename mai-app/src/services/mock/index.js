// src/services/mock/index.js
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

export function isMockEnabled() {
  return USE_MOCKS;
}

const REGIONS = ['North', 'South', 'East', 'West'];
const AGENTS = [
  { id: 'a1', name: 'Alice Johnson', region: 'North' },
  { id: 'a2', name: 'Bob Smith',    region: 'South' },
  { id: 'a3', name: 'Carol Lee',    region: 'East' },
  { id: 'a4', name: 'Dan Brown',    region: 'West' },
  { id: 'a5', name: 'Eva Green',    region: 'North' },
];

const SALES = (() => {
  const arr = [];
  const today = new Date();
  for (let i = 0; i < 120; i++) {
    const agent = AGENTS[Math.floor(Math.random() * AGENTS.length)];
    const amount = Math.round(500 + Math.random() * 5000);
    const d = new Date(today);
    d.setDate(today.getDate() - Math.floor(Math.random() * 60));
    arr.push({
      id: 'S' + (1000 + i),
      agentId: agent.id,
      agentName: agent.name,
      region: agent.region,
      amount,
      date: d.toISOString().slice(0, 10)
    });
  }
  return arr.sort((a, b) => (a.date < b.date ? 1 : -1));
})();

function calcSummary({ startDate, endDate, region } = {}) {
  let rows = SALES;
  if (startDate) rows = rows.filter(s => s.date >= startDate);
  if (endDate) rows = rows.filter(s => s.date <= endDate);
  if (region) rows = rows.filter(s => s.region === region);
  const revenue = rows.reduce((sum, s) => sum + s.amount, 0);
  const deals = rows.length;
  const target = Math.round(revenue * 1.2) || 10000;
  const winRatePct = 45 + Math.round(Math.random() * 20);
  const deltaRevenuePct = -5 + Math.round(Math.random() * 20);
  const trend = [];
  for (let i = 29; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const day = date.toISOString().slice(0, 10);
    const dayTotal = rows.filter(s => s.date === day).reduce((sum, s) => sum + s.amount, 0);
    trend.push(dayTotal);
  }
  return { revenue, target, deals, winRatePct, deltaRevenuePct, trend };
}

function paginate(items, page = 0, pageSize = 10) {
  const start = page * pageSize;
  const end = start + pageSize;
  return { items: items.slice(start, end), total: items.length, page, pageSize };
}

function agentStats() {
  const map = Object.create(null);
  for (const a of AGENTS) map[a.id] = { ...a, revenue: 0, achievementsCount: 0 };
  for (const s of SALES) map[s.agentId].revenue += s.amount;
  for (const id in map) map[id].achievementsCount = Math.floor(Math.random() * 4);
  return Object.values(map);
}

export async function mockRequest(path, { method = 'GET', params = {}, body } = {}) {
  const p = path.startsWith('/') ? path : `/${path}`;

  // ---------- AUTH (folosit doar dacă vrei, AuthProvider moșează oricum login-ul) ----------
  if (p === '/auth/login' && method === 'POST') {
    const email = typeof body === 'string' ? body : body?.email || 'user@example.com';
    const role = email.toLowerCase().includes('manager') ? 'manager' : 'salesman';
    const user = { id: 'u-' + role, name: role === 'manager' ? 'Manager Mia' : 'Sales Sam', email, role };
    return { token: 'mock-token-' + role, user };
  }

  // ---------- MANAGER ----------
  if (p === '/manager/sales/summary') {
    return calcSummary(params || {});
  }
  if (p === '/manager/sales') {
    let rows = SALES;
    const { query, startDate, endDate, region } = params || {};
    if (startDate) rows = rows.filter(s => s.date >= startDate);
    if (endDate) rows = rows.filter(s => s.date <= endDate);
    if (region) rows = rows.filter(s => s.region === region);
    if (query) {
      const q = String(query).toLowerCase();
      rows = rows.filter(s =>
        String(s.id).toLowerCase().includes(q) || String(s.agentName).toLowerCase().includes(q)
      );
    }
    return paginate(rows, Number(params?.page) || 0, Number(params?.pageSize) || 10);
  }
  if (p === '/manager/agents') {
    const rows = agentStats();
    return paginate(rows, Number(params?.page) || 0, Number(params?.pageSize) || 10);
  }
  if (p.startsWith('/manager/agents/')) {
    const id = decodeURIComponent(p.split('/').pop());
    const agent = AGENTS.find(a => a.id === id) || agentStats()[0];
    const achievements = [
      { id: 'ach1', tier: 'bronze', label: 'First 10k', points: 1000, earnedAt: new Date().toISOString() },
      { id: 'ach2', tier: 'silver', label: '25k Club', points: 2500, earnedAt: new Date(Date.now() - 86400000 * 10).toISOString() },
    ];
    const feedback = [
      { id: 'f1', title: 'Improve follow-ups', body: 'Call leads within 24h.', createdAt: new Date().toISOString(), read: false },
      { id: 'f2', title: 'Great job on Q2', body: 'Keep the momentum!', createdAt: new Date(Date.now() - 86400000 * 3).toISOString(), read: true },
    ];
    return { agent, achievements, feedback };
  }
  if (p === '/manager/prompts') {
    return [
      { id: 'p1', label: 'Top underperforming regions', prompt: 'List the bottom 3 regions by revenue this month.' },
      { id: 'p2', label: 'Agent coaching tips', prompt: 'Suggest coaching tips for low win-rate agents.' },
      { id: 'p3', label: 'Pipeline risks', prompt: 'Identify risks in current pipeline and mitigation actions.' },
    ];
  }

  // ---------- SALES (self) ----------
  if (p === '/sales/me/summary') {
    return calcSummary(params || {});
  }
  if (p === '/sales/me/stats') {
    const trend = [], target = [];
    for (let i = 11; i >= 0; i--) {
      const v = Math.round(3000 + Math.random() * 4000);
      trend.push(v);
      target.push(Math.round(v * 1.1));
    }
    return { trend, target };
  }
  if (p === '/sales/me/improvements') {
    return [
      { id: 'i1', title: 'Follow up faster', description: 'Reduce response time to new leads to under 2 hours.', createdAt: new Date().toISOString(), done: false },
      { id: 'i2', title: 'Upsell add-ons', description: 'Offer premium support in all demos this week.', createdAt: new Date(Date.now() - 86400000).toISOString(), done: false },
    ];
  }
  if (p.startsWith('/sales/me/improvements/')) {
    return { ok: true };
  }
  if (p === '/sales/me/achievements') {
    return [
      { id: 'a1', tier: 'bronze', label: 'First 10k', points: 1000, earnedAt: new Date(Date.now() - 86400000 * 20).toISOString() },
      { id: 'a2', tier: 'silver', label: '25k Club', points: 2500, earnedAt: new Date(Date.now() - 86400000 * 5).toISOString() },
    ];
  }
  if (p === '/sales/me/feedback') {
    return [
      { id: 'fb1', title: 'Great demo!', body: 'You handled objections well. Keep it up.', createdAt: new Date(Date.now() - 86400000 * 2).toISOString(), read: false },
      { id: 'fb2', title: 'Try discovery questions', body: 'Ask 3 extra discovery questions in next calls.', createdAt: new Date(Date.now() - 86400000 * 7).toISOString(), read: true },
    ];
  }
  if (p.startsWith('/sales/me/feedback/') && p.endsWith('/ack')) {
    return { ok: true };
  }

  // ---------- Chat ----------
  if (p === '/chat') {
    const prompt = typeof body === 'string' ? body : body?.prompt || '';
    return {
      content: `AI (mock): I received your prompt: "${prompt}".\n• Idea 1\n• Idea 2\n• Idea 3`
    };
  }

  // default
  return { ok: true };
}
