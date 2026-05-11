# app/routes/user_routes.py
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.utils.db import (
    oracle_fetchall, oracle_execute, oracle_callproc,
    log_activity, log_search, log_failed_transaction
)

user_bp = Blueprint('user', __name__, url_prefix='/user')

# ── Auth Guard ───────────────────────────────────────────────
def login_required():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return None

# ── Home ─────────────────────────────────────────────────────
@user_bp.route('/home')
def home():
    guard = login_required()
    if guard: return guard

    prod_rows = oracle_fetchall(
        "SELECT p.product_id AS pid, p.name AS pname, p.brand AS pbrand, "
        "p.price AS pprice, p.original_price AS orig_price, "
        "p.stock AS pstock, p.badge AS pbadge, p.image_url AS pimage, "
        "p.views AS pviews, c.name AS catname, "
        "NVL((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS avg_rating, "
        "NVL((SELECT COUNT(*) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS rev_count "
        "FROM products p JOIN categories c ON p.category_id = c.category_id "
        "WHERE p.status = 'Active' AND ROWNUM <= 8 ORDER BY p.views DESC"
    )
    products = []
    for p in prod_rows:
        products.append({
            'id':             p['pid'],
            'name':           p['pname'],
            'brand':          p['pbrand'],
            'price':          p['pprice'],
            'original_price': p['orig_price'],
            'stock':          p['pstock'],
            'badge':          p['pbadge'],
            'image':          p['pimage'],
            'views':          p['pviews'],
            'category':       p['catname'],
            'rating':         float(p['avg_rating']) if p['avg_rating'] else 0.0,
            'reviews':        int(p['rev_count'])    if p['rev_count']  else 0,
        })

    rev_rows = oracle_fetchall(
        "SELECT rv.review_id AS rid, c.full_name AS reviewer, "
        "c.avatar_url AS ravatar, p.name AS pname, "
        "rv.rating AS rrating, rv.review_comment AS rcomment, "
        "TO_CHAR(rv.review_date, 'Mon DD, YYYY') AS rdate "
        "FROM reviews rv "
        "JOIN customers c ON rv.customer_id = c.customer_id "
        "JOIN products p ON rv.product_id = p.product_id "
        "ORDER BY rv.review_date DESC FETCH FIRST 5 ROWS ONLY"
    )
    reviews = []
    for r in rev_rows:
        reviews.append({
            'id':      r['rid'],
            'user':    r['reviewer'],
            'avatar':  r['ravatar'],
            'product': r['pname'],
            'rating':  r['rrating'],
            'comment': r['rcomment'],
            'date':    r['rdate'],
        })

    return render_template('user/home.html', products=products, reviews=reviews)

# ── Products List ────────────────────────────────────────────
@user_bp.route('/products')
def products():
    guard = login_required()
    if guard: return guard

    search   = request.args.get('q', '').strip()
    category = request.args.get('category', 'All')

    base_sql = (
        "SELECT p.product_id AS pid, p.name AS pname, p.brand AS pbrand, "
        "p.price AS pprice, p.original_price AS orig_price, "
        "p.stock AS pstock, p.badge AS pbadge, p.image_url AS pimage, "
        "p.views AS pviews, c.name AS catname, "
        "NVL((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS avg_rating, "
        "NVL((SELECT COUNT(*) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS rev_count "
        "FROM products p JOIN categories c ON p.category_id = c.category_id "
        "WHERE p.status = 'Active'"
    )
    params = []

    if search and category != 'All':
        base_sql += " AND (LOWER(p.name) LIKE :1 OR LOWER(p.brand) LIKE :1) AND c.name = :2"
        params = [f'%{search.lower()}%', category]
    elif search:
        base_sql += " AND (LOWER(p.name) LIKE :1 OR LOWER(p.brand) LIKE :1)"
        params = [f'%{search.lower()}%']
    elif category != 'All':
        base_sql += " AND c.name = :1"
        params = [category]

    base_sql += " ORDER BY p.views DESC"
    raw = oracle_fetchall(base_sql, params)

    all_products = []
    for p in raw:
        all_products.append({
            'id':             p['pid'],
            'name':           p['pname'],
            'brand':          p['pbrand'],
            'price':          p['pprice'],
            'original_price': p['orig_price'],
            'stock':          p['pstock'],
            'badge':          p['pbadge'],
            'image':          p['pimage'],
            'views':          p['pviews'],
            'category':       p['catname'],
            'rating':         float(p['avg_rating']) if p['avg_rating'] else 0.0,
            'reviews':        int(p['rev_count'])    if p['rev_count']  else 0,
        })

    if search:
        log_search(session.get('user_id'), search, len(all_products))

    cat_rows  = oracle_fetchall("SELECT name AS catname FROM categories ORDER BY name")
    cat_names = ['All'] + [c['catname'] for c in cat_rows]

    return render_template('user/products.html',
                           products=all_products,
                           categories=cat_names,
                           selected_category=category,
                           search_query=search)

