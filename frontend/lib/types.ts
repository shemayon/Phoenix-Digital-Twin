export interface Asset {
  assetId: string;
  name: string;
  location: string | null;
  status: string | null;
  performancePct: number | null;
  energyUsage: number | null;
  temperature: number | null;
  downtimeHours: number | null;
}

export interface TelemetryValue {
  source: 'plc' | 'scada';
  signalId: string;
  tagName: string;
  description?: string | null;
  unit?: string | null;
  value: number;
  status: 'normal' | 'warning' | 'critical';
  timestamp: string;
}

export interface TwinAlert {
  alertId: string;
  message: string;
  severity: 'normal' | 'warning' | 'critical';
  tagName?: string | null;
  originatedFrom: 'plc' | 'scada';
  detectedAt: string;
}

export interface PredictiveSuggestion {
  suggestionId: string;
  title: string;
  description: string;
  severity: 'normal' | 'warning' | 'critical';
  relatedAssets: string[];
  recommendedActions: string[];
  confidence: number;
  etaHours: number;
}

export interface KpiMetric {
  id: string;
  name: string;
  value: number;
  unit?: string | null;
  trend: number;
  status: 'normal' | 'warning' | 'critical';
}

export interface ActiveFault {
  scenarioId: string;
  name: string;
  severity: 'normal' | 'warning' | 'critical';
  remainingTicks: number;
  startedAt: string;
}

export interface TwinCommand {
  tagName: string;
  valueDelta: number;
}

export interface TwinSnapshot {
  generatedAt: string;
  simulationTime: number;
  telemetry: TelemetryValue[];
  alerts: TwinAlert[];
  predictiveSuggestions: PredictiveSuggestion[];
  kpis: KpiMetric[];
  activeFaults: ActiveFault[];
  anomalyScore: number;
}

export interface FaultScenario {
  scenarioId: string;
  name: string;
  description: string;
  targetTag: string;
  delta: number;
  durationTicks: number;
  severity: 'normal' | 'warning' | 'critical';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}
