import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Customer, Account, Transaction } from '../types';
import {
  Users,
  Search,
  CreditCard,
  History,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  X
} from 'lucide-react';

export const CustomersPage: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [customerAccounts, setCustomerAccounts] = useState<Account[]>([]);
  const [customerTxns, setCustomerTxns] = useState<Transaction[]>([]);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const fetchCustomers = async (search?: string) => {
    try {
      setLoading(true);
      const data = await api.getCustomers(search);
      setCustomers(data);
      if (!selectedCustomer && data.length > 0) {
        handleSelectCustomer(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  const handleSelectCustomer = async (cust: Customer) => {
    setSelectedCustomer(cust);
    setLoadingDetail(true);
    try {
      const [accts, txns] = await Promise.all([
        api.getCustomerAccounts(cust.id),
        api.getCustomerTransactions(cust.id, 10),
      ]);
      setCustomerAccounts(accts);
      setCustomerTxns(txns);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCustomers(searchTerm);
  };

  return (
    <div className="flex h-full overflow-hidden bg-slate-50">
      {/* Customer Directory Table */}
      <div className="flex-1 flex flex-col overflow-hidden border-r border-slate-200 bg-white">
        {/* Search Header */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between gap-4">
          <form onSubmit={handleSearchSubmit} className="flex-1 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search customers by name, ID (e.g. CUST-1001), email, or city..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-300 text-xs focus:outline-hidden focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
            />
          </form>
          <button
            onClick={() => fetchCustomers(searchTerm)}
            className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600"
            title="Reload customers"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Table View */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-48 text-slate-400 text-xs gap-2">
              <RefreshCw className="w-4 h-4 animate-spin text-sky-600" />
              <span>Loading customer records...</span>
            </div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 sticky top-0">
                <tr>
                  <th className="py-3 px-4">Customer ID</th>
                  <th className="py-3 px-4">Full Name</th>
                  <th className="py-3 px-4">City</th>
                  <th className="py-3 px-4">KYC Status</th>
                  <th className="py-3 px-4">Credit Score</th>
                  <th className="py-3 px-4">Monthly Income</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map((c) => {
                  const isSelected = selectedCustomer?.id === c.id;
                  return (
                    <tr
                      key={c.id}
                      onClick={() => handleSelectCustomer(c)}
                      className={`cursor-pointer transition ${
                        isSelected
                          ? 'bg-sky-50/80 font-medium text-sky-950'
                          : 'hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      <td className="py-3 px-4 font-mono font-semibold text-slate-900">{c.id}</td>
                      <td className="py-3 px-4 font-semibold text-slate-900">{c.full_name}</td>
                      <td className="py-3 px-4 text-slate-500">{c.city}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            c.kyc_status === 'VERIFIED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {c.kyc_status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`font-semibold ${
                            c.credit_score >= 750
                              ? 'text-emerald-600'
                              : c.credit_score >= 650
                              ? 'text-sky-600'
                              : 'text-amber-600'
                          }`}
                        >
                          {c.credit_score}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-medium">
                        ₹{c.monthly_income.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Customer Detail Drawer */}
      <div className="w-96 border-l border-slate-200 bg-white flex flex-col shrink-0 overflow-y-auto p-5 space-y-6">
        {selectedCustomer ? (
          <>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
                  {selectedCustomer.id}
                </span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                    selectedCustomer.kyc_status === 'VERIFIED'
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}
                >
                  {selectedCustomer.kyc_status}
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-900">{selectedCustomer.full_name}</h3>
              <p className="text-xs text-slate-500">{selectedCustomer.email} • {selectedCustomer.phone}</p>
              <p className="text-xs text-slate-500">City: {selectedCustomer.city}</p>
            </div>

            {/* Financial Profile Card */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Declared Monthly Income:</span>
                <span className="font-bold text-slate-900">
                  ₹{selectedCustomer.monthly_income.toLocaleString('en-IN')}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Credit Bureau Score:</span>
                <span className="font-bold text-slate-900">{selectedCustomer.credit_score}</span>
              </div>
            </div>

            {/* Linked Accounts */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5 uppercase tracking-wider">
                <CreditCard className="w-3.5 h-3.5 text-sky-600" />
                <span>Linked Accounts ({customerAccounts.length})</span>
              </h4>

              {loadingDetail ? (
                <div className="text-xs text-slate-400 py-3">Loading accounts...</div>
              ) : (
                <div className="space-y-2">
                  {customerAccounts.map((acct) => (
                    <div
                      key={acct.id}
                      className="p-3 rounded-lg border border-slate-200 bg-white space-y-1 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800">{acct.account_type}</span>
                        <span className="font-mono text-[11px] text-slate-400">{acct.account_number}</span>
                      </div>
                      <div className="flex items-center justify-between pt-1">
                        <span className="text-slate-500 text-[11px]">Balance:</span>
                        <span className="font-bold text-slate-900">
                          ₹{acct.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Transactions */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5 uppercase tracking-wider">
                <History className="w-3.5 h-3.5 text-sky-600" />
                <span>Recent Activity</span>
              </h4>

              {loadingDetail ? (
                <div className="text-xs text-slate-400 py-3">Loading activity...</div>
              ) : (
                <div className="space-y-2">
                  {customerTxns.slice(0, 5).map((t) => (
                    <div
                      key={t.id}
                      className="p-2.5 rounded-lg border border-slate-100 bg-slate-50/70 text-xs flex items-center justify-between"
                    >
                      <div>
                        <div className="font-semibold text-slate-800 leading-tight">{t.merchant}</div>
                        <div className="text-[10px] text-slate-400">{t.category} • {t.location}</div>
                      </div>
                      <div className="text-right">
                        <span
                          className={`font-semibold text-xs ${
                            t.txn_type === 'CREDIT' ? 'text-emerald-600' : 'text-slate-800'
                          }`}
                        >
                          {t.txn_type === 'CREDIT' ? '+' : '-'}₹{t.amount.toLocaleString('en-IN')}
                        </span>
                        {t.is_flagged && (
                          <span className="block text-[9px] text-red-600 font-bold">FLAGGED</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-slate-400 text-xs">
            Select a customer from the directory to inspect profile and account ledgers.
          </div>
        )}
      </div>
    </div>
  );
};
