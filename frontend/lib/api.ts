import type { Asset, FaultScenario, TwinSnapshot } from './types';

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

const json = async <T>(res: Response): Promise<T> => {
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
};

export const fetchAssets = (): Promise<Asset[]> =>
  fetch(`${BASE}/idsl/assets`).then(r => json<Asset[]>(r));

export const fetchSnapshot = (): Promise<TwinSnapshot> =>
  fetch(`${BASE}/twin/snapshot`).then(r => json<TwinSnapshot>(r));

export const fetchFaultScenarios = (): Promise<FaultScenario[]> =>
  fetch(`${BASE}/twin/fault-scenarios`).then(r => json<FaultScenario[]>(r));

export const triggerFault = (scenarioId: string): Promise<FaultScenario> =>
  fetch(`${BASE}/twin/fault-scenarios/${scenarioId}/trigger`, { method: 'POST' }).then(r =>
    json<FaultScenario>(r)
  );

export const clearFault = (scenarioId: string): Promise<void> =>
  fetch(`${BASE}/twin/fault-scenarios/${scenarioId}/clear`, { method: 'POST' }).then(() => void 0);

export const sendCommand = (tagName: string, valueDelta: number): Promise<void> =>
  fetch(`${BASE}/twin/command`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tagName, valueDelta }),
  }).then(() => void 0);

export const fetchHistory = (): Promise<TwinSnapshot[]> =>
  fetch(`${BASE}/twin/history`).then(r => json<TwinSnapshot[]>(r));

export const fetchTopology = (): Promise<any> =>
  fetch(`${BASE}/twin/topology`).then(r => json<any>(r));

export const sendChat = (message: string, assetId?: string): Promise<{ reply: string }> =>
  fetch(`${BASE}/chat/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, assetId }),
  }).then(r => json<{ reply: string }>(r));

export const buildWsUrl = (): string => {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  if (typeof window === 'undefined') return '';
  if (base.startsWith('http')) return base.replace(/^http/, 'ws') + '/twin/stream';
  return `ws://${window.location.hostname}:8000/twin/stream`;
};
