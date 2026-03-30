const API_BASE = '/api';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  health: () => fetchJSON<{ status: string; version: string; mode: string }>('/health'),
  
  arrondissements: () => fetchJSON<any[]>('/arrondissements'),
  
  arrondissement: (code: string) => fetchJSON<any>(`/arrondissements/${code}`),
  
  kpiSummary: () => fetchJSON<any>('/kpis/summary'),
  
  kpiRankings: (sortBy = 'score_parkshare', order = 'desc') =>
    fetchJSON<any[]>(`/kpis/rankings?sort_by=${sortBy}&order=${order}`),
  
  kpiConfig: () => fetchJSON<any>('/kpis/config'),

  mapGeoJSON: (kpi = 'score_parkshare') => fetchJSON<any>(`/map/geojson?kpi=${kpi}`),
  
  correlations: () => fetchJSON<any>('/correlations'),
  
  scatterData: (varX: string, varY: string) =>
    fetchJSON<any>(`/correlations/scatter?var_x=${varX}&var_y=${varY}`),
  
  pipelineRun: () => fetchJSON<any>('/pipeline/run', { method: 'POST' }),
  
  pipelineStatus: () => fetchJSON<any>('/pipeline/status'),
  
  chatbot: (query: string) =>
    fetchJSON<{ query: string; response: string; source: string }>('/chatbot/query', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),
};
