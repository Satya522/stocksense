import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect, useState } from 'react';

function AnimatedNumber({ value }) {
  const [displayValue, setDisplayValue] = useState(0);
  useEffect(() => {
    const num = parseFloat(String(value).replace(/[^0-9.]/g, ''));
    if (isNaN(num)) return;
    const controls = animate(0, num, {
      duration: 1.2,
      ease: [0.22, 1, 0.36, 1],
      onUpdate(v) {
        setDisplayValue(Math.round(v));
      },
    });
    return controls.stop;
  }, [value]);

  const prefix = String(value).match(/^[^0-9]*/)?.[0] || '';
  const suffix = String(value).match(/[^0-9.]*$/)?.[0] || '';
  return <>{prefix}{displayValue}{suffix}</>;
}

export default function MetricCard({ title, value, subtitle, icon: Icon, color = 'text-accent', bgGlow = 'bg-accent', trend }) {
  return (
    <motion.div 
      whileHover={{ y: -6, scale: 1.02 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className="glass-panel-hover p-6 relative overflow-hidden group cursor-default"
    >
      {/* Decorative corner glow */}
      <div 
        className={`absolute -top-12 -right-12 w-40 h-40 ${bgGlow} blur-[80px] opacity-[0.08] group-hover:opacity-[0.18] transition-opacity duration-700 rounded-full`}
      />
      
      {/* Shimmer overlay on hover */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 shimmer rounded-2xl" />
      
      <div className="flex justify-between items-start mb-5 relative z-10">
        <div>
          <h3 className="text-muted text-xs font-semibold tracking-wider uppercase">{title}</h3>
          {subtitle && <p className="text-muted/60 text-[11px] mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.06] ${color} shadow-lg`}>
          <Icon size={20} />
        </div>
      </div>
      
      <div className="text-4xl font-display font-bold text-white relative z-10 tracking-tight mb-2">
        <AnimatedNumber value={value} />
      </div>

      {trend && (
        <div className={`flex items-center gap-1.5 text-xs font-medium relative z-10 ${trend > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
          <span>{trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%</span>
          <span className="text-muted">vs last month</span>
        </div>
      )}
    </motion.div>
  );
}
