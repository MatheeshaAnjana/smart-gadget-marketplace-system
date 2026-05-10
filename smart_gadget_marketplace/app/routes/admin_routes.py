from flask import Blueprint, render_template
from app.utils.dummy_data import PRODUCTS, USERS, ORDERS, REVIEWS, STATS

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html', stats=STATS, products=PRODUCTS[:5], orders=ORDERS[:5])

@admin_bp.route('/products')
def products():
    return render_template('admin/products.html', products=PRODUCTS)

@admin_bp.route('/add-product')
def add_product():
    return render_template('admin/add_product.html')

@admin_bp.route('/edit-product/<int:product_id>')
def edit_product(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), PRODUCTS[0])
    return render_template('admin/edit_product.html', product=product)

@admin_bp.route('/users')
def users():
    return render_template('admin/users.html', users=USERS)

@admin_bp.route('/ratings')
def ratings():
    return render_template('admin/ratings.html', reviews=REVIEWS)

@admin_bp.route('/orders')
def orders():
    return render_template('admin/orders.html', orders=ORDERS)

@admin_bp.route('/analytics')
def analytics():
    return render_template('admin/analytics.html', stats=STATS)
