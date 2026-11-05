import { motion } from 'framer-motion';

export default function StockHealthRing({ healthy, warning, critical, total }) {
  const healthyPct = (healthy / total) * 100;
  const warningPct = (warning / total) * 100;
  const criticalPct = (critical / total) * 100;

  const radius = 60;
  const circumference = 2 * Math.PI * radius;

  const segments = [
    { pct: healthyPct, color: '#10b981', label: 'Healthy', count: healthy },
    { pct: warningPct, color: '#f59e0b', label: 'Warning', count: warning },
    { pct: criticalPct, color: '#ef4444', label: 'Critical', count: critical },
  ];

  let offset = 0;

  return (
    <div className="flex items-center gap-8">
      <div className="relative w-36 h-36 shrink-0">
        <svg viewBox="0 0 140 140" className="w-full h-full -rotate-90">
          <circle cx="70" cy="70" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="14" />
          {segments.map((seg, i) => {
            const dashLen = (seg.pct / 100) * circumference;
            const dashOffset = offset;
            offset += dashLen;
            return (
              <motion.circle
                key={i}
                cx="70" cy="70" r={radius}
                fill="none"
                stroke={seg.color}
                strokeWidth="14"
                strokeLinecap="round"
                strokeDasharray={`${dashLen} ${circumference - dashLen}`}
                strokeDashoffset={-dashOffset}
                initial={{ strokeDasharray: `0 ${circumference}` }}
                animate={{ strokeDasharray: `${dashLen} ${circumference - dashLen}` }}
                transition={{ duration: 1.2, delay: i * 0.2, ease: [0.22, 1, 0.36, 1] }}
              />
            );
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-display font-bold text-white">{total}</span>
          <span className="text-[10px] text-muted uppercase tracking-wider">Items</span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {segments.map((seg, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: seg.color, boxShadow: `0 0 8px ${seg.color}40` }} />
            <div>
              <p className="text-sm font-medium text-white">{seg.label}</p>
              <p className="text-xs text-muted">{seg.count} items ({Math.round(seg.pct)}%)</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
