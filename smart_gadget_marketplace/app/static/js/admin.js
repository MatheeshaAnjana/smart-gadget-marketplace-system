/* ===== ADMIN.JS ===== */

// ===== SIDEBAR TOGGLE =====
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebarClose = document.getElementById('sidebarClose');
const adminSidebar = document.getElementById('adminSidebar');
const adminMain = document.getElementById('adminMain');

if (sidebarToggle && adminSidebar) {
  sidebarToggle.addEventListener('click', () => {
    adminSidebar.classList.toggle('collapsed');
    adminSidebar.classList.toggle('open');
    adminMain && adminMain.classList.toggle('expanded');
  });
}

if (sidebarClose && adminSidebar) {
  sidebarClose.addEventListener('click', () => {
    adminSidebar.classList.remove('open');
    adminSidebar.classList.add('collapsed');
  });
}

// Close sidebar on mobile overlay click
document.addEventListener('click', (e) => {
  if (window.innerWidth <= 1024 && adminSidebar) {
    if (!e.target.closest('.admin-sidebar') && !e.target.closest('#sidebarToggle')) {
      adminSidebar.classList.remove('open');
    }
  }
});

// ===== ACTIVE SIDEBAR LINK =====
document.querySelectorAll('.sidebar-link').forEach(link => {
  if (link.href === window.location.href) link.classList.add('active');
});

// ===== STATUS SELECT =====
document.querySelectorAll('.status-select').forEach(select => {
  select.addEventListener('change', function() {
    const orderId = this.closest('tr')?.querySelector('td:first-child strong')?.textContent || '';
    showToast(`Order ${orderId} status updated to: ${this.value}`, 'success');
  });
});
