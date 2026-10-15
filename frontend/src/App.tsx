import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import { HealthStatus } from './types';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewPage } from './pages/OverviewPage';
import { AssistantPage } from './pages/AssistantPage';
import { CustomersPage } from './pages/CustomersPage';
import { AccountsPage } from './pages/AccountsPage';
import { FraudPage } from './pages/FraudPage';
import { CreditPage } from './pages/CreditPage';
import { TracesPage } from './pages/TracesPage';
import { AuditPage } from './pages/AuditPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [currentTab, setCurrentTab] = useState('overview');
  const [health, setHealth] = useState<HealthStatus | null>(null);

  const fetchHealth = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (err) {
      console.error('Failed to load system health:', err);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Heartbeat check every 30s
    return () => clearInterval(interval);
  }, []);

  const renderActiveTab = () => {
    switch (currentTab) {
      case 'overview':
        return <OverviewPage onNavigate={(tab) => setCurrentTab(tab)} />;
      case 'assistant':
        return <AssistantPage />;
      case 'customers':
        return <CustomersPage />;
      case 'accounts':
        return <AccountsPage />;
      case 'fraud':
        return <FraudPage />;
      case 'credit':
        return <CreditPage />;
      case 'traces':
        return <TracesPage />;
      case 'audit':
        return <AuditPage />;
      case 'settings':
        return <SettingsPage health={health} onRefreshHealth={fetchHealth} />;
      default:
        return <OverviewPage onNavigate={(tab) => setCurrentTab(tab)} />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100 font-sans">
      {/* Dark Navy Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={(tab) => setCurrentTab(tab)}
        health={health}
      />

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <Header currentTab={currentTab} health={health} />
        <main className="flex-1 overflow-y-auto bg-slate-50">
          {renderActiveTab()}
        </main>
      </div>
    </div>
  );
}

export default App;
