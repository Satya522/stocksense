import { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Box,
  IndianRupee,
  ShoppingCart,
  RefreshCw,
  Activity,
  Database,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { api } from '../lib/api';
import '../index.css';

/* ── Constants ── */

const HEALTH_COLORS = {
  Healthy: '#2DD4BF',
  Warning: '#F5A623',
  Critical: '#F5455C',
};

const METRIC_TONES = {
  blue: { icon: Box, color: '#4F8EF7', bg: 'rgba(79,142,247,0.15)' },
  teal: { icon: IndianRupee, color: '#2DD4BF', bg: 'rgba(45,212,191,0.15)' },
  amber: { icon: AlertTriangle, color: '#F5A623', bg: 'rgba(245,166,35,0.15)' },
  violet: { icon: ShoppingCart, color: '#7C5CFF', bg: 'rgba(124,92,255,0.15)' },
};

/* ── Helpers ── */

function formatIndianNumber(value) {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'string') return value;
  return new Intl.NumberFormat('en-IN').format(value);
}

function formatCurrency(value) {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'string' && (value.includes('Cr') || value.includes('₹') || value.includes('L') || value.includes('K'))) {
    return value;
  }
  const raw = String(value).replace(/[₹,L\s]/g, '');
  const num = parseFloat(raw);
  if (isNaN(num)) return String(value);
  if (num >= 10000000) return `₹${(num / 10000000).toLocaleString('en-IN', { maximumFractionDigits: 1 })} Cr`;
  if (num >= 100000) return `₹${(num / 100000).toFixed(1)}L`;
  if (num >= 1000) return `₹${new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(num)}`;
  return `₹${num}`;
}

function formatCompact(value) {
  if (value === null || value === undefined) return '';
  const num = Number(value);
  if (num >= 1000) {
    const k = num / 1000;
    return k % 1 === 0 ? `${k}K` : `${k.toFixed(1)}K`;
  }
  return String(num);
}

function cleanItemName(name) {
  // Strip 'SK ' prefix and common long suffixes for chart labels
  let clean = String(name ?? '')
    .replace(/^SK\s+/i, '')
    .replace(/^SK-/i, '');
  return clean.length > 12 ? clean.slice(0, 12) + '...' : clean;
}

function formatTimeDiff(dateStr) {
  if (!dateStr) return '';
  const now = new Date();
  const then = new Date(dateStr);
  const diffMs = now - then;
  const diffHrs = Math.floor(diffMs / 3600000);
  if (diffHrs < 1) return 'Just now';
  if (diffHrs < 24) return `${diffHrs}h ago`;
  return `${Math.floor(diffHrs / 24)}d ago`;
}

/* ── Sub-components ── */

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="ss-chart-tooltip">
      <span className="ss-chart-tooltip__label">{label}</span>
      <strong>{formatIndianNumber(payload[0]?.value)}</strong>
    </div>
  );
}

function MetricCard({ label, value, subtitle, tone, valueKind = 'number' }) {
  const toneConfig = METRIC_TONES[tone];
  const Icon = toneConfig.icon;
  const displayValue = valueKind === 'currency' ? formatCurrency(value) : formatIndianNumber(value);

  return (
    <article className="ss-metric" aria-label={label}>
      <div className="ss-metric__top">
        <span className="ss-kicker">{label}</span>
        <span
          className="ss-metric__icon"
          style={{ color: toneConfig.color, background: toneConfig.bg }}
          aria-hidden="true"
        >
          <Icon size={17} strokeWidth={2} />
        </span>
      </div>
      <div className="ss-metric__value">{displayValue}</div>
      <div className="ss-metric__subtitle">{subtitle}</div>
    </article>
  );
}

