/* ===== PRODUCTS.JS ===== */

// ===== HERO SLIDER =====
let currentSlide = 0;
let slideInterval;
const slides = document.querySelectorAll('.slide');
const dotsContainer = document.getElementById('sliderDots');

function initSlider() {
  if (!slides.length) return;

  // Create dots
  if (dotsContainer) {
    slides.forEach((_, i) => {
      const dot = document.createElement('div');
      dot.className = `dot ${i === 0 ? 'active' : ''}`;
      dot.onclick = () => goToSlide(i);
      dotsContainer.appendChild(dot);
    });
  }

  startAutoSlide();
}

function goToSlide(n) {
  slides[currentSlide].classList.remove('active');
  currentSlide = (n + slides.length) % slides.length;
  slides[currentSlide].classList.add('active');

  // Transition effect
  slides[currentSlide].style.animation = 'none';
  slides[currentSlide].offsetHeight;
  slides[currentSlide].style.animation = 'slideIn 0.6s ease';

  if (dotsContainer) {
    dotsContainer.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === currentSlide));
  }
}

function nextSlide() {
  goToSlide(currentSlide + 1);
  resetAutoSlide();
}

function prevSlide() {
  goToSlide(currentSlide - 1);
  resetAutoSlide();
}

function startAutoSlide() {
  slideInterval = setInterval(() => goToSlide(currentSlide + 1), 5000);
}

function resetAutoSlide() {
  clearInterval(slideInterval);
  startAutoSlide();
}

// Slide animation
const sliderStyle = document.createElement('style');
sliderStyle.textContent = `
  @keyframes slideIn {
    from { opacity: 0.5; transform: scale(0.98); }
    to { opacity: 1; transform: scale(1); }
  }
  .slide { display: none; }
  .slide.active { display: flex; animation: slideIn 0.5s ease; }
`;
document.head.appendChild(sliderStyle);

// ===== HOME PRODUCT FILTER =====
function filterHomeProducts(category) {
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');

  const cards = document.querySelectorAll('#featuredGrid .product-card');
  cards.forEach(card => {
    const cat = card.dataset.category;
    if (category === 'All' || cat === category) {
      card.style.display = '';
      card.style.animation = 'fadeIn 0.3s ease';
    } else {
      card.style.display = 'none';
    }
  });
}

// ===== PRODUCTS PAGE FILTER =====
function filterProducts() {
  const searchEl = document.getElementById('productSearch');
  const catEl = document.getElementById('categoryFilter');
  const sortEl = document.getElementById('sortFilter');
  const container = document.getElementById('productsContainer');
  const emptyState = document.getElementById('emptyState');
  const countEl = document.getElementById('productCount');
  if (!container) return;

  const q = searchEl ? searchEl.value.toLowerCase() : '';
  const cat = catEl ? catEl.value : 'All';
  const sort = sortEl ? sortEl.value : 'default';

  let cards = Array.from(container.querySelectorAll('.product-card'));

  // Filter
  let visible = 0;
  cards.forEach(card => {
    const name = card.dataset.name || '';
    const cardCat = card.dataset.category || '';
    const matchSearch = !q || name.includes(q);
    const matchCat = cat === 'All' || cardCat === cat;
    const show = matchSearch && matchCat;
    card.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  // Sort
  if (sort !== 'default') {
    const visibleCards = cards.filter(c => c.style.display !== 'none');
    visibleCards.sort((a, b) => {
      if (sort === 'price-low') return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
      if (sort === 'price-high') return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
      if (sort === 'rating') return parseFloat(b.dataset.rating) - parseFloat(a.dataset.rating);
      if (sort === 'popular') return parseFloat(b.dataset.views) - parseFloat(a.dataset.views);
      return 0;
    });
    visibleCards.forEach(card => container.appendChild(card));
  }

  if (countEl) countEl.textContent = `${visible} product${visible !== 1 ? 's' : ''}`;
  if (emptyState) emptyState.style.display = visible === 0 ? 'flex' : 'none';
}

function resetFilters() {
  const searchEl = document.getElementById('productSearch');
  const catEl = document.getElementById('categoryFilter');
  const sortEl = document.getElementById('sortFilter');
  if (searchEl) searchEl.value = '';
  if (catEl) catEl.value = 'All';
  if (sortEl) sortEl.value = 'default';
  filterProducts();
}

function setView(mode) {
  const container = document.getElementById('productsContainer');
  const gridBtn = document.getElementById('gridViewBtn');
  const listBtn = document.getElementById('listViewBtn');
  if (!container) return;

  if (mode === 'list') {
    container.style.gridTemplateColumns = '1fr';
    gridBtn && gridBtn.classList.remove('active');
    listBtn && listBtn.classList.add('active');
  } else {
    container.style.gridTemplateColumns = '';
    gridBtn && gridBtn.classList.add('active');
    listBtn && listBtn.classList.remove('active');
  }
}

// Fade-in animation
const fadeStyle = document.createElement('style');
fadeStyle.textContent = `@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }`;
document.head.appendChild(fadeStyle);

// Init
document.addEventListener('DOMContentLoaded', initSlider);
