import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, ShieldAlert, Clock, CheckCircle2, Check, RefreshCw } from 'lucide-react';
import { api } from '../lib/api';

const DEFAULT_ANOMALIES = [
  { id: 'anom-1', item: 'Raspberry Pi 4', code: 'SKU002', type: 'Sudden Drop', severity: 'critical', message: 'Stock dropped by 85% in 2 days without a matching sales order.', time: '2 hours ago' },
  { id: 'anom-2', item: 'OLED Display 0.96"', code: 'SKU009', type: 'Below Safety', severity: 'critical', message: 'Current qty (5) is 67% below the safety stock level (15).', time: '4 hours ago' },
  { id: 'anom-3', item: 'Servo Motor SG90', code: 'SKU004', type: 'Demand Spike', severity: 'warning', message: 'Forecasted demand (85 units) is 3x higher than the 30-day average.', time: '6 hours ago' },
  { id: 'anom-4', item: '16x2 LCD Display', code: 'SKU006', type: 'Below Safety', severity: 'critical', message: 'Current qty (12) is 52% below the safety stock level (25).', time: '8 hours ago' },
  { id: 'anom-5', item: 'Stepper Motor NEMA17', code: 'SKU010', type: 'Slow Moving', severity: 'info', message: 'No stock movement in the last 14 days. Consider promotional pricing.', time: '12 hours ago' },
  { id: 'anom-6', item: 'Arduino Uno R3', code: 'SKU001', type: 'Demand Spike', severity: 'warning', message: 'Incoming purchase orders suggest a 2.5x surge next week.', time: '1 day ago' },
];

const severityConfig = {
  critical: { bg: 'bg-rose-500/10', border: 'border-rose-500/20', icon: ShieldAlert, iconColor: 'text-rose-400', badge: 'bg-rose-500/20 text-rose-400' },
  warning: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: AlertTriangle, iconColor: 'text-amber-400', badge: 'bg-amber-500/20 text-amber-400' },
  info: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', icon: Clock, iconColor: 'text-blue-400', badge: 'bg-blue-500/20 text-blue-400' },
};

