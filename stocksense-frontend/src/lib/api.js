const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

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
  addItem: async (item) => {
    try {
      const res = await fetch(`${API_BASE}/api/inventory/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      });
      return await res.json();
    } catch (err) {
      return { success: false, error: err.message };
    }
  },
  updateItem: async (item) => {
    try {
      const res = await fetch(`${API_BASE}/api/inventory/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      });
      return await res.json();
    } catch (err) {
      return { success: false, error: err.message };
    }
  },
  deleteItem: async (item) => {
    try {
      const res = await fetch(`${API_BASE}/api/inventory/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      });
      return await res.json();
    } catch (err) {
      return { success: false, error: err.message };
    }
  },
  createReorder: async (order) => {
    try {
      const res = await fetch(`${API_BASE}/api/reorder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(order),
      });
      return await res.json();
    } catch (err) {
      return { success: false, error: err.message };
    }
  },
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
