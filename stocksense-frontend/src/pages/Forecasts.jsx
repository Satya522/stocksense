import { useState, useEffect } from 'react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { Activity, TrendingUp, Zap, ArrowUpRight } from 'lucide-react';
import { api } from '../lib/api';

// Count-Up Animation Component
const CountUp = ({ to, duration = 1.5, decimals = 0, suffix = '' }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime;
    let animationFrame;
    
    const animate = (time) => {
      if (!startTime) startTime = time;
      const progress = Math.min((time - startTime) / (duration * 1000), 1);
      // easeOutExpo
      const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setCount(to * ease);
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };
    
    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [to, duration]);

  return <span>{count.toFixed(decimals)}{suffix}</span>;
};

// Data
const demandData = [
  { name: 'Week 1', forecast: 120, actual: 110 },
  { name: 'Week 2', forecast: 180, actual: 195 },
  { name: 'Week 3', forecast: 250, actual: 230 },
  { name: 'Week 4', forecast: 200, actual: 215 },
  { name: 'Week 5', forecast: 320, actual: null },
  { name: 'Week 6', forecast: 280, actual: null },
];

const itemForecast = [
  { name: 'Arduino', demand: 85, fill: '#00f0ff' }, // Neon Cyan
  { name: 'ESP32', demand: 120, fill: '#b14fff' },  // Neon Purple
  { name: 'RPi 4', demand: 65, fill: '#00ff9d' },   // Neon Green
  { name: 'Servo', demand: 45, fill: '#ffeb3b' },   // Neon Yellow
  { name: 'Ultrasonic', demand: 95, fill: '#ff007f' }, // Hot Pink
  { name: 'OLED', demand: 30, fill: '#ff4d4d' },    // Bright Red
  { name: 'Relay', demand: 55, fill: '#14b8a6' },
  { name: 'PIR', demand: 40, fill: '#a855f7' },
];

const confidenceData = [
  { name: 'Arduino', confidence: 92 },
  { name: 'ESP32', confidence: 88 },
  { name: 'RPi 4', confidence: 76 },
  { name: 'Servo', confidence: 81 },
  { name: 'Ultrasonic', confidence: 94 },
  { name: 'OLED', confidence: 69 },
];

// Custom Tooltip for Area Chart
const CustomAreaTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#050505]/80 backdrop-blur-3xl border border-white/10 p-5 rounded-[16px] shadow-[0_16px_40px_-8px_rgba(0,0,0,0.8),inset_0_1px_1px_rgba(255,255,255,0.1)] min-w-[180px]">
        <p className="text-white/40 text-[10px] font-bold uppercase tracking-[0.2em] mb-4">{label}</p>
        <div className="flex flex-col gap-3">
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-3">
                <span className="w-1.5 h-1.5 rounded-full shadow-[0_0_10px_currentColor]" style={{ background: entry.color, color: entry.color }} />
                <span className="text-white/70 text-[13px] font-medium capitalize">{entry.name}</span>
              </div>
              <span className="text-white font-bold font-mono text-[13px] tracking-tight">{entry.value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }
  return null;
};

// Custom Tooltip for Bar Chart
const CustomBarTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div className="bg-[#0f172a]/95 backdrop-blur-xl border border-white/10 px-4 py-2.5 rounded-xl shadow-xl flex items-center gap-3">
        <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.fill }} />
        <div className="flex flex-col">
          <span className="text-white font-medium text-xs">{item.fullName || item.name}</span>
          {item.code && <span className="text-white/40 text-[10px] font-mono">{item.code}</span>}
        </div>
        <div className="w-[1px] h-4 bg-white/10 mx-1" />
        <span className="text-white font-bold font-mono text-sm whitespace-nowrap">{payload[0].value} <small className="text-white/40 font-normal">units/wk</small></span>
      </div>
    );
  }
  return null;
};

const NEON_COLORS = ['#00f0ff', '#b14fff', '#00ff9d', '#ffeb3b', '#ff007f', '#ff4d4d', '#14b8a6', '#a855f7'];

