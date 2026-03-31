import { useState, useEffect } from 'react';
import { api } from '../api';

function getScoreClass(score: number) {
  if (score >= 70) return 'score-high';
  if (score >= 40) return 'score-medium';
  return 'score-low';
}

function getBarColor(score: number) {
  if (score >= 60) return '#16A34A';
  if (score >= 35) return '#D97706';
  return '#DC2626';
}

interface Props {
  onNavigate: (page: string) => void;
}

export default function Overview({ onNavigate }: Props) {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.kpiSummary().then(setSummary).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading"><div className="spinner" /> Chargement...</div>;
  if (!summary) return <div className="loading">Erreur de chargement</div>;

  const downloadCSV = () => {
    if (!summary?.all_scores) return;
    const headers = ['Rang', 'Arrondissement', 'Score Parkshare', 'Pression Stationnement', 'Densite Residentielle'];
    const rows = summary.all_scores.map((d: any) =>
      [d.rang, d.nom, d.score_parkshare, d.kpi_pression_stationnement, d.kpi_densite_residentielle].join(',')
    );
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parkshare_rankings.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="page-header">
        <h2>Vue d'ensemble</h2>
        <p>Analyse du potentiel commercial Parkshare par arrondissement de Paris</p>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Arrondissements analyses</div>
          <div className="kpi-value">{summary.total_arrondissements}</div>
          <div className="kpi-sub">Paris intra-muros</div>
        </div>
        <div className="kpi-card success">
          <div className="kpi-label">Score moyen</div>
          <div className="kpi-value">{summary.score_moyen}<span>/100</span></div>
          <div className="kpi-sub">Potentiel Parkshare</div>
        </div>
        <div className="kpi-card success">
          <div className="kpi-label">Score maximum</div>
          <div className="kpi-value">{summary.score_max}<span>/100</span></div>
          <div className="kpi-sub">{summary.top_5[0]?.nom}</div>
        </div>
        <div className="kpi-card danger">
          <div className="kpi-label">Score minimum</div>
          <div className="kpi-value">{summary.score_min}<span>/100</span></div>
          <div className="kpi-sub">{summary.bottom_5[0]?.nom}</div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Top 5 - Fort potentiel</div>
          <div className="table-container">
            <table>
              <thead>
                <tr><th>Rang</th><th>Arrondissement</th><th>Score</th></tr>
              </thead>
              <tbody>
                {summary.top_5.map((d: any) => (
                  <tr key={d.code_arrondissement}>
                    <td><span className={`rank-badge ${d.rang <= 3 ? 'top-3' : ''}`}>{d.rang}</span></td>
                    <td>{d.nom}</td>
                    <td><span className={`score-badge ${getScoreClass(d.score_parkshare)}`}>{d.score_parkshare}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Bottom 5 - Faible potentiel</div>
          <div className="table-container">
            <table>
              <thead>
                <tr><th>Rang</th><th>Arrondissement</th><th>Score</th></tr>
              </thead>
              <tbody>
                {summary.bottom_5.map((d: any) => (
                  <tr key={d.code_arrondissement}>
                    <td><span className="rank-badge">{d.rang}</span></td>
                    <td>{d.nom}</td>
                    <td><span className={`score-badge ${getScoreClass(d.score_parkshare)}`}>{d.score_parkshare}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="export-bar">
        <button className="btn btn-primary" onClick={() => onNavigate('map')}>Voir la carte</button>
        <button className="btn btn-outline" onClick={() => onNavigate('rankings')}>Classement complet</button>
        <button className="btn btn-outline" onClick={downloadCSV}>Export CSV</button>
      </div>

      {summary.all_scores && (
        <div className="card">
          <div className="card-title">Scores par arrondissement</div>
          <div style={{ display: 'flex', gap: 4, alignItems: 'flex-end', height: 200, marginTop: 12, padding: '0 4px' }}>
            {summary.all_scores
              .sort((a: any, b: any) => a.rang - b.rang)
              .map((d: any) => (
                <div
                  key={d.code_arrondissement}
                  style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}
                  title={`${d.nom}: ${d.score_parkshare}/100`}
                >
                  <span style={{ fontSize: 10, fontFamily: "'JetBrains Mono', monospace", color: 'var(--text-muted)', fontWeight: 500 }}>
                    {d.score_parkshare}
                  </span>
                  <div style={{
                    width: '100%',
                    height: `${d.score_parkshare}%`,
                    background: getBarColor(d.score_parkshare),
                    minHeight: 4,
                    borderRadius: '2px 2px 0 0',
                  }} />
                  <span style={{ fontSize: 9, color: 'var(--text-disabled)', writingMode: 'vertical-rl', height: 36, fontWeight: 500, overflow: 'hidden' }}>
                    {d.nom.replace(' arrondissement', '').replace('e ', 'e')}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
