import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Inventory from './pages/Inventory';
import Forecasts from './pages/Forecasts';
import Anomalies from './pages/Anomalies';
import SystemMap from './pages/SystemMap';
import AIChatBox from './components/AIChatBox';

function App() {
  const [activeTab, setActiveTab] = useState(() => {
    return localStorage.getItem('stocksense_active_tab') || 'dashboard';
  });
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    localStorage.setItem('stocksense_active_tab', activeTab);
  }, [activeTab]);

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
