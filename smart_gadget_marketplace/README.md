# 🚀 Smart Gadget Marketplace

A modern, fully responsive e-commerce marketplace UI built with Python Flask, featuring a complete shopping experience and professional admin dashboard.

---

## ✨ Features

- **Complete Storefront** — Hero slider, product grid, filters, search, reviews, newsletter
- **Product Pages** — Detailed product view with image gallery, specs, tabs, related products
- **Shopping Cart** — Add/remove items, quantity control, coupon codes (SAVE10, GADGET20, TECH15)
- **Checkout** — Shipping/billing forms, payment methods, success modal with receipt
- **User Profile** — Order history, delivery tracking, wishlist, account settings
- **Admin Dashboard** — Stats cards, Chart.js charts, full CRUD tables for products/users/orders/ratings
- **Authentication** — Login (User/Admin roles) and Register with validation
- **Responsive** — Fully mobile-friendly with hamburger menu

---

## 🛠️ Setup & Run

### 1. Prerequisites
Make sure you have **Python 3.8+** installed.

### 2. Navigate to the project folder
```bash
cd smart_gadget_marketplace
```

### 3. Create a virtual environment (recommended)
```bash
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the app
```bash
python run.py
```

### 6. Open in browser
```
http://localhost:5000
```

---

## 🔑 Login Credentials

Use **any email and password** — this is a frontend demo with dummy data.

| Role  | Redirect |
|-------|----------|
| User  | `/user/home` — Marketplace storefront |
| Admin | `/admin/dashboard` — Admin panel |

---

## 🗂️ Project Structure

```
smart_gadget_marketplace/
├── app/
│   ├── static/
│   │   ├── css/           # Stylesheets
│   │   └── js/            # JavaScript modules
│   ├── templates/
│   │   ├── layouts/       # Base templates
│   │   ├── includes/      # Navbar, footer, sidebar
│   │   ├── auth/          # Login, Register
│   │   ├── user/          # All user pages
│   │   └── admin/         # All admin pages
│   ├── routes/            # Flask route blueprints
│   └── utils/             # Dummy data
├── run.py
└── requirements.txt
```

---

## 🎨 Design

- **Theme**: White + Light Blue (`#0ea5e9`)
- **Fonts**: Plus Jakarta Sans + Space Grotesk
- **UI Style**: Glassmorphism cards, smooth animations, modern marketplace look
- **Charts**: Chart.js (sales, categories, user growth, analytics)

---

## 🛒 Coupon Codes (Cart)

| Code      | Discount |
|-----------|----------|
| `SAVE10`  | 10% off  |
| `GADGET20`| 20% off  |
| `TECH15`  | 15% off  |

---

## 📱 Pages

| URL | Page |
|-----|------|
| `/login` | Login |
| `/register` | Register |
| `/user/home` | Homepage |
| `/user/products` | All Products |
| `/user/product/<id>` | Product Detail |
| `/user/cart` | Shopping Cart |
| `/user/checkout` | Checkout |
| `/user/profile` | User Profile |
| `/user/orders` | Order History |
| `/user/wishlist` | Wishlist |
| `/user/ratings` | Ratings & Reviews |
| `/admin/dashboard` | Admin Dashboard |
| `/admin/products` | Manage Products |
| `/admin/users` | Manage Users |
| `/admin/orders` | Manage Orders |
| `/admin/ratings` | Manage Reviews |
| `/admin/analytics` | Analytics |

---

Built with ❤️ — Flask + Vanilla JS + CSS3