function InventoryHealth({ data }) {
  const total = data.reduce((sum, item) => sum + Number(item.value || 0), 0);
  const healthy = data.find((item) => item.name === 'Healthy')?.value ?? 0;
  const healthyPct = total ? ((healthy / total) * 100).toFixed(1) : '0.0';
  const getWidth = (value) => `${total ? (Number(value || 0) / total) * 100 : 0}%`;

  return (
    <article className="ss-section ss-health" aria-label="Inventory Health">
      <div className="ss-section__head">
        <div>
          <span className="ss-kicker">INVENTORY HEALTH</span>
          <h2>Operational condition</h2>
        </div>
        <div className="ss-live"><span /> LIVE</div>
      </div>

      <div className="ss-health__hero">
        <div>
          <div className="ss-health__total">{formatIndianNumber(total)}</div>
          <div className="ss-meta-label">WAREHOUSE ALLOCATIONS (BINS)</div>
        </div>
        <div className="ss-health__score">
          <strong>{healthyPct}%</strong>
          <span>healthy inventory</span>
        </div>
      </div>

      <div className="ss-health__bar" aria-label={`Healthy ${healthyPct}%`}>
        {data.map((item) => (
          <span
            key={item.name}
            className={`ss-health__segment ss-health__segment--${item.name.toLowerCase()}`}
            style={{ width: getWidth(item.value) }}
          />
        ))}
      </div>

      <div className="ss-health__rows">
        {data.map((item) => {
          const pct = total ? ((Number(item.value || 0) / total) * 100).toFixed(1) : '0.0';
          const color = HEALTH_COLORS[item.name] || '#5C6274';
          return (
            <div className="ss-health__row" key={item.name}>
              <div className="ss-health__state">
                <span className="ss-health__dot" style={{ background: color }} />
                <span>{item.name}</span>
              </div>
              <strong>{formatIndianNumber(item.value)}</strong>
              <span>{pct}%</span>
            </div>
          );
        })}
      </div>
    </article>
  );
}

function TopItemsChart({ data }) {
  const normalized = data.map((item) => ({
    ...item,
    shortName: cleanItemName(item.name),
    quantity: item.value || item.quantity || 0,
  }));

  return (
    <article className="ss-section ss-chart" aria-label="Top Items by Quantity">
      <div className="ss-section__head">
        <div>
          <span className="ss-kicker">TOP ITEMS BY QUANTITY</span>
          <h2>Highest-volume inventory</h2>
        </div>
        <span className="ss-chart__meta">Top {normalized.length}</span>
      </div>

      <div className="ss-chart__frame">
        {normalized.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={normalized} margin={{ top: 18, right: 8, left: 4, bottom: 62 }}>
              <defs>
                <linearGradient id="stocksenseBarGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8F79FF" />
                  <stop offset="100%" stopColor="#5D46BC" />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.04)" />
              <XAxis
                dataKey="shortName"
                angle={-40}
                textAnchor="end"
                height={55}
                tick={{ fill: '#9BA1B0', fontSize: 9, fontWeight: 500 }}
                axisLine={false}
                tickLine={false}
                interval={0}
              />
              <YAxis
                tick={{ fill: '#9BA1B0', fontSize: 9 }}
                axisLine={false}
                tickLine={false}
                width={48}
                tickFormatter={(value) => formatCompact(value)}
                domain={[0, 'auto']}
              />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} content={<CustomTooltip />} />
              <Bar
                dataKey="quantity"
                fill="url(#stocksenseBarGradient)"
                radius={[7, 7, 2, 2]}
                maxBarSize={58}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="ss-empty">No chart data — start API server</div>
        )}
      </div>
    </article>
  );
}

function AISummary({ totalItems, stockValue, text }) {
  return (
    <article className="ss-section ss-summary" aria-label="AI Summary">
      <div className="ss-section__head">
        <div>
          <span className="ss-kicker">AI SUMMARY</span>
          <h2>Decision snapshot</h2>
        </div>
        <span className="ss-mono-badge">LIVE MODEL</span>
      </div>
      <div className="ss-summary__grid" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: '16px' }}>
        <div>
          <span className="ss-mono-label">CATALOG_SKUS / INVENTORY</span>
          <strong>{formatIndianNumber(totalItems)} Items</strong>
        </div>
        <div>
          <span className="ss-mono-label">total_stock_value</span>
          <strong>{formatCurrency(stockValue)}</strong>
        </div>
      </div>
      <div className="ss-summary__content" style={{ fontSize: '13px', lineHeight: '1.6', color: 'rgba(255,255,255,0.85)', background: 'rgba(255,255,255,0.02)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
        {text ? <p style={{ margin: 0 }}>{text}</p> : <div className="ss-empty">No AI insights generated yet.</div>}
      </div>
    </article>
  );
}

