export interface Customer {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  city: string;
  kyc_status: 'VERIFIED' | 'PENDING' | 'REJECTED';
  credit_score: number;
  monthly_income: number;
  created_at?: string;
}

export interface Account {
  id: string;
  customer_id: string;
  account_number: string;
  account_type: string;
  balance: number;
  currency: string;
  status: 'ACTIVE' | 'DORMANT' | 'FROZEN';
  created_at?: string;
}

export interface Transaction {
  id: string;
  account_id: string;
  customer_id: string;
  amount: number;
  txn_type: 'DEBIT' | 'CREDIT';
  category: string;
  merchant: string;
  location: string;
  timestamp: string;
  status: 'COMPLETED' | 'PENDING' | 'FLAGGED' | 'REVERSED';
  is_flagged: boolean;
  flag_reason?: string | null;
}

export interface FraudAlert {
  id: string;
  transaction_id: string;
  customer_id: string;
  risk_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  rule_triggered: string;
  status: 'NEW' | 'INVESTIGATING' | 'RESOLVED' | 'DISMISSED';
  review_notes?: string | null;
  created_at: string;
}

export interface FraudAnalysis {
  transaction_id: string;
  customer_id: string;
  amount: number;
  merchant: string;
  location: string;
  risk_score: number;
  risk_level: string;
  triggered_rules: string[];
  recommended_action: string;
  is_flagged: boolean;
  disclaimer: string;
}

export interface LoanApplication {
  id: string;
  customer_id: string;
  requested_amount: number;
  tenure_months: number;
  purpose: string;
  monthly_income: number;
  existing_obligations: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'UNDER_REVIEW';
  interest_rate: number;
  estimated_emi: number;
  dti_ratio: number;
  notes?: string | null;
  created_at: string;
}

export interface LoanEligibilityResult {
  customer_id: string;
  customer_name: string;
  requested_amount: number;
  tenure_months: number;
  monthly_income: number;
  existing_obligations: number;
  estimated_emi: number;
  proposed_total_obligations: number;
  debt_to_income_ratio: number;
  max_permissible_dti: number;
  credit_score: number;
  min_required_credit_score: number;
  applicable_interest_rate: number;
  is_eligible: boolean;
  status: string;
  reasons: string[];
  disclaimer: string;
}

export interface AgentTraceItem {
  step_index: number;
  agent_name: string;
  tool_name: string;
  status: string;
  latency_ms: number;
  input_payload: Record<string, any>;
  output_payload: Record<string, any>;
  summary: string;
  warning?: string | null;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  selected_agents?: string[];
  tools_invoked?: string[];
  traces?: AgentTraceItem[];
  provider?: string;
  model?: string;
  latency_ms?: number;
  warnings?: string[];
}

export interface AgentSpec {
  name: string;
  role: string;
  description: string;
  capabilities: string[];
  tools: string[];
}

export interface ExecutionTrace {
  id: string;
  request_id: string;
  step_index: number;
  timestamp: string;
  agent_name: string;
  tool_name: string;
  status: string;
  latency_ms: number;
  input_payload: string;
  output_payload: string;
  warning?: string | null;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  actor: string;
  event_type: string;
  request_id: string;
  details: Record<string, any>;
}

export interface DashboardSummary {
  total_customers: number;
  total_accounts: number;
  total_deposits: number;
  total_transactions: number;
  flagged_transactions_count: number;
  active_fraud_alerts: number;
  total_loan_applications: number;
  system_status: string;
  currency: string;
  activity_chart: { name: string; volume: number; count: number }[];
  recent_transactions: Transaction[];
  recent_alerts: FraudAlert[];
}

export interface HealthStatus {
  status: string;
  database: string;
  llm_provider: string;
  llm_model: string;
  llm_mode: string;
  is_simulated_system: boolean;
  version: string;
}
