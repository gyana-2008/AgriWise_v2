/**
 * 🌾 AGRIWISE AI - API Communication Service
 * Handles live REST API calls with error handling and fallback resiliency.
 */

const AgriAPI = {
  baseUrl: window.location.origin,

  async get(endpoint, params = {}) {
    const url = new URL(endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`);
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null) {
        url.searchParams.append(key, params[key]);
      }
    });

    try {
      const res = await fetch(url.toString());
      if (!res.ok) {
        throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (err) {
      console.warn(`API call failed for ${endpoint}:`, err);
      throw err;
    }
  },

  async post(endpoint, data = {}) {
    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (err) {
      console.warn(`API POST failed for ${endpoint}:`, err);
      throw err;
    }
  },

  async patch(endpoint, data = {}) {
    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (err) {
      console.warn(`API PATCH failed for ${endpoint}:`, err);
      throw err;
    }
  },

  // Authentication API
  login(credentials) {
    return this.post('/api/auth/login', credentials);
  },

  sendOtp(phone, role = 'FARMER') {
    return this.post('/api/auth/send-otp', { phone, role });
  },

  verifyOtp(phone, otp, role = 'FARMER') {
    return this.post('/api/auth/verify-otp', { phone, otp, role });
  },

  logout() {
    return this.post('/api/auth/logout', {});
  },

  register(userData) {
    return this.post('/api/auth/register', userData);
  },

  getCurrentUser(role) {
    return this.get('/api/auth/me', role ? { role } : {});
  },

  // Specific API calls
  getLiveWeather(lat, lon, locName) {
    return this.get('/api/weather', { lat, lon, location: locName });
  },

  getFarms() {
    return this.get('/api/farms');
  },

  getFarm(id) {
    return this.get(`/api/farms/${id}`);
  },

  saveFarm(farmData) {
    return this.post('/api/farms', farmData);
  },

  getCropRecommendations(farmId) {
    return this.get('/api/recommendations/crops', { farm_id: farmId });
  },

  getSeeds(cropName) {
    return this.get('/api/seeds', { crop_name: cropName });
  },

  getFertilizerPlan(cropName, areaAcres, farmId) {
    return this.get('/api/recommendations/fertilizer', { crop_name: cropName, area_acres: areaAcres, farm_id: farmId });
  },

  getFertilizerDealers() {
    return this.get('/api/fertilizers/market');
  },

  getMarketPrices(cropName) {
    return this.get('/api/markets/prices', { crop_name: cropName });
  },

  getShortageData(cropName) {
    return this.get('/api/markets/shortage', { crop_name: cropName });
  },

  getBuyers(cropName) {
    return this.get('/api/buyers', { crop_name: cropName });
  },

  getTransporters() {
    return this.get('/api/transporters');
  },

  estimateProfit(params) {
    return this.post('/api/profit/estimate', params);
  },

  chatAssistant(message) {
    return this.post('/api/assistant/chat', { message });
  },

  getOrders(params = {}) {
    return this.get('/api/orders', params);
  },

  createOrder(orderData) {
    return this.post('/api/orders', orderData);
  },

  updateOrderStatus(orderId, status) {
    return this.patch(`/api/orders/${orderId}/status`, { status });
  },

  getNotifications() {
    return this.get('/api/notifications');
  },

  getAdminMetrics() {
    return this.get('/api/admin/metrics');
  },

  getAdminWeights() {
    return this.get('/api/admin/weights');
  },

  updateAdminWeights(weights) {
    return this.post('/api/admin/weights', weights);
  },

  // Agricultural Payment Gateway APIs
  createPaymentIntent(data) {
    return this.post('/api/payments/create-intent', data);
  },

  verifyPayment(data) {
    return this.post('/api/payments/verify', data);
  },

  getPaymentTransactions(params = {}) {
    return this.get('/api/payments/transactions', params);
  },

  getPaymentReceipt(txId) {
    return this.get(`/api/payments/receipt/${txId}`);
  },

  getPaymentStats() {
    return this.get('/api/payments/stats');
  },

  releaseEscrow(txId) {
    return this.post('/api/payments/escrow-release', { transaction_id: txId });
  },

  // Farm Equipment Rental & Custom Hiring Centre (CHC) APIs
  getEquipment(params = {}) {
    return this.get('/api/equipment', params);
  },

  getEquipmentDetails(id) {
    return this.get(`/api/equipment/${id}`);
  },

  checkEquipmentAvailability(data) {
    return this.post('/api/equipment/check-availability', data);
  },

  bookEquipment(data) {
    return this.post('/api/equipment/book', data);
  },

  getMyEquipmentRentals(farmerId) {
    return this.get('/api/equipment/my-rentals', farmerId ? { farmer_id: farmerId } : {});
  },

  cancelEquipmentBooking(bookingId, reason) {
    return this.post('/api/equipment/cancel-booking', { booking_id: bookingId, reason: reason || 'Cancelled by farmer' });
  },

  listEquipment(data) {
    return this.post('/api/equipment/list', data);
  },

  updateEquipmentStatus(id, isAvailable) {
    return this.patch(`/api/equipment/${id}/status`, { available: isAvailable });
  },

  getEquipmentReceipt(bookingId) {
    return this.get(`/api/equipment/booking/${bookingId}/receipt`);
  }
};

window.AgriAPI = AgriAPI;
