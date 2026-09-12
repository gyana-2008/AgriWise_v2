/**
 * 🌾 AGRIWISE AI - Universal Shopping Cart Engine
 * Handles agricultural input purchases (Seeds, Fertilizers, Equipment),
 * cart persistence across navigation, slide-over drawer UI, and order checkout.
 */

const AgriCart = {
  storageKey: 'agriwise_cart',
  drawerId: 'agri-cart-drawer',
  backdropId: 'agri-cart-backdrop',

  // Get current items from localStorage
  getItems() {
    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Error reading cart:', e);
      return [];
    }
  },

  // Save items to localStorage and notify UI
  saveItems(items) {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(items));
      this.updateBadges();
      this.renderDrawer();
    } catch (e) {
      console.error('Error saving cart:', e);
    }
  },

  // Add an item to cart
  addItem(product, qty = 1) {
    if (!product || !product.id) return;
    const items = this.getItems();
    const existingIndex = items.findIndex(item => String(item.id) === String(product.id));

    if (existingIndex > -1) {
      items[existingIndex].quantity += qty;
    } else {
      items.push({
        id: product.id,
        name: product.name || 'Agricultural Input',
        price: Number(product.price) || 0,
        unit: product.unit || 'bag',
        category: product.category || 'Inputs',
        image: product.image || 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=120&auto=format&fit=crop&q=80',
        dealer_name: product.dealer_name || 'AgriWise Verified Dealer',
        dealer_id: product.dealer_id || null,
        quantity: Math.max(1, qty)
      });
    }

    this.saveItems(items);
    this.showToast(`✅ Added ${product.name} to Cart!`);
    this.openDrawer();
  },

  // Update item quantity
  updateQuantity(productId, newQty) {
    let items = this.getItems();
    if (newQty <= 0) {
      this.removeItem(productId);
      return;
    }
    const target = items.find(item => String(item.id) === String(productId));
    if (target) {
      target.quantity = Number(newQty);
      this.saveItems(items);
    }
  },

  // Remove item from cart
  removeItem(productId) {
    let items = this.getItems();
    items = items.filter(item => String(item.id) !== String(productId));
    this.saveItems(items);
    this.showToast('🗑️ Item removed from cart');
  },

  // Clear all items
  clearCart() {
    this.saveItems([]);
  },

  // Count total items
  getItemCount() {
    const items = this.getItems();
    return items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0);
  },

  // Calculate Subtotal in INR
  getSubtotal() {
    const items = this.getItems();
    return items.reduce((sum, item) => sum + (Number(item.price) * Number(item.quantity) || 0), 0);
  },

  // Format currency helper
  formatMoney(amount) {
    if (window.AgriCharts && typeof window.AgriCharts.formatMoney === 'function') {
      return window.AgriCharts.formatMoney(amount, false);
    }
    if (window.AgriState && typeof window.AgriState.formatCurrency === 'function') {
      return window.AgriState.formatCurrency(amount);
    }
    return `₹${Number(amount || 0).toLocaleString('en-IN')}`;
  },

  // Update all badge elements in DOM
  updateBadges() {
    const count = this.getItemCount();
    const badges = document.querySelectorAll('.cart-badge, #nav-cart-count, [data-cart-count]');
    badges.forEach(b => {
      b.textContent = count;
      if (count > 0) {
        b.classList.remove('hidden');
        b.style.display = 'inline-flex';
      } else {
        b.style.display = 'none';
      }
    });
  },

  // Toast Notification
  showToast(message) {
    let toast = document.getElementById('agri-cart-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'agri-cart-toast';
      toast.className = 'agri-cart-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(this._toastTimeout);
    this._toastTimeout = setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  },

  // Ensure Drawer markup is injected
  ensureDrawerMarkup() {
    if (document.getElementById(this.drawerId)) return;

    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.id = this.backdropId;
    backdrop.className = 'agri-cart-backdrop';
    backdrop.onclick = () => this.closeDrawer();
    document.body.appendChild(backdrop);

    // Create drawer
    const drawer = document.createElement('aside');
    drawer.id = this.drawerId;
    drawer.className = 'agri-cart-drawer';
    drawer.setAttribute('aria-label', 'Shopping Cart');
    drawer.innerHTML = `
      <div class="cart-header">
        <div class="cart-header-title">
          <span class="cart-header-icon">🛒</span>
          <h3>AgriWise Cart (<span class="cart-count-title">0</span>)</h3>
        </div>
        <button class="cart-close-btn" onclick="AgriCart.closeDrawer()" title="Close Cart">✕</button>
      </div>
      <div class="cart-body" id="agri-cart-body">
        <!-- Rendered dynamically -->
      </div>
      <div class="cart-footer" id="agri-cart-footer">
        <!-- Rendered dynamically -->
      </div>
    `;
    document.body.appendChild(drawer);
  },

  // Render the cart drawer contents
  renderDrawer() {
    this.ensureDrawerMarkup();
    const body = document.getElementById('agri-cart-body');
    const footer = document.getElementById('agri-cart-footer');
    const titleCount = document.querySelector('.cart-count-title');
    if (!body || !footer) return;

    const items = this.getItems();
    const totalCount = this.getItemCount();
    if (titleCount) titleCount.textContent = totalCount;

    if (items.length === 0) {
      body.innerHTML = `
        <div class="cart-empty-state">
          <div class="cart-empty-icon">🌾</div>
          <h4>Your cart is empty</h4>
          <p>Explore certified seeds, subsidized fertilizers, and farm equipment from local verified dealers.</p>
          <a href="/fertilizer-market" class="btn btn-primary btn-sm" style="margin-top: 1rem;">
            Browse Farm Inputs
          </a>
        </div>
      `;
      footer.innerHTML = '';
      return;
    }

    // Render items list
    let itemsHtml = '<div class="cart-items-list">';
    items.forEach(item => {
      const lineTotal = item.price * item.quantity;
      itemsHtml += `
        <div class="cart-item-row" data-id="${item.id}">
          <img src="${item.image}" alt="${item.name}" class="cart-item-thumb" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=120&auto=format&fit=crop&q=80';">
          <div class="cart-item-info">
            <div class="cart-item-name">${item.name}</div>
            <div class="cart-item-subtext">${item.dealer_name || 'Verified Dealer'} • ${this.formatMoney(item.price)} / ${item.unit}</div>
            <div class="cart-item-actions">
              <div class="cart-qty-picker">
                <button type="button" class="qty-btn" onclick="AgriCart.updateQuantity('${item.id}', ${item.quantity - 1})">-</button>
                <span class="qty-num">${item.quantity}</span>
                <button type="button" class="qty-btn" onclick="AgriCart.updateQuantity('${item.id}', ${item.quantity + 1})">+</button>
              </div>
              <span class="cart-item-linetotal">${this.formatMoney(lineTotal)}</span>
              <button type="button" class="cart-item-remove" onclick="AgriCart.removeItem('${item.id}')" title="Remove item">🗑️</button>
            </div>
          </div>
        </div>
      `;
    });
    itemsHtml += '</div>';
    body.innerHTML = itemsHtml;

    // Delivery Address prefill
    const user = (window.AgriState && window.AgriState.currentUser) || {};
    const defaultAddr = [user.village, user.district, user.state].filter(Boolean).join(', ') || 'Ludhiana, Punjab';

    const subtotal = this.getSubtotal();
    const deliveryFee = 0; // Free delivery for farmers
    const grandTotal = subtotal + deliveryFee;

    footer.innerHTML = `
      <div class="cart-delivery-box">
        <label for="cart-delivery-addr">📍 Delivery Address / Village:</label>
        <input type="text" id="cart-delivery-addr" class="cart-addr-input" value="${defaultAddr}" placeholder="Enter farm delivery address">
      </div>
      <div class="cart-bill-breakdown">
        <div class="bill-row">
          <span>Items Subtotal:</span>
          <strong>${this.formatMoney(subtotal)}</strong>
        </div>
        <div class="bill-row">
          <span>Subsidized Delivery:</span>
          <span class="text-success" style="color: #10b981; font-weight: 600;">FREE (Govt DBT/Local Dealer)</span>
        </div>
        <div class="bill-row total-row">
          <span>Total Payable:</span>
          <strong class="total-amount">${this.formatMoney(grandTotal)}</strong>
        </div>
      </div>
      <div class="cart-checkout-actions">
        <button type="button" class="btn btn-success btn-block" id="btn-cart-checkout" onclick="AgriCart.processCheckout()">
          ✅ Place Order (${this.formatMoney(grandTotal)})
        </button>
      </div>
    `;
  },

  // Open Drawer
  openDrawer() {
    this.ensureDrawerMarkup();
    this.renderDrawer();
    const drawer = document.getElementById(this.drawerId);
    const backdrop = document.getElementById(this.backdropId);
    if (drawer && backdrop) {
      backdrop.classList.add('active');
      drawer.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  },

  // Close Drawer
  closeDrawer() {
    const drawer = document.getElementById(this.drawerId);
    const backdrop = document.getElementById(this.backdropId);
    if (drawer && backdrop) {
      backdrop.classList.remove('active');
      drawer.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  toggleDrawer() {
    const drawer = document.getElementById(this.drawerId);
    if (drawer && drawer.classList.contains('active')) {
      this.closeDrawer();
    } else {
      this.openDrawer();
    }
  },

  // Process Checkout & create real DB Order
  async processCheckout() {
    const items = this.getItems();
    if (items.length === 0) {
      alert('Your cart is empty.');
      return;
    }

    const addrInput = document.getElementById('cart-delivery-addr');
    const address = addrInput ? addrInput.value.trim() : 'Local Farm Address';
    if (!address) {
      alert('Please enter a delivery address or village name.');
      return;
    }

    const btn = document.getElementById('btn-cart-checkout');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⏳ Processing Order...';
    }

    try {
      const user = (window.AgriState && window.AgriState.currentUser) || { id: 1, name: 'Farmer' };
      const subtotal = this.getSubtotal();

      const primaryDealer = items[0]?.dealer_name || 'IFFCO Kisan Seva Kendra';
      const primaryDealerId = items[0]?.dealer_id || null;

      const orderPayload = {
        user_id: user.id || 1,
        dealer_id: primaryDealerId,
        partner_name: primaryDealer,
        category: 'INPUTS',
        amount_inr: subtotal,
        delivery_address: address,
        items_json: JSON.stringify(items),
        status: 'ORDERED'
      };

      const result = await window.AgriAPI.createOrder(orderPayload);

      // Order created successfully!
      this.clearCart();
      this.closeDrawer();

      // Show friendly confirmation modal
      this.showOrderSuccessModal(result.order || result, address, subtotal);
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Failed to place order. Please try again: ' + (err.message || 'Server error'));
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '✅ Place Order';
      }
    }
  },

  // Modal confirming order with redirect option
  showOrderSuccessModal(order, address, amount) {
    const orderId = order.order_id || order.id || ('AGRI-' + Math.floor(100000 + Math.random() * 900000));
    const modal = document.createElement('div');
    modal.className = 'agri-order-modal-backdrop';
    modal.innerHTML = `
      <div class="agri-order-modal">
        <div class="modal-icon">🎉</div>
        <h3>Order Placed Successfully!</h3>
        <p class="modal-subtitle">Order Reference: <strong>${orderId}</strong></p>
        <div class="order-details-card">
          <div class="detail-row">
            <span>Total Value:</span>
            <strong>${this.formatMoney(amount)}</strong>
          </div>
          <div class="detail-row">
            <span>Delivery Destination:</span>
            <span>${address}</span>
          </div>
          <div class="detail-row">
            <span>Payment Mode:</span>
            <span class="badge badge-success">Cash on Delivery / DBT</span>
          </div>
          <div class="detail-row">
            <span>Status:</span>
            <span class="badge badge-primary">ORDERED (Dealer Dispatching)</span>
          </div>
        </div>
        <p style="font-size: 0.85rem; color: #64748b; margin: 1rem 0;">
          The local dealer will call to confirm dispatch. You can track status in your Orders tab.
        </p>
        <div class="modal-actions" style="display: flex; gap: 0.75rem; justify-content: center;">
          <a href="/farmer-orders" class="btn btn-primary" style="flex: 1; text-align: center; text-decoration: none;">
            📦 View My Orders
          </a>
          <button type="button" class="btn btn-secondary" onclick="this.closest('.agri-order-modal-backdrop').remove()">
            Continue Shopping
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  },

  // Initialize on page load
  init() {
    this.ensureDrawerMarkup();
    this.updateBadges();

    window.addEventListener('storage', (e) => {
      if (e.key === this.storageKey) {
        this.updateBadges();
        this.renderDrawer();
      }
    });

    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-add-to-cart]');
      if (!btn) return;
      try {
        const rawData = btn.getAttribute('data-product');
        if (rawData) {
          const prod = JSON.parse(rawData);
          this.addItem(prod);
        }
      } catch (err) {
        console.warn('Error parsing data-product:', err);
      }
    });
  }
};

window.AgriCart = AgriCart;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => AgriCart.init());
} else {
  AgriCart.init();
}
