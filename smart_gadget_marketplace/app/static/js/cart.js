/* ===== CART.JS ===== */

let cart = JSON.parse(localStorage.getItem('sgCart') || '[]');

function saveCart() {
  localStorage.setItem('sgCart', JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const count = cart.reduce((sum, item) => sum + item.qty, 0);
  document.querySelectorAll('#cartCount').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

function addToCart(id, name, price, image) {
  const existing = cart.find(i => i.id === id);
  if (existing) {
    existing.qty++;
  } else {
    cart.push({ id, name, price, image, qty: 1 });
  }
  saveCart();
  showToast(`🛒 "${name.substring(0, 30)}..." added to cart!`, 'success');

  // Animate cart icon
  const cartBtn = document.querySelector('.cart-btn');
  if (cartBtn) {
    cartBtn.classList.add('bounce');
    setTimeout(() => cartBtn.classList.remove('bounce'), 600);
  }
}

function removeFromCart(id) {
  cart = cart.filter(i => i.id !== id);
  saveCart();
  renderCart();
  showToast('Item removed from cart', 'info');
}

function updateQty(id, delta) {
  const item = cart.find(i => i.id === id);
  if (!item) return;
  item.qty = Math.max(1, item.qty + delta);
  saveCart();
  renderCart();
}

function clearCart() {
  cart = [];
  saveCart();
  renderCart();
  showToast('Cart cleared', 'info');
}

function getCartTotal() {
  return cart.reduce((sum, item) => sum + item.price * item.qty, 0);
}

function renderCart() {
  const list = document.getElementById('cartItemsList');
  const emptyCart = document.getElementById('emptyCart');
  const countEl = document.getElementById('cartItemCount');
  if (!list) return;

  if (cart.length === 0) {
    list.style.display = 'none';
    if (emptyCart) emptyCart.style.display = 'flex';
    if (countEl) countEl.textContent = '0';
    updateSummary(0);
    return;
  }

  list.style.display = 'block';
  if (emptyCart) emptyCart.style.display = 'none';
  if (countEl) countEl.textContent = cart.reduce((s, i) => s + i.qty, 0);

  list.innerHTML = cart.map(item => `
    <div class="cart-item">
      <img class="cart-item-img" src="${item.image}" alt="${item.name}" onerror="this.src='https://via.placeholder.com/80'"/>
      <div class="cart-item-info">
        <h4>${item.name}</h4>
        <div class="cart-item-price">$${(item.price * item.qty).toFixed(2)}</div>
        <div class="cart-item-controls">
          <div class="item-qty">
            <button onclick="updateQty(${item.id}, -1)">−</button>
            <span>${item.qty}</span>
            <button onclick="updateQty(${item.id}, 1)">+</button>
          </div>
          <button class="item-remove" onclick="removeFromCart(${item.id})">
            <i class="fas fa-trash"></i> Remove
          </button>
        </div>
      </div>
    </div>
  `).join('');

  updateSummary(getCartTotal());
}

let appliedDiscount = 0;
const COUPONS = { 'SAVE10': 10, 'GADGET20': 20, 'TECH15': 15 };

function updateSummary(subtotal) {
  const subtotalEl = document.getElementById('subtotal');
  const discountEl = document.getElementById('discount');
  const totalEl = document.getElementById('totalPrice');
  const shippingEl = document.getElementById('shipping');
  if (!subtotalEl) return;

  const shipping = subtotal > 50 ? 0 : 9.99;
  const discountAmt = subtotal * (appliedDiscount / 100);
  const total = subtotal - discountAmt + shipping;

  subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
  if (shippingEl) shippingEl.textContent = shipping === 0 ? 'Free' : `$${shipping.toFixed(2)}`;
  if (discountEl) discountEl.textContent = `-$${discountAmt.toFixed(2)}`;
  if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
}

function applyCoupon() {
  const input = document.getElementById('couponInput');
  if (!input) return;
  const code = input.value.trim().toUpperCase();
  if (COUPONS[code]) {
    appliedDiscount = COUPONS[code];
    showToast(`Coupon "${code}" applied! ${appliedDiscount}% off 🎉`, 'success');
    updateSummary(getCartTotal());
    input.value = '';
  } else {
    showToast('Invalid coupon code', 'error');
    appliedDiscount = 0;
  }
}

function renderCheckoutSummary() {
  const el = document.getElementById('checkoutItems');
  const subtotalEl = document.getElementById('coSubtotal');
  const taxEl = document.getElementById('coTax');
  const totalEl = document.getElementById('coTotal');
  if (!el) return;

  if (cart.length === 0) {
    el.innerHTML = '<p style="color:var(--gray-400);font-size:0.9rem;margin-bottom:1rem;">No items in cart</p>';
  } else {
    el.innerHTML = cart.map(item => `
      <div class="summary-row" style="border-bottom:1px solid var(--gray-50);padding-bottom:0.75rem;margin-bottom:0.75rem;">
        <span style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${item.name} ×${item.qty}</span>
        <span>$${(item.price * item.qty).toFixed(2)}</span>
      </div>
    `).join('');
  }

  const subtotal = getCartTotal();
  const tax = subtotal * 0.08;
  const total = subtotal + tax;
  if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
  if (taxEl) taxEl.textContent = `$${tax.toFixed(2)}`;
  if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
}

// CSS for bounce animation
const style = document.createElement('style');
style.textContent = `.cart-btn.bounce { animation: cartBounce 0.5s ease; } @keyframes cartBounce { 0%,100%{transform:scale(1)} 50%{transform:scale(1.3)} }`;
document.head.appendChild(style);

// Init
updateCartCount();
