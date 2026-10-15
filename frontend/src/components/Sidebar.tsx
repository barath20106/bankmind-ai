import React from 'react';
import {
  LayoutDashboard,
  Bot,
  Users,
  CreditCard,
  ShieldAlert,
  Coins,
  Activity,
  ScrollText,
  Settings,
  Cpu
} from 'lucide-react';
import { HealthStatus } from '../types';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  health: HealthStatus | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, health }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'assistant', label: 'AI Assistant', icon: Bot, badge: 'Multi-Agent' },
    { id: 'customers', label: 'Customers', icon: Users },
    { id: 'accounts', label: 'Accounts & Ledger', icon: CreditCard },
    { id: 'fraud', label: 'Fraud & Risk', icon: ShieldAlert, badgeAlert: true },
    { id: 'credit', label: 'Credit & Loans', icon: Coins },
    { id: 'traces', label: 'Agent Traces', icon: Activity },
    { id: 'audit', label: 'Audit Log', icon: ScrollText },
    { id: 'settings', label: 'Settings & Model', icon: Settings },
  ];

  const isGemini = health?.llm_provider === 'gemini';

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-sky-600 to-teal-500 flex items-center justify-center text-white font-bold shadow-md shadow-sky-900/30">
            BM
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
              BankMind <span className="text-xs px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 font-semibold border border-sky-400/30">AI</span>
            </h1>
            <p className="text-[11px] text-slate-400">Multi-Agent Banking Platform</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-sky-600 text-white shadow-sm shadow-sky-700/50'
                    : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-300 font-medium border border-teal-500/30">
                    {item.badge}
                  </span>
                )}
                {item.badgeAlert && (
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Model & System Status Widget */}
      <div className="p-3 m-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
        <div className="flex items-center gap-2 mb-1.5">
          <Cpu className={`w-3.5 h-3.5 ${isGemini ? 'text-teal-400' : 'text-sky-400'}`} />
          <span className="font-semibold text-slate-200">Active Engine</span>
        </div>
        <div className="flex items-center gap-1.5 mb-1">
          <span className={`w-2 h-2 rounded-full ${isGemini ? 'bg-teal-400' : 'bg-emerald-400'}`}></span>
          <p className="text-slate-300 font-medium truncate">
            {health?.llm_mode || 'Loading status...'}
          </p>
        </div>
        <p className="text-[11px] text-slate-400 truncate">
          {health?.llm_model || 'System Initializing'}
        </p>

        <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
          <span>Mode: Simulated</span>
          <span className="text-slate-400">INR (₹)</span>
        </div>
      </div>
    </aside>
  );
};