# ── Product Detail ───────────────────────────────────────────
@user_bp.route('/product/<int:product_id>')
def product_details(product_id):
    guard = login_required()
    if guard: return guard

    rows = oracle_fetchall(
        "SELECT p.product_id AS pid, p.name AS pname, p.brand AS pbrand, "
        "p.price AS pprice, p.original_price AS orig_price, "
        "p.stock AS pstock, p.badge AS pbadge, p.image_url AS pimage, "
        "p.description AS pdesc, p.views AS pviews, c.name AS catname, "
        "NVL((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS avg_rating, "
        "NVL((SELECT COUNT(*) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS rev_count "
        "FROM products p JOIN categories c ON p.category_id = c.category_id "
        "WHERE p.product_id = :1",
        [product_id]
    )
    if not rows:
        return redirect(url_for('user.products'))

    r = rows[0]
    product = {
        'id':             r['pid'],
        'name':           r['pname'],
        'brand':          r['pbrand'],
        'price':          r['pprice'],
        'original_price': r['orig_price'],
        'stock':          r['pstock'],
        'badge':          r['pbadge'],
        'image':          r['pimage'],
        'description':    r['pdesc'],
        'views':          r['pviews'],
        'category':       r['catname'],
        'rating':         float(r['avg_rating']) if r['avg_rating'] else 0.0,
        'reviews':        int(r['rev_count'])    if r['rev_count']  else 0,
    }

    oracle_execute(
        "UPDATE products SET views = views + 1 WHERE product_id = :1",
        [product_id]
    )
    log_activity('product_view', {
        'user_id':      session.get('user_id'),
        'product_id':   product_id,
        'product_name': product['name']
    })

    rel_rows = oracle_fetchall(
        "SELECT p.product_id AS pid, p.name AS pname, p.brand AS pbrand, "
        "p.price AS pprice, p.image_url AS pimage, c.name AS catname, "
        "NVL((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS avg_rating "
        "FROM products p JOIN categories c ON p.category_id = c.category_id "
        "WHERE c.name = :1 AND p.product_id != :2 AND p.status = 'Active' AND ROWNUM <= 4",
        [product['category'], product_id]
    )
    related = []
    for rr in rel_rows:
        related.append({
            'id':       rr['pid'],
            'name':     rr['pname'],
            'brand':    rr['pbrand'],
            'price':    rr['pprice'],
            'image':    rr['pimage'],
            'category': rr['catname'],
            'rating':   float(rr['avg_rating']) if rr['avg_rating'] else 0.0,
        })

    rv_rows = oracle_fetchall(
        "SELECT rv.rating AS rrating, rv.review_comment AS rcomment, "
        "TO_CHAR(rv.review_date, 'Mon DD, YYYY') AS rdate, "
        "c.full_name AS reviewer, c.avatar_url AS ravatar "
        "FROM reviews rv JOIN customers c ON rv.customer_id = c.customer_id "
        "WHERE rv.product_id = :1 ORDER BY rv.review_date DESC",
        [product_id]
    )
    product_reviews = []
    for rv in rv_rows:
        product_reviews.append({
            'rating':  rv['rrating'],
            'comment': rv['rcomment'],
            'date':    rv['rdate'],
            'user':    rv['reviewer'],
            'avatar':  rv['ravatar'],
        })

    return render_template('user/product_details.html',
                           product=product,
                           related=related,
                           reviews=product_reviews)

