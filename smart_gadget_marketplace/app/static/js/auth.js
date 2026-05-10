/* ===== AUTH.JS ===== */

// ===== REGISTER VALIDATION =====
function handleRegister() {
  const name = document.getElementById('regName')?.value.trim();
  const email = document.getElementById('regEmail')?.value.trim();
  const password = document.getElementById('regPassword')?.value;
  const confirm = document.getElementById('regConfirm')?.value;

  if (!name) return showToast('Please enter your full name', 'error');
  if (!email || !email.includes('@')) return showToast('Please enter a valid email', 'error');
  if (!password || password.length < 6) return showToast('Password must be at least 6 characters', 'error');
  if (password !== confirm) return showToast('Passwords do not match', 'error');

  // Show success modal
  const modal = document.getElementById('successModal');
  if (modal) modal.style.display = 'flex';
}

// ===== PASSWORD STRENGTH =====
const passInput = document.getElementById('regPassword');
const passStrength = document.getElementById('passStrength');
const strengthFill = document.getElementById('strengthFill');
const strengthText = document.getElementById('strengthText');

if (passInput) {
  passInput.addEventListener('input', () => {
    const val = passInput.value;
    if (!val) { if (passStrength) passStrength.style.display = 'none'; return; }
    if (passStrength) passStrength.style.display = 'block';

    let score = 0;
    if (val.length >= 6) score++;
    if (val.length >= 10) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^a-zA-Z0-9]/.test(val)) score++;

    const levels = [
      { color: '#ef4444', text: 'Very Weak', width: '20%' },
      { color: '#f97316', text: 'Weak', width: '40%' },
      { color: '#f59e0b', text: 'Fair', width: '60%' },
      { color: '#22c55e', text: 'Strong', width: '80%' },
      { color: '#16a34a', text: 'Very Strong', width: '100%' },
    ];

    const level = levels[Math.min(score - 1, 4)] || levels[0];
    if (strengthFill) { strengthFill.style.width = level.width; strengthFill.style.background = level.color; }
    if (strengthText) { strengthText.textContent = level.text; strengthText.style.color = level.color; }
  });
}

// ===== LOGIN FORM =====
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const email = loginForm.querySelector('input[type="email"]')?.value;
      const password = loginForm.querySelector('input[type="password"]')?.value;
      if (!email || !password) {
        e.preventDefault();
        showToast('Please fill in all fields', 'error');
      }
    });
  }
});
