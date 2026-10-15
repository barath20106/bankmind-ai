import React from 'react';
import { HealthStatus } from '../types';
import { ShieldCheck, Sparkles, Database } from 'lucide-react';

interface HeaderProps {
  currentTab: string;
  health: HealthStatus | null;
}

const tabTitles: Record<string, { title: string; subtitle: string }> = {
  overview: {
    title: 'Executive Banking Dashboard',
    subtitle: 'Real-time telemetry, deposit volumes, risk alerts, and operational metrics',
  },
  assistant: {
    title: 'AI Banking Assistant',
    subtitle: 'Autonomous Supervisor orchestrating Banking, Risk, Credit, and Compliance specialists',
  },
  customers: {
    title: 'Customer Directory & Accounts',
    subtitle: 'Fictional demo customer records, KYC status, and linked banking accounts',
  },
  accounts: {
    title: 'Simulated Accounts & Ledger',
    subtitle: 'Live balance ledgers, transaction records, and category spending analytics',
  },
  fraud: {
    title: 'Fraud & Risk Surveillance Center',
    subtitle: 'Deterministic rule evaluations, offshore wire surveillance, and risk scoring',
  },
  credit: {
    title: 'Credit Underwriting & Loan Eligibility',
    subtitle: 'Automated debt-to-income (DTI) assessment and EMI schedule calculation',
  },
  traces: {
    title: 'Multi-Agent Execution Traces',
    subtitle: 'Granular step-by-step telemetry, latency measurements, and tool inputs/outputs',
  },
  audit: {
    title: 'Regulatory & Governance Audit Trail',
    subtitle: 'Immutable compliance events, AML surveillance triggers, and operator actions',
  },
  settings: {
    title: 'Settings & Model Configuration',
    subtitle: 'Google Gen AI provider controls, environment status, and seed data utilities',
  },
};

export const Header: React.FC<HeaderProps> = ({ currentTab, health }) => {
  const current = tabTitles[currentTab] || {
    title: 'BankMind AI Platform',
    subtitle: 'Simulated multi-agent banking system',
  };

  const isGemini = health?.llm_provider === 'gemini';

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between">
      <div>
        <h2 className="text-base font-bold text-slate-900 tracking-tight">{current.title}</h2>
        <p className="text-xs text-slate-500">{current.subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Environment Simulation Pill */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 text-xs border border-slate-200">
          <ShieldCheck className="w-3.5 h-3.5 text-slate-500" />
          <span className="font-medium">Simulated Banking Sandbox</span>
        </div>

        {/* Database Status Indicator */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs border border-emerald-200/80">
          <Database className="w-3 h-3 text-emerald-600" />
          <span className="font-medium">SQLite Connected</span>
        </div>

        {/* Active Engine Badge */}
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
            isGemini
              ? 'bg-teal-50 text-teal-800 border-teal-300'
              : 'bg-sky-50 text-sky-800 border-sky-300'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-sky-600" />
          <span>{health?.llm_mode || 'Demo Engine'}</span>
        </div>
      </div>
    </header>
  );
};
