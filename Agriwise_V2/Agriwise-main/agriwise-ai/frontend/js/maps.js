/**
 * 🌾 AGRIWISE AI - Map Services & Interactive India Shortage Map
 * Leaflet.js GPS picker + Interactive SVG National Crop Shortage Map.
 */

const AgriMaps = {
  // 1. Initialize Leaflet Farm Location Picker Map
  initFarmMap(elementId, initialLat, initialLon, onLocationChange) {
    if (!window.L) {
      console.warn("Leaflet library not loaded");
      return null;
    }

    const lat = initialLat || 30.9010;
    const lon = initialLon || 75.8573;

    const map = L.map(elementId).setView([lat, lon], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let marker = L.marker([lat, lon], { draggable: true }).addTo(map);
    marker.bindPopup("<b>Selected Farm Location</b><br>Sahnewal, Ludhiana").openPopup();

    marker.on('dragend', (e) => {
      const pos = marker.getLatLng();
      if (onLocationChange) {
        onLocationChange(pos.lat, pos.lng);
      }
    });

    map.on('click', (e) => {
      marker.setLatLng(e.latlng);
      if (onLocationChange) {
        onLocationChange(e.latlng.lat, e.latlng.lng);
      }
    });

    return { map, marker };
  },

  // 2. Interactive SVG India Crop Shortage Map
  renderIndiaShortageMap(containerId, shortageData, onStateClick) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // State code to Status mapping
    const statusMap = {};
    shortageData.forEach(d => {
      statusMap[d.state_code] = d;
    });

    // Helper to get status color
    const getColor = (code) => {
      const record = statusMap[code];
      if (!record) return '#e2e8f0'; // Default gray
      if (record.status.includes('High Shortage')) return '#ef4444'; // Red
      if (record.status.includes('Medium Shortage')) return '#f59e0b'; // Amber
      if (record.status.includes('Surplus')) return '#10b981'; // Green
      return '#0284c7'; // Balanced (Blue)
    };

    // Responsive SVG Layout with Indian State Regions
    // We represent Indian states with stylized interactive SVG polygons & labels
    const states = [
      { code: 'PB', name: 'Punjab', x: 260, y: 160, w: 75, h: 55 },
      { code: 'HR', name: 'Haryana', x: 280, y: 225, w: 70, h: 50 },
      { code: 'DL', name: 'Delhi', x: 340, y: 235, w: 35, h: 30 },
      { code: 'RJ', name: 'Rajasthan', x: 180, y: 240, w: 110, h: 100 },
      { code: 'UP', name: 'Uttar Pradesh', x: 360, y: 240, w: 120, h: 80 },
      { code: 'GJ', name: 'Gujarat', x: 140, y: 350, w: 95, h: 80 },
      { code: 'MP', name: 'Madhya Pradesh', x: 280, y: 340, w: 130, h: 90 },
      { code: 'MH', name: 'Maharashtra', x: 230, y: 445, w: 125, h: 95 },
      { code: 'KA', name: 'Karnataka', x: 250, y: 560, w: 85, h: 100 },
      { code: 'AP', name: 'Andhra Pradesh', x: 350, y: 530, w: 90, h: 100 },
      { code: 'TN', name: 'Tamil Nadu', x: 290, y: 675, w: 85, h: 90 },
      { code: 'WB', name: 'West Bengal', x: 530, y: 330, w: 65, h: 90 },
      { code: 'BR', name: 'Bihar', x: 490, y: 265, w: 75, h: 65 },
      { code: 'TS', name: 'Telangana', x: 335, y: 465, w: 80, h: 65 },
      { code: 'OR', name: 'Odisha', x: 445, y: 410, w: 80, h: 75 }
    ];

    let svgShapes = states.map(st => {
      const color = getColor(st.code);
      const data = statusMap[st.code];
      const tooltip = data ? `${data.state_name}: ${data.status} (Deficit: ${data.deficit_tonnes > 0 ? '+' : ''}${data.deficit_tonnes.toLocaleString()} T)` : st.name;

      return `
        <g class="map-state-node" data-code="${st.code}" style="cursor: pointer;" onclick="AgriMaps.onStateClicked('${st.code}')">
          <rect x="${st.x}" y="${st.y}" width="${st.w}" height="${st.h}" rx="10"
                fill="${color}" stroke="#ffffff" stroke-width="2.5"
                filter="drop-shadow(0 2px 4px rgba(0,0,0,0.12))">
            <title>${tooltip}</title>
          </rect>
          <text x="${st.x + st.w / 2}" y="${st.y + st.h / 2 - 4}"
                font-family="sans-serif" font-size="13" font-weight="700" fill="#ffffff" text-anchor="middle">
            ${st.code}
          </text>
          <text x="${st.x + st.w / 2}" y="${st.y + st.h / 2 + 12}"
                font-family="sans-serif" font-size="10" font-weight="500" fill="#ffffff" text-anchor="middle">
            ${st.name}
          </text>
        </g>
      `;
    }).join('');

    container.innerHTML = `
      <div style="position: relative; width: 100%; text-align: center;">
        <svg viewBox="100 120 530 680" style="max-width: 620px; width: 100%; height: auto; display: block; margin: 0 auto;">
          <!-- Map Background Grid -->
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f1f5f9" stroke-width="1"/>
            </pattern>
          </defs>
          <rect x="100" y="120" width="530" height="680" fill="url(#grid)" />
          ${svgShapes}
        </svg>

        <!-- Map Legend -->
        <div style="display: flex; justify-content: center; gap: 1.25rem; flex-wrap: wrap; margin-top: 1rem; font-size: 0.82rem; font-weight: 600;">
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 14px; height: 14px; border-radius: 4px; background: #ef4444; display: inline-block;"></span>
            <span>High Shortage (Severe Deficit)</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 14px; height: 14px; border-radius: 4px; background: #f59e0b; display: inline-block;"></span>
            <span>Medium Shortage</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 14px; height: 14px; border-radius: 4px; background: #0284c7; display: inline-block;"></span>
            <span>Balanced Supply</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 14px; height: 14px; border-radius: 4px; background: #10b981; display: inline-block;"></span>
            <span>Surplus (Exporting State)</span>
          </div>
        </div>
      </div>
    `;

    // Save click handler
    this._onStateClick = onStateClick;
    this._statusMap = statusMap;
  },

  onStateClicked(stateCode) {
    if (this._onStateClick && this._statusMap) {
      const data = this._statusMap[stateCode];
      this._onStateClick(stateCode, data);
    }
  }
};

window.AgriMaps = AgriMaps;
