'use client';

import type { TelemetryValue } from '@/lib/types';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldCheck, AlertCircle, AlertTriangle } from 'lucide-react';

const statusId: Record<string, string> = {
  normal: 'emerald',
  warning: 'amber',
  critical: 'red',
};

const pillClass: Record<string, string> = {
  normal: 'bg-emerald-400/15 text-emerald-300 border border-emerald-400/25',
  warning: 'bg-amber-400/15 text-amber-300 border border-amber-400/25',
  critical: 'bg-red-400/15 text-red-300 border border-red-400/25 pulse-warning',
};

const Icons: Record<string, any> = {
  normal: ShieldCheck,
  warning: AlertTriangle,
  critical: AlertCircle,
};

export default function TelemetryTable({
  rows,
  selectedTag,
  onSelectTag,
}: {
  rows: TelemetryValue[];
  selectedTag: string;
  onSelectTag: (tag: string) => void;
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/40">
      <div className="max-h-[360px] overflow-auto">
        <table className="w-full text-sm border-collapse">
          <thead className="sticky top-0 z-10 bg-slate-900/90 backdrop-blur-sm shadow-sm">
            <tr className="text-slate-500 uppercase text-[10px] font-bold tracking-widest border-b border-slate-800">
              <th className="px-4 py-3 text-left">Signal</th>
              <th className="px-4 py-3 text-left">Metric</th>
              <th className="px-4 py-3 text-right">Value</th>
              <th className="px-4 py-3 text-center">Status</th>
              <th className="px-4 py-3 text-right">Source</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence initial={false}>
              {rows.map((row, idx) => {
                const StatusIcon = Icons[row.status] || Activity;
                const isSelected = row.tagName === selectedTag;
                const isCritical = row.status === 'critical';
                const nameParts = row.tagName.split('/');
                const shortName = nameParts[nameParts.length - 1];
                const category = nameParts.length > 2 ? nameParts[1].replace('_', ' ') : 'Global';
                
                return (
                  <motion.tr
                    key={row.tagName}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={() => onSelectTag(isSelected ? '' : row.tagName)}
                    className={`group cursor-pointer transition-all duration-200 border-b border-slate-800/40 ${
                      isSelected 
                        ? 'bg-teal-500/10' 
                        : row.status === 'critical' 
                          ? 'bg-red-500/5 hover:bg-red-500/10' 
                          : 'hover:bg-slate-800/50'
                    }`}
                  >
                    <td className="px-4 py-3 font-mono text-xs text-slate-300 flex items-center gap-2">
                       <div className={`w-1.5 h-1.5 rounded-full ${
                         isSelected ? 'bg-teal-400 shadow-[0_0_8px_rgba(45,212,191,0.8)]' : 'bg-slate-700'
                       }`} />
                       <div className="flex flex-col">
                         <span className="text-[11px] font-black text-slate-200 uppercase tracking-tighter">
                           {shortName}
                         </span>
                         <span className="text-[9px] font-bold text-slate-600 uppercase tracking-widest" title={row.tagName}>
                           {category}
                         </span>
                       </div>
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs">
                      {row.description ?? '—'}
                    </td>
                    <td className={`px-4 py-3 text-right font-black tabular-nums ${
                      row.status === 'critical' ? 'text-red-300' : row.status === 'warning' ? 'text-amber-300' : 'text-slate-100'
                    }`}>
                      {row.value.toLocaleString()}
                      <span className="text-[10px] text-slate-500 font-bold ml-1 uppercase">{row.unit}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-tighter ${
                        row.status === 'critical' 
                          ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                          : row.status === 'warning'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-400'
                      }`}>
                        {row.status}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right text-[10px] text-slate-500 font-bold uppercase">
                      {row.source}
                    </td>
                  </motion.tr>
                );
              })}
            </AnimatePresence>
            {!rows.length && (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center text-slate-600 italic">
                  Systems initializing. Awaiting incoming stream...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
