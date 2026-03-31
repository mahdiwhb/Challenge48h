import { useState, useEffect, useMemo } from 'react';
import Plot from 'react-plotly.js';
import { api } from '../api';

export default function Correlations() {
  const [corrData, setCorrData] = useState<any>(null);
  const [scatterData, setScatterData] = useState<any>(null);
  const [varX, setVarX] = useState('densite_population');
  const [varY, setVarY] = useState('score_parkshare');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.correlations().then(setCorrData).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    api.scatterData(varX, varY).then(setScatterData);
  }, [varX, varY]);

  const heatmapData = useMemo(() => {
    if (!corrData?.matrix) return null;
    const vars = corrData.variables;
    const labels = vars.map((v: string) => corrData.labels[v] || v);
    const z = vars.map((v1: string) =>
      vars.map((v2: string) => corrData.matrix[v1]?.[v2] ?? 0)
    );
    return { z, x: labels, y: labels };
  }, [corrData]);

  const scatterPlotData = useMemo(() => {
    if (!scatterData?.data) return null;
    return {
      x: scatterData.data.map((d: any) => d.x_val),
      y: scatterData.data.map((d: any) => d.y_val),
      text: scatterData.data.map((d: any) => d.nom),
      marker: {
        size: scatterData.data.map((d: any) => Math.max(8, d.score_parkshare / 5)),
        color: scatterData.data.map((d: any) => d.score_parkshare),
        colorscale: [[0, '#DC2626'], [0.5, '#D97706'], [1, '#16A34A']],
        showscale: true,
        colorbar: { title: 'Score', tickfont: { color: '#64748B' }, titlefont: { color: '#334155' } },
      },
    };
  }, [scatterData]);

  if (loading) return <div className="loading"><div className="spinner" /> Chargement...</div>;

  const allVars = corrData?.variables || [];

  return (
    <div>
      <div className="page-header">
        <h2>Analyse de corrélation</h2>
        <p>Relations entre les variables du scoring Parkshare</p>
      </div>

      {/* Heatmap */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Matrice de corrélation (Pearson)</div>
        {heatmapData && (
          <Plot
            data={[{
              type: 'heatmap',
              z: heatmapData.z,
              x: heatmapData.x,
              y: heatmapData.y,
              colorscale: [
                [0, '#DC2626'],
                [0.5, '#D97706'],
                [1, '#16A34A'],
              ],
              zmin: -1,
              zmax: 1,
              text: heatmapData.z.map((row: number[]) => row.map((v: number) => v.toFixed(2))),
              texttemplate: '%{text}',
              hovertemplate: '%{x} × %{y}<br>Corrélation: %{z:.3f}<extra></extra>',
            }]}
            layout={{
              margin: { l: 160, r: 40, t: 20, b: 160 },
              height: 450,
              font: { size: 11, color: '#334155', family: "'Inter', sans-serif" },
              paper_bgcolor: '#FFFFFF',
              plot_bgcolor: '#FFFFFF',
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        )}
      </div>

      {/* Scatter plot */}
      <div className="card">
        <div className="card-title">Scatter plot interactif</div>
        <div className="filters-bar">
          <label>Axe X :</label>
          <select className="filter-select" value={varX} onChange={e => setVarX(e.target.value)}>
            {allVars.filter((v: string) => v !== 'score_parkshare').map((v: string) => (
              <option key={v} value={v}>{corrData?.labels[v] || v}</option>
            ))}
          </select>
          <label>Axe Y :</label>
          <select className="filter-select" value={varY} onChange={e => setVarY(e.target.value)}>
            <option value="score_parkshare">Score Parkshare</option>
            {allVars.filter((v: string) => v !== 'score_parkshare').map((v: string) => (
              <option key={v} value={v}>{corrData?.labels[v] || v}</option>
            ))}
          </select>
        </div>
        {scatterPlotData && (
          <Plot
            data={[{
              type: 'scatter',
              mode: 'markers+text',
              x: scatterPlotData.x,
              y: scatterPlotData.y,
              text: scatterPlotData.text,
              textposition: 'top center',
              textfont: { size: 9, color: '#64748B' },
              marker: scatterPlotData.marker,
              hovertemplate: '%{text}<br>X: %{x:.1f}<br>Y: %{y:.1f}<extra></extra>',
            }]}
            layout={{
              margin: { l: 60, r: 40, t: 20, b: 60 },
              height: 450,
              xaxis: { title: scatterData?.x_label || varX, gridcolor: '#E2E5EA', zerolinecolor: '#CBD5E1', tickfont: { color: '#64748B' }, titlefont: { color: '#334155' } },
              yaxis: { title: scatterData?.y_label || varY, gridcolor: '#E2E5EA', zerolinecolor: '#CBD5E1', tickfont: { color: '#64748B' }, titlefont: { color: '#334155' } },
              font: { size: 12, color: '#334155', family: "'Inter', sans-serif" },
              paper_bgcolor: '#FFFFFF',
              plot_bgcolor: '#FFFFFF',
            }}
            config={{ responsive: true, displayModeBar: true }}
            style={{ width: '100%' }}
          />
        )}
      </div>
    </div>
  );
}
