import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Account, Transaction } from '../types';
import {
  CreditCard,
  Search,
  Filter,
  ArrowUpRight,
  ArrowDownLeft,
  RefreshCw,
  AlertTriangle,
  Building2
} from 'lucide-react';

export const AccountsPage: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [flagFilter, setFlagFilter] = useState<boolean | undefined>(undefined);
  const [searchTerm, setSearchTerm] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [accts, txns] = await Promise.all([
        api.getAccounts(),
        api.getTransactions(100, selectedCategory || undefined, flagFilter),
      ]);
      setAccounts(accts);
      setTransactions(txns);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedCategory, flagFilter]);

  const totalBalance = accounts.reduce((acc, curr) => acc + curr.balance, 0);

  const categories = Array.from(new Set(transactions.map((t) => t.category))).filter(Boolean);

  const filteredTxns = transactions.filter((t) => {
    if (!searchTerm) return true;
    const q = searchTerm.toLowerCase();
    return (
      t.id.toLowerCase().includes(q) ||
      t.customer_id.toLowerCase().includes(q) ||
      t.merchant.toLowerCase().includes(q) ||
      t.category.toLowerCase().includes(q)
    );
  });

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Liquidity Stat Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Simulated Accounts & Ledger</h2>
          <p className="text-sm text-slate-500">Live account balances and transaction clearing telemetry</p>
        </div>
        <div className="px-4 py-2 bg-white rounded-xl border border-slate-200 text-right shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-400 block uppercase">Aggregate Book Value</span>
          <span className="text-lg font-bold text-slate-900 font-mono">
            ₹{totalBalance.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </span>
        </div>
      </div>

      {/* Account Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {accounts.slice(0, 8).map((acct) => (
          <div
            key={acct.id}
            className="p-4 rounded-xl border border-slate-200/90 bg-white shadow-2xs space-y-3"
          >
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                {acct.account_type}
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                {acct.status}
              </span>
            </div>

            <div>
              <div className="text-lg font-bold text-slate-900 font-mono">
                ₹{acct.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <div className="text-[11px] text-slate-400 font-mono tracking-wider mt-0.5">
                {acct.account_number}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Customer:</span>
              <span className="font-semibold text-sky-700 font-mono">{acct.customer_id}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Ledger Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        {/* Table Filters */}
        <div className="p-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by TXN ID, merchant, customer..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg border border-slate-300 text-xs focus:outline-hidden focus:border-sky-500"
            />
          </div>

          <div className="flex items-center gap-2 text-xs">
            {/* Category Dropdown */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 bg-white text-xs focus:outline-hidden"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            {/* Flagged Filter */}
            <button
              onClick={() => {
                if (flagFilter === undefined) setFlagFilter(true);
                else if (flagFilter === true) setFlagFilter(false);
                else setFlagFilter(undefined);
              }}
              className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition ${
                flagFilter === true
                  ? 'bg-red-50 text-red-700 border-red-300'
                  : flagFilter === false
                  ? 'bg-slate-100 text-slate-700 border-slate-300'
                  : 'bg-white text-slate-600 border-slate-300'
              }`}
            >
              {flagFilter === true ? '⚠️ Flagged Only' : flagFilter === false ? 'Unflagged Only' : 'All Transactions'}
            </button>

            <button
              onClick={loadData}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Transaction Table */}
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading ledger data...</div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">TXN ID</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Merchant & Description</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Flag / Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredTxns.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">{t.id}</td>
                    <td className="py-3 px-4 font-mono text-sky-700 font-medium">{t.customer_id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800">{t.merchant}</td>
                    <td className="py-3 px-4 text-slate-500">{t.category}</td>
                    <td className="py-3 px-4 text-slate-500">{t.location}</td>
                    <td className="py-3 px-4 font-semibold">
                      <span className={t.txn_type === 'CREDIT' ? 'text-emerald-600' : 'text-slate-900'}>
                        {t.txn_type === 'CREDIT' ? '+' : '-'}₹{t.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {t.is_flagged ? (
                        <div className="flex items-center gap-1.5 text-red-600">
                          <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                          <span className="text-[11px] font-semibold truncate max-w-xs" title={t.flag_reason || ''}>
                            {t.flag_reason || 'Flagged'}
                          </span>
                        </div>
                      ) : (
                        <span className="text-slate-400 text-[11px]">Normal</span>
                      )}
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
