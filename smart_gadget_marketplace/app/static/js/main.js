/* ===== MAIN.JS — Global JS ===== */

// ===== AUTH GUARD FOR ADD TO CART =====
// If the user is not logged in, redirect to login instead of adding to cart.
// cart.js defines the real addToCart(); we wrap it here after DOM loads.
document.addEventListener('DOMContentLoaded', function () {
  const _realAddToCart = window.addToCart;

  window.addToCart = function (id, name, price, image) {
    if (!window.SG_USER_LOGGED_IN) {
      // Save intended destination so user returns to this page after login
      const loginUrl = window.SG_LOGIN_URL + '?next=' + encodeURIComponent(window.location.pathname);
      showToast('Please log in to add items to your cart 🔒', 'warning');
      setTimeout(function () { window.location.href = loginUrl; }, 1000);
      return;
    }
    // User is logged in — call the real implementation from cart.js
    if (typeof _realAddToCart === 'function') {
      _realAddToCart(id, name, price, image);
    }
  };

  // Update cart badge count from localStorage on every page load
  try {
    const cart = JSON.parse(localStorage.getItem('sgCart') || '[]');
    const totalQty = cart.reduce(function (sum, item) { return sum + (item.qty || 1); }, 0);
    const badge = document.getElementById('cartCount');
    if (badge && totalQty > 0) badge.textContent = totalQty;
  } catch (e) { /* ignore parse errors */ }
});

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type) {
  type = type || 'info';
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', info: 'fa-info-circle', warning: 'fa-exclamation-circle' };
  toast.className = 'toast ' + type;
  toast.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + '"></i> ' + message;
  container.appendChild(toast);
  setTimeout(function () {
    toast.classList.add('fade-out');
    setTimeout(function () { toast.remove(); }, 300);
  }, 3000);
}

// ===== BACK TO TOP =====
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', function () {
  if (backToTop) backToTop.classList.toggle('visible', window.scrollY > 400);
});
if (backToTop) backToTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

// ===== HAMBURGER MENU =====
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', function () {
    navLinks.classList.toggle('open');
    hamburger.classList.toggle('active');
  });
}

// ===== NOTIFICATION PANEL =====
function toggleNotifications() {
  const panel = document.getElementById('notifPanel');
  if (panel) panel.classList.toggle('show');
}

function clearNotifications() {
  const list = document.querySelector('.notif-list');
  if (list) {
    list.innerHTML = '<p style="padding:1rem;text-align:center;color:var(--gray-400);font-size:0.9rem;">No notifications</p>';
    document.querySelectorAll('.notif-btn .badge').forEach(function (b) { b.textContent = '0'; });
  }
  showToast('Notifications cleared', 'success');
}

// Close notification panel on outside click
document.addEventListener('click', function (e) {
  const panel = document.getElementById('notifPanel');
  if (panel && !e.target.closest('.notif-btn') && !e.target.closest('.notification-panel')) {
    panel.classList.remove('show');
  }
});

// ===== NAVBAR SEARCH =====
const PRODUCT_DATA = [
  { id: 1, name: 'Sony WH-1000XM5 Headphones',   price: '$349.99',   image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=60' },
  { id: 2, name: 'Apple iPad Pro 12.9"',           price: '$1,099.00', image: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=60' },
  { id: 3, name: 'Samsung Galaxy Watch 6',          price: '$299.99',   image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=60' },
  { id: 4, name: 'DJI Mini 4 Pro Drone',            price: '$759.00',   image: 'https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=60' },
  { id: 5, name: 'Logitech MX Master 3S',           price: '$99.99',    image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=60' },
  { id: 6, name: 'GoPro HERO12 Black',              price: '$399.99',   image: 'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=60' },
  { id: 7, name: 'Apple AirPods Pro 2nd Gen',       price: '$249.00',   image: 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=60' },
  { id: 8, name: 'ASUS ROG Gaming Laptop',          price: '$1,499.00', image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=60' },
];

const navSearch    = document.getElementById('navSearch');
const searchResults = document.getElementById('searchResults');

if (navSearch && searchResults) {
  navSearch.addEventListener('input', function () {
    const q = navSearch.value.toLowerCase().trim();
    if (!q) { searchResults.classList.remove('show'); return; }
    const matches = PRODUCT_DATA.filter(function (p) { return p.name.toLowerCase().includes(q); }).slice(0, 5);
    if (!matches.length) { searchResults.classList.remove('show'); return; }
    searchResults.innerHTML = matches.map(function (p) {
      return '<div class="search-result-item" onclick="window.location=\'/user/product/' + p.id + '\'">'
           + '<img src="' + p.image + '" alt="' + p.name + '"/>'
           + '<div><span>' + p.name + '</span><small>' + p.price + '</small></div>'
           + '</div>';
    }).join('');
    searchResults.classList.add('show');
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-search')) searchResults.classList.remove('show');
  });
}

// ===== PASSWORD TOGGLE =====
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const btn = input.parentElement.querySelector('.toggle-pass i');
  if (input.type === 'password') {
    input.type = 'text';
    if (btn) btn.className = 'fas fa-eye-slash';
  } else {
    input.type = 'password';
    if (btn) btn.className = 'fas fa-eye';
  }
}

// ===== NEWSLETTER =====
function subscribeNewsletter() {
  const emailInput = document.getElementById('newsletterEmail') || document.querySelector('.newsletter-form input[type="email"]');
  if (emailInput && emailInput.value) {
    if (!emailInput.value.includes('@')) {
      showToast('Please enter a valid email address', 'error');
      return;
    }
    showToast('🎉 Subscribed successfully! Welcome to SmartGadget!', 'success');
    emailInput.value = '';
  } else {
    showToast('Please enter your email address', 'error');
  }
}

// ===== SMOOTH SCROLL =====
document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// ===== TABLE FILTER (Admin) =====
function filterTable(query, tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;
  const rows = table.querySelectorAll('tbody tr');
  const q = query.toLowerCase();
  rows.forEach(function (row) {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

// ===== NAVBAR SCROLL EFFECT =====
window.addEventListener('scroll', function () {
  const navbar = document.getElementById('navbar');
  if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 20);
});

// ===== MODAL CLOSE ON OVERLAY CLICK =====
document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) overlay.style.display = 'none';
  });
});

// ===== WISHLIST TOGGLE =====
function toggleWishlist(btn, productId) {
  btn.classList.toggle('active');
  const icon = btn.querySelector('i');
  if (btn.classList.contains('active')) {
    icon.className = 'fas fa-heart';
    showToast('Added to wishlist ❤️', 'success');
  } else {
    icon.className = 'far fa-heart';
    showToast('Removed from wishlist', 'info');
  }
}

// ===== ORDERS FILTER =====
function filterOrders(query, status) {
  const rows = document.querySelectorAll('#ordersTable tbody tr');
  rows.forEach(function (row) {
    const text = row.textContent.toLowerCase();
    const matchQuery  = !query  || text.includes(query.toLowerCase());
    const matchStatus = !status || text.includes(status.toLowerCase());
    row.style.display = matchQuery && matchStatus ? '' : 'none';
  });
}

console.log('%c SmartGadget Marketplace 🚀', 'color: #0ea5e9; font-size: 16px; font-weight: bold;');