import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Inventory from './pages/Inventory';
import Forecasts from './pages/Forecasts';
import Anomalies from './pages/Anomalies';
import SystemMap from './pages/SystemMap';
import AIChatBox from './components/AIChatBox';

function App() {
  const VALID_TABS = ['dashboard', 'inventory', 'forecasts', 'anomalies', 'system', 'chat'];

  const getInitialTab = () => {
    const hash = window.location.hash.replace('#', '').trim().toLowerCase();
    if (VALID_TABS.includes(hash)) {
      return hash;
    }
    return localStorage.getItem('stocksense_active_tab') || 'dashboard';
  };

  const [activeTab, setActiveTab] = useState(getInitialTab);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    localStorage.setItem('stocksense_active_tab', activeTab);
    if (window.location.hash.replace('#', '') !== activeTab) {
      window.location.hash = activeTab;
    }
  }, [activeTab]);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '').trim().toLowerCase();
      if (VALID_TABS.includes(hash)) {
        setActiveTab(hash);
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return (
    <div className={`app-wrapper ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isCollapsed={isSidebarCollapsed}
        toggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {activeTab === 'dashboard' && <Dashboard />}

      {activeTab === 'inventory' && (
        <main className="stocksense-page">
          <Inventory />
        </main>
      )}

      {/* Other pages use the generic page wrapper */}
      {activeTab !== 'dashboard' && activeTab !== 'inventory' && (
        <main className="stocksense-page">
          <div className="stocksense-content">
            {activeTab === 'forecasts' && <Forecasts />}
            {activeTab === 'anomalies' && <Anomalies />}
            {activeTab === 'system' && <SystemMap />}
            {activeTab === 'chat' && (
              <div style={{ maxWidth: 900, margin: '0 auto', width: '100%' }}>
                <AIChatBox />
              </div>
            )}
          </div>
        </main>
      )}
    </div>
  );
}

export default App;
