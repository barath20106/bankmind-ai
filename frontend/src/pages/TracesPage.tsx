import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ExecutionTrace } from '../types';
import {
  Activity,
  Search,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronRight,
  Code2
} from 'lucide-react';

export const TracesPage: React.FC = () => {
  const [traces, setTraces] = useState<ExecutionTrace[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterRequestId, setFilterRequestId] = useState('');
  const [expandedTraceId, setExpandedTraceId] = useState<string | null>(null);

  const fetchTraces = async (reqId?: string) => {
    try {
      setLoading(true);
      const data = await api.getTraces(reqId || undefined);
      setTraces(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTraces();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTraces(filterRequestId);
  };

  const avgLatency = traces.length > 0
    ? (traces.reduce((acc, t) => acc + (t.latency_ms || 0), 0) / traces.length).toFixed(1)
    : '0';

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Agent Execution Traces</h2>
          <p className="text-sm text-slate-500">
            Telemetry, agent routing latency, and tool invocation inputs/outputs
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-600">
            <span className="font-semibold text-slate-900">{traces.length}</span> Traces Logged
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-600 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-sky-600" />
            <span>Avg Latency: <strong className="text-slate-900 font-mono">{avgLatency} ms</strong></span>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex items-center justify-between gap-4">
        <form onSubmit={handleSearch} className="flex-1 relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Filter by Request ID (e.g. REQ-)..."
            value={filterRequestId}
            onChange={(e) => setFilterRequestId(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 rounded-lg border border-slate-300 text-xs focus:outline-hidden focus:border-sky-500"
          />
        </form>

        <div className="flex items-center gap-2">
          {filterRequestId && (
            <button
              onClick={() => {
                setFilterRequestId('');
                fetchTraces('');
              }}
              className="text-xs text-slate-500 hover:text-slate-700 underline"
            >
              Clear filter
            </button>
          )}
          <button
            onClick={() => fetchTraces(filterRequestId)}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
            title="Refresh traces"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Traces Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading execution traces...</div>
          ) : traces.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-400">
              No traces recorded yet. Submit inquiries in the AI Assistant to generate traces.
            </div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Step</th>
                  <th className="py-3 px-4">Request ID</th>
                  <th className="py-3 px-4">Agent</th>
                  <th className="py-3 px-4">Tool Invoked</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Payload Inspector</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {traces.map((t) => {
                  const isExpanded = expandedTraceId === t.id;
                  let parsedIn = {};
                  let parsedOut = {};
                  try {
                    parsedIn = JSON.parse(t.input_payload);
                  } catch {
                    parsedIn = { raw: t.input_payload };
                  }
                  try {
                    parsedOut = JSON.parse(t.output_payload);
                  } catch {
                    parsedOut = { raw: t.output_payload };
                  }

                  return (
                    <React.Fragment key={t.id}>
                      <tr className="hover:bg-slate-50/80 transition">
                        <td className="py-3 px-4 font-bold text-slate-500">{t.step_index}</td>
                        <td className="py-3 px-4 font-mono font-medium text-slate-800">{t.request_id}</td>
                        <td className="py-3 px-4">
                          <span className="font-semibold text-slate-900 px-2 py-0.5 rounded bg-slate-100 border border-slate-200">
                            {t.agent_name}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-sky-700 font-semibold">{t.tool_name}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                              t.status === 'SUCCESS'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {t.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-600">{t.latency_ms} ms</td>
                        <td className="py-3 px-4 text-slate-400 text-[11px]">
                          {new Date(t.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => setExpandedTraceId(isExpanded ? null : t.id)}
                            className="flex items-center gap-1 text-sky-600 hover:text-sky-800 font-semibold"
                          >
                            <Code2 className="w-3.5 h-3.5" />
                            <span>{isExpanded ? 'Collapse' : 'Inspect'}</span>
                          </button>
                        </td>
                      </tr>

                      {/* Expandable JSON Detail Row */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={8} className="p-4 bg-slate-900 text-white border-t border-slate-800">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-[11px]">
                              <div>
                                <span className="text-slate-400 font-semibold block mb-1">
                                  Input Arguments:
                                </span>
                                <pre className="p-3 bg-slate-950 rounded-lg text-sky-300 overflow-x-auto max-h-48 border border-slate-800">
                                  {JSON.stringify(parsedIn, null, 2)}
                                </pre>
                              </div>
                              <div>
                                <span className="text-slate-400 font-semibold block mb-1">
                                  Execution Output Result:
                                </span>
                                <pre className="p-3 bg-slate-950 rounded-lg text-emerald-300 overflow-x-auto max-h-48 border border-slate-800">
                                  {JSON.stringify(parsedOut, null, 2)}
                                </pre>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
