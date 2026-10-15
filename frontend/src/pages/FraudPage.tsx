import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { FraudAlert, FraudAnalysis } from '../types';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  Search,
  RefreshCw,
  Sliders,
  ShieldCheck,
  Zap,
  Lock,
  ArrowRight
} from 'lucide-react';

export const FraudPage: React.FC = () => {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  
  // Interactive Risk Analyzer state
  const [analyzeTxnId, setAnalyzeTxnId] = useState('TXN-3001');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<FraudAnalysis | null>(null);
  const [analyzerError, setAnalyzerError] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await api.getFraudAlerts(statusFilter || undefined);
      setAlerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    runAnalysis('TXN-3001');
  }, [statusFilter]);

  const runAnalysis = async (txnIdToAnalyze?: string) => {
    const target = txnIdToAnalyze || analyzeTxnId;
    if (!target.trim()) return;

    try {
      setAnalyzing(true);
      setAnalyzerError(null);
      const res = await api.analyzeFraud(target.trim());
      setAnalysisResult(res);
    } catch (err: any) {
      setAnalyzerError(err.message || 'Transaction not found or analysis error');
      setAnalysisResult(null);
    } finally {
      setAnalyzing(false);
    }
  };

  const demoScenarios = [
    { id: 'TXN-3001', label: 'TXN-3001 (Offshore Dubai Wire - Critical)', risk: 'CRITICAL' },
    { id: 'TXN-3017', label: 'TXN-3017 (Crypto P2P Zurich - Critical)', risk: 'CRITICAL' },
    { id: 'TXN-3019', label: 'TXN-3019 (Velocity Structuring ₹49,999 - High)', risk: 'HIGH' },
    { id: 'TXN-3004', label: 'TXN-3004 (Standard Grocery Mumbai - Low)', risk: 'LOW' },
  ];

  const criticalCount = alerts.filter((a) => a.severity === 'CRITICAL').length;
  const highCount = alerts.filter((a) => a.severity === 'HIGH').length;

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header & Metrics */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Fraud & Risk Surveillance Center</h2>
          <p className="text-sm text-slate-500">
            Deterministic AML rules, suspicious velocity detection, and behavioral telemetry
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-50 text-red-700 border border-red-200 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
            <span>{criticalCount} Critical Alerts</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-xs font-semibold">
            <span>{highCount} High Risk</span>
          </div>
        </div>
      </div>

      {/* Interactive Transaction Risk Investigator */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-md border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <h3 className="text-sm font-bold text-white tracking-wide uppercase">
              Interactive Deterministic Risk Investigator
            </h3>
          </div>
          <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
            Rule-Based Engine (Use Case 3)
          </span>
        </div>

        {/* Input Bar & Preset Chips */}
        <div className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={analyzeTxnId}
              onChange={(e) => setAnalyzeTxnId(e.target.value.toUpperCase())}
              placeholder="Enter Transaction ID (e.g. TXN-3001)..."
              className="px-4 py-2 bg-slate-950/80 border border-slate-700 rounded-xl text-xs font-mono text-white placeholder-slate-500 focus:outline-hidden focus:border-amber-400 flex-1"
            />
            <button
              onClick={() => runAnalysis()}
              disabled={analyzing}
              className="px-5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-xl transition flex items-center gap-1.5 disabled:opacity-50"
            >
              {analyzing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldAlert className="w-3.5 h-3.5" />}
              <span>Inspect Risk</span>
            </button>
          </div>

          {/* Quick Scenario Chips */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 text-[11px]">Test Presets:</span>
            {demoScenarios.map((sc) => (
              <button
                key={sc.id}
                onClick={() => {
                  setAnalyzeTxnId(sc.id);
                  runAnalysis(sc.id);
                }}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-medium border transition ${
                  analyzeTxnId === sc.id
                    ? 'bg-amber-400/20 text-amber-300 border-amber-400/40'
                    : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700'
                }`}
              >
                {sc.label}
              </button>
            ))}
          </div>
        </div>

        {/* Analysis Output Box */}
        {analyzerError && (
          <div className="mt-4 p-3 bg-red-950/60 border border-red-800/80 rounded-xl text-red-300 text-xs">
            {analyzerError}
          </div>
        )}

        {analysisResult && (
          <div className="mt-5 pt-5 border-t border-slate-700/80 grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Score & Verdict Card */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-700 flex flex-col justify-between">
              <div>
                <span className="text-[11px] text-slate-400 block uppercase font-semibold">Risk Score</span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span
                    className={`text-4xl font-extrabold font-mono ${
                      analysisResult.risk_score >= 80
                        ? 'text-red-400'
                        : analysisResult.risk_score >= 60
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {analysisResult.risk_score}
                  </span>
                  <span className="text-slate-500 text-xs">/ 100</span>
                </div>
                <div className="mt-2 flex items-center gap-1.5">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      analysisResult.risk_level === 'CRITICAL'
                        ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                        : analysisResult.risk_level === 'HIGH'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}
                  >
                    {analysisResult.risk_level} LEVEL
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800">
                <span className="text-[10px] text-slate-400 block">Recommended Review Action:</span>
                <span className="font-mono text-xs font-bold text-amber-300">
                  {analysisResult.recommended_action}
                </span>
              </div>
            </div>

            {/* Transaction Facts */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-700 space-y-2 text-xs">
              <span className="text-[11px] text-slate-400 block uppercase font-semibold">Ledger Telemetry</span>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Transaction ID:</span>
                <span className="font-mono font-bold text-white">{analysisResult.transaction_id}</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Customer:</span>
                <span className="font-mono text-sky-400">{analysisResult.customer_id}</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Amount:</span>
                <span className="font-bold text-white">₹{analysisResult.amount.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Merchant:</span>
                <span className="font-semibold text-slate-200">{analysisResult.merchant}</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Location Origin:</span>
                <span className="font-semibold text-slate-200">{analysisResult.location}</span>
              </div>
            </div>

            {/* Triggered Rules */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-700 space-y-2 text-xs">
              <span className="text-[11px] text-slate-400 block uppercase font-semibold">
                Deterministic Rules Triggered ({analysisResult.triggered_rules.length})
              </span>
              <div className="space-y-1.5 max-h-36 overflow-y-auto">
                {analysisResult.triggered_rules.map((r, i) => (
                  <div key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5 leading-snug">
                    <span className="text-amber-400 shrink-0">•</span>
                    <span>{r}</span>
                  </div>
                ))}
              </div>
              <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800">
                {analysisResult.disclaimer}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Surveillance Alerts Ledger */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Seeded Surveillance Alerts</h3>
            <p className="text-xs text-slate-500">Live fraud queue monitored by RiskFraudAgent</p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs text-slate-700 bg-white"
            >
              <option value="">All Statuses</option>
              <option value="NEW">NEW</option>
              <option value="INVESTIGATING">INVESTIGATING</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
            <button
              onClick={fetchAlerts}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading surveillance alerts...</div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Alert ID</th>
                  <th className="py-3 px-4">Transaction</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Severity & Score</th>
                  <th className="py-3 px-4">Triggered Rule Policy</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Review Notes</th>
                  <th className="py-3 px-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {alerts.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">{a.id}</td>
                    <td className="py-3 px-4 font-mono text-sky-700 font-semibold">{a.transaction_id}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">{a.customer_id}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                          a.severity === 'CRITICAL'
                            ? 'bg-red-100 text-red-700'
                            : a.severity === 'HIGH'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-blue-100 text-blue-700'
                        }`}
                      >
                        {a.severity} ({a.risk_score})
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-700 max-w-xs">{a.rule_triggered}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">
                        {a.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 text-[11px]">{a.review_notes || '—'}</td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => {
                          setAnalyzeTxnId(a.transaction_id);
                          runAnalysis(a.transaction_id);
                        }}
                        className="text-sky-600 hover:text-sky-800 font-semibold text-xs flex items-center gap-1"
                      >
                        <span>Investigate</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
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
