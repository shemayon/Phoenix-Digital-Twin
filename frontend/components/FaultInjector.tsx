'use client';

import { useState } from 'react';
import type { ActiveFault, FaultScenario } from '@/lib/types';
import { clearFault, triggerFault } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, AlertTriangle, Flame, Shield, Activity, X } from 'lucide-react';

const icons: Record<string, any> = {
  'reactor-temp-spike': Flame,
  'crusher-vibration-spike': Activity,
  'coolant-flow-drop': Shield,
  'motor-current-rise': Zap,
};

const severityColor: Record<string, string> = {
  critical: 'text-red-400 border-red-500/30 bg-red-500/5',
  warning: 'text-amber-400 border-amber-500/30 bg-amber-500/5',
  normal: 'text-teal-400 border-teal-500/30 bg-teal-500/5',
};

export default function FaultInjector({
  scenarios,
  activeFaults,
  onChanged,
}: {
  scenarios: FaultScenario[];
  activeFaults: ActiveFault[];
  onChanged?: () => void;
}) {
  const [busy, setBusy] = useState<Record<string, boolean>>({});
  const activeIds = new Set(activeFaults.map(f => f.scenarioId));

  const handleToggle = async (id: string, isActive: boolean) => {
    setBusy(b => ({ ...b, [id]: true }));
    try {
      isActive ? await clearFault(id) : await triggerFault(id);
      onChanged?.();
    } catch (e) {
      console.error(e);
    } finally {
      setBusy(b => ({ ...b, [id]: false }));
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Active Fault Status */}
      <AnimatePresence>
        {activeFaults.length > 0 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 mb-2">
              <div className="flex items-center gap-2 mb-2 text-red-400 font-black text-[10px] uppercase tracking-widest">
                <AlertTriangle className="w-3 h-3 pulse-critical" />
                Live Perturbations in Progress
              </div>
              <div className="space-y-1.5">
                {activeFaults.map(f => (
                  <div key={f.scenarioId} className="flex items-center justify-between bg-slate-900/60 rounded-lg px-2.5 py-1.5">
                    <span className="text-xs font-semibold text-red-200">{f.name}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-mono text-red-400 tabular-nums font-bold">
                        {f.remainingTicks}s
                      </span>
                      <button 
                        onClick={() => handleToggle(f.scenarioId, true)}
                        className="text-slate-500 hover:text-white transition-colors"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scenario Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-3">
        {scenarios.map(scenario => {
          const isActive = activeIds.has(scenario.scenarioId);
          const Icon = icons[scenario.scenarioId] || Zap;
          return (
            <motion.div
              key={scenario.scenarioId}
              whileHover={{ y: -2, backgroundColor: 'rgba(30, 41, 59, 0.4)' }}
              className={`relative group rounded-xl border p-4 transition-all duration-300 ${
                isActive 
                  ? 'border-red-500/40 bg-red-950/20 shadow-[0_0_20px_rgba(248,113,113,0.1)]' 
                  : 'border-slate-800 bg-slate-900/40'
              }`}
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className={`p-2 rounded-lg bg-slate-950 border border-slate-800 shadow-sm transition-colors ${isActive ? 'text-red-400 border-red-500/20' : 'text-slate-400 group-hover:text-teal-400'}`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <button
                  onClick={() => handleToggle(scenario.scenarioId, isActive)}
                  disabled={busy[scenario.scenarioId]}
                  className={`px-3 py-1.5 rounded-lg text-xs font-black uppercase tracking-tight transition-all duration-200 disabled:opacity-50 ${
                    isActive
                      ? 'bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30 hover:text-white'
                      : 'bg-slate-800 text-slate-400 border border-slate-700 hover:bg-teal-500/20 hover:text-teal-300 hover:border-teal-500/40'
                  }`}
                >
                  {busy[scenario.scenarioId] ? '…' : isActive ? 'Terminate' : 'Deploy'}
                </button>
              </div>
              
              <div className="min-w-0">
                <h4 className="text-xs font-bold text-slate-100 truncate">{scenario.name}</h4>
                <p className="text-[10px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
                  {scenario.description}
                </p>
                <div className="mt-3 flex items-center gap-2">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-black uppercase border ${severityColor[scenario.severity] ?? ''}`}>
                    {scenario.severity}
                  </span>
                  <span className="text-[9px] font-mono text-slate-700 opacity-80">
                    Δ{scenario.delta > 0 ? '+' : ''}{scenario.delta} · {scenario.targetTag}
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