export default function Anomalies() {
  const [anomalyList, setAnomalyList] = useState(DEFAULT_ANOMALIES);
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [resolvedIds, setResolvedIds] = useState(new Set());
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchAnomalies = async () => {
    setIsRefreshing(true);
    try {
      const res = await api.anomalies();
      if (res && Array.isArray(res.data) && res.data.length > 0) {
        const mapped = res.data.map((item, idx) => {
          const z = Math.abs(Number(item.z_score) || 0);
          const sev = z >= 3 ? 'critical' : z >= 2 ? 'warning' : 'info';
          return {
            id: `api-anom-${idx}`,
            item: item.item_code || 'Unknown Item',
            code: item.warehouse ? `${item.item_code} (${item.warehouse})` : item.item_code,
            type: item.anomaly_type || 'Z-Score Anomaly',
            severity: sev,
            message: item.voucher_no
              ? `Voucher ${item.voucher_no} (${item.voucher_type}) moved ${item.actual_qty} units (Z: ${z.toFixed(2)}).`
              : `Irregular movement of ${item.actual_qty || 0} units recorded on ${item.posting_date || 'recent date'}.`,
            time: item.posting_date || 'Recent'
          };
        });
        setAnomalyList(mapped);
      }
    } catch {
      // Keep DEFAULT_ANOMALIES as graceful fallback
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
  }, []);

  const handleResolve = (id) => {
    setResolvedIds(prev => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  };

  const activeAnomalies = anomalyList.filter(a => !resolvedIds.has(a.id));
  const displayedAnomalies = filterSeverity === 'all'
    ? activeAnomalies
    : activeAnomalies.filter(a => a.severity === filterSeverity);

  const criticalCount = activeAnomalies.filter(a => a.severity === 'critical').length;
  const warningCount = activeAnomalies.filter(a => a.severity === 'warning').length;
  const infoCount = activeAnomalies.filter(a => a.severity === 'info').length;

  return (
    <div className="flex flex-col gap-8 max-w-7xl font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <motion.h1 initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-4xl font-bold tracking-tight mb-1">
            Anomaly Detection
          </motion.h1>
          <p className="text-muted text-base">Z-Score & IQR anomaly detection flags unusual patterns in your stock movement.</p>
        </div>
        <button
          onClick={fetchAnomalies}
          disabled={isRefreshing}
          className="self-start sm:self-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] text-sm font-medium transition-all"
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
          <span>Refresh Scan</span>
        </button>
      </div>

      {/* Summary strip & Filter chips */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="flex flex-wrap gap-4">
          <div className="glass-panel px-5 py-3 flex items-center gap-3">
            <ShieldAlert size={18} className="text-rose-400" />
            <span className="text-sm"><span className="font-bold text-white">{criticalCount}</span> <span className="text-muted">Critical</span></span>
          </div>
          <div className="glass-panel px-5 py-3 flex items-center gap-3">
            <AlertTriangle size={18} className="text-amber-400" />
            <span className="text-sm"><span className="font-bold text-white">{warningCount}</span> <span className="text-muted">Warning</span></span>
          </div>
          <div className="glass-panel px-5 py-3 flex items-center gap-3">
            <CheckCircle2 size={18} className="text-emerald-400" />
            <span className="text-sm"><span className="font-bold text-white">{resolvedIds.size}</span> <span className="text-muted">Resolved</span></span>
          </div>
        </motion.div>

        {/* Severity Filter */}
        <div className="flex items-center gap-2 bg-white/[0.02] border border-white/[0.06] p-1 rounded-xl text-xs font-semibold">
          {['all', 'critical', 'warning', 'info'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                filterSeverity === sev
                  ? 'bg-white/10 text-white shadow-sm'
                  : 'text-white/40 hover:text-white/80'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Anomaly cards */}
      <div className="flex flex-col gap-4">
        <AnimatePresence>
          {displayedAnomalies.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-panel p-10 flex flex-col items-center justify-center text-center gap-3"
            >
              <CheckCircle2 size={36} className="text-emerald-400" />
              <p className="text-white font-semibold">All anomalies in this category are resolved or healthy!</p>
              <span className="text-xs text-muted">Stock movements are currently aligned with normal velocity limits.</span>
            </motion.div>
          ) : (
            displayedAnomalies.map((anomaly, i) => {
              const cfg = severityConfig[anomaly.severity] || severityConfig.warning;
              const IconComp = cfg.icon;
              return (
                <motion.div
                  key={anomaly.id}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: 0.05 + i * 0.04 }}
                  className={`glass-panel p-6 border ${cfg.border} relative overflow-hidden group`}
                >
                  {/* Severity glow */}
                  <div className={`absolute -left-4 top-1/2 -translate-y-1/2 w-20 h-20 ${anomaly.severity === 'critical' ? 'bg-rose-500' : anomaly.severity === 'warning' ? 'bg-amber-500' : 'bg-blue-500'} blur-[50px] opacity-[0.08]`} />

                  <div className="flex items-start justify-between gap-4 relative z-10">
                    <div className="flex items-start gap-4 flex-1 min-w-0">
                      <div className={`p-2.5 rounded-xl ${cfg.bg} ${cfg.iconColor} shrink-0`}>
                        <IconComp size={20} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-3 mb-1.5">
                          <h3 className="font-semibold text-white">{anomaly.item}</h3>
                          <span className="text-xs font-mono text-muted">{anomaly.code}</span>
                          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${cfg.badge}`}>
                            {anomaly.type}
                          </span>
                        </div>
                        <p className="text-sm text-muted/80 leading-relaxed">{anomaly.message}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 shrink-0">
                      <span className="text-[11px] text-muted hidden sm:inline-block">{anomaly.time}</span>
                      <button
                        onClick={() => handleResolve(anomaly.id)}
                        title="Acknowledge and mark resolved"
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-emerald-500/20 border border-white/[0.06] hover:border-emerald-500/30 text-xs font-medium text-white/70 hover:text-emerald-300 transition-all"
                      >
                        <Check size={13} />
                        <span>Acknowledge</span>
                      </button>
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