# ── Cart ─────────────────────────────────────────────────────
@user_bp.route('/cart')
def cart():
    guard = login_required()
    if guard: return guard
    return render_template('user/cart.html')

# ── Checkout ─────────────────────────────────────────────────
@user_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    guard = login_required()
    if guard: return guard

    if request.method == 'POST':
        product_id  = request.form.get('product_id', type=int)
        quantity    = request.form.get('quantity',   type=int, default=1)
        method      = request.form.get('payment_method', 'Card')
        customer_id = session['user_id']
        try:
            oracle_callproc('place_order', [customer_id, product_id, quantity, method])
            log_activity('order_placed', {
                'user_id':    customer_id,
                'product_id': product_id,
                'quantity':   quantity,
                'method':     method
            })
            flash('Order placed successfully!', 'success')
            return redirect(url_for('user.orders'))
        except Exception as e:
            err_msg = str(e)
            log_failed_transaction(customer_id, 'PENDING', 0, method, err_msg)
            flash(f'Order failed: {err_msg}', 'danger')
            return redirect(url_for('user.checkout'))

    return render_template('user/checkout.html')

# ── Profile ──────────────────────────────────────────────────
@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    guard = login_required()
    if guard: return guard

    customer_id = session['user_id']

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        address   = request.form.get('address', '').strip()
        oracle_execute(
            "UPDATE customers SET full_name = :1, phone = :2, address = :3 WHERE customer_id = :4",
            [full_name, phone, address, customer_id]
        )
        session['user_name'] = full_name
        flash('Profile updated!', 'success')

    usr_rows = oracle_fetchall(
        "SELECT full_name AS uname, email AS uemail, phone AS uphone, "
        "address AS uaddress, avatar_url AS uavatar, status AS ustatus, "
        "TO_CHAR(created_at, 'Mon YYYY') AS ujoined "
        "FROM customers WHERE customer_id = :1",
        [customer_id]
    )
    user_data = {}
    if usr_rows:
        u = usr_rows[0]
        user_data = {
            'name':    u['uname'],
            'email':   u['uemail'],
            'phone':   u['uphone'],
            'address': u['uaddress'],
            'avatar':  u['uavatar'],
            'status':  u['ustatus'],
            'joined':  u['ujoined'],
        }

    ord_rows = oracle_fetchall(
        "SELECT o.order_id AS oid, TO_CHAR(o.order_date,'Mon DD, YYYY') AS odate, "
        "o.total_amount AS ototal, o.status AS ostatus, d.status AS dstatus "
        "FROM orders o LEFT JOIN deliveries d ON o.order_id = d.order_id "
        "WHERE o.customer_id = :1 ORDER BY o.order_date DESC",
        [customer_id]
    )
    orders = []
    for o in ord_rows:
        orders.append({
            'id':       o['oid'],
            'date':     o['odate'],
            'total':    o['ototal'],
            'status':   o['ostatus'],
            'delivery': o['dstatus'],
        })

    return render_template('user/profile.html', user=user_data, orders=orders)

# ── Orders ───────────────────────────────────────────────────
@user_bp.route('/orders')
def orders():
    guard = login_required()
    if guard: return guard

    customer_id = session['user_id']
    ord_rows = oracle_fetchall(
        "SELECT o.order_id AS oid, TO_CHAR(o.order_date,'Mon DD, YYYY') AS odate, "
        "o.total_amount AS ototal, o.status AS ostatus, "
        "d.status AS dstatus, pay.status AS paystatus, pay.method AS paymethod "
        "FROM orders o "
        "LEFT JOIN deliveries d ON o.order_id = d.order_id "
        "LEFT JOIN payments pay ON o.order_id = pay.order_id "
        "WHERE o.customer_id = :1 ORDER BY o.order_date DESC",
        [customer_id]
    )
    all_orders = []
    for o in ord_rows:
        items = oracle_fetchall(
            "SELECT pr.name AS pname, oi.quantity AS qty, oi.unit_price AS uprice "
            "FROM order_items oi JOIN products pr ON oi.product_id = pr.product_id "
            "WHERE oi.order_id = :1",
            [o['oid']]
        )
        all_orders.append({
            'id':             o['oid'],
            'date':           o['odate'],
            'total':          o['ototal'],
            'status':         o['ostatus'],
            'delivery':       o['dstatus'],
            'payment':        o['paystatus'],
            'payment_method': o['paymethod'],
            'products':       [i['pname'] for i in items],
        })

    return render_template('user/orders.html', orders=all_orders)

