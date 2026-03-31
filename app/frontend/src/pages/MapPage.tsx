import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import type { Layer, LeafletMouseEvent, Map as LMap } from 'leaflet';
import L from 'leaflet';
import { api } from '../api';

function getColor(value: number): string {
  if (value >= 80) return '#16A34A';
  if (value >= 60) return '#65A30D';
  if (value >= 40) return '#D97706';
  if (value >= 20) return '#EA580C';
  return '#DC2626';
}

const PARIS_BOUNDS: L.LatLngBoundsExpression = [
  [48.815, 2.224],
  [48.903, 2.470],
];

function FitParis() {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(PARIS_BOUNDS, { padding: [10, 10] });
    map.setMaxBounds([
      [48.78, 2.18],
      [48.93, 2.52],
    ]);
    map.setMinZoom(11);
  }, [map]);
  return null;
}

export default function MapPage() {
  const [mapData, setMapData] = useState<any>(null);
  const [activeKpi, setActiveKpi] = useState('score_parkshare');
  const [selected, setSelected] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const geoJsonRef = useRef<any>(null);

  const loadMap = (kpi: string) => {
    setLoading(true);
    api.mapGeoJSON(kpi).then((data) => {
      setMapData(data);
      setActiveKpi(kpi);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { loadMap('score_parkshare'); }, []);

  const style = (feature: any) => {
    const val = feature.properties[activeKpi] || 0;
    return {
      fillColor: getColor(val),
      weight: 1,
      opacity: 0.8,
      color: '#94A3B8',
      fillOpacity: 0.6,
    };
  };

  const onEachFeature = (feature: any, layer: Layer) => {
    const p = feature.properties;
    layer.bindTooltip(`<strong>${p.nom}</strong><br/>Score: ${p.score_parkshare ?? 'N/A'}/100<br/>Rang: ${p.rang ?? 'N/A'}/20`);
    layer.on({
      click: () => setSelected(p),
      mouseover: (e: LeafletMouseEvent) => {
        e.target.setStyle({ weight: 2, fillOpacity: 0.8, color: '#475569' });
        e.target.bringToFront();
      },
      mouseout: (e: LeafletMouseEvent) => {
        if (geoJsonRef.current) geoJsonRef.current.resetStyle(e.target);
      },
    });
  };

  return (
    <div>
      <div className="page-header">
        <h2>Carte interactive</h2>
        <p>Potentiel Parkshare par arrondissement de Paris</p>
      </div>

      <div className="filters-bar">
        <label>Indicateur :</label>
        {mapData?.kpi_options?.map((opt: any) => (
          <button
            key={opt.value}
            className={`btn ${activeKpi === opt.value ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => loadMap(opt.value)}
            style={{ fontSize: 12, padding: '6px 14px' }}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="grid-2-1">
        <div>
          {loading ? (
            <div className="loading"><div className="spinner" /> Chargement de la carte...</div>
          ) : (
            <div className="map-container">
              <MapContainer
                center={[48.8566, 2.3522]}
                zoom={12}
                scrollWheelZoom={true}
                style={{ height: 540, width: '100%' }}
                maxBounds={[[48.78, 2.18], [48.93, 2.52]]}
                minZoom={11}
                maxZoom={16}
              >
                <FitParis />
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'
                  url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                />
                {mapData?.geojson && (
                  <GeoJSON
                    ref={geoJsonRef}
                    key={activeKpi + JSON.stringify(mapData.geojson).slice(0, 50)}
                    data={mapData.geojson}
                    style={style}
                    onEachFeature={onEachFeature}
                  />
                )}
              </MapContainer>
              <div className="map-legend">
                <span>Faible</span>
                <div className="legend-gradient" />
                <span>Fort</span>
                <span style={{ marginLeft: 8, color: 'var(--text-muted)', fontSize: 11 }}>
                  {mapData?.kpi_options?.find((o: any) => o.value === activeKpi)?.label}
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="detail-panel">
          {selected ? (() => {
            const score = selected.score_parkshare ?? 0;
            const tier = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low';
            const barColor = score >= 70 ? '#16A34A' : score >= 40 ? '#D97706' : '#DC2626';
            return (
              <>
                <div className="detail-header">
                  <h3>{selected.nom}</h3>
                  <div className="detail-score-hero">
                    <div className={`detail-score-badge ${tier}`}>{score}</div>
                    <div className="detail-score-meta">
                      <span className="score-label">Score Parkshare</span>
                      <span className="score-rank">Rang {selected.rang}/20</span>
                      <div className="detail-score-bar-track">
                        <div className="detail-score-bar-fill" style={{ width: `${score}%`, background: barColor }} />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="detail-body">
                  <div className="detail-section-title">Demographie</div>
                  <div className="detail-row">
                    <span className="detail-label">Population<span className="detail-hint">Nombre d'habitants (INSEE)</span></span>
                    <span className="detail-value">{selected.population?.toLocaleString('fr-FR')} hab.</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Densite<span className="detail-hint">Habitants par km2 de superficie</span></span>
                    <span className="detail-value">{selected.densite_population?.toLocaleString('fr-FR')} hab/km2</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Logements collectifs<span className="detail-hint">Part des logements en immeuble collectif</span></span>
                    <span className="detail-value">{selected.part_logements_collectifs}%</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Nb logements<span className="detail-hint">Total de logements dans l'arrondissement</span></span>
                    <span className="detail-value">{selected.nb_logements?.toLocaleString('fr-FR')}</span>
                  </div>

                  <div className="detail-section-title">Stationnement</div>
                  <div className="detail-row">
                    <span className="detail-label">Nb voitures<span className="detail-hint">Vehicules immatricules dans l'arrondissement</span></span>
                    <span className="detail-value">{selected.nb_voitures?.toLocaleString('fr-FR')}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Taux motorisation<span className="detail-hint">Vehicules pour 1 000 habitants</span></span>
                    <span className="detail-value">{selected.taux_motorisation} ‰</span>
                  </div>

                  <div className="detail-section-title">Indicateurs Parkshare</div>
                  <div className="detail-row">
                    <span className="detail-label">Pression stationnement<span className="detail-hint">Indice normalise, 100 = pression maximale</span></span>
                    <span className="detail-value">{selected.kpi_pression_stationnement}/100</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Densite residentielle<span className="detail-hint">Logements collectifs par km2, normalise sur 100</span></span>
                    <span className="detail-value">{selected.kpi_densite_residentielle}/100</span>
                  </div>
                </div>
              </>
            );
          })() : (
            <div className="empty-state">
              <div className="empty-icon">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  <path d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
                </svg>
              </div>
              <p>Selectionnez un arrondissement</p>
              <p className="hint">Cliquez sur la carte pour voir les details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
