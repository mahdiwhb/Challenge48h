import { useState, useEffect } from 'react';
import { api } from '../api';

function getScoreClass(score: number) {
  if (score >= 70) return 'score-high';
  if (score >= 40) return 'score-medium';
  return 'score-low';
}

export default function Rankings() {
  const [data, setData] = useState<any[]>([]);
  const [sortBy, setSortBy] = useState('score_parkshare');
  const [order, setOrder] = useState('desc');
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api.kpiRankings(sortBy, order).then(setData).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [sortBy, order]);

  const handleSort = (col: string) => {
    if (sortBy === col) {
      setOrder(order === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(col);
      setOrder('desc');
    }
  };

  const sortIcon = (col: string) => {
    if (sortBy !== col) return ' ↕';
    return order === 'desc' ? ' ↓' : ' ↑';
  };

  const downloadCSV = () => {
    const headers = ['Rang', 'Code', 'Arrondissement', 'Score Parkshare', 'Pression Stationnement', 'Densité Résidentielle'];
    const rows = data.map(d =>
      [d.rang, d.code_arrondissement, d.nom, d.score_parkshare, d.kpi_pression_stationnement, d.kpi_densite_residentielle].join(',')
    );
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parkshare_classement.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parkshare_classement.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="page-header">
        <h2>Classement des arrondissements</h2>
        <p>Classement par potentiel commercial Parkshare</p>
      </div>

      <div className="export-bar">
        <button className="btn btn-outline" onClick={downloadCSV}>Export CSV</button>
        <button className="btn btn-outline" onClick={downloadJSON}>Export JSON</button>
      </div>

      {loading ? (
        <div className="loading"><div className="spinner" /> Chargement...</div>
      ) : (
        <div className="card">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ cursor: 'pointer' }} onClick={() => handleSort('rang')}>
                    Rang{sortIcon('rang')}
                  </th>
                  <th style={{ cursor: 'pointer' }} onClick={() => handleSort('nom')}>
                    Arrondissement{sortIcon('nom')}
                  </th>
                  <th style={{ cursor: 'pointer' }} onClick={() => handleSort('score_parkshare')}>
                    Score Parkshare{sortIcon('score_parkshare')}
                  </th>
                  <th style={{ cursor: 'pointer' }} onClick={() => handleSort('kpi_pression_stationnement')}>
                    Pression stationnement{sortIcon('kpi_pression_stationnement')}
                  </th>
                  <th style={{ cursor: 'pointer' }} onClick={() => handleSort('kpi_densite_residentielle')}>
                    Densité résidentielle{sortIcon('kpi_densite_residentielle')}
                  </th>
                  <th>Barre</th>
                </tr>
              </thead>
              <tbody>
                {data.map((d) => (
                  <tr key={d.code_arrondissement}>
                    <td>
                      <span className={`rank-badge ${d.rang <= 3 ? 'top-3' : ''}`}>
                        {d.rang}
                      </span>
                    </td>
                    <td style={{ fontWeight: 500 }}>{d.nom}</td>
                    <td>
                      <span className={`score-badge ${getScoreClass(d.score_parkshare)}`}>
                        {d.score_parkshare}
                      </span>
                    </td>
                    <td>{d.kpi_pression_stationnement}</td>
                    <td>{d.kpi_densite_residentielle}</td>
                    <td style={{ width: 200 }}>
                      <div style={{
                        height: 4,
                        background: 'var(--border)',
                        position: 'relative',
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${d.score_parkshare}%`,
                          background: d.score_parkshare >= 60 ? 'var(--status-available)' : d.score_parkshare >= 35 ? 'var(--accent)' : 'var(--status-full)',
                        }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
