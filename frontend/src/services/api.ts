import {
  Customer,
  Account,
  Transaction,
  FraudAlert,
  FraudAnalysis,
  LoanApplication,
  LoanEligibilityResult,
  AgentSpec,
  ExecutionTrace,
  AuditEvent,
  DashboardSummary,
  HealthStatus
} from '../types';

const API_BASE = '/api';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errData = await response.json();
      errorDetail = errData.detail || errData.message || errorDetail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // System Health
  getHealth: () => fetchJSON<HealthStatus>('/health'),

  // Dashboard
  getDashboardSummary: () => fetchJSON<DashboardSummary>('/dashboard/summary'),

  // Customers
  getCustomers: (search?: string) => {
    const q = search ? `?search=${encodeURIComponent(search)}` : '';
    return fetchJSON<Customer[]>(`/customers${q}`);
  },
  getCustomer: (id: string) => fetchJSON<Customer>(`/customers/${id}`),
  getCustomerAccounts: (id: string) => fetchJSON<Account[]>(`/customers/${id}/accounts`),
  getCustomerTransactions: (id: string, limit = 20) =>
    fetchJSON<Transaction[]>(`/customers/${id}/transactions?limit=${limit}`),

  // Accounts & Transactions
  getAccounts: () => fetchJSON<Account[]>('/accounts'),
  getTransactions: (limit = 50, category?: string, isFlagged?: boolean) => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (category) params.append('category', category);
    if (isFlagged !== undefined) params.append('is_flagged', isFlagged.toString());
    return fetchJSON<Transaction[]>(`/transactions?${params.toString()}`);
  },

  // Fraud & Risk
  getFraudAlerts: (status?: string) => {
    const q = status ? `?status=${encodeURIComponent(status)}` : '';
    return fetchJSON<FraudAlert[]>(`/fraud/alerts${q}`);
  },
  analyzeFraud: (transactionId: string) =>
    fetchJSON<FraudAnalysis>('/fraud/analyze', {
      method: 'POST',
      body: JSON.stringify({ transaction_id: transactionId }),
    }),

  // Loans & Credit
  getLoans: () => fetchJSON<LoanApplication[]>('/loans'),
  checkLoanEligibility: (payload: {
    customer_id: string;
    requested_amount: number;
    tenure_months: number;
    annual_interest_rate?: number;
  }) =>
    fetchJSON<LoanEligibilityResult>('/loans/eligibility', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  calculateEMI: (payload: { principal: number; annual_interest_rate: number; tenure_months: number }) =>
    fetchJSON<any>('/loans/emi', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // AI Assistant Chat
  sendChatMessage: (message: string, customerId?: string) =>
    fetchJSON<{
      request_id: string;
      answer: string;
      selected_agents: string[];
      tools_invoked: string[];
      traces: any[];
      provider: string;
      model: string;
      latency_ms: number;
      warnings: string[];
    }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, customer_id: customerId }),
    }),

  // Agents, Traces, Audit
  getAgents: () => fetchJSON<AgentSpec[]>('/agents'),
  getTraces: (requestId?: string, limit = 50) => {
    const q = requestId ? `?request_id=${encodeURIComponent(requestId)}&limit=${limit}` : `?limit=${limit}`;
    return fetchJSON<ExecutionTrace[]>(`/traces${q}`);
  },
  getAuditLogs: (eventType?: string, limit = 50) => {
    const q = eventType ? `?event_type=${encodeURIComponent(eventType)}&limit=${limit}` : `?limit=${limit}`;
    return fetchJSON<AuditEvent[]>(`/audit${q}`);
  },
};