# ── Wishlist ─────────────────────────────────────────────────
@user_bp.route('/wishlist')
def wishlist():
    guard = login_required()
    if guard: return guard

    customer_id = session['user_id']
    raw = oracle_fetchall(
        "SELECT p.product_id AS pid, p.name AS pname, p.brand AS pbrand, "
        "p.price AS pprice, p.original_price AS orig_price, "
        "p.image_url AS pimage, p.stock AS pstock, p.badge AS pbadge, "
        "NVL((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS avg_rating "
        "FROM wishlist w JOIN products p ON w.product_id = p.product_id "
        "WHERE w.customer_id = :1",
        [customer_id]
    )
    items = []
    for p in raw:
        items.append({
            'id':             p['pid'],
            'name':           p['pname'],
            'brand':          p['pbrand'],
            'price':          p['pprice'],
            'original_price': p['orig_price'],
            'image':          p['pimage'],
            'stock':          p['pstock'],
            'badge':          p['pbadge'],
            'rating':         float(p['avg_rating']) if p['avg_rating'] else 0.0,
        })
    return render_template('user/wishlist.html', products=items)

@user_bp.route('/wishlist/add/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    guard = login_required()
    if guard: return guard
    try:
        oracle_execute(
            "INSERT INTO wishlist (customer_id, product_id) VALUES (:1, :2)",
            [session['user_id'], product_id]
        )
    except Exception:
        pass
    return redirect(request.referrer or url_for('user.products'))

@user_bp.route('/wishlist/remove/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    guard = login_required()
    if guard: return guard
    oracle_execute(
        "DELETE FROM wishlist WHERE customer_id = :1 AND product_id = :2",
        [session['user_id'], product_id]
    )
    return redirect(url_for('user.wishlist'))

# ── Ratings ──────────────────────────────────────────────────
@user_bp.route('/ratings', methods=['GET', 'POST'])
def ratings():
    guard = login_required()
    if guard: return guard

    customer_id = session['user_id']

    if request.method == 'POST':
        product_id  = request.form.get('product_id',  type=int)
        rating_val  = request.form.get('rating',      type=float)
        comment_val = request.form.get('comment', '').strip()

        existing = oracle_fetchall(
            "SELECT review_id AS rid FROM reviews WHERE customer_id = :1 AND product_id = :2",
            [customer_id, product_id]
        )
        if existing:
            oracle_execute(
                "UPDATE reviews SET rating = :1, review_comment = :2, review_date = SYSDATE "
                "WHERE customer_id = :3 AND product_id = :4",
                [rating_val, comment_val, customer_id, product_id]
            )
        else:
            oracle_execute(
                "INSERT INTO reviews (customer_id, product_id, rating, review_comment) "
                "VALUES (:1, :2, :3, :4)",
                [customer_id, product_id, rating_val, comment_val]
            )
        flash('Review submitted!', 'success')
        return redirect(url_for('user.ratings'))

    rv_rows = oracle_fetchall(
        "SELECT rv.review_id AS rid, p.name AS pname, rv.rating AS rrating, "
        "rv.review_comment AS rcomment, TO_CHAR(rv.review_date, 'Mon DD, YYYY') AS rdate "
        "FROM reviews rv JOIN products p ON rv.product_id = p.product_id "
        "WHERE rv.customer_id = :1 ORDER BY rv.review_date DESC",
        [customer_id]
    )
    reviews = []
    for r in rv_rows:
        reviews.append({
            'id':      r['rid'],
            'product': r['pname'],
            'rating':  r['rrating'],
            'comment': r['rcomment'],
            'date':    r['rdate'],
        })

    prod_rows = oracle_fetchall(
        "SELECT product_id AS pid, name AS pname FROM products WHERE status = 'Active' ORDER BY name"
    )
    all_products = [{'id': p['pid'], 'name': p['pname']} for p in prod_rows]

    return render_template('user/ratings.html', reviews=reviews, products=all_products)