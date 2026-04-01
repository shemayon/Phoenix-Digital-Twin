'use client';

import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { TelemetryValue } from '@/lib/types';
import { Activity } from 'lucide-react';

interface HistoryPoint {
  time: string;
  value: number;
  anomaly?: number;
}

export default function TrendChart({
  tagName,
  currentValue,
  unit,
  anomalyScore,
}: {
  tagName: string;
  currentValue: number;
  unit?: string | null;
  anomalyScore?: number;
}) {
  const [history, setHistory] = useState<HistoryPoint[]>([]);

  useEffect(() => {
    if (!tagName) return;

    setHistory(prev => {
      const now = new Date().toLocaleTimeString([], { hour12: false });
      const next = [...prev, { time: now, value: currentValue, anomaly: (anomalyScore || 0) * 100 }];
      // Keep last 30 points
      return next.slice(-30);
    });
  }, [tagName, currentValue, anomalyScore]);

  // If tag changes, reset history (optional, or keep it if it's the same tag)
  useEffect(() => {
    setHistory([]);
  }, [tagName]);

  if (!tagName) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-600 bg-slate-900/40 rounded-2xl border border-slate-800/50 border-dashed p-8">
        <Activity className="w-12 h-12 mb-4 opacity-20" />
        <p className="text-sm font-medium">Select a signal from the table to view trend</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-teal-400 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Live Trend: {tagName}
          </h3>
          <p className="text-[10px] text-slate-500 uppercase tracking-tighter">
            Real-time Telemetry History (Last 30s)
          </p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-black text-white tabular-nums">
            {currentValue.toFixed(2)}
          </span>
          <span className="text-xs text-slate-500 ml-1 font-medium">{unit}</span>
        </div>
      </div>

      <div className="flex-1 min-h-[200px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="time"
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
              minTickGap={30}
            />
            <YAxis
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              domain={['auto', 'auto']}
              tickFormatter={(v: number) => v.toFixed(1)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                fontSize: '11px',
                color: '#f1f5f9',
              }}
              itemStyle={{ color: '#2dd4bf' }}
              cursor={{ stroke: '#2dd4bf', strokeWidth: 1, strokeDasharray: '4 4' }}
            />
            <Line
              type="monotone"
              dataKey="value"
              name="Signal Value"
              stroke="#2dd4bf"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
              activeDot={{ r: 4, fill: '#2dd4bf', stroke: '#111827', strokeWidth: 2 }}
            />
            <Line
              type="monotone"
              dataKey="anomaly"
              name="Neural Anomaly Score (%)"
              stroke="#f43f5e"
              strokeWidth={1.5}
              strokeDasharray="5 5"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
