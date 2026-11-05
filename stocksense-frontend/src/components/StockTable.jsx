import { motion } from 'framer-motion';

const stockData = [
  { item: 'Arduino Uno R3', code: 'SKU001', qty: 150, reorder: 50, status: 'healthy' },
  { item: 'Raspberry Pi 4', code: 'SKU002', qty: 8, reorder: 20, status: 'critical' },
  { item: 'ESP32 DevKit', code: 'SKU003', qty: 200, reorder: 40, status: 'healthy' },
  { item: 'Servo Motor SG90', code: 'SKU004', qty: 25, reorder: 30, status: 'warning' },
  { item: 'Ultrasonic Sensor', code: 'SKU005', qty: 180, reorder: 50, status: 'healthy' },
  { item: '16x2 LCD Display', code: 'SKU006', qty: 12, reorder: 25, status: 'critical' },
  { item: 'Relay Module 4CH', code: 'SKU007', qty: 90, reorder: 30, status: 'healthy' },
  { item: 'PIR Motion Sensor', code: 'SKU008', qty: 28, reorder: 20, status: 'healthy' },
  { item: 'OLED Display 0.96"', code: 'SKU009', qty: 5, reorder: 15, status: 'critical' },
  { item: 'Stepper Motor NEMA17', code: 'SKU010', qty: 35, reorder: 30, status: 'warning' },
];

const statusConfig = {
  healthy: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'In Stock' },
  warning: { bg: 'bg-amber-500/10', text: 'text-amber-400', dot: 'bg-amber-400', label: 'Low' },
  critical: { bg: 'bg-rose-500/10', text: 'text-rose-400', dot: 'bg-rose-400', label: 'Critical' },
};

export default function StockTable() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/[0.06]">
            <th className="text-left text-[11px] text-muted uppercase tracking-wider font-semibold py-3 px-4">Item</th>
            <th className="text-left text-[11px] text-muted uppercase tracking-wider font-semibold py-3 px-4">Code</th>
            <th className="text-right text-[11px] text-muted uppercase tracking-wider font-semibold py-3 px-4">Qty</th>
            <th className="text-right text-[11px] text-muted uppercase tracking-wider font-semibold py-3 px-4">Reorder</th>
            <th className="text-center text-[11px] text-muted uppercase tracking-wider font-semibold py-3 px-4">Stock Level</th>
            <th className="text-center text-[11px] text-muted uppercase tracking-wider font-semibold py-3 px-4">Status</th>
          </tr>
        </thead>
        <tbody>
          {stockData.map((item, i) => {
            const cfg = statusConfig[item.status];
            const fillPct = Math.min((item.qty / (item.reorder * 3)) * 100, 100);
            return (
              <motion.tr
                key={item.code}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05, duration: 0.3 }}
                className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors"
              >
                <td className="py-3.5 px-4 font-medium text-white">{item.item}</td>
                <td className="py-3.5 px-4 text-muted font-mono text-xs">{item.code}</td>
                <td className="py-3.5 px-4 text-right font-semibold text-white tabular-nums">{item.qty}</td>
                <td className="py-3.5 px-4 text-right text-muted tabular-nums">{item.reorder}</td>
                <td className="py-3.5 px-4">
                  <div className="w-full h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${fillPct}%` }}
                      transition={{ delay: i * 0.05 + 0.3, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                      className={`h-full rounded-full ${item.status === 'healthy' ? 'bg-emerald-400' : item.status === 'warning' ? 'bg-amber-400' : 'bg-rose-400'}`}
                    />
                  </div>
                </td>
                <td className="py-3.5 px-4 text-center">
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${cfg.bg} ${cfg.text}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
                    {cfg.label}
                  </span>
                </td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
