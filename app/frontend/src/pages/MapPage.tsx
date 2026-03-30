import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import type { Layer, LeafletMouseEvent } from 'leaflet';
import { api } from '../api';

function getColor(value: number): string {
  if (value >= 80) return '#3EE8A0';
  if (value >= 60) return '#59C890';
  if (value >= 40) return '#F2A93B';
  if (value >= 20) return '#E87850';
  return '#E85050';
}

export default function MapPage() {
  const [mapData, setMapData] = useState<any>(null);
  const [activeKpi, setActiveKpi] = useState('score_parkshare');
  const [selected, setSelected] = useState<any>(null);
  const [loading, setLoading] = useState(true);

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
      weight: 1.5,
      opacity: 1,
      color: '#1E2D42',
      fillOpacity: 0.75,
    };
  };

  const onEachFeature = (feature: any, layer: Layer) => {
    const p = feature.properties;
    layer.bindTooltip(
      `<strong>${p.nom}</strong><br/>Score: ${p.score_parkshare ?? 'N/A'}/100<br/>Rang: ${p.rang ?? 'N/A'}`,
      { sticky: true }
    );
    layer.on({
      click: () => setSelected(p),
      mouseover: (e: LeafletMouseEvent) => {
        e.target.setStyle({ weight: 2.5, fillOpacity: 0.95 });
      },
      mouseout: (e: LeafletMouseEvent) => {
        e.target.setStyle({ weight: 1.5, fillOpacity: 0.75 });
      },
    });
  };

  return (
    <div>
      <div className="page-header">
        <h2>Carte interactive</h2>
        <p>Visualisation du potentiel Parkshare par arrondissement</p>
      </div>

      <div className="filters-bar">
        <label style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Indicateur :</label>
        {mapData?.kpi_options?.map((opt: any) => (
          <button
            key={opt.value}
            className={`btn ${activeKpi === opt.value ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => loadMap(opt.value)}
            style={{ fontSize: 13, padding: '6px 14px' }}
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
                style={{ height: 500, width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {mapData?.geojson && (
                  <GeoJSON
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
                <span style={{ marginLeft: 8, color: 'var(--text-muted)', fontSize: 11, fontFamily: "'DM Mono', monospace" }}>
                  {mapData?.kpi_options?.find((o: any) => o.value === activeKpi)?.label}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Detail panel */}
        <div className="detail-panel">
          {selected ? (
            <>
              <h3>{selected.nom}</h3>
              <div className="detail-row">
                <span className="detail-label">Score Parkshare</span>
                <span className="detail-value">{selected.score_parkshare}/100</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Rang</span>
                <span className="detail-value">{selected.rang}/20</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Population</span>
                <span className="detail-value">{selected.population?.toLocaleString('fr-FR')}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Densité</span>
                <span className="detail-value">{selected.densite_population?.toLocaleString('fr-FR')} hab/km²</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">% Logements collectifs</span>
                <span className="detail-value">{selected.part_logements_collectifs}%</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Taux motorisation</span>
                <span className="detail-value">{selected.taux_motorisation}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Pression stationnement</span>
                <span className="detail-value">{selected.kpi_pression_stationnement}/100</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Densité résidentielle</span>
                <span className="detail-value">{selected.kpi_densite_residentielle}/100</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Nb voitures</span>
                <span className="detail-value">{selected.nb_voitures?.toLocaleString('fr-FR')}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Nb logements</span>
                <span className="detail-value">{selected.nb_logements?.toLocaleString('fr-FR')}</span>
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
              <p style={{ fontSize: 14, fontFamily: "'DM Mono', monospace", letterSpacing: '0.04em' }}>Cliquez sur un arrondissement</p>
              <p style={{ fontSize: 12, marginTop: 6, color: 'var(--text-disabled)' }}>pour voir ses détails</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
