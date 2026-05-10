from flask import Blueprint, render_template
from app.utils.dummy_data import PRODUCTS, REVIEWS, CATEGORIES, ORDERS

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/home')
def home():
    featured = PRODUCTS[:8]
    return render_template('user/home.html', products=featured, reviews=REVIEWS)

@user_bp.route('/products')
def products():
    return render_template('user/products.html', products=PRODUCTS, categories=CATEGORIES)

@user_bp.route('/product/<int:product_id>')
def product_details(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), PRODUCTS[0])
    related = [p for p in PRODUCTS if p['category'] == product['category'] and p['id'] != product['id']][:4]
    return render_template('user/product_details.html', product=product, related=related, reviews=REVIEWS)

@user_bp.route('/cart')
def cart():
    return render_template('user/cart.html')

@user_bp.route('/checkout')
def checkout():
    return render_template('user/checkout.html')

@user_bp.route('/profile')
def profile():
    return render_template('user/profile.html', orders=ORDERS)

@user_bp.route('/orders')
def orders():
    return render_template('user/orders.html', orders=ORDERS)

@user_bp.route('/wishlist')
def wishlist():
    wishlist_items = PRODUCTS[:4]
    return render_template('user/wishlist.html', products=wishlist_items)

@user_bp.route('/ratings')
def ratings():
    return render_template('user/ratings.html', reviews=REVIEWS, products=PRODUCTS)
