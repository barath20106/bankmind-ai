import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { LoanApplication, Customer, LoanEligibilityResult } from '../types';
import {
  Coins,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Calculator,
  RefreshCw,
  Scale,
  ShieldCheck,
  Percent,
  Calendar,
  AlertCircle
} from 'lucide-react';

export const CreditPage: React.FC = () => {
  const [loans, setLoans] = useState<LoanApplication[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  // Calculator inputs
  const [selectedCustomerId, setSelectedCustomerId] = useState('CUST-1002');
  const [requestedAmount, setRequestedAmount] = useState(300000);
  const [tenureMonths, setTenureMonths] = useState(36);
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<LoanEligibilityResult | null>(null);
  const [calcError, setCalcError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [loansData, custsData] = await Promise.all([
        api.getLoans(),
        api.getCustomers(),
      ]);
      setLoans(loansData);
      setCustomers(custsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    runEligibilityCheck('CUST-1002', 300000, 36);
  }, []);

  const runEligibilityCheck = async (
    cId?: string,
    amt?: number,
    tenure?: number
  ) => {
    const targetCust = cId || selectedCustomerId;
    const targetAmt = amt || requestedAmount;
    const targetTenure = tenure || tenureMonths;

    try {
      setCalculating(true);
      setCalcError(null);
      const res = await api.checkLoanEligibility({
        customer_id: targetCust,
        requested_amount: targetAmt,
        tenure_months: targetTenure,
      });
      setResult(res);
    } catch (err: any) {
      setCalcError(err.message || 'Failed to calculate loan eligibility');
      setResult(null);
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Credit Underwriting & Loan Eligibility</h2>
          <p className="text-sm text-slate-500">
            Prudential DTI underwriting, EMI amortization schedules, and risk assessment
          </p>
        </div>

        {/* Policy Badges */}
        <div className="flex items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-semibold border border-slate-200">
            Policy: Max 40% DTI
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-semibold border border-slate-200">
            Min Credit: 650
          </span>
        </div>
      </div>

      {/* Interactive Loan Eligibility Simulator (Use Case 4) */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center text-teal-600">
              <Calculator className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">Interactive Underwriting Simulator</h3>
              <p className="text-xs text-slate-500">Evaluate customer loan eligibility and EMI burden (Use Case 4)</p>
            </div>
          </div>
          <span className="text-[11px] px-2.5 py-1 rounded bg-teal-50 text-teal-700 font-bold border border-teal-200">
            CreditLoanAgent
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Column (5 cols) */}
          <div className="lg:col-span-5 space-y-5">
            {/* Customer Picker */}
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1.5">
                Target Customer
              </label>
              <select
                value={selectedCustomerId}
                onChange={(e) => {
                  setSelectedCustomerId(e.target.value);
                  runEligibilityCheck(e.target.value, requestedAmount, tenureMonths);
                }}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs text-slate-800 bg-white focus:outline-hidden focus:border-teal-500"
              >
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.id} — {c.full_name} ({c.city}, KYC: {c.kyc_status}, Score: {c.credit_score})
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 mt-1">
                Tip: CUST-1002 is prime candidate; CUST-1007 triggers unverified KYC rejection.
              </p>
            </div>

            {/* Requested Amount */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-semibold text-slate-700">Requested Principal (INR)</label>
                <span className="text-xs font-bold text-slate-900 font-mono">
                  ₹{requestedAmount.toLocaleString('en-IN')}
                </span>
              </div>
              <input
                type="range"
                min="50000"
                max="2000000"
                step="25000"
                value={requestedAmount}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setRequestedAmount(val);
                  runEligibilityCheck(selectedCustomerId, val, tenureMonths);
                }}
                className="w-full accent-teal-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>₹50,000</span>
                <span>₹10,00,000</span>
                <span>₹20,00,000</span>
              </div>
            </div>

            {/* Tenure Months */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-semibold text-slate-700">Loan Tenure</label>
                <span className="text-xs font-bold text-slate-900 font-mono">{tenureMonths} Months ({tenureMonths / 12} yrs)</span>
              </div>
              <input
                type="range"
                min="12"
                max="60"
                step="6"
                value={tenureMonths}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setTenureMonths(val);
                  runEligibilityCheck(selectedCustomerId, requestedAmount, val);
                }}
                className="w-full accent-teal-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>12 mo</span>
                <span>36 mo</span>
                <span>60 mo</span>
              </div>
            </div>

            <button
              onClick={() => runEligibilityCheck()}
              disabled={calculating}
              className="w-full py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs transition flex items-center justify-center gap-2"
            >
              {calculating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
              <span>Recalculate Underwriting</span>
            </button>
          </div>

          {/* Results Output Column (7 cols) */}
          <div className="lg:col-span-7 bg-slate-50 p-6 rounded-xl border border-slate-200 flex flex-col justify-between">
            {calcError && (
              <div className="p-3 bg-red-100 text-red-700 rounded-lg text-xs font-medium">
                {calcError}
              </div>
            )}

            {result && (
              <div className="space-y-5">
                {/* Status Verdict Header */}
                <div
                  className={`p-4 rounded-xl flex items-center justify-between border ${
                    result.is_eligible
                      ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
                      : 'bg-red-50 text-red-900 border-red-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {result.is_eligible ? (
                      <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
                    ) : (
                      <XCircle className="w-6 h-6 text-red-600 shrink-0" />
                    )}
                    <div>
                      <h4 className="text-sm font-bold">
                        {result.is_eligible ? 'QUALIFIED FOR SANCTION' : 'INELIGIBLE / UNDERWRITING REJECTION'}
                      </h4>
                      <p className="text-xs opacity-80">
                        {result.customer_name} ({result.customer_id})
                      </p>
                    </div>
                  </div>
                  <span className="text-xs font-extrabold uppercase px-2.5 py-1 rounded bg-white font-mono shadow-2xs">
                    {result.status}
                  </span>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                  <div className="p-3 bg-white rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold block">Monthly EMI</span>
                    <span className="text-base font-bold text-slate-900 font-mono">
                      ₹{result.estimated_emi.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>

                  <div className="p-3 bg-white rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold block">Interest Rate</span>
                    <span className="text-base font-bold text-slate-900 font-mono">
                      {result.applicable_interest_rate}% p.a.
                    </span>
                  </div>

                  <div className="p-3 bg-white rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold block">DTI Ratio</span>
                    <span
                      className={`text-base font-bold font-mono ${
                        result.debt_to_income_ratio > 40 ? 'text-red-600' : 'text-emerald-600'
                      }`}
                    >
                      {result.debt_to_income_ratio}%
                    </span>
                  </div>

                  <div className="p-3 bg-white rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold block">Credit Score</span>
                    <span
                      className={`text-base font-bold font-mono ${
                        result.credit_score >= 650 ? 'text-slate-900' : 'text-red-600'
                      }`}
                    >
                      {result.credit_score}
                    </span>
                  </div>
                </div>

                {/* DTI Gauge Bar */}
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between text-[11px] font-medium text-slate-600">
                    <span>Debt-to-Income (DTI) Burden</span>
                    <span>Max Ceiling: {result.max_permissible_dti}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        result.debt_to_income_ratio > 40 ? 'bg-red-500' : 'bg-teal-500'
                      }`}
                      style={{ width: `${Math.min(result.debt_to_income_ratio * 2, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Underwriting Reasons List */}
                <div className="space-y-1.5 pt-2 border-t border-slate-200 text-xs">
                  <span className="text-[11px] font-semibold text-slate-700 block">Assessment Audit Log:</span>
                  {result.reasons.map((r, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-slate-600">
                      <span className={result.is_eligible ? 'text-emerald-500' : 'text-red-500'}>•</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>

                <div className="text-[10px] text-slate-400 italic pt-1">
                  {result.disclaimer}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Seeded Loan Applications Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Seeded Loan Pipeline</h3>
            <p className="text-xs text-slate-500">Recorded applications evaluated by CreditLoanAgent</p>
          </div>
          <button
            onClick={loadData}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading loan applications...</div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Application ID</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Purpose</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Tenure</th>
                  <th className="py-3 px-4">Monthly EMI</th>
                  <th className="py-3 px-4">DTI Ratio</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loans.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">{l.id}</td>
                    <td className="py-3 px-4 font-mono text-sky-700 font-semibold">{l.customer_id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800">{l.purpose}</td>
                    <td className="py-3 px-4 font-mono font-bold">
                      ₹{l.requested_amount.toLocaleString('en-IN')}
                    </td>
                    <td className="py-3 px-4 text-slate-600">{l.tenure_months} mo</td>
                    <td className="py-3 px-4 font-mono">₹{l.estimated_emi.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
                    <td className="py-3 px-4 font-mono font-semibold">{l.dti_ratio}%</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                          l.status === 'APPROVED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : l.status === 'REJECTED'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {l.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 max-w-xs truncate" title={l.notes || ''}>
                      {l.notes || '—'}
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
