/**
 * 🌾 AGRIWISE AI - Universal Navigation & Demo Journey Controller
 * Injects responsive top banner, sticky navbar, footer, role selector, and mobile drawer.
 */

const AgriNav = {
  init() {
    this.ensureCartLoaded();
    this.renderDemoBanner();
    this.renderHeader();
    this.renderMobileDrawer();
    this.renderMobileBottomNav();
    this.renderFooter();
    this.highlightActivePage();
    this.syncLanguageDropdown();
    if (window.AgriI18n && typeof window.AgriI18n.applyTranslations === 'function') {
      window.AgriI18n.applyTranslations();
    }
    if (window.AgriCart && typeof window.AgriCart.updateBadges === 'function') {
      window.AgriCart.updateBadges();
    }
  },

  ensureCartLoaded() {
    if (!window.AgriCart && !document.querySelector('script[src*="cart.js"]')) {
      const script = document.createElement('script');
      script.src = '/js/cart.js';
      document.head.appendChild(script);
    }
  },

  syncLanguageDropdown() {
    const langSelect = document.getElementById('langSelect');
    const curLang = (window.AgriState && window.AgriState.currentLang) || localStorage.getItem('agriwise_lang') || 'en';
    if (langSelect) {
      langSelect.value = curLang;
    }
  },

  getCurrentPath() {
    const path = window.location.pathname.replace(/^\/|\/$/g, '').toLowerCase();
    return path || 'index';
  },

  renderDemoBanner() {
    const currentPath = this.getCurrentPath();
    const steps = window.AgriState.demoJourneySteps;
    const currentStepIndex = steps.findIndex(s => s.route.includes(currentPath));
    const currentStepNum = currentStepIndex >= 0 ? currentStepIndex + 1 : 1;
    const nextStep = steps[currentStepIndex + 1] || steps[0];

    const bannerHtml = `
      <div class="demo-journey-banner">
        <div class="demo-banner-left">
          <span class="demo-badge-pulse">🚀 Demo Journey</span>
          <span class="banner-text-long">Hackathon Evaluator Guided Tour:</span>
          <span>Step ${currentStepNum} of ${steps.length}: <strong>${steps[currentStepIndex >= 0 ? currentStepIndex : 0].title}</strong></span>
        </div>
        <div class="demo-banner-actions">
          <a href="${nextStep.route}" class="btn-demo-action">
            <span>Next Step: ${nextStep.title.split('.')[1] || 'Next'}</span>
            <span>➔</span>
          </a>
          <button onclick="AgriNav.showJourneyModal()" class="btn-demo-action" style="background: rgba(0,0,0,0.25);">
            <span>📑 All Steps</span>
          </button>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('afterbegin', bannerHtml);
  },

  renderHeader() {
    const currentRole = window.AgriState.currentRole || 'FARMER';

    const currentPath = this.getCurrentPath();

    // Universal core agricultural navigation tabs that are ALWAYS visible on top
    let navLinksHtml = `
      <a href="/dashboard" class="nav-link" data-route="dashboard">🌾 Dashboard</a>
      <a href="/crop-recommendation" class="nav-link" data-route="crop-recommendation">🌱 Crops</a>
      <a href="/fertilizer-market" class="nav-link" data-route="fertilizer-market">🛒 Inputs</a>
      <a href="/market-intelligence" class="nav-link" data-route="market-intelligence">💹 Markets</a>
      <a href="/transport-marketplace" class="nav-link" data-route="transport-marketplace">🚚 Services</a>
      <a href="/farm-equipment" class="nav-link" data-route="farm-equipment">🚜 Farm Equipment</a>
      <a href="/farmer-orders" class="nav-link" data-route="farmer-orders">📦 Orders</a>
      <a href="/ai-assistant" class="nav-link" data-route="ai-assistant">🤖 AI Advisor</a>
    `;

    // Specialized role portal tabs seamlessly appended when active or browsing that section
    if (currentRole === 'DEALER' || currentPath.includes('dealer')) {
      navLinksHtml += `<a href="/dealer-dashboard" class="nav-link" data-route="dealer-dashboard">🏪 Dealer Hub</a>`;
    } else if (currentRole === 'SERVICE_PROVIDER' || currentRole === 'TRANSPORTER' || currentPath.includes('transport-dashboard')) {
      navLinksHtml += `<a href="/transport-dashboard" class="nav-link" data-route="transport-dashboard">🚜 Fleet Hub</a>`;
    } else if (currentRole === 'ADMIN' || currentPath.includes('admin')) {
      navLinksHtml += `<a href="/admin" class="nav-link" data-route="admin">⚙️ Admin</a>`;
    } else if (currentRole === 'BUYER' || currentPath.includes('buyer')) {
      navLinksHtml += `<a href="/buyer-dashboard" class="nav-link" data-route="buyer-dashboard">🏢 Buyers</a>`;
    }

    // Static verified role badge
    let roleBadgeClass = 'badge-role-farmer';
    let roleBadgeText = 'Farmer';
    let roleBadgeIcon = '👨‍🌾';

    if (currentRole === 'DEALER') {
      roleBadgeClass = 'badge-role-dealer';
      roleBadgeText = 'Dealer';
      roleBadgeIcon = '🏪';
    } else if (currentRole === 'SERVICE_PROVIDER' || currentRole === 'TRANSPORTER') {
      roleBadgeClass = 'badge-role-provider';
      roleBadgeText = 'Service Provider';
      roleBadgeIcon = '🚜';
    } else if (currentRole === 'BUYER') {
      roleBadgeClass = 'badge-role-buyer';
      roleBadgeText = 'Buyer';
      roleBadgeIcon = '🏢';
    } else if (currentRole === 'ADMIN') {
      roleBadgeClass = 'badge-role-admin';
      roleBadgeText = 'Admin';
      roleBadgeIcon = '⚙️';
    }

    const headerHtml = `
      <header class="main-header">
        <div class="container nav-container">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <!-- Mobile Menu Toggle Button -->
            <button type="button" class="mobile-menu-toggle" onclick="AgriNav.toggleMobileDrawer()" title="Open Navigation Menu">
              ☰
            </button>
            <a href="/" class="brand-logo">
              <div class="brand-icon">🌾</div>
              <span>AGRIWISE<span class="ai-tag">AI</span></span>
            </a>
          </div>

          <nav class="nav-links">
            ${navLinksHtml}
          </nav>

          <div class="header-actions">
            <!-- Static Permanent Registered Role Badge -->
            <div class="user-role-badge ${roleBadgeClass}" onclick="AgriNav.toggleUserDropdown(event)" style="cursor: pointer;" title="Active Role: ${roleBadgeText} (Click to manage role)">
              <span>${roleBadgeIcon}</span>
              <span class="badge-role-text">${roleBadgeText}</span>
            </div>

            <!-- Shopping Cart Button with Live Counter Badge -->
            <button type="button" class="nav-cart-btn" onclick="AgriNav.handleCartClick()" title="View Agricultural Cart">
              <span>🛒</span>
              <span class="cart-btn-label">Cart</span>
              <span class="cart-badge" id="nav-cart-count" style="display: none;">0</span>
            </button>

            <!-- Multilingual Indian Languages Switcher -->
            <select id="langSelect" class="lang-select" onchange="AgriNav.handleLangChange(this.value)" title="Choose Language / भाषा चुनें">
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
              <option value="mr">मराठी (Marathi)</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="gu">ગુજરાતી (Gujarati)</option>
              <option value="bn">বাংলা (Bengali)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
            </select>

            <!-- Notifications Button -->
            <a href="/notifications" class="notif-bell-btn" title="View Agricultural & Weather Notifications">
              🔔
              <span class="notif-badge-count">3</span>
            </a>

            <!-- User Authentication Status & Profile Dropdown -->
            ${this.renderUserAuthNav()}
          </div>
        </div>
      </header>
    `;

    document.querySelector('.demo-journey-banner').insertAdjacentHTML('afterend', headerHtml);
    this.setupDropdownListeners();
  },

  handleCartClick() {
    if (window.AgriCart && typeof window.AgriCart.openDrawer === 'function') {
      window.AgriCart.openDrawer();
    } else {
      window.location.href = '/fertilizer-market';
    }
  },

  handleLangChange(langCode) {
    if (window.AgriState && typeof window.AgriState.setLang === 'function') {
      window.AgriState.setLang(langCode);
    }
    if (window.AgriI18n && typeof window.AgriI18n.setLanguage === 'function') {
      window.AgriI18n.setLanguage(langCode);
    }
  },

  renderMobileDrawer() {
    if (document.getElementById('mobileNavDrawer')) return;

    const currentRole = window.AgriState.currentRole || 'FARMER';
    const user = window.AgriState.currentUser || { name: 'Farmer User', role: currentRole };

    let roleIcon = '👨‍🌾';
    let roleText = 'Farmer';
    if (currentRole === 'DEALER') { roleIcon = '🏪'; roleText = 'Input Dealer'; }
    else if (currentRole === 'SERVICE_PROVIDER' || currentRole === 'TRANSPORTER') { roleIcon = '🚜'; roleText = 'Service Provider'; }

    const drawerHtml = `
      <div id="mobileNavBackdrop" class="mobile-nav-backdrop" onclick="AgriNav.closeMobileDrawer()"></div>
      <aside id="mobileNavDrawer" class="mobile-nav-drawer">
        <div class="mobile-drawer-header">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.4rem;">🌾</span>
            <h3>AGRIWISE AI</h3>
          </div>
          <button type="button" class="mobile-drawer-close" onclick="AgriNav.closeMobileDrawer()">&times;</button>
        </div>

        <div class="mobile-drawer-user">
          <div>
            <div style="font-weight: 700; color: var(--text-main); font-size: 0.95rem;">${user.name}</div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">${roleIcon} Registered as ${roleText}</div>
          </div>
          <button type="button" class="btn btn-outline-primary btn-sm" onclick="AgriNav.handleCartClick(); AgriNav.closeMobileDrawer();" style="padding: 4px 8px; font-size: 0.8rem;">
            🛒 Cart (<span class="cart-badge" style="position: static; display: inline-flex; font-size: 0.7rem; min-width: 16px; height: 16px;">0</span>)
          </button>
        </div>

        <nav class="mobile-drawer-links">
          <a href="/dashboard" class="mobile-drawer-link" data-route="dashboard">
            <span>🌾</span> <span>Farm Dashboard</span>
          </a>
          <a href="/crop-recommendation" class="mobile-drawer-link" data-route="crop-recommendation">
            <span>🌱</span> <span>Crops & Recommendations</span>
          </a>
          <a href="/fertilizer-market" class="mobile-drawer-link" data-route="fertilizer-market">
            <span>🛒</span> <span>Inputs & Fertilizer Market</span>
          </a>
          <a href="/transport-marketplace" class="mobile-drawer-link" data-route="transport-marketplace">
            <span>🚚</span> <span>Services & Mandi Logistics</span>
          </a>
          <a href="/farm-equipment" class="mobile-drawer-link" data-route="farm-equipment">
            <span>🚜</span> <span>Farm Equipment Rental</span>
          </a>
          <a href="/market-intelligence" class="mobile-drawer-link" data-route="market-intelligence">
            <span>💹</span> <span>Market & Live Mandi Prices</span>
          </a>
          <a href="/farmer-orders" class="mobile-drawer-link" data-route="farmer-orders">
            <span>📦</span> <span>My Orders & Bookings</span>
          </a>
          <a href="/farm-profile" class="mobile-drawer-link" data-route="farm-profile">
            <span>👤</span> <span>Farm Profile & Land GPS</span>
          </a>
          <a href="/farm-analysis" class="mobile-drawer-link" data-route="farm-analysis">
            <span>🔬</span> <span>Soil & Water Health Score</span>
          </a>
          <a href="/crop-shortage" class="mobile-drawer-link" data-route="crop-shortage">
            <span>🗺</span> <span>Crop Shortage & Deficit Map</span>
          </a>
          <a href="/payment" class="mobile-drawer-link" data-route="payment">
            <span>💳</span> <span>Payments & KCC Wallet</span>
          </a>
          <a href="/ai-assistant" class="mobile-drawer-link" data-route="ai-assistant">
            <span>🤖</span> <span>AI Agronomist Advisor</span>
          </a>
          <a href="/weather" class="mobile-drawer-link" data-route="weather">
            <span>⛅</span> <span>Weather Forecast & Alerts</span>
          </a>
          <a href="/notifications" class="mobile-drawer-link" data-route="notifications">
            <span>🔔</span> <span>Notifications</span>
          </a>

          <div style="height: 1px; background: var(--border-light); margin: 0.75rem 1rem;"></div>

          <div style="padding: 0.5rem 1.25rem;">
            <label style="display: block; font-size: 0.8rem; font-weight: 700; color: var(--text-muted); margin-bottom: 4px;">Choose Language / भाषा:</label>
            <select class="lang-select" style="width: 100%;" onchange="AgriNav.handleLangChange(this.value)">
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
              <option value="mr">मराठी (Marathi)</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="gu">ગુજરાતી (Gujarati)</option>
              <option value="bn">বাংলা (Bengali)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
            </select>
          </div>

          <div style="padding: 0.75rem 1.25rem;">
            <button type="button" class="btn btn-secondary btn-block btn-sm" onclick="AgriState.logout()" style="color: #dc2626;">
              🚪 Sign Out
            </button>
          </div>
        </nav>
      </aside>
    `;
    document.body.insertAdjacentHTML('beforeend', drawerHtml);
  },

  toggleMobileDrawer() {
    const drawer = document.getElementById('mobileNavDrawer');
    const backdrop = document.getElementById('mobileNavBackdrop');
    if (drawer && backdrop) {
      const isOpen = drawer.classList.contains('active');
      if (isOpen) {
        this.closeMobileDrawer();
      } else {
        drawer.classList.add('active');
        backdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    }
  },

  closeMobileDrawer() {
    const drawer = document.getElementById('mobileNavDrawer');
    const backdrop = document.getElementById('mobileNavBackdrop');
    if (drawer && backdrop) {
      drawer.classList.remove('active');
      backdrop.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  renderUserAuthNav() {
    const currentRole = window.AgriState.currentRole || 'FARMER';
    const isAuth = window.AgriState.isAuthenticated();
    const user = window.AgriState.currentUser || {
      name: currentRole === 'FARMER' ? 'Gurpreet Singh' :
            currentRole === 'DEALER' ? 'Rajinder Kumar' :
            currentRole === 'TRANSPORTER' ? 'Balwinder Singh' :
            currentRole === 'BUYER' ? 'ABC Agro Foods' : 'Administrator',
      role: currentRole
    };

    const roleEmoji = currentRole === 'FARMER' ? '👨‍🌾' :
                      currentRole === 'DEALER' ? '🏪' :
                      currentRole === 'TRANSPORTER' ? '🚛' :
                      currentRole === 'BUYER' ? '🏢' : '⚙️';

    const roleDashboardUrl = currentRole === 'DEALER' ? '/dealer-dashboard' :
                            currentRole === 'TRANSPORTER' ? '/transport-dashboard' :
                            currentRole === 'BUYER' ? '/buyer-dashboard' :
                            currentRole === 'ADMIN' ? '/admin' : '/dashboard';

    if (isAuth) {
      return `
        <div class="user-nav-dropdown">
          <button type="button" class="user-nav-btn" onclick="AgriNav.toggleUserDropdown(event)" title="My Account Profile">
            <span>${roleEmoji}</span>
            <span style="max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.name.split(' ')[0]}</span>
            <span style="font-size: 0.7rem; color: var(--text-muted);">▼</span>
          </button>
          <div id="userNavMenu" class="user-menu-dropdown">
            <div class="user-menu-header">
              <div class="user-menu-name">${user.name}</div>
              <div class="user-menu-meta">${roleEmoji} ${currentRole} • Punjab</div>
            </div>
            <a href="${roleDashboardUrl}" class="user-menu-item">
              <span>📊</span>
              <span>My Role Dashboard</span>
            </a>
            <a href="/farm-profile" class="user-menu-item">
              <span>🌾</span>
              <span>Farm Profile & Land</span>
            </a>
            <a href="/farmer-orders" class="user-menu-item">
              <span>📦</span>
              <span>Orders & Contracts</span>
            </a>
            <a href="/payment" class="user-menu-item">
              <span>💳</span>
              <span>KCC & Escrow Wallet</span>
            </a>
            <div class="user-menu-divider"></div>
            <div style="padding: 6px 12px 2px 12px; font-size: 0.72rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Switch Persona (Demo / Evaluation)</div>
            <div style="display: flex; gap: 4px; padding: 4px 12px 8px 12px; flex-wrap: wrap;">
              <button type="button" class="btn btn-sm ${currentRole === 'FARMER' ? 'btn-primary' : 'btn-secondary'}" style="padding: 2px 7px; font-size: 0.74rem;" onclick="AgriNav.switchRolePersona('FARMER')">👨‍🌾 Farmer</button>
              <button type="button" class="btn btn-sm ${currentRole === 'DEALER' ? 'btn-primary' : 'btn-secondary'}" style="padding: 2px 7px; font-size: 0.74rem;" onclick="AgriNav.switchRolePersona('DEALER')">🏪 Dealer</button>
              <button type="button" class="btn btn-sm ${(currentRole === 'SERVICE_PROVIDER' || currentRole === 'TRANSPORTER') ? 'btn-primary' : 'btn-secondary'}" style="padding: 2px 7px; font-size: 0.74rem;" onclick="AgriNav.switchRolePersona('SERVICE_PROVIDER')">🚜 Provider</button>
              <button type="button" class="btn btn-sm ${currentRole === 'ADMIN' ? 'btn-primary' : 'btn-secondary'}" style="padding: 2px 7px; font-size: 0.74rem;" onclick="AgriNav.switchRolePersona('ADMIN')">⚙️ Admin</button>
            </div>
            <div class="user-menu-divider"></div>
            <a href="/login" class="user-menu-item" style="color: var(--primary-700);">
              <span>🔄</span>
              <span>Switch Account / Login</span>
            </a>
            <button type="button" onclick="AgriState.logout()" class="user-menu-item" style="width: 100%; border: none; background: none; text-align: left; cursor: pointer; color: #dc2626;">
              <span>🚪</span>
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      `;
    } else {
      return `
        <a href="/login" class="btn btn-outline-primary btn-sm" style="font-weight: 700; white-space: nowrap;">
          <span>🔐 Sign In</span>
        </a>
      `;
    }
  },

  toggleUserDropdown(e) {
    if (e) e.stopPropagation();
    const menu = document.getElementById('userNavMenu');
    if (menu) menu.classList.toggle('show');
  },

  switchRolePersona(newRole) {
    if (window.AgriState) {
      AgriState.currentRole = newRole;
      if (AgriState.currentUser) {
        AgriState.currentUser.role = newRole;
        localStorage.setItem('agriwise_user', JSON.stringify(AgriState.currentUser));
      }
      localStorage.setItem('agriwise_role', newRole);
    }
    const dest = newRole === 'DEALER' ? '/dealer-dashboard' :
                 (newRole === 'SERVICE_PROVIDER' || newRole === 'TRANSPORTER') ? '/transport-dashboard' :
                 newRole === 'ADMIN' ? '/admin' : '/dashboard';
    window.location.href = dest;
  },

  setupDropdownListeners() {
    document.addEventListener('click', () => {
      const menu = document.getElementById('userNavMenu');
      if (menu && menu.classList.contains('show')) {
        menu.classList.remove('show');
      }
    });
  },

  renderMobileBottomNav() {
    const currentRole = window.AgriState.currentRole || 'FARMER';
    const isDealer = currentRole === 'DEALER';
    const isProvider = currentRole === 'SERVICE_PROVIDER' || currentRole === 'TRANSPORTER';

    const homeRoute = isDealer ? '/dealer-dashboard' : isProvider ? '/transport-dashboard' : '/dashboard';
    const homeLabel = isDealer ? 'Dealer' : isProvider ? 'Fleet' : 'Home';

    const mobileNavHtml = `
      <div class="mobile-bottom-nav">
        <a href="${homeRoute}" class="mobile-nav-item" data-route="${homeRoute.replace('/', '')}">
          <span class="mobile-nav-icon">🌾</span>
          <span>${homeLabel}</span>
        </a>
        <a href="/crop-recommendation" class="mobile-nav-item" data-route="crop-recommendation">
          <span class="mobile-nav-icon">🌱</span>
          <span>Crops</span>
        </a>
        <a href="/fertilizer-market" class="mobile-nav-item" data-route="fertilizer-market">
          <span class="mobile-nav-icon">🛒</span>
          <span>Inputs</span>
        </a>
        <a href="/farm-equipment" class="mobile-nav-item" data-route="farm-equipment">
          <span class="mobile-nav-icon">🚜</span>
          <span>Rentals</span>
        </a>
        <a href="/farmer-orders" class="mobile-nav-item" data-route="farmer-orders">
          <span class="mobile-nav-icon">📦</span>
          <span>Orders</span>
        </a>
        <button type="button" class="mobile-nav-item" style="background: none; border: none; cursor: pointer; width: 100%;" onclick="AgriNav.toggleMobileDrawer()">
          <span class="mobile-nav-icon">☰</span>
          <span>Menu</span>
        </button>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', mobileNavHtml);
  },

  renderFooter() {
    const footerHtml = `
      <footer class="main-footer">
        <div class="container">
          <div class="footer-grid">
            <div class="footer-col">
              <div class="brand-logo" style="color: #fff; margin-bottom: 1rem;">
                <div class="brand-icon">🌾</div>
                <span>AGRIWISE<span class="ai-tag">AI</span></span>
              </div>
              <p style="color: #94a3b8; font-size: 0.9rem; max-width: 380px;">
                Intelligent Crop, Seed, Input & Market Decision Platform designed for Indian agriculture. Empowering farmers with AI recommendations, live weather advisories, and direct mandi linkages.
              </p>
              <div style="display: flex; gap: 0.75rem; margin-top: 1.25rem;">
                <span class="badge badge-emerald">ICAR Agronomic Aligned</span>
                <span class="badge badge-blue">Open-Meteo Live</span>
              </div>
            </div>

            <div class="footer-col">
              <h5>Farmer Decision Suite</h5>
              <ul>
                <li><a href="/farm-profile">Farm Profile & GPS</a></li>
                <li><a href="/farm-analysis">Soil & Water Health Score</a></li>
                <li><a href="/crop-recommendation">Crop Recommendation Engine</a></li>
                <li><a href="/seed-recommendation">Certified Seed Comparison</a></li>
                <li><a href="/cultivation-plan">Day 0 to Harvest Timeline</a></li>
                <li><a href="/fertilizer-recommendation">N-P-K Fertilizer Plan</a></li>
              </ul>
            </div>

            <div class="footer-col">
              <h5>Market & Logistics</h5>
              <ul>
                <li><a href="/fertilizer-market">Nearby Input Dealers</a></li>
                <li><a href="/farm-equipment">Farm Equipment & Tractor Rental</a></li>
                <li><a href="/payment">Agri Payment Gateway & Escrow</a></li>
                <li><a href="/market-intelligence">Bloomberg Mandi Dashboard</a></li>
                <li><a href="/crop-shortage">National Deficit & Shortage Map</a></li>
                <li><a href="/buyer-marketplace">Verified Wholesale Millers</a></li>
                <li><a href="/transport-marketplace">Local Truck Transport Fleet</a></li>
                <li><a href="/profit-estimator">Multi-Scenario ROI Calculator</a></li>
              </ul>
            </div>

            <div class="footer-col">
              <h5>Platform & System</h5>
              <ul>
                <li><a href="/ai-assistant">Conversational AI Agronomist</a></li>
                <li><a href="/farm-calendar">Seasonal Task Calendar</a></li>
                <li><a href="/notifications">Severe Weather Alerts</a></li>
                <li><a href="/farm-report">Personalized Farm Dossier</a></li>
                <li><a href="/admin">Admin Weight Configuration</a></li>
                <li><a href="/login">Role Authentication</a></li>
              </ul>
            </div>
          </div>

          <div class="footer-bottom">
            <div>
              © 2026 AGRIWISE AI Technologies Pvt Ltd. All rights reserved. Made with ❤️ for Indian Farmers.
            </div>
            <div style="font-size: 0.8rem; color: #64748b;">
              ⚠️ Agronomic guidance based on ICAR guidelines. Local agricultural extension specialists and soil testing laboratories take precedence.
            </div>
          </div>
        </div>
      </footer>
    `;
    document.body.insertAdjacentHTML('beforeend', footerHtml);
  },

  highlightActivePage() {
    const current = this.getCurrentPath();
    document.querySelectorAll('.nav-link, .mobile-nav-item').forEach(el => {
      const route = el.getAttribute('data-route');
      if (route && (route === current || current.includes(route))) {
        el.classList.add('active');
      }
    });
  },

  showJourneyModal() {
    const steps = window.AgriState.demoJourneySteps;
    const currentPath = this.getCurrentPath();

    let itemsHtml = steps.map((s, idx) => {
      const isCurrent = s.route.includes(currentPath);
      return `
        <a href="${s.route}" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: ${isCurrent ? '#ecfdf5' : '#fff'}; border: 1px solid ${isCurrent ? '#10b981' : '#e2e8f0'}; border-radius: 8px; margin-bottom: 8px; text-decoration: none; color: inherit;">
          <div>
            <div style="font-weight: 700; font-size: 0.92rem; color: ${isCurrent ? '#047857' : '#0f172a'};">${s.title}</div>
            <div style="font-size: 0.8rem; color: #64748b;">${s.desc}</div>
          </div>
          <span style="color: #059669; font-weight: 700;">➔</span>
        </a>
      `;
    }).join('');

    const modalHtml = `
      <div id="journeyModal" style="position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 2000; display: flex; align-items: center; justify-content: center; padding: 1.5rem;" onclick="if(event.target.id === 'journeyModal') this.remove();">
        <div style="background: #fff; border-radius: 16px; max-width: 540px; width: 100%; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.2);">
          <div style="padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; background: #064e3b; color: #fff;">
            <div>
              <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 2px;">🌾 AgriWise AI End-to-End Journey</h3>
              <p style="font-size: 0.82rem; color: #a7f3d0; margin-bottom: 0;">Complete 15-step Farm-to-Market Evaluation Workflow</p>
            </div>
            <button onclick="document.getElementById('journeyModal').remove()" style="background: transparent; border: none; color: #fff; font-size: 1.5rem; cursor: pointer;">&times;</button>
          </div>
          <div style="padding: 1.25rem; overflow-y: auto; flex: 1;">
            ${itemsHtml}
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
  }
};

window.AgriNav = AgriNav;
document.addEventListener('DOMContentLoaded', () => {
  AgriNav.init();
});
