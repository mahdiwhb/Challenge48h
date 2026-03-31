import { useState } from 'react';
import Overview from './pages/Overview';
import MapPage from './pages/MapPage';
import Rankings from './pages/Rankings';
import Correlations from './pages/Correlations';
import PipelineAdmin from './pages/PipelineAdmin';
import Chatbot from './pages/Chatbot';

const Icon = ({ d }: { d: string }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

const PAGES = [
  { id: 'overview', label: 'Vue d\'ensemble', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4' },
  { id: 'map', label: 'Carte', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
  { id: 'rankings', label: 'Classement', icon: 'M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12' },
  { id: 'correlations', label: 'Correlations', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4v16' },
  { id: 'pipeline', label: 'Pipeline', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
  { id: 'chatbot', label: 'Assistant', icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z' },
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
          <p>Etude de marche - Paris</p>
        </div>
        <nav className="sidebar-nav">
          {PAGES.map((p) => (
            <button
              key={p.id}
              className={`nav-item ${page === p.id ? 'active' : ''}`}
              onClick={() => setPage(p.id)}
            >
              <span className="nav-icon"><Icon d={p.icon} /></span>
              {p.label}
            </button>
          ))}
        </nav>
        <div style={{ padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.08)', fontSize: 11, color: 'rgba(255,255,255,0.35)' }}>
          v1.0.0 - Demo
        </div>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}
