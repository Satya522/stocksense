import {
  AlertTriangle,
  Boxes,
  Bot,
  ChartNoAxesCombined,
  Home,
  Map,
  Menu,
} from 'lucide-react';
import '../index.css';

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: Home },
  { id: 'inventory', label: 'Inventory', icon: Boxes },
  { id: 'forecasts', label: 'Forecasts', icon: ChartNoAxesCombined },
  { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
  { id: 'system', label: 'System Map', icon: Map },
  { id: 'chat', label: 'AI Chat', icon: Bot },
];

export default function Sidebar({ activeTab, setActiveTab, isCollapsed, toggleSidebar }) {
  return (
    <aside className="stocksense-sidebar" aria-label="StockSense navigation">
      <div className="stocksense-sidebar__header">
        <div className="stocksense-brand" onClick={() => setActiveTab('dashboard')} title="StockSense Dashboard">
          <span className="stocksense-brand__mark">SS</span>
          {!isCollapsed && (
            <span className="stocksense-brand__copy">
              <strong>StockSense</strong>
              <small>COMMAND CENTER</small>
            </span>
          )}
        </div>
        
        <button className="sidebar-toggle" onClick={toggleSidebar} aria-label="Toggle Sidebar">
          <Menu size={18} />
        </button>
      </div>

      <nav className="stocksense-nav">
        {TABS.map(({ id, label, icon: Icon }) => {
          const active = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`stocksense-nav__item${active ? ' is-active' : ''}`}
              title={isCollapsed ? label : undefined}
            >
              <Icon size={16} strokeWidth={1.8} className="nav-icon" />
              {!isCollapsed && <span>{label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="stocksense-sidebar__status">
        <span className="stocksense-status-dot" title="ERPNext connected" />
        {!isCollapsed && (
          <div>
            <strong>ERPNext connected</strong>
            <span>Live operational data</span>
          </div>
        )}
      </div>
    </aside>
  );
}
