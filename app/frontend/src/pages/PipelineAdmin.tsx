import { useState, useEffect } from 'react';
import { api } from '../api';

export default function PipelineAdmin() {
  const [status, setStatus] = useState<any>(null);
  const [config, setConfig] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadStatus = () => {
    Promise.all([api.pipelineStatus(), api.kpiConfig()])
      .then(([s, c]) => { setStatus(s); setConfig(c); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadStatus(); }, []);

  const runPipeline = () => {
    setRunning(true);
    api.pipelineRun()
      .then(() => {
        setTimeout(loadStatus, 3000);
      })
      .finally(() => setRunning(false));
  };

  if (loading) return <div className="loading"><div className="spinner" /> Chargement...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Pipeline & Administration</h2>
        <p>Gestion du pipeline de données et configuration du scoring</p>
      </div>

      <div className="grid-2">
        {/* Pipeline status */}
        <div className="card">
          <div className="card-title">Etat du pipeline</div>
          {status?.latest ? (
            <div>
              <div className="detail-row">
                <span className="detail-label">Dernier run</span>
                <span className="detail-value">{new Date(status.latest.started_at).toLocaleString('fr-FR')}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Statut</span>
                <span className={`status-badge ${status.latest.status}`}>{status.latest.status}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Durée</span>
                <span className="detail-value">{status.latest.duration_seconds?.toFixed(1)}s</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Mode</span>
                <span className="detail-value">{status.latest.mode}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Arrondissements</span>
                <span className="detail-value">{status.latest.num_arrondissements}</span>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>Aucun run enregistré</p>
          )}
          <button
            className="btn btn-primary"
            style={{ marginTop: 16, width: '100%' }}
            onClick={runPipeline}
            disabled={running}
          >
            {running ? 'Exécution...' : 'Relancer le pipeline'}
          </button>
        </div>

        {/* Scoring config */}
        <div className="card">
          <div className="card-title">Pondérations du scoring</div>
          {config && (
            <div className="table-container">
              <table>
                <thead>
                  <tr><th>Variable</th><th>Poids</th><th>Description</th></tr>
                </thead>
                <tbody>
                  {Object.entries(config).map(([key, val]: [string, any]) => (
                    <tr key={key}>
                      <td style={{ fontWeight: 500 }}>{key.replace(/_/g, ' ')}</td>
                      <td>
                        <span className="score-badge score-high">{(val.weight * 100).toFixed(0)}%</span>
                      </td>
                      <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>{val.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Run history */}
      {status?.runs && status.runs.length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-title">Historique des runs</div>
          <div className="table-container">
            <table>
              <thead>
                <tr><th>ID</th><th>Date</th><th>Mode</th><th>Statut</th><th>Durée</th></tr>
              </thead>
              <tbody>
                {status.runs.map((r: any) => (
                  <tr key={r.id}>
                    <td>#{r.id}</td>
                    <td>{new Date(r.started_at).toLocaleString('fr-FR')}</td>
                    <td>{r.mode}</td>
                    <td><span className={`status-badge ${r.status}`}>{r.status}</span></td>
                    <td>{r.duration_seconds?.toFixed(1)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Documentation */}
      <div className="card" style={{ marginTop: 24 }}>
        <div className="card-title">Documentation pipeline</div>
        <div className="doc-block">
          <p><strong>Pipeline data :</strong> Ingestion → Nettoyage → Transformation → KPIs → Corrélations → Stockage SQLite</p>
          <p><strong>Automatisation :</strong> Le pipeline peut être déclenché manuellement via le bouton ci-dessus, 
          ou automatisé via cron : <code>0 2 * * * cd /app && python -m data.scripts.run_pipeline</code></p>
          <p><strong>Sources :</strong> En mode démo, les données proviennent de fichiers CSV seed. 
          En production, le script d'ingestion se connecterait aux API Paris Open Data et INSEE.</p>
        </div>
      </div>
    </div>
  );
}
