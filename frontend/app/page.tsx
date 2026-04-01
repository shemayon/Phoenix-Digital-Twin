'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { Asset, FaultScenario, TwinSnapshot, TelemetryValue } from '@/lib/types';
import { fetchAssets, fetchFaultScenarios, fetchSnapshot } from '@/lib/api';
import KpiBar from '@/components/KpiBar';
import TelemetryTable from '@/components/TelemetryTable';
import AlertPanel from '@/components/AlertPanel';
import FaultInjector from '@/components/FaultInjector';
import ChatBot from '@/components/ChatBot';
import TrendChart from '@/components/TrendChart';
import ThreeScene from '@/components/ThreeScene';
import HistoryView from '@/components/HistoryView';
import TopologyView from '@/components/TopologyView';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldCheck, 
  Activity, 
  LayoutDashboard, 
  Settings, 
  Bell, 
  Layers,
  ChevronRight,
  Database,
  History,
  Server,
  Box,
  Cpu
} from 'lucide-react';

function LiveIndicator({ connected }: { connected: boolean }) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/50 border border-slate-800">
      <div className="relative flex h-2 w-2">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
          connected ? 'bg-emerald-400' : 'bg-slate-600'
        }`} />
        <span className={`relative inline-flex rounded-full h-2 w-2 ${
          connected ? 'bg-emerald-500' : 'bg-slate-500'
        }`} />
      </div>
      <span className={`text-[10px] font-black uppercase tracking-widest ${
        connected ? 'text-emerald-400' : 'text-slate-500'
      }`}>
        {connected ? 'Sync: Nominal' : 'Sync: Lost'}
      </span>
    </div>
  );
}

export default function Dashboard() {
  const [snapshot, setSnapshot] = useState<TwinSnapshot | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [scenarios, setScenarios] = useState<FaultScenario[]>([]);
  const [selectedAsset, setSelectedAsset] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [connected, setConnected] = useState(false);
  const [tick, setTick] = useState(0);
  const [activeView, setActiveView] = useState<'fleet' | 'spatial' | 'logs' | 'nodes'>('fleet');
  const wsRef = useRef<WebSocket | null>(null);

  // Initial data fetch
  useEffect(() => {
    fetchAssets().then(setAssets).catch(console.error);
    fetchSnapshot().then(setSnapshot).catch(console.error);
    fetchFaultScenarios().then(setScenarios).catch(console.error);
  }, []);

  // WebSocket for real-time telemetry
  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
    let wsUrl: string;
    if (base.startsWith('http')) {
      wsUrl = base.replace(/^http/, 'ws') + '/twin/stream';
    } else {
      wsUrl = `ws://localhost:8000/twin/stream`;
    }

    function connect() {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;
        ws.onopen = () => setConnected(true);
        ws.onclose = () => {
          setConnected(false);
          setTimeout(connect, 3000);
        };
        ws.onerror = () => ws.close();
        ws.onmessage = evt => {
          try {
            const data = JSON.parse(evt.data) as TwinSnapshot;
            setSnapshot(data);
            setTick(prev => prev + 1);
          } catch { /* ignore */ }
        };
      } catch { /* ignore */ }
    }

    connect();
    return () => wsRef.current?.close();
  }, []);

  const refreshScenarios = useCallback(() => {
    fetchFaultScenarios().then(setScenarios).catch(console.error);
    fetchSnapshot().then(setSnapshot).catch(console.error);
  }, []);

  const telemetry = snapshot?.telemetry ?? [];
  const alerts = snapshot?.alerts ?? [];
  const kpis = snapshot?.kpis ?? [];
  const activeFaults = snapshot?.activeFaults ?? [];

  const selectedSignal = telemetry.find(s => s.tagName === selectedTag);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-inter selection:bg-teal-500/30 selection:text-teal-200">
      {/* Background elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 right-0 w-[800px] h-[600px] bg-teal-500/5 blur-[120px] rounded-full translate-x-1/3 -translate-y-1/2" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[400px] bg-violet-500/5 blur-[100px] rounded-full -translate-x-1/3 translate-y-1/2" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl px-6 py-4">
        <div className="max-w-[1920px] mx-auto flex items-center justify-between gap-8">
          <div className="flex items-center gap-6">
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Neural Anomaly Score</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                   <motion.div 
                     className={`h-full ${(snapshot?.anomalyScore || 0) > 0.6 ? 'bg-red-500' : 'bg-teal-500'}`}
                     animate={{ width: `${(snapshot?.anomalyScore || 0) * 100}%` }}
                   />
                </div>
                <span className={`text-[10px] font-black tabular-nums ${(snapshot?.anomalyScore || 0) > 0.6 ? 'text-red-400' : 'text-teal-400'}`}>
                  {((snapshot?.anomalyScore || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>
            
            <div className="h-8 w-[1px] bg-slate-800" />
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-teal-400 to-violet-600 text-white shadow-lg shadow-teal-500/20">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-base font-black text-white leading-none tracking-tight">PHOENIX COMMAND</h1>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] mt-1 italic">Industrial Digital Twin v2.0</p>
              </div>
            </div>
            
            <nav className="hidden lg:flex items-center gap-1 ml-4">
               <button 
                 onClick={() => setActiveView('fleet')}
                 className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-xs font-bold uppercase tracking-widest ${
                   activeView === 'fleet' ? 'bg-slate-900 border border-slate-800 text-teal-400' : 'text-slate-500 hover:text-slate-300'
                 }`}
               >
                  <LayoutDashboard className="w-3.5 h-3.5" />
                  Fleet
               </button>
               <button 
                 onClick={() => setActiveView('spatial')}
                 className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-xs font-bold uppercase tracking-widest ${
                   activeView === 'spatial' ? 'bg-slate-900 border border-slate-800 text-teal-400' : 'text-slate-500 hover:text-slate-300'
                 }`}
               >
                  <Box className="w-3.5 h-3.5" />
                  Spatial
               </button>
               <button 
                 onClick={() => setActiveView('logs')}
                 className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-xs font-bold uppercase tracking-widest ${
                   activeView === 'logs' ? 'bg-slate-900 border border-slate-800 text-teal-400' : 'text-slate-500 hover:text-slate-300'
                 }`}
               >
                  <Database className="w-3.5 h-3.5" />
                  Logs
               </button>
               <button 
                 onClick={() => setActiveView('nodes')}
                 className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-xs font-bold uppercase tracking-widest ${
                   activeView === 'nodes' ? 'bg-slate-900 border border-slate-800 text-teal-400' : 'text-slate-500 hover:text-slate-300'
                 }`}
               >
                  <Cpu className="w-3.5 h-3.5" />
                  Nodes
               </button>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800">
               <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Tick Cluster</span>
               <span className="text-[10px] font-mono text-teal-500/80 font-bold tabular-nums">#{tick.toString().padStart(6, '0')}</span>
            </div>
            
            <LiveIndicator connected={connected} />
            
            <div className="h-6 w-px bg-slate-800 mx-2" />
            
            <div className="relative group">
               <select
                 id="asset-selector"
                 value={selectedAsset}
                 onChange={e => setSelectedAsset(e.target.value)}
                 className="appearance-none bg-slate-900 border border-slate-700 text-slate-200 text-xs font-bold uppercase tracking-widest rounded-lg pl-3 pr-8 py-2 focus:outline-none focus:border-teal-500/50 cursor-pointer shadow-sm hover:border-slate-600 transition-colors"
               >
                 <option value="">Global Fleet</option>
                 {assets.map(a => (
                   <option key={a.assetId} value={a.assetId}>{a.name}</option>
                 ))}
               </select>
               <ChevronRight className="absolute right-2 top-2.5 w-3.5 h-3.5 text-slate-500 pointer-events-none group-hover:text-teal-400 rotate-90" />
            </div>
          </div>
        </div>
      </header>

      {/* Dashboard Content */}
      <main className="flex-1 w-full max-w-[1920px] mx-auto px-6 py-6 overflow-hidden">
        <AnimatePresence mode="wait">
          {activeView === 'fleet' ? (
            <motion.div 
              key="fleet-view"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.02 }}
              transition={{ duration: 0.2 }}
              className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6 h-full"
            >
              <div className="flex flex-col gap-6 min-w-0">
                <section>
                  <KpiBar kpis={kpis} />
                </section>

                <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">
                   <section className="bg-slate-900/60 border border-slate-800/80 rounded-3xl p-6 shadow-xl relative overflow-hidden min-h-[300px]">
                      <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
                         <Activity className="w-48 h-48 rotate-12" />
                      </div>
                      <TrendChart 
                        tagName={selectedSignal?.tagName || ''} 
                        currentValue={selectedSignal?.value || 0}
                        unit={selectedSignal?.unit}
                        anomalyScore={snapshot?.anomalyScore}
                      />
                   </section>

                   <section className="bg-slate-900/60 border border-slate-800/80 rounded-3xl p-6 shadow-xl min-h-[300px]">
                      <AlertPanel alerts={alerts} />
                   </section>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-6">
                  <section className="min-w-0">
                     <div className="flex items-center justify-between mb-4 px-2">
                        <div className="flex items-center gap-2">
                           <Layers className="w-4 h-4 text-teal-400" />
                           <h2 className="text-xs font-black text-slate-200 uppercase tracking-widest">Real-time Telemetry Engine</h2>
                        </div>
                        <span className="text-[10px] text-slate-600 font-bold uppercase tracking-tighter">
                           Streaming {telemetry.length} Synthetic Nodes (UNS)
                        </span>
                     </div>
                     <TelemetryTable
                       rows={telemetry}
                       selectedTag={selectedTag}
                       onSelectTag={setSelectedTag}
                     />
                  </section>

                  <section className="flex flex-col gap-4">
                     <div className="flex items-center gap-2 mb-1 px-2">
                        <Bell className="w-4 h-4 text-violet-400" />
                        <h2 className="text-xs font-black text-slate-200 uppercase tracking-widest">Stress Injection Control</h2>
                     </div>
                     <div className="flex-1 overflow-auto max-h-[360px] pr-1">
                       <FaultInjector
                         scenarios={scenarios}
                         activeFaults={activeFaults}
                         onChanged={refreshScenarios}
                       />
                     </div>
                  </section>
                </div>
              </div>

              <aside className="relative flex flex-col gap-6">
                <div className="xl:sticky xl:top-[100px] h-full xl:max-h-[calc(100vh-140px)]">
                  <ChatBot selectedAsset={selectedAsset} />
                </div>
              </aside>
            </motion.div>
          ) : activeView === 'spatial' ? (
             <motion.div
               key="spatial-view"
               initial={{ opacity: 0, scale: 0.95 }}
               animate={{ opacity: 1, scale: 1 }}
               exit={{ opacity: 0, scale: 1.05 }}
               className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6 h-full"
             >
                <div className="flex flex-col gap-6">
                   <div className="flex-1 min-h-[500px]">
                      <ThreeScene telemetry={telemetry} />
                   </div>
                   <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
                      <h3 className="text-xs font-black text-slate-200 uppercase tracking-widest mb-4">Spatial Alerts</h3>
                      <AlertPanel alerts={alerts} />
                   </div>
                </div>
                <aside className="relative flex flex-col gap-6">
                  <ChatBot selectedAsset={selectedAsset} />
                </aside>
             </motion.div>
          ) : activeView === 'logs' ? (
            <motion.div
              key="logs-view"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="h-full"
            >
               <HistoryView />
            </motion.div>
          ) : (
            <motion.div
              key="nodes-view"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="h-full"
            >
               <TopologyView />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer / Status Bar */}
      <footer className="border-t border-slate-800/60 bg-slate-950 px-6 py-2">
         <div className="max-w-[1920px] mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4 text-[9px] font-bold text-slate-600 uppercase tracking-widest">
               <span>System: Phoenix-DC-01</span>
               <span className="w-1 h-1 rounded-full bg-slate-800" />
               <span>Kernel: next-15.0</span>
               <span className="w-1 h-1 rounded-full bg-slate-800" />
               <span>Region: Global-01</span>
            </div>
            <p className="text-[9px] font-black text-slate-700 uppercase tracking-[0.3em]">
               © 2026 PHOENIX DIGITAL TWIN TECHNOLOGIES
            </p>
         </div>
      </footer>
    </div>
  );
}
