/* ===== PROFILE.JS ===== */

// Load wishlist from localStorage
document.addEventListener('DOMContentLoaded', () => {
  const wishlistEl = document.getElementById('wishlistItems');
  if (!wishlistEl) return;

  // Show a sample wishlist item from cart data
  const cart = JSON.parse(localStorage.getItem('sgCart') || '[]');
  if (cart.length > 0) {
    wishlistEl.innerHTML = cart.slice(0, 3).map(item => `
      <div class="product-card">
        <div class="product-image-wrap">
          <img src="${item.image}" alt="${item.name}" onerror="this.src='https://via.placeholder.com/200'"/>
        </div>
        <div class="product-info">
          <h3 class="product-name">${item.name}</h3>
          <div class="product-footer">
            <span class="price">$${item.price.toFixed(2)}</span>
            <button class="add-cart-btn" onclick="addToCart(${item.id}, '${item.name}', ${item.price}, '${item.image}')">
              <i class="fas fa-cart-plus"></i>
            </button>
          </div>
        </div>
      </div>
    `).join('');
  }
});
