'use client';

import { useEffect, useState } from 'react';
import { fetchHistory } from '@/lib/api';
import type { TwinSnapshot } from '@/lib/types';
import { motion } from 'framer-motion';
import { Clock, AlertTriangle, Activity } from 'lucide-react';

export default function HistoryView() {
  const [history, setHistory] = useState<TwinSnapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory()
      .then(data => {
        setHistory(data.reverse()); // Show newest first
        setLoading(false);
      })
      .catch(console.error);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 h-full overflow-hidden flex flex-col">
      <div className="flex items-center gap-3 mb-6">
        <Clock className="w-5 h-5 text-teal-400" />
        <h2 className="text-sm font-black text-slate-200 uppercase tracking-widest">Historical Event Stream</h2>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-[10px] font-black text-slate-500 uppercase tracking-widest">
              <th className="pb-3 pl-2">Timestamp</th>
              <th className="pb-3">Event Type</th>
              <th className="pb-3">Snapshot Metrics</th>
              <th className="pb-3 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="text-xs">
            {history.map((snapshot, idx) => (
              <motion.tr 
                key={snapshot.generatedAt}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.02 }}
                className="border-b border-slate-800/40 hover:bg-slate-800/30 transition-colors group"
              >
                <td className="py-4 pl-2 font-mono text-slate-400">
                  {new Date(snapshot.generatedAt).toLocaleTimeString()}
                </td>
                <td className="py-4">
                  <div className="flex items-center gap-2">
                    {snapshot.alerts.length > 0 ? (
                      <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-red-500/10 text-red-400 border border-red-500/20 text-[10px] font-bold uppercase">
                        <AlertTriangle className="w-3 h-3" />
                        Incident
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase">
                        <Activity className="w-3 h-3" />
                        Nominal
                      </span>
                    )}
                  </div>
                </td>
                <td className="py-4 text-slate-500">
                   {snapshot.alerts.length > 0 
                     ? `${snapshot.alerts.length} alerts active` 
                     : `All ${snapshot.telemetry.length} nodes operational`}
                </td>
                <td className="py-4 text-right">
                  <span className="text-[10px] font-black text-slate-600 uppercase tracking-tighter">
                    Tick #{Math.floor(snapshot.simulationTime).toString().padStart(4, '0')}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