function RecentActivity({ data }) {
  return (
    <article className="ss-section ss-activity" aria-label="Recent Activity">
      <div className="ss-section__head">
        <div>
          <span className="ss-kicker">RECENT ACTIVITY</span>
          <h2>Latest inventory events</h2>
        </div>
        <span className="ss-chart__meta">{data.length} updates</span>
      </div>
      <div className="ss-activity__list">
        {data.length ? data.slice(0, 20).map((item, index) => (
          <div className="ss-activity__row" key={`${item.title || item.item_code}-${index}`}>
            <div>
              <strong>{item.title || item.item_name || item.item_code}</strong>
              <span>{item.meta || `${item.voucher_type || ''} · ${formatTimeDiff(item.posting_date)}`}</span>
            </div>
            <b className={Number(item.value ?? item.qty_change) < 0 ? 'is-negative' : 'is-positive'}>
              {Number(item.value ?? item.qty_change) > 0 ? '+' : ''}{formatIndianNumber(item.value ?? item.qty_change)}
            </b>
          </div>
        )) : (
          <div className="ss-empty">No recent activity</div>
        )}
      </div>
    </article>
  );
}

/* ── Main Dashboard with live API data ── */

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [summary, setSummary] = useState(null);
  const [topItems, setTopItems] = useState([]);
  const [activity, setActivity] = useState([]);
  const [healthRing, setHealthRing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastSync, setLastSync] = useState(null);

  const loadData = async () => {
    setLoading(true);
    const [statsData, summaryData, topData, activityData, healthData] = await Promise.all([
      api.dashboardStats(),
      api.dashboardSummary(),
      api.dashboardTopItems(),
      api.dashboardActivity(),
      api.dashboardHealthRing(),
    ]);

    if (statsData) setStats(statsData);
    if (summaryData) setSummary(summaryData.summary);
    if (topData) setTopItems(topData.data || []);
    if (activityData) setActivity(activityData.data || []);
    if (healthData) setHealthRing(healthData);
    setLastSync(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }));
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  /* Map API health data to the visual component format */
  const healthData = healthRing
    ? [
        { name: 'Healthy', value: healthRing.healthy },
        { name: 'Warning', value: healthRing.warning },
        { name: 'Critical', value: healthRing.critical },
      ]
    : [
        { name: 'Healthy', value: 0 },
        { name: 'Warning', value: 0 },
        { name: 'Critical', value: 0 },
      ];

  /* Map top items for chart */
  const chartData = topItems.map(item => ({
    name: item.name || item.item_name || '',
    quantity: item.value || item.quantity || 0,
  }));

  return (
    <main className="stocksense-page">
      <div className="stocksense-content">

        {/* Header */}
        <header className="ss-header">
          <div>
            <span className="ss-eyebrow">01 · OPERATIONS / DASHBOARD</span>
            <h1>Command Center</h1>
            <p>A live view of inventory health, stock value, and operational movement.</p>
          </div>
          <div className="ss-header__actions">
            <span>Synced {lastSync || '—'}</span>
            <button className="ss-refresh" type="button" onClick={loadData}>
              <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
            </button>
          </div>
        </header>

        {/* Metrics Rail */}
        <section className="ss-metrics" aria-label="Key metrics">
          <MetricCard label="TOTAL ITEMS" value={stats?.total_items} tone="blue" subtitle="Across active catalog" />
          <MetricCard label="STOCK VALUE" value={stats?.total_value} tone="teal" subtitle="Current valuation" valueKind="currency" />
          <MetricCard label="LOW STOCK ALERTS" value={stats?.low_stock_alerts} tone="amber" subtitle="Needs attention" />
          <MetricCard label="ORDERS THIS MONTH" value={stats?.orders_this_month} tone="violet" subtitle="Sales + Purchase orders" />
        </section>

        {/* Workspace: Health + Chart */}
        <section className="ss-workspace">
          <InventoryHealth data={healthData} />
          <TopItemsChart data={chartData} />
        </section>

        {/* Bottom: AI Summary + Activity */}
        <section className="ss-bottom-grid">
          <AISummary
            totalItems={stats?.total_items}
            stockValue={stats?.total_value}
            text={summary}
          />
          <RecentActivity data={activity} />
        </section>

      </div>

      {/* Footer (outside content wrapper to span full width) */}
      <footer className="ss-footer">
        <Activity size={13} />
        <span>Operational telemetry</span>
        <span className="ss-footer__divider" />
        <Database size={13} />
        <span>ERPNext data source</span>
      </footer>
    </main>
  );
}
