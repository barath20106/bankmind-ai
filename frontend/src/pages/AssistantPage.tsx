import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import { ChatMessage, AgentTraceItem } from '../types';
import {
  Send,
  Bot,
  User,
  Activity,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  ChevronRight,
  ChevronDown,
  Info,
  RefreshCw,
  Cpu
} from 'lucide-react';

export const AssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text: "👋 Welcome to **BankMind AI**! I am your autonomous banking intelligence supervisor. Ask me anything about customer balances, transaction spending, fraud investigations, or loan eligibility. You can type your request or click any of the recommended scenarios below.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeMessageId, setActiveMessageId] = useState<string | null>(null);
  const [expandedTraceIdx, setExpandedTraceIdx] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (messageText?: string) => {
    const textToSend = (messageText || inputMessage).trim();
    if (!textToSend || loading) return;

    const userMsgId = `user-${Date.now()}`;
    const userMessage: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await api.sendChatMessage(textToSend);

      const assistantMsgId = response.request_id || `asst-${Date.now()}`;
      const assistantMessage: ChatMessage = {
        id: assistantMsgId,
        sender: 'assistant',
        text: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        selected_agents: response.selected_agents,
        tools_invoked: response.tools_invoked,
        traces: response.traces,
        provider: response.provider,
        model: response.model,
        latency_ms: response.latency_ms,
        warnings: response.warnings,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setActiveMessageId(assistantMsgId);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: `⚠️ **Error communicating with supervisor agent:** ${err.message || 'Please check backend server connectivity.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        warnings: ['Backend connection or tool execution failure.'],
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const activeMessage = messages.find((m) => m.id === activeMessageId) ||
    [...messages].reverse().find((m) => m.sender === 'assistant' && m.traces && m.traces.length > 0);

  const suggestedPrompts = [
    {
      title: 'Use Case 1: Account Balance',
      tag: 'Banking',
      query: 'What is the current balance of customer CUST-1001?',
    },
    {
      title: 'Use Case 2: Spending Summary',
      tag: 'Analytics',
      query: 'Show the last 10 transactions for customer CUST-1001 and summarize their spending.',
    },
    {
      title: 'Use Case 3: Fraud Investigation',
      tag: 'Risk/Fraud',
      query: 'Investigate transaction TXN-3001. Why was it flagged?',
    },
    {
      title: 'Use Case 4: Loan Eligibility',
      tag: 'Credit',
      query: 'Can customer CUST-1002 qualify for a loan of ₹300000 over 36 months?',
    },
    {
      title: 'Use Case 5: Cross-Agent Review',
      tag: 'Multi-Agent',
      query: "Review customer CUST-1001's spending, check for suspicious activity, and suggest whether a loan payment would be affordable.",
    },
  ];

  return (
    <div className="flex h-full overflow-hidden bg-slate-50">
      {/* Left Chat Section */}
      <div className="flex-1 flex flex-col border-r border-slate-200 bg-white">
        {/* Suggested Prompt Chips */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 overflow-x-auto flex gap-2 shrink-0">
          {suggestedPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p.query)}
              disabled={loading}
              className="text-left shrink-0 px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:border-sky-400 hover:bg-sky-50/50 text-xs text-slate-700 transition shadow-2xs group flex items-center gap-2"
            >
              <span className="font-semibold text-sky-700">{p.title}:</span>
              <span className="text-slate-600 truncate max-w-xs">{p.query}</span>
            </button>
          ))}
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            const isSelected = activeMessage?.id === msg.id;

            return (
              <div
                key={msg.id}
                onClick={() => {
                  if (msg.traces && msg.traces.length > 0) {
                    setActiveMessageId(msg.id);
                  }
                }}
                className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''} ${
                  msg.traces && msg.traces.length > 0 ? 'cursor-pointer' : ''
                }`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    isUser
                      ? 'bg-slate-800 text-white'
                      : 'bg-gradient-to-tr from-sky-600 to-teal-500 text-white shadow-xs'
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div className={`space-y-1.5 max-w-2xl`}>
                  <div
                    className={`p-4 rounded-2xl text-xs leading-relaxed transition ${
                      isUser
                        ? 'bg-sky-600 text-white rounded-tr-none'
                        : `bg-white border text-slate-800 rounded-tl-none shadow-xs ${
                            isSelected
                              ? 'border-sky-400 ring-2 ring-sky-100'
                              : 'border-slate-200/90'
                          }`
                    }`}
                  >
                    <div className="whitespace-pre-wrap font-sans prose prose-xs max-w-none">
                      {msg.text}
                    </div>

                    {/* Agent Pill Footer */}
                    {!isUser && msg.selected_agents && msg.selected_agents.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center gap-1.5 text-[10px]">
                        <span className="text-slate-400 font-medium">Orchestrated:</span>
                        {msg.selected_agents.map((ag) => (
                          <span
                            key={ag}
                            className="px-1.5 py-0.5 rounded bg-sky-50 text-sky-700 font-semibold border border-sky-200"
                          >
                            {ag}
                          </span>
                        ))}
                        {msg.latency_ms && (
                          <span className="ml-auto text-slate-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {msg.latency_ms} ms
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className={`text-[10px] text-slate-400 px-1 ${isUser ? 'text-right' : ''}`}>
                    {msg.timestamp}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex gap-3 max-w-xl">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-600 to-teal-500 text-white flex items-center justify-center shrink-0 shadow-xs">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-4 rounded-2xl bg-white border border-slate-200 rounded-tl-none shadow-xs text-xs space-y-2">
                <div className="flex items-center gap-2 text-sky-700 font-semibold">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Supervisor decomposing request & invoking banking tools...</span>
                </div>
                <p className="text-slate-500 text-[11px]">
                  Classifying intent, querying SQLite source of truth, and synthesizing grounded answer.
                </p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-4 bg-white border-t border-slate-200">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask a banking question (e.g. 'What is the balance of customer CUST-1001?')..."
              disabled={loading}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-hidden focus:border-sky-500 focus:ring-2 focus:ring-sky-100 text-xs text-slate-800 placeholder-slate-400"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="px-4 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-xs"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Submit</span>
            </button>
          </form>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
            <span>Grounding: 100% verified tool execution against simulated SQLite database.</span>
            <span>Simulated & Non-binding</span>
          </div>
        </div>
      </div>

      {/* Right Agent Execution Timeline / Telemetry Drawer */}
      <div className="w-96 border-l border-slate-200 bg-white flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-sky-600" />
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Agent Execution Telemetry
            </h3>
          </div>
          {activeMessage?.provider && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold border border-slate-200">
              {activeMessage.provider}
            </span>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!activeMessage?.traces || activeMessage.traces.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs space-y-2">
              <Sparkles className="w-8 h-8 mx-auto text-slate-300" />
              <p className="font-semibold text-slate-600">No execution traces active</p>
              <p className="text-[11px] text-slate-400 max-w-xs mx-auto">
                Submit an inquiry or select a message to inspect step-by-step specialist agent routing and real tool payloads.
              </p>
            </div>
          ) : (
            <>
              {/* Telemetry Summary Card */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1.5">
                <div className="flex items-center justify-between font-semibold text-slate-800">
                  <span>Request ID:</span>
                  <span className="font-mono text-sky-600">{activeMessage.id}</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Total Latency:</span>
                  <span className="font-medium text-slate-800">{activeMessage.latency_ms || 0} ms</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Model Engine:</span>
                  <span className="font-medium text-slate-800">{activeMessage.model || 'Deterministic'}</span>
                </div>
              </div>

              {/* Step-by-Step Execution Timeline */}
              <div className="space-y-3">
                <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Invocation Sequence ({activeMessage.traces.length} steps)
                </h4>

                <div className="space-y-2">
                  {activeMessage.traces.map((trace, idx) => {
                    const isExpanded = expandedTraceIdx === idx;
                    return (
                      <div
                        key={idx}
                        className="p-3 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-2 text-xs transition"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-1.5">
                            <span className="w-5 h-5 rounded-full bg-sky-100 text-sky-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                              {trace.step_index || idx + 1}
                            </span>
                            <div>
                              <span className="font-bold text-slate-900 block leading-tight">
                                {trace.agent_name}
                              </span>
                              <span className="font-mono text-[10px] text-sky-600">
                                {trace.tool_name}()
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center gap-1 text-[10px]">
                            <span
                              className={`px-1.5 py-0.5 rounded font-semibold ${
                                trace.status === 'SUCCESS'
                                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                  : 'bg-red-50 text-red-700 border border-red-200'
                              }`}
                            >
                              {trace.status}
                            </span>
                            <span className="text-slate-400">{trace.latency_ms}ms</span>
                          </div>
                        </div>

                        <p className="text-[11px] text-slate-600 leading-snug">{trace.summary}</p>

                        {/* Expandable JSON Payload */}
                        <div className="pt-1 border-t border-slate-100">
                          <button
                            onClick={() => setExpandedTraceIdx(isExpanded ? null : idx)}
                            className="flex items-center gap-1 text-[10px] text-slate-400 hover:text-slate-600 font-semibold"
                          >
                            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                            <span>{isExpanded ? 'Hide Payload' : 'View Input / Output Payload'}</span>
                          </button>

                          {isExpanded && (
                            <div className="mt-2 space-y-2 text-[10px] font-mono">
                              <div>
                                <span className="text-slate-500 font-semibold block">Input:</span>
                                <pre className="p-2 bg-slate-900 text-slate-200 rounded-md overflow-x-auto max-h-32">
                                  {JSON.stringify(trace.input_payload, null, 2)}
                                </pre>
                              </div>
                              <div>
                                <span className="text-slate-500 font-semibold block">Output:</span>
                                <pre className="p-2 bg-slate-900 text-emerald-300 rounded-md overflow-x-auto max-h-36">
                                  {JSON.stringify(trace.output_payload, null, 2)}
                                </pre>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