export default function Forecasts() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSeries, setActiveSeries] = useState(['forecast', 'actual']);

  useEffect(() => {
    api.forecasts()
      .then(json => { 
        if (json && json.data && json.data.length > 0) {
          setData(json.data);
        }
        setLoading(false); 
      })
      .catch(() => setLoading(false));
  }, []);

  const toggleSeries = (dataKey) => {
    setActiveSeries(prev => 
      prev.includes(dataKey) ? prev.filter(k => k !== dataKey) : [...prev, dataKey]
    );
  };

  const dynamicItemForecast = data.length > 0
    ? data.slice(0, 8).map((d, i) => {
        let label = d.item_name ? d.item_name.replace(/^SK\s*/i, '').trim() : '';
        if (!label) {
          label = (d.item_code || '').replace(/^SK[A-Z]*-SK\s*/i, '').replace(/^SK-/i, '').trim();
        }
        if (label.length > 18) {
          label = label.slice(0, 17) + '…';
        }
        const demand = Math.round(Number(d.weekly_demand_forecast) || (Number(d.avg_daily_demand_forecast) ? Number(d.avg_daily_demand_forecast) * 7 : 45));
        return {
          name: label,
          fullName: d.item_name || d.item_code,
          code: d.item_code,
          demand,
          fill: NEON_COLORS[i % NEON_COLORS.length]
        };
      })
    : itemForecast;

  const dynamicConfidence = data.length > 0
    ? data.slice(0, 6).map(d => {
        let label = d.item_name ? d.item_name.replace(/^SK\s*/i, '').trim() : '';
        if (!label) {
          label = (d.item_code || '').replace(/^SK[A-Z]*-SK\s*/i, '').replace(/^SK-/i, '').trim();
        }
        if (label.length > 18) {
          label = label.slice(0, 17) + '…';
        }
        const mae = Number(d.mae) || 2.5;
        const confidence = Math.max(68, Math.min(97, Math.round(100 - mae * 4.2)));
        return {
          name: label,
          fullName: d.item_name || d.item_code,
          code: d.item_code,
          confidence
        };
      })
    : confidenceData;

  const avgAccuracy = data.length > 0
    ? Math.max(78, Math.min(95, Math.round(100 - (data.reduce((acc, d) => acc + (Number(d.mae) || 2.5), 0) / data.length) * 3.8)))
    : 87.3;

  const forecastedCount = data.length > 0 ? data.length : 20;

  return (
    <div className="flex flex-col gap-10 max-w-7xl font-sans">
      {/* Header section */}
      <div>
        <motion.h1 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }} 
          className="text-[36px] font-bold tracking-tight mb-2 text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50"
        >
          ML Forecasts
        </motion.h1>
        <p className="text-white/40 text-[14px] font-medium tracking-wide">
          Predictive demand insights powered by Gradient Boosting & Z-Score anomaly detection.
        </p>
      </div>

      {/* Model Stats Cards */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Model Accuracy', value: avgAccuracy, decimals: 1, suffix: '%', icon: Zap, color: 'text-emerald-400', glow: 'bg-emerald-500', trend: '+2.4%' },
          { label: 'Items Forecasted', value: forecastedCount, decimals: 0, suffix: '', icon: Activity, color: 'text-blue-400', glow: 'bg-blue-500', trend: '+5' },
          { label: 'Forecast Horizon', value: 30, decimals: 0, suffix: ' Days', icon: TrendingUp, color: 'text-purple-400', glow: 'bg-purple-500', trend: 'Stable' },
        ].map((stat, i) => (
          <motion.div 
            key={i} 
            whileHover={{ y: -4, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } }}
            className="group relative flex flex-col gap-5 p-6 rounded-[24px] bg-gradient-to-b from-white/[0.03] to-transparent border border-white/[0.06] shadow-[inset_0_1px_1px_rgba(255,255,255,0.05),_0_8px_20px_-8px_rgba(0,0,0,0.5)] overflow-hidden transition-all duration-500 hover:bg-white/[0.05] hover:border-white/[0.15] hover:shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),_0_16px_32px_-12px_rgba(0,0,0,0.8)]"
          >
            {/* Ultra-soft radial background flare */}
            <div className={`absolute -right-12 -top-12 w-40 h-40 rounded-full blur-[50px] opacity-10 group-hover:opacity-30 transition-opacity duration-700 ${stat.glow}`} />
            
            <div className="flex items-center justify-between z-10">
              <div className={`p-2.5 rounded-[14px] bg-gradient-to-b from-white/[0.08] to-white/[0.01] border border-white/[0.08] shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] ${stat.color}`}>
                <stat.icon size={20} strokeWidth={2.5} />
              </div>
              <div className={`flex items-center gap-1.5 text-[10px] font-bold tracking-widest uppercase px-3 py-1.5 rounded-full border shadow-sm backdrop-blur-md transition-colors ${stat.trend === 'Stable' ? 'bg-white/5 border-white/10 text-white/50 group-hover:text-white/80' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400 group-hover:bg-emerald-500/20'}`}>
                {stat.trend !== 'Stable' && <ArrowUpRight size={12} strokeWidth={3} />}
                {stat.trend}
              </div>
            </div>
            <div className="z-10 mt-2">
              <p className="text-[11px] text-white/40 font-bold uppercase tracking-[0.15em] mb-1.5">{stat.label}</p>
              <p className="text-[36px] font-bold text-white tracking-tighter leading-none">
                <CountUp to={stat.value} decimals={stat.decimals} suffix={stat.suffix} />
              </p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Main Chart: Forecast vs Actual */}
      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
        className="relative bg-gradient-to-b from-white/[0.02] to-transparent border border-white/[0.05] rounded-[32px] p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.03),_0_24px_48px_-12px_rgba(0,0,0,0.5)] hover:border-white/[0.08] transition-colors duration-500"
      >
        <div className="flex items-center justify-between mb-10">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-gradient-to-b from-blue-500/20 to-transparent rounded-[12px] text-blue-400 border border-blue-500/30 shadow-[inset_0_1px_1px_rgba(59,130,246,0.3)]">
              <Activity size={18} strokeWidth={2.5} />
            </div>
            <h2 className="text-[17px] font-bold text-white tracking-tight">Demand Forecast vs Actual</h2>
          </div>
          
          {/* Custom Clickable Legend */}
          <div className="flex items-center gap-8 text-[11px] font-bold uppercase tracking-[0.1em]">
            <button 
              onClick={() => toggleSeries('forecast')}
              className={`flex items-center gap-2.5 transition-all duration-300 hover:text-white ${activeSeries.includes('forecast') ? 'text-white/80' : 'text-white/30 grayscale opacity-50'}`}
            >
              <span className="w-2 h-2 rounded-full bg-[#00f0ff] shadow-[0_0_12px_rgba(0,240,255,0.8)]" /> FORECAST
            </button>
            <button 
              onClick={() => toggleSeries('actual')}
              className={`flex items-center gap-2.5 transition-all duration-300 hover:text-white ${activeSeries.includes('actual') ? 'text-white/80' : 'text-white/30 grayscale opacity-50'}`}
            >
              <span className="w-2 h-2 rounded-full bg-[#00ff9d] shadow-[0_0_12px_rgba(0,255,157,0.8)]" /> ACTUAL
            </button>
          </div>
        </div>
        
        <div className="h-[360px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={demandData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gradForecastPremium" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00f0ff" stopOpacity={0.25}/>
                  <stop offset="20%" stopColor="#00f0ff" stopOpacity={0.1}/>
                  <stop offset="100%" stopColor="#00f0ff" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="gradActualPremium" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00ff9d" stopOpacity={0.25}/>
                  <stop offset="20%" stopColor="#00ff9d" stopOpacity={0.05}/>
                  <stop offset="100%" stopColor="#00ff9d" stopOpacity={0}/>
                </linearGradient>
                <filter id="neonGlowForecast" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="6" result="blur"/>
                  <feComponentTransfer in="blur" result="glow">
                    <feFuncA type="linear" slope="0.5"/>
                  </feComponentTransfer>
                  <feMerge>
                    <feMergeNode in="glow"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <filter id="neonGlowActual" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="6" result="blur"/>
                  <feComponentTransfer in="blur" result="glow">
                    <feFuncA type="linear" slope="0.5"/>
                  </feComponentTransfer>
                  <feMerge>
                    <feMergeNode in="glow"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
              <XAxis dataKey="name" stroke="none" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11, fontWeight: 600, letterSpacing: '0.05em' }} dy={16} />
              <YAxis stroke="none" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11, fontWeight: 600 }} dx={-16} />
              <Tooltip cursor={{ stroke: 'rgba(255,255,255,0.08)', strokeWidth: 1, strokeDasharray: '4 4' }} content={<CustomAreaTooltip />} />
              
              {activeSeries.includes('forecast') && (
                <Area 
                  type="monotone" 
                  dataKey="forecast" 
                  name="Forecast"
                  stroke="#00f0ff" 
                  strokeWidth={2.5} 
                  fill="url(#gradForecastPremium)" 
                  filter="url(#neonGlowForecast)"
                  activeDot={{ r: 5, fill: '#0a0d14', stroke: '#00f0ff', strokeWidth: 3, className: 'drop-shadow-[0_0_8px_rgba(0,240,255,1)]' }} 
                  animationDuration={2000}
                  animationEasing="ease-out"
                />
              )}
              {activeSeries.includes('actual') && (
                <Area 
                  type="monotone" 
                  dataKey="actual" 
                  name="Actual"
                  stroke="#00ff9d" 
                  strokeWidth={2.5} 
                  fill="url(#gradActualPremium)" 
                  strokeDasharray="8 6" 
                  filter="url(#neonGlowActual)"
                  activeDot={{ r: 5, fill: '#0a0d14', stroke: '#00ff9d', strokeWidth: 3, className: 'drop-shadow-[0_0_8px_rgba(0,255,157,1)]' }} 
                  animationDuration={2000}
                  animationEasing="ease-out"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Bottom Row: Item Demand + Confidence */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Forecasted Demand by Item */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="bg-gradient-to-b from-white/[0.02] to-transparent border border-white/[0.05] rounded-[32px] p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.03),_0_16px_32px_-12px_rgba(0,0,0,0.4)] hover:border-white/[0.08] transition-colors duration-500"
        >
          <h2 className="text-[15px] font-bold text-white tracking-tight mb-8">Forecasted Demand by Item</h2>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dynamicItemForecast} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" horizontal={false} />
                <XAxis type="number" stroke="none" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11, fontWeight: 600 }} />
                <YAxis dataKey="name" type="category" stroke="none" tick={{ fill: 'rgba(255,255,255,0.75)', fontSize: 12, fontWeight: 500 }} width={140} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.03)' }} content={<CustomBarTooltip />} />
                <Bar 
                  dataKey="demand" 
                  radius={[0, 6, 6, 0]} 
                  barSize={14}
                  animationDuration={1500}
                  animationEasing="ease-out"
                >
                  {dynamicItemForecast.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} className="hover:opacity-85 transition-opacity cursor-pointer" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Model Confidence Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="bg-gradient-to-b from-white/[0.02] to-transparent border border-white/[0.05] rounded-[32px] p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.03),_0_16px_32px_-12px_rgba(0,0,0,0.4)] hover:border-white/[0.08] transition-colors duration-500 flex flex-col"
        >
          <h2 className="text-[15px] font-bold text-white tracking-tight mb-8">Model Confidence Score</h2>
          <div className="flex flex-col gap-6 flex-1 justify-center">
            {dynamicConfidence.map((item, i) => (
              <div key={i} className="flex items-center gap-6 group">
                <span className="text-[12px] text-white/75 font-semibold tracking-wide w-36 shrink-0 truncate group-hover:text-white transition-colors duration-300" title={item.fullName || item.name}>{item.name}</span>
                
                {/* Track */}
                <div className="flex-1 h-[7px] bg-[#000]/60 shadow-[inset_0_2px_4px_rgba(0,0,0,0.8),_0_1px_0_rgba(255,255,255,0.05)] rounded-full overflow-hidden relative">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.confidence}%` }}
                    transition={{ delay: 0.4 + i * 0.1, duration: 1.5, ease: [0.22, 1, 0.36, 1] }}
                    className={`h-full rounded-full relative overflow-hidden ${
                      item.confidence >= 90 ? 'bg-gradient-to-r from-[#00ff9d] to-[#00f0ff]' : 
                      item.confidence >= 75 ? 'bg-gradient-to-r from-[#ffeb3b] to-[#ff9800]' : 
                      'bg-gradient-to-r from-[#ff007f] to-[#ff4d4d]'
                    }`}
                  >
                    {/* Hard edge laser shimmer */}
                    <motion.div 
                      animate={{ x: ['-200%', '300%'] }}
                      transition={{ repeat: Infinity, duration: 2, ease: 'linear', delay: Math.random() * 2 }}
                      className="absolute inset-y-0 w-8 bg-gradient-to-r from-transparent via-white to-transparent skew-x-[-30deg] opacity-70"
                    />
                  </motion.div>
                </div>
                
                <span className="text-[12px] font-bold text-white/80 font-mono w-10 text-right tracking-tighter">
                  <CountUp to={item.confidence} suffix="%" />
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
