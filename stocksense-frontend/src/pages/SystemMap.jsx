import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import {
  Database, Server, MonitorSmartphone, FileSpreadsheet, BarChart3,
  BrainCircuit, ArrowRight, ArrowDown, Cloud, Boxes, Zap, Cable,
  CheckCircle2, XCircle, Layers, Globe, Code2, ChevronRight
} from 'lucide-react';

const integrations = [
  {
    id: 'erpnext',
    name: 'ERPNext (ERP)',
    icon: Boxes,
    color: '#3b82f6',
    desc: 'Core ERP system running in Docker. Manages inventory, sales, purchases, warehouses.',
    tech: 'Frappe Framework · Docker · MariaDB',
    status: 'connected',
    position: 'center',
  },
  {
    id: 'mariadb',
    name: 'MariaDB',
    icon: Database,
    color: '#06b6d4',
    desc: 'ERPNext database — direct SQL access for analytics, queries, and real-time data extraction.',
    tech: 'Port 3306 · pymysql · SQLAlchemy',
    status: 'connected',
    position: 'center',
  },
  {
    id: 'python',
    name: 'Python Analytics',
    icon: Code2,
    color: '#10b981',
    desc: 'Data pipeline — extraction, NLP query engine, ML demand forecasting, anomaly detection via Z-Score.',
    tech: 'Flask API · pandas · scikit-learn',
    status: 'connected',
    position: 'right',
  },
  {
    id: 'react',
    name: 'React Dashboard',
    icon: MonitorSmartphone,
    color: '#8b5cf6',
    desc: 'This premium frontend — real-time charts, metrics, inventory table, AI chat.',
    tech: 'React 19 · Vite · Tailwind v4 · Recharts',
    status: 'connected',
    position: 'right',
  },
  {
    id: 'excel',
    name: 'Excel VBA Automation',
    icon: FileSpreadsheet,
    color: '#22c55e',
    desc: 'Warehouse_Automation.xlsm — auto-syncs stock data to/from ERPNext via REST API calls.',
    tech: 'VBA · ERPNext REST API · Power Query',
    status: 'connected',
    position: 'left',
  },
  {
    id: 'gsheets',
    name: 'Google Sheets',
    icon: Globe,
    color: '#f59e0b',
    desc: 'Apps Script automation — pulls live data from ERPNext API, custom reports, shared dashboards.',
    tech: 'Google Apps Script · UrlFetchApp · JSON',
    status: 'connected',
    position: 'left',
  },
  {
    id: 'powerbi',
    name: 'Power BI',
    icon: BarChart3,
    color: '#ec4899',
    desc: 'StockSense_Phase1.pbix — Power Query M-queries connect to MariaDB for visual dashboards.',
    tech: '7 M-Queries · DirectQuery · DAX',
    status: 'connected',
    position: 'left',
  },
  {
    id: 'sql',
    name: 'SQL Analytics',
    icon: Layers,
    color: '#14b8a6',
    desc: '4 optimized SQL queries — current stock, low stock alerts, sales summary, stock ledger.',
    tech: 'current_stock · low_stock · sales_order · ledger',
    status: 'connected',
    position: 'right',
  },
  {
    id: 'ml',
    name: 'ML Engine',
    icon: BrainCircuit,
    color: '#a855f7',
    desc: 'Gradient Boosting demand forecast + Z-Score anomaly detection on stock movement patterns.',
    tech: 'demand_forecast.py · anomaly_detection.py',
    status: 'connected',
    position: 'right',
  },
];

const dataFlows = [
  { from: 'ERPNext', to: 'MariaDB', label: 'Stores data', color: '#3b82f6' },
  { from: 'MariaDB', to: 'Python API', label: 'SQL queries', color: '#06b6d4' },
  { from: 'Python API', to: 'React Dashboard', label: 'REST JSON', color: '#10b981' },
  { from: 'MariaDB', to: 'Power BI', label: 'M-Queries', color: '#ec4899' },
  { from: 'ERPNext', to: 'Excel VBA', label: 'REST API', color: '#22c55e' },
  { from: 'ERPNext', to: 'Google Sheets', label: 'REST API', color: '#f59e0b' },
  { from: 'MariaDB', to: 'SQL Analytics', label: 'Direct SQL', color: '#14b8a6' },
  { from: 'Python API', to: 'ML Engine', label: 'Predictions', color: '#a855f7' },
];

const powerQueryDetails = [
  { name: 'current_stock.m', desc: 'Live stock levels from tabBin' },
  { name: 'low_stock_items.m', desc: 'Items below reorder level' },
  { name: 'sales_order_summary.m', desc: 'Monthly sales aggregation' },
  { name: 'stock_ledger_recent.m', desc: 'Recent stock movements' },
  { name: 'forecast_results.m', desc: 'ML demand predictions' },
  { name: 'anomaly_results.m', desc: 'Z-Score anomaly flags' },
  { name: 'multi_source_etl.m', desc: 'Combined ETL pipeline' },
];

