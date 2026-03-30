import { useState } from 'react';
import Overview from './pages/Overview';
import MapPage from './pages/MapPage';
import Rankings from './pages/Rankings';
import Correlations from './pages/Correlations';
import PipelineAdmin from './pages/PipelineAdmin';
import Chatbot from './pages/Chatbot';

const PAGES = [
  { id: 'overview', label: 'Vue d\'ensemble', icon: '///' },
  { id: 'map', label: 'Carte interactive', icon: '<>' },
  { id: 'rankings', label: 'Classement', icon: '#1' },
  { id: 'correlations', label: 'Corrélations', icon: '~x' },
  { id: 'pipeline', label: 'Pipeline / Admin', icon: '>>>' },
  { id: 'chatbot', label: 'Assistant IA', icon: '?>' },
];

export default function App() {
  const [page, setPage] = useState('overview');

  const renderPage = () => {
    switch (page) {
      case 'overview': return <Overview onNavigate={setPage} />;
      case 'map': return <MapPage />;
      case 'rankings': return <Rankings />;
      case 'correlations': return <Correlations />;
      case 'pipeline': return <PipelineAdmin />;
      case 'chatbot': return <Chatbot />;
      default: return <Overview onNavigate={setPage} />;
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>Park<span>share</span></h1>
          <p>Étude de marché — Paris</p>
        </div>
        <nav className="sidebar-nav">
          {PAGES.map((p) => (
            <button
              key={p.id}
              className={`nav-item ${page === p.id ? 'active' : ''}`}
              onClick={() => setPage(p.id)}
            >
              <span className="nav-icon">{p.icon}</span>
              {p.label}
            </button>
          ))}
        </nav>
        <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)', fontFamily: "'DM Mono', monospace", fontSize: 10, color: 'var(--text-disabled)', letterSpacing: '0.06em' }}>
          v1.0.0 — Mode demo
        </div>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}
