const API_BASE = 'http://localhost:5000';

export async function fetchJson(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`[API] ${endpoint} failed:`, err.message);
    return null;
  }
}

export const api = {
  dashboardStats: () => fetchJson('/api/dashboard/stats'),
  dashboardStock: () => fetchJson('/api/dashboard/stock'),
  dashboardActivity: () => fetchJson('/api/dashboard/activity'),
  dashboardTopItems: () => fetchJson('/api/dashboard/top-items'),
  dashboardHealthRing: () => fetchJson('/api/dashboard/health-ring'),
  dashboardSummary: () => fetchJson('/api/dashboard/summary'),
  dashboardWarehouses: () => fetchJson('/api/dashboard/warehouses'),
  forecasts: () => fetchJson('/api/forecasts'),
  anomalies: () => fetchJson('/api/anomalies'),
  ask: async (question) => {
    try {
      const res = await fetch(`${API_BASE}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      return await res.json();
    } catch (err) {
      return { error: 'Server not reachable. Start ai_query_api.py first.' };
    }
  }
};
