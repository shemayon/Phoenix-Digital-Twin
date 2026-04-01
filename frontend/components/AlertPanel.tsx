'use client';

import type { TwinAlert } from '@/lib/types';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, AlertTriangle, Info, BellRing } from 'lucide-react';

const alertIcons: Record<string, any> = {
  critical: AlertCircle,
  warning: AlertTriangle,
  normal: Info,
};

const severityColor: Record<string, string> = {
  critical: 'text-red-400',
  warning: 'text-amber-400',
  normal: 'text-blue-400',
};

const severityBorder: Record<string, string> = {
  critical: 'border-red-500/20 bg-red-950/20 shadow-[inset_0_0_12px_rgba(248,113,113,0.05)]',
  warning: 'border-amber-500/20 bg-amber-950/10',
  normal: 'border-blue-500/20 bg-blue-950/10',
};

export default function AlertPanel({ alerts }: { alerts: TwinAlert[] }) {
  return (
    <div className="flex flex-col gap-3 overflow-hidden">
      <div className="flex items-center gap-2 mb-1 px-1">
        <BellRing className="w-4 h-4 text-violet-400" />
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Incident Log</h3>
      </div>
      
      <div className="flex flex-col gap-2.5 max-h-[300px] overflow-y-auto pr-1">
        <AnimatePresence initial={false}>
          {alerts.map(alert => {
            const Icon = alertIcons[alert.severity] || Info;
            return (
              <motion.div
                key={alert.alertId}
                initial={{ opacity: 0, x: -20, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className={`rounded-xl border p-4 transition-all duration-300 group ${severityBorder[alert.severity] ?? 'border-slate-800 bg-slate-900/50'}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 p-1.5 rounded-lg bg-slate-900 shadow-sm ${severityColor[alert.severity]}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-[11px] font-black text-slate-300 uppercase tracking-tight truncate">
                        {alert.tagName ?? 'System Exception'}
                      </span>
                      <span className="text-[9px] font-bold text-slate-600 tabular-nums">
                        {new Date(alert.detectedAt).toLocaleTimeString([], { hour12: false })}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed group-hover:text-slate-300 transition-colors">
                      {alert.message}
                    </p>
                    
                    {alert.tagName && (
                      <div className="mt-3 flex items-center gap-2">
                        <button
                          onClick={() => {
                            const internalTag = alert.tagName?.split('/').pop()?.toUpperCase() || '';
                            const delta = internalTag.includes('TEMP') ? -10 : internalTag.includes('VIB') ? -5 : -2;
                            import('@/lib/api').then(api => api.sendCommand(alert.tagName!, delta));
                          }}
                          className="px-3 py-1 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-400 text-[10px] font-black uppercase tracking-widest hover:bg-teal-500/20 transition-all active:scale-95"
                        >
                          Execute Correction
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
        
        {alerts.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="py-12 flex flex-col items-center justify-center text-center px-4"
          >
            <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center mb-3">
              <ShieldCheck className="w-6 h-6 text-emerald-400 opacity-60" />
            </div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">No Active Alerts</p>
            <p className="text-[10px] text-slate-600 mt-1">Operational integrity confirmed</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}

function ShieldCheck({ className }: { className?: string }) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      width="24" height="24" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      className={className}
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}
