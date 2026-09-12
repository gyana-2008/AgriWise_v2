/**
 * 🌾 AGRIWISE AI - Lightweight Canvas Charting Engine
 * Zero-dependency, high-performance HTML5 Canvas charts for Mandi prices,
 * Farm health radar, weather curves, and multi-scenario ROI.
 */

const AgriCharts = {
  // Format numbers to Indian currency standards (e.g., ₹1,000, ₹25,000, ₹1.5 Lakh, ₹10 Lakh)
  formatMoney(num, compact = true) {
    if (num === null || num === undefined || isNaN(num)) return '₹0';
    num = Number(num);
    const sign = num < 0 ? '-' : '';
    const abs = Math.abs(num);

    if (compact) {
      if (abs >= 10000000) {
        const cr = (abs / 10000000).toFixed(abs % 10000000 === 0 ? 0 : 2);
        return `${sign}₹${cr} Cr`;
      }
      if (abs >= 100000) {
        const lakh = (abs / 100000).toFixed(abs % 100000 === 0 ? 0 : 2);
        return `${sign}₹${lakh} Lakh`;
      }
      if (abs >= 1000) {
        return `${sign}₹${Math.round(abs).toLocaleString('en-IN')}`;
      }
    }
    return `${sign}₹${Math.round(abs).toLocaleString('en-IN')}`;
  },

  // 1. Line Chart with Gradient Fill (Mandi Prices & Weather)
  drawLineChart(canvasId, labels, dataPoints, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Support high-DPI crisp rendering
    const parentWidth = canvas.parentElement.clientWidth || 600;
    const width = canvas.width = parentWidth;
    const height = canvas.height = options.height || (parentWidth < 480 ? 220 : 280);

    ctx.clearRect(0, 0, width, height);

    const isMobile = width < 500;
    const padding = {
      top: 35,
      right: isMobile ? 15 : 30,
      bottom: isMobile ? 35 : 45,
      left: isMobile ? 55 : 75
    };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    if (!dataPoints || dataPoints.length === 0) return;

    const maxVal = Math.max(...dataPoints) * 1.08;
    const minVal = Math.max(0, Math.min(...dataPoints) * 0.92);
    const valRange = (maxVal - minVal) || 1;

    // Grid lines & Y-axis labels
    const gridLines = 4;
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 1;

    for (let i = 0; i <= gridLines; i++) {
      const y = padding.top + (chartH / gridLines) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      // Y-axis formatted currency labels
      const labelVal = Math.round(maxVal - (valRange / gridLines) * i);
      ctx.fillStyle = '#64748b';
      ctx.font = isMobile ? '10px sans-serif' : '11px sans-serif';
      ctx.textAlign = 'right';
      const formattedLabel = options.prefix === '₹' ? this.formatMoney(labelVal, true) : (options.prefix ? `${options.prefix}${labelVal}` : labelVal);
      ctx.fillText(formattedLabel, padding.left - 8, y + 4);
    }

    // Points calculation
    const points = dataPoints.map((val, idx) => {
      const x = padding.left + (chartW / Math.max(1, dataPoints.length - 1)) * idx;
      const y = padding.top + chartH - ((val - minVal) / valRange) * chartH;
      return { x, y, val, label: labels[idx] };
    });

    // Gradient fill under curve
    const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
    gradient.addColorStop(0, options.fillColor || 'rgba(5, 150, 105, 0.28)');
    gradient.addColorStop(1, 'rgba(5, 150, 105, 0.01)');

    ctx.beginPath();
    ctx.moveTo(points[0].x, height - padding.bottom);
    points.forEach(pt => ctx.lineTo(pt.x, pt.y));
    ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw Smooth Line
    ctx.beginPath();
    ctx.strokeStyle = options.lineColor || '#059669';
    ctx.lineWidth = 3;
    points.forEach((pt, idx) => {
      if (idx === 0) ctx.moveTo(pt.x, pt.y);
      else ctx.lineTo(pt.x, pt.y);
    });
    ctx.stroke();

    // Draw Points & X-Labels
    const stepInterval = isMobile && dataPoints.length > 7 ? Math.ceil(dataPoints.length / 5) : 1;
    let maxPt = points[0];
    let minPt = points[0];

    points.forEach((pt, idx) => {
      if (pt.val > maxPt.val) maxPt = pt;
      if (pt.val < minPt.val) minPt = pt;

      ctx.beginPath();
      ctx.arc(pt.x, pt.y, isMobile ? 3.5 : 4.5, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = options.lineColor || '#059669';
      ctx.lineWidth = 2.5;
      ctx.fill();
      ctx.stroke();

      // Show subset of X labels to avoid mobile crowding
      if (idx % stepInterval === 0 || idx === points.length - 1) {
        ctx.fillStyle = '#64748b';
        ctx.font = isMobile ? '10px sans-serif' : '11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(pt.label, pt.x, height - (isMobile ? 8 : 12));
      }
    });

    // Highlight High & Low values directly on chart
    if (points.length > 2 && options.prefix === '₹') {
      [maxPt, minPt].forEach((p, idx) => {
        const isHigh = idx === 0;
        const text = isHigh ? `Peak: ₹${p.val.toLocaleString('en-IN')}` : `Low: ₹${p.val.toLocaleString('en-IN')}`;
        ctx.fillStyle = isHigh ? '#047857' : '#b45309';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        const labelY = isHigh ? p.y - 10 : p.y + 16;
        ctx.fillText(text, Math.min(width - 45, Math.max(padding.left + 35, p.x)), labelY);
      });
    }

    // Attach interactive tooltip listener
    this.setupLineTooltip(canvas, points, options);
  },

  // 2. Multi-scenario Bar Chart (Conservative, Expected, Optimistic)
  drawScenarioBarChart(canvasId, scenarios) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const parentWidth = canvas.parentElement.clientWidth || 600;
    const width = canvas.width = parentWidth;
    const isMobile = width < 500;
    const height = canvas.height = isMobile ? 300 : 310;

    ctx.clearRect(0, 0, width, height);

    const keys = ['conservative', 'expected', 'optimistic'];
    const labels = isMobile ? ['Conservative', 'Expected', 'Optimistic'] : ['Conservative', 'Expected (Baseline)', 'Optimistic'];
    const colors = ['#f59e0b', '#059669', '#0284c7'];

    const padding = {
      top: 50,
      right: isMobile ? 15 : 30,
      bottom: isMobile ? 55 : 50,
      left: isMobile ? 65 : 85
    };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const revenues = keys.map(k => (scenarios[k] ? scenarios[k].expected_revenue_inr : 0));
    const profits = keys.map(k => (scenarios[k] ? scenarios[k].estimated_net_profit_inr : 0));
    const maxVal = Math.max(...revenues, ...profits) * 1.25 || 100000;

    // Draw Top Legend: Grey = Revenue, Green/Amber/Blue = Net Profit
    ctx.textAlign = 'left';
    ctx.font = '11px sans-serif';

    // Legend item 1: Gross Revenue
    ctx.fillStyle = '#94a3b8';
    ctx.fillRect(padding.left, 16, 12, 12);
    ctx.fillStyle = '#334155';
    ctx.fillText('Gross Revenue (₹)', padding.left + 18, 26);

    // Legend item 2: Net Return
    ctx.fillStyle = '#059669';
    ctx.fillRect(padding.left + (isMobile ? 125 : 160), 16, 12, 12);
    ctx.fillStyle = '#334155';
    ctx.fillText('Net Estimated Profit (₹)', padding.left + (isMobile ? 125 : 160) + 18, 26);

    // Horizontal Grid & Indian Currency Y-Axis Labels
    const gridLines = 4;
    for (let i = 0; i <= gridLines; i++) {
      const y = padding.top + (chartH / gridLines) * i;
      ctx.strokeStyle = '#f1f5f9';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      const val = Math.round(maxVal - (maxVal / gridLines) * i);
      ctx.fillStyle = '#64748b';
      ctx.font = isMobile ? '10px sans-serif' : '11px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(this.formatMoney(val, true), padding.left - 8, y + 4);
    }

    const groupWidth = chartW / keys.length;
    const barWidth = Math.min(isMobile ? 24 : 42, groupWidth * 0.32);
    const barGap = isMobile ? 4 : 8;

    keys.forEach((k, idx) => {
      const sc = scenarios[k] || {};
      const rev = revenues[idx];
      const prof = profits[idx];

      const revH = Math.max(4, (rev / maxVal) * chartH);
      const profH = Math.max(4, (prof / maxVal) * chartH);

      const totalBarsWidth = barWidth * 2 + barGap;
      const groupCenterX = padding.left + groupWidth * idx + groupWidth / 2;
      const revX = groupCenterX - totalBarsWidth / 2;
      const profX = revX + barWidth + barGap;

      const revY = padding.top + chartH - revH;
      const profY = padding.top + chartH - profH;

      // 1. Revenue Bar (Light slate)
      ctx.fillStyle = '#cbd5e1';
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(revX, revY, barWidth, revH, [4, 4, 0, 0]);
      else ctx.rect(revX, revY, barWidth, revH);
      ctx.fill();

      // Money value visible above Revenue bar
      ctx.fillStyle = '#475569';
      ctx.font = isMobile ? 'bold 9px sans-serif' : 'bold 10.5px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(this.formatMoney(rev, true), revX + barWidth / 2, revY - 6);

      // 2. Net Profit Bar (Colored)
      ctx.fillStyle = colors[idx];
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(profX, profY, barWidth, profH, [4, 4, 0, 0]);
      else ctx.rect(profX, profY, barWidth, profH);
      ctx.fill();

      // Money value & ROI visible above Profit bar
      ctx.fillStyle = colors[idx];
      ctx.font = isMobile ? 'bold 9.5px sans-serif' : 'bold 11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(this.formatMoney(prof, true), profX + barWidth / 2, profY - 16);

      // ROI % tag
      ctx.font = isMobile ? '8.5px sans-serif' : '9.5px sans-serif';
      ctx.fillText(`${sc.roi_percentage || 0}% ROI`, profX + barWidth / 2, profY - 5);

      // Scenario Name below
      ctx.fillStyle = '#1e293b';
      ctx.font = isMobile ? 'bold 10px sans-serif' : 'bold 11.5px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(labels[idx], groupCenterX, height - (isMobile ? 16 : 14));
    });

    this.setupBarTooltip(canvas, keys, labels, scenarios, width, height, padding, groupWidth, barWidth, barGap);
  },

  // Tooltip handler for line chart
  setupLineTooltip(canvas, points, options) {
    let tooltip = document.getElementById('chartTooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'chartTooltip';
      tooltip.style.position = 'absolute';
      tooltip.style.display = 'none';
      tooltip.style.padding = '0.5rem 0.75rem';
      tooltip.style.background = '#0f172a';
      tooltip.style.color = '#ffffff';
      tooltip.style.borderRadius = '6px';
      tooltip.style.fontSize = '0.8rem';
      tooltip.style.pointerEvents = 'none';
      tooltip.style.boxShadow = '0 10px 25px rgba(0,0,0,0.3)';
      tooltip.style.zIndex = '3000';
      document.body.appendChild(tooltip);
    }

    const handler = (e) => {
      const rect = canvas.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const x = clientX - rect.left;
      const y = clientY - rect.top;

      let closest = null;
      let minDistance = 40;

      points.forEach(pt => {
        const dist = Math.hypot(pt.x - x, pt.y - y);
        if (dist < minDistance) {
          minDistance = dist;
          closest = pt;
        }
      });

      if (closest) {
        tooltip.innerHTML = `
          <div style="font-weight:700; color:#34d399;">📅 ${closest.label}</div>
          <div style="font-size:1rem; font-weight:800; margin-top:2px;">₹${closest.val.toLocaleString('en-IN')} / quintal</div>
        `;
        tooltip.style.display = 'block';
        tooltip.style.left = `${clientX + 12}px`;
        tooltip.style.top = `${clientY - 40}px`;
      } else {
        tooltip.style.display = 'none';
      }
    };

    canvas.onmousemove = handler;
    canvas.ontouchstart = handler;
    canvas.ontouchmove = handler;
    canvas.onmouseleave = () => { tooltip.style.display = 'none'; };
  },

  // Tooltip handler for scenario bar chart
  setupBarTooltip(canvas, keys, labels, scenarios, width, height, padding, groupWidth, barWidth, barGap) {
    let tooltip = document.getElementById('scenarioBarTooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'scenarioBarTooltip';
      tooltip.style.position = 'absolute';
      tooltip.style.display = 'none';
      tooltip.style.padding = '0.75rem 1rem';
      tooltip.style.background = '#0f172a';
      tooltip.style.color = '#ffffff';
      tooltip.style.borderRadius = '8px';
      tooltip.style.fontSize = '0.82rem';
      tooltip.style.pointerEvents = 'none';
      tooltip.style.boxShadow = '0 10px 25px rgba(0,0,0,0.3)';
      tooltip.style.zIndex = '3000';
      document.body.appendChild(tooltip);
    }

    const handler = (e) => {
      const rect = canvas.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const x = clientX - rect.left;

      let matchedIdx = -1;
      keys.forEach((k, idx) => {
        const groupLeft = padding.left + groupWidth * idx;
        if (x >= groupLeft && x <= groupLeft + groupWidth) {
          matchedIdx = idx;
        }
      });

      if (matchedIdx >= 0) {
        const k = keys[matchedIdx];
        const sc = scenarios[k] || {};
        const rev = sc.expected_revenue_inr || 0;
        const cost = sc.total_cost_inr || 0;
        const prof = sc.estimated_net_profit_inr || 0;
        const roi = sc.roi_percentage || 0;

        tooltip.innerHTML = `
          <div style="font-weight:800; color:#38bdf8; margin-bottom:4px; font-size:0.9rem;">📊 ${labels[matchedIdx]}</div>
          <div>Gross Revenue: <strong style="color:#cbd5e1;">₹${rev.toLocaleString('en-IN')}</strong> (${AgriCharts.formatMoney(rev, true)})</div>
          <div>Cultivation Cost: <strong style="color:#f87171;">₹${cost.toLocaleString('en-IN')}</strong></div>
          <div style="margin-top:2px; padding-top:4px; border-top:1px solid #334155;">
            Net Profit: <strong style="color:#34d399; font-size:0.95rem;">₹${prof.toLocaleString('en-IN')}</strong> (${AgriCharts.formatMoney(prof, true)})
          </div>
          <div style="color:#fbbf24; font-weight:700; margin-top:2px;">ROI: ${roi}%</div>
        `;
        tooltip.style.display = 'block';
        tooltip.style.left = `${clientX + 14}px`;
        tooltip.style.top = `${clientY - 60}px`;
      } else {
        tooltip.style.display = 'none';
      }
    };

    canvas.onmousemove = handler;
    canvas.ontouchstart = handler;
    canvas.ontouchmove = handler;
    canvas.onmouseleave = () => { tooltip.style.display = 'none'; };
  },

  // 3. Radar Chart for Farm Suitability Breakdown
  drawRadarChart(canvasId, scores) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = Math.min(canvas.parentElement.clientWidth || 320, 320);
    canvas.width = canvas.height = size;

    ctx.clearRect(0, 0, size, size);

    const centerX = size / 2;
    const centerY = size / 2;
    const radius = size * 0.36;

    const categories = [
      { label: 'Climate', key: 'climate' },
      { label: 'Soil', key: 'soil' },
      { label: 'Water', key: 'water' },
      { label: 'Weather', key: 'weather' },
      { label: 'Season', key: 'season' },
      { label: 'Market', key: 'market' },
      { label: 'Economics', key: 'economics' }
    ];

    const numAxes = categories.length;
    const angleStep = (Math.PI * 2) / numAxes;

    // Background concentric polygon webs
    for (let level = 1; level <= 4; level++) {
      const r = (radius / 4) * level;
      ctx.beginPath();
      for (let i = 0; i < numAxes; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = '#e2e8f0';
      ctx.stroke();
    }

    // Axes
    for (let i = 0; i < numAxes; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.strokeStyle = '#cbd5e1';
      ctx.stroke();

      // Axis label
      const labelX = centerX + (radius + 20) * Math.cos(angle);
      const labelY = centerY + (radius + 20) * Math.sin(angle);
      ctx.fillStyle = '#64748b';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(categories[i].label, labelX, labelY + 4);
    }

    // Data polygon
    ctx.beginPath();
    categories.forEach((cat, i) => {
      const val = scores[cat.key] || 80;
      const r = (radius * (val / 100));
      const angle = i * angleStep - Math.PI / 2;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(16, 185, 129, 0.35)';
    ctx.fill();
    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 2.5;
    ctx.stroke();
  }
};

window.AgriCharts = AgriCharts;