export default function SystemMap() {
  const [apiHealth, setApiHealth] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    api.dashboardStats()
      .then(d => setApiHealth(d ? { status: 'ok' } : null))
      .catch(() => setApiHealth(null));
  }, []);

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-1 text-white">
          System Architecture
        </h1>
        <p className="text-muted text-base">How all 9 integrated systems work together in real-time.</p>
      </div>

      {/* Connection Status Strip */}
      <div className="flex flex-wrap gap-3">
        {[
          { name: 'ERPNext', ok: true, port: '8080' },
          { name: 'MariaDB', ok: true, port: '3307' },
          { name: 'Python API', ok: !!apiHealth, port: '5000' },
          { name: 'React UI', ok: true, port: '5173' },
        ].map((s, i) => (
          <div key={i} className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-medium ${
            s.ok ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400' : 'border-rose-500/20 bg-rose-500/5 text-rose-400'
          }`}>
            {s.ok ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
            {s.name}
            <span className="text-muted/60">:{s.port}</span>
          </div>
        ))}
      </div>

      {/* Visual Architecture Diagram */}
      <div className="glass-panel p-8 relative overflow-hidden">
        <h2 className="text-lg font-bold mb-8 flex items-center gap-2 text-white">
          <Cable className="text-accent" size={20} /> Data Flow Architecture
        </h2>

        {/* Architecture Grid - Desktop */}
        <div className="hidden lg:grid grid-cols-[1fr_minmax(80px,auto)_1.5fr_minmax(80px,auto)_1fr] gap-x-4 gap-y-6 items-center w-full">
          {/* Row 1 */}
          <ArchNode icon={FileSpreadsheet} label="Excel VBA" sub="Warehouse_Automation.xlsm" color="#22c55e" onClick={() => setSelectedNode('excel')} />
          <FlowArrow label="REST API" direction="right" color="#22c55e" />
          <div className="row-span-2 h-full flex items-center justify-center relative z-10 w-full">
            <ArchNode icon={Boxes} label="ERPNext (ERP)" sub="Docker · localhost:8080" color="#3b82f6" large onClick={() => setSelectedNode('erpnext')} />
          </div>
          <FlowArrow label="Direct SQL" direction="right" color="#14b8a6" />
          <ArchNode icon={Layers} label="SQL Analytics" sub="4 Optimized Queries" color="#14b8a6" onClick={() => setSelectedNode('sql')} />

          {/* Row 2 */}
          <ArchNode icon={Globe} label="Google Sheets" sub="Apps Script Sync" color="#f59e0b" onClick={() => setSelectedNode('gsheets')} />
          <FlowArrow label="REST API" direction="right" color="#f59e0b" />
          {/* Center is spanned */}
          <FlowArrow label="pymysql" direction="right" color="#10b981" />
          <div className="flex flex-col gap-2 w-full">
            <ArchNode icon={Code2} label="Python API" sub="ai_query_api.py" color="#10b981" onClick={() => setSelectedNode('python')} />
            <div className="pl-6">
              <ArchNode icon={BrainCircuit} label="ML Engine" sub="Forecast + Anomaly" color="#a855f7" small onClick={() => setSelectedNode('ml')} />
            </div>
          </div>

          {/* Row 3 - Connecting Arrow */}
          <div className="col-span-2"></div>
          <div className="flex justify-center -my-2 relative z-0">
            <ArrowDown className="text-muted/30" size={24} />
          </div>
          <div className="col-span-2"></div>

          {/* Row 4 */}
          <ArchNode icon={BarChart3} label="Power BI" sub="7 M-Queries" color="#ec4899" onClick={() => setSelectedNode('powerbi')} />
          <FlowArrow label="M-Query" direction="left" color="#ec4899" />
          <ArchNode icon={Database} label="MariaDB" sub="Port 3307 · ERP Database" color="#06b6d4" large onClick={() => setSelectedNode('mariadb')} />
          <FlowArrow label="JSON API" direction="right" color="#8b5cf6" />
          <ArchNode icon={MonitorSmartphone} label="React UI" sub="Port 5173" color="#8b5cf6" onClick={() => setSelectedNode('react')} />
        </div>

        {/* Mobile Fallback */}
        <div className="lg:hidden flex flex-col items-center justify-center gap-4 py-12 text-center border border-white/[0.05] rounded-xl bg-white/[0.01]">
          <Cable className="text-accent/30" size={48} />
          <p className="text-muted text-sm max-w-xs">Please view on a larger screen to see the interactive architecture diagram.</p>
        </div>
      </div>

      {/* Integration Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {integrations.map((intg, i) => {
          const IconComp = intg.icon;
          return (
            <div
              key={intg.id}
              className="glass-panel p-6 cursor-pointer relative overflow-hidden group hover:border-white/[0.15] hover:bg-white/[0.04] transition-all"
              onClick={() => setSelectedNode(selectedNode === intg.id ? null : intg.id)}
            >
              {/* Glow */}
              <div className="absolute -top-8 -right-8 w-24 h-24 rounded-full blur-[50px] opacity-[0.08] group-hover:opacity-[0.15] transition-opacity duration-500"
                style={{ backgroundColor: intg.color }} />

              <div className="flex items-start gap-4 relative z-10">
                <div className="p-3 rounded-xl border border-white/[0.06] shrink-0"
                  style={{ backgroundColor: intg.color + '15', color: intg.color }}>
                  <IconComp size={22} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-white text-sm">{intg.name}</h3>
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.6)]" />
                  </div>
                  <p className="text-xs text-muted/70 leading-relaxed mb-3">{intg.desc}</p>
                  <div className="flex items-center gap-1.5 text-[10px] font-mono text-muted/50 bg-white/[0.02] px-2 py-1 rounded-md w-fit">
                    <Zap size={10} />
                    {intg.tech}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Data Flow Table */}
      <div className="glass-panel p-8">
        <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
          <Zap className="text-accent" size={20} /> Data Flow Connections
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {dataFlows.map((flow, i) => (
            <div key={i}
              className="flex items-center gap-3 py-3 px-4 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-white/[0.08] transition-colors"
            >
              <span className="text-sm font-medium text-white w-28 shrink-0">{flow.from}</span>
              <div className="flex items-center gap-1 flex-1">
                <div className="h-[1px] flex-1 bg-gradient-to-r from-transparent" style={{ backgroundImage: `linear-gradient(to right, transparent, ${flow.color}40, transparent)` }} />
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full border border-white/[0.06] text-muted whitespace-nowrap">{flow.label}</span>
                <div className="h-[1px] flex-1 bg-gradient-to-r to-transparent" style={{ backgroundImage: `linear-gradient(to right, ${flow.color}40, transparent)` }} />
                <ChevronRight size={12} style={{ color: flow.color }} />
              </div>
              <span className="text-sm font-medium text-white w-28 shrink-0 text-right">{flow.to}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Power Query Details */}
      <div className="glass-panel p-8">
        <h2 className="text-lg font-bold mb-6 flex items-center gap-2 text-white">
          <BarChart3 className="text-pink-400" size={20} /> Power BI — M-Query Pipeline
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {powerQueryDetails.map((pq, i) => (
            <div key={i}
              className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/[0.04]"
            >
              <div className="w-8 h-8 rounded-lg bg-pink-500/10 text-pink-400 flex items-center justify-center shrink-0">
                <FileSpreadsheet size={16} />
              </div>
              <div>
                <p className="text-xs font-mono font-semibold text-white">{pq.name}</p>
                <p className="text-[11px] text-muted">{pq.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// --- Sub-components ---

function ArchNode({ icon: Icon, label, sub, color, large, small, onClick, className = '' }) {
  return (
    <motion.button
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`flex items-center gap-3 w-full text-left rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.06] hover:shadow-lg hover:shadow-[${color}20] transition-all ${
        large ? 'p-4' : small ? 'p-2.5' : 'p-3'
      } ${className}`}
    >
      <div className={`${large ? 'p-3' : 'p-2'} rounded-lg shrink-0`}
        style={{ backgroundColor: color + '15', color }}>
        <Icon size={large ? 22 : small ? 14 : 18} />
      </div>
      <div>
        <p className={`font-semibold text-white ${large ? 'text-sm' : 'text-xs'}`}>{label}</p>
        <p className={`text-muted/60 ${large ? 'text-[11px]' : 'text-[10px]'}`}>{sub}</p>
      </div>
    </motion.button>
  );
}

function FlowArrow({ label, direction, color }) {
  return (
    <div className="flex items-center justify-center w-full px-1">
      {direction === 'left' && <ArrowRight size={14} style={{ color, transform: 'rotate(180deg)' }} className="shrink-0 mr-1" />}
      <div className="h-[1px] flex-1" style={{ background: `linear-gradient(90deg, transparent, ${color}40, transparent)` }} />
      <span className="text-[10px] font-mono px-2 py-0.5 rounded-md border border-white/[0.08] bg-background text-muted shadow-sm whitespace-nowrap mx-1" style={{ color }}>
        {label}
      </span>
      <div className="h-[1px] flex-1" style={{ background: `linear-gradient(90deg, transparent, ${color}40, transparent)` }} />
      {direction === 'right' && <ArrowRight size={14} style={{ color }} className="shrink-0 ml-1" />}
    </div>
  );
}
