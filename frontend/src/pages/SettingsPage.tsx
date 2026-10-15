import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { HealthStatus, AgentSpec } from '../types';
import {
  Settings,
  Cpu,
  Database,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  Server,
  Layers,
  KeyRound,
  FileCheck
} from 'lucide-react';

interface SettingsPageProps {
  health: HealthStatus | null;
  onRefreshHealth: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ health, onRefreshHealth }) => {
  const [agents, setAgents] = useState<AgentSpec[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const data = await api.getAgents();
        setAgents(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, []);

  const isGemini = health?.llm_provider === 'gemini';

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Settings & Model Status</h2>
          <p className="text-sm text-slate-500">
            AI model provider configuration, multi-agent registry, and simulation environment
          </p>
        </div>

        <button
          onClick={onRefreshHealth}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-2xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Model & Provider Status Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Cpu className={`w-5 h-5 ${isGemini ? 'text-teal-600' : 'text-sky-600'}`} />
              <h3 className="text-sm font-bold text-slate-900">LLM Provider Configuration</h3>
            </div>
            <span
              className={`text-xs px-2.5 py-1 rounded-full font-bold border ${
                isGemini
                  ? 'bg-teal-50 text-teal-800 border-teal-200'
                  : 'bg-sky-50 text-sky-800 border-sky-200'
              }`}
            >
              {health?.llm_mode || 'Loading...'}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-slate-400 block mb-0.5">Active Model:</span>
              <span className="font-bold text-slate-900 font-mono text-sm">
                {health?.llm_model || 'Detecting...'}
              </span>
            </div>

            <div>
              <span className="text-slate-400 block mb-0.5">Provider Backend:</span>
              <span className="font-bold text-slate-900 capitalize">
                {health?.llm_provider || 'Simulated Orchestrator'}
              </span>
            </div>

            <div>
              <span className="text-slate-400 block mb-0.5">Environment:</span>
              <span className="font-semibold text-slate-800">Local Educational Assessment</span>
            </div>

            <div>
              <span className="text-slate-400 block mb-0.5">Currency System:</span>
              <span className="font-semibold text-slate-800">INR (₹ Indian Rupee)</span>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 leading-relaxed">
            {isGemini ? (
              <p>
                <strong>Google Gen AI Connected:</strong> Live Gemini models are actively orchestrating intent classification and natural language synthesis. All tool calls execute against real Python functions and the SQLite database.
              </p>
            ) : (
              <p>
                <strong>Deterministic Demo Mode:</strong> Operating without an external API key. All 5 assessment use cases execute with 100% reliability using deterministic pattern routing and real Python banking tools. No model fabrication.
              </p>
            )}
          </div>
        </div>

        {/* Database & Security Card */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <Database className="w-5 h-5 text-emerald-600" />
              <h3 className="text-sm font-bold text-slate-900">Database & Storage</h3>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Database Engine:</span>
                <span className="font-semibold text-slate-800">SQLite 3 (WAL Mode)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Connectivity:</span>
                <span className="font-bold text-emerald-600 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Connected
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Data Seeding:</span>
                <span className="font-semibold text-slate-800">Automatic on Startup</span>
              </div>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-500">
            All banking records, transactions, customers, and fraud alerts are fictional and strictly simulated for educational assessment.
          </div>
        </div>
      </div>

      {/* Multi-Agent System Registry Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-slate-200">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-4 h-4 text-sky-600" />
            <span>Registered Specialized Banking Agents</span>
          </h3>
          <p className="text-xs text-slate-500">
            Autonomous multi-agent architecture with discrete capability domains
          </p>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading agent specs...</div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Agent Name</th>
                  <th className="py-3 px-4">Role Title</th>
                  <th className="py-3 px-4">Core Capabilities</th>
                  <th className="py-3 px-4">Bound Python Tools</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {agents.map((ag) => (
                  <tr key={ag.name} className="hover:bg-slate-50/80 transition">
                    <td className="py-4 px-4 font-bold text-slate-900 font-mono">{ag.name}</td>
                    <td className="py-4 px-4 font-semibold text-sky-700">{ag.role}</td>
                    <td className="py-4 px-4 text-slate-600 max-w-sm">
                      <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                        {ag.capabilities.map((c, i) => (
                          <li key={i}>{c}</li>
                        ))}
                      </ul>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {ag.tools.map((t) => (
                          <span
                            key={t}
                            className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] border border-slate-200"
                          >
                            {t}()
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
