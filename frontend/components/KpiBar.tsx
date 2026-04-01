'use client';

import type { KpiMetric } from '@/lib/types';
import { motion } from 'framer-motion';
import { Activity, Zap, Thermometer, Clock, ShieldCheck, AlertTriangle } from 'lucide-react';

const icons: Record<string, any> = {
  'asset-performance': Activity,
  'asset-downtime': Clock,
  'energy-usage': Zap,
  'avg-temp': Thermometer,
};

const statusColor: Record<string, string> = {
  normal: 'text-emerald-400',
  warning: 'text-amber-400',
  critical: 'text-red-400',
};

const statusBg: Record<string, string> = {
  normal: 'bg-emerald-400/5 border-emerald-400/10',
  warning: 'bg-amber-400/5 border-amber-400/10',
  critical: 'bg-red-400/5 border-red-400/10 shadow-[0_0_15px_rgba(248,113,113,0.1)]',
};

export default function KpiBar({ kpis }: { kpis: KpiMetric[] }) {
  if (!kpis.length) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[0, 1, 2, 3].map(i => (
          <div key={i} className="bg-slate-900/40 border border-slate-800/50 rounded-2xl p-5 h-28 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi, idx) => {
        const Icon = icons[kpi.id] || ShieldCheck;
        return (
          <motion.div
            key={kpi.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            whileHover={{ scale: 1.02, backgroundColor: 'rgba(30, 41, 59, 0.6)' }}
            className={`relative overflow-hidden rounded-2xl p-5 border transition-all duration-300 ${
              statusBg[kpi.status] ?? 'bg-slate-900/40 border-slate-800/60'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-1">
                  {kpi.name}
                </p>
                <div className="flex items-baseline gap-1">
                  <span className={`text-3xl font-black tracking-tight tabular-nums ${statusColor[kpi.status] ?? 'text-white'}`}>
                    {kpi.value}
                  </span>
                  <span className="text-xs font-semibold text-slate-500 lowercase">{kpi.unit}</span>
                </div>
              </div>
              <div className={`p-2 rounded-xl ${statusBg[kpi.status] ?? 'bg-slate-800/50 text-slate-400'}`}>
                <Icon className={`w-5 h-5 ${statusColor[kpi.status] ?? ''}`} />
              </div>
            </div>

            <div className="mt-3 flex items-center gap-2">
              <div className={`flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-md ${
                kpi.trend >= 0 ? 'text-emerald-400 bg-emerald-400/10' : 'text-red-400 bg-red-400/10'
              }`}>
                {kpi.trend >= 0 ? '↗' : '↘'} {Math.abs(kpi.trend).toFixed(1)}%
              </div>
              <span className="text-[10px] text-slate-600 font-medium uppercase tracking-wider italic">
                vs yesterday
              </span>
            </div>
            
            {/* Background Glow */}
            <div className={`absolute -right-4 -bottom-4 w-16 h-16 blur-2xl opacity-10 rounded-full ${
              kpi.status === 'critical' ? 'bg-red-500' : kpi.status === 'warning' ? 'bg-amber-500' : 'bg-teal-500'
            }`} />
          </motion.div>
        );
      })}
    </div>
  );
}
