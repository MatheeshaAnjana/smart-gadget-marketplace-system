# app/routes/admin_routes.py
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.utils.db import oracle_fetchall, oracle_execute, get_mongo_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ── Auth Guard ───────────────────────────────────────────────
def admin_required():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return None

# ── Dashboard ────────────────────────────────────────────────
@admin_bp.route('/dashboard')
def dashboard():
    guard = admin_required()
    if guard: return guard

    stats_rows = oracle_fetchall(
        "SELECT "
        "(SELECT COUNT(*) FROM products WHERE status = 'Active') AS total_products, "
        "(SELECT COUNT(*) FROM customers) AS total_users, "
        "(SELECT COUNT(*) FROM orders) AS total_orders, "
        "(SELECT NVL(SUM(amount),0) FROM payments WHERE status = 'Paid') AS revenue "
        "FROM DUAL"
    )
    stats = dict(stats_rows[0]) if stats_rows else {}

    monthly = oracle_fetchall(
        "SELECT TO_CHAR(paid_at,'Mon') AS mth, SUM(amount) AS mtotal "
        "FROM payments WHERE status = 'Paid' AND paid_at >= ADD_MONTHS(SYSDATE,-12) "
        "GROUP BY TO_CHAR(paid_at,'Mon'), TO_CHAR(paid_at,'YYYY-MM') "
        "ORDER BY TO_CHAR(paid_at,'YYYY-MM')"
    )
    stats['monthly_sales']  = [float(r['mtotal']) for r in monthly]
    stats['monthly_labels'] = [r['mth'] for r in monthly]

    cat_sales = oracle_fetchall(
        "SELECT c.name AS catname, SUM(oi.quantity) AS sold "
        "FROM order_items oi "
        "JOIN products p ON oi.product_id = p.product_id "
        "JOIN categories c ON p.category_id = c.category_id "
        "GROUP BY c.name ORDER BY sold DESC"
    )
    stats['category_sales'] = {r['catname']: int(r['sold']) for r in cat_sales}

    prod_raw = oracle_fetchall(
        "SELECT p.product_id AS pid, p.name AS pname, p.price AS pprice, "
        "p.stock AS pstock, p.badge AS pbadge, p.image_url AS pimage, "
        "NVL((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS avg_rating "
        "FROM products p WHERE p.status = 'Active' ORDER BY p.created_at DESC FETCH FIRST 5 ROWS ONLY"
    )
    recent_products = []
    for p in prod_raw:
        recent_products.append({
            'id':     p['pid'],
            'name':   p['pname'],
            'price':  p['pprice'],
            'stock':  p['pstock'],
            'badge':  p['pbadge'],
            'image':  p['pimage'],
            'rating': float(p['avg_rating']) if p['avg_rating'] else 0.0,
        })

    ord_raw = oracle_fetchall(
        "SELECT o.order_id AS oid, c.full_name AS cname, "
        "TO_CHAR(o.order_date,'Mon DD, YYYY') AS odate, "
        "o.total_amount AS ototal, o.status AS ostatus, d.status AS dstatus "
        "FROM orders o "
        "JOIN customers c ON o.customer_id = c.customer_id "
        "LEFT JOIN deliveries d ON o.order_id = d.order_id "
        "ORDER BY o.order_date DESC FETCH FIRST 5 ROWS ONLY"
    )
    recent_orders = []
    for o in ord_raw:
        recent_orders.append({
            'id':       o['oid'],
            'user':     o['cname'],
            'date':     o['odate'],
            'total':    o['ototal'],
            'status':   o['ostatus'],
            'delivery': o['dstatus'],
        })

    return render_template('admin/dashboard.html',
                           stats=stats,
                           products=recent_products,
                           orders=recent_orders)

# ── Products ─────────────────────────────────────────────────
@admin_bp.route('/products')
def products():
    guard = admin_required()
    if guard: return guard

    prod_raw = oracle_fetchall(
        "SELECT p.product_id AS pid, p.name AS pname, p.brand AS pbrand, "
        "p.price AS pprice, p.stock AS pstock, p.badge AS pbadge, "
        "p.status AS pstatus, p.image_url AS pimage, c.name AS catname, "
        "NVL((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.product_id = p.product_id), 0) AS avg_rating "
        "FROM products p JOIN categories c ON p.category_id = c.category_id "
        "ORDER BY p.created_at DESC"
    )
    all_products = []
    for p in prod_raw:
        all_products.append({
            'id':       p['pid'],
            'name':     p['pname'],
            'brand':    p['pbrand'],
            'price':    p['pprice'],
            'stock':    p['pstock'],
            'badge':    p['pbadge'],
            'status':   p['pstatus'],
            'image':    p['pimage'],
            'category': p['catname'],
            'rating':   float(p['avg_rating']) if p['avg_rating'] else 0.0,
        })
    return render_template('admin/products.html', products=all_products)

# ── Add Product ──────────────────────────────────────────────
@admin_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    guard = admin_required()
    if guard: return guard

    cat_raw    = oracle_fetchall("SELECT category_id AS cid, name AS catname FROM categories ORDER BY name")
    categories = [{'id': c['cid'], 'name': c['catname']} for c in cat_raw]

    if request.method == 'POST':
        oracle_execute(
            "INSERT INTO products (seller_id, category_id, name, brand, description, "
            "price, original_price, stock, badge, image_url, status) "
            "VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, 'Active')",
            [
                session['user_id'],
                request.form.get('category_id', type=int),
                request.form.get('name', '').strip(),
                request.form.get('brand', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('price', type=float),
                request.form.get('original_price', type=float),
                request.form.get('stock', type=int),
                request.form.get('badge', '').strip(),
                request.form.get('image_url', '').strip(),
            ]
        )
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/add_product.html', categories=categories)

# ── Edit Product ─────────────────────────────────────────────
@admin_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    guard = admin_required()
    if guard: return guard

    cat_raw    = oracle_fetchall("SELECT category_id AS cid, name AS catname FROM categories ORDER BY name")
    categories = [{'id': c['cid'], 'name': c['catname']} for c in cat_raw]

    if request.method == 'POST':
        oracle_execute(
            "UPDATE products SET category_id = :1, name = :2, brand = :3, description = :4, "
            "price = :5, original_price = :6, stock = :7, badge = :8, image_url = :9 "
            "WHERE product_id = :10",
            [
                request.form.get('category_id', type=int),
                request.form.get('name', '').strip(),
                request.form.get('brand', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('price', type=float),
                request.form.get('original_price', type=float),
                request.form.get('stock', type=int),
                request.form.get('badge', '').strip(),
                request.form.get('image_url', '').strip(),
                product_id
            ]
        )
        flash('Product updated!', 'success')
        return redirect(url_for('admin.products'))

    rows = oracle_fetchall(
        "SELECT product_id AS pid, name AS pname, brand AS pbrand, price AS pprice, "
        "original_price AS orig_price, stock AS pstock, badge AS pbadge, "
        "image_url AS pimage, description AS pdesc, category_id AS cid "
        "FROM products WHERE product_id = :1",
        [product_id]
    )
    if not rows:
        return redirect(url_for('admin.products'))

    p = rows[0]
    product = {
        'id':             p['pid'],
        'name':           p['pname'],
        'brand':          p['pbrand'],
        'price':          p['pprice'],
        'original_price': p['orig_price'],
        'stock':          p['pstock'],
        'badge':          p['pbadge'],
        'image':          p['pimage'],
        'description':    p['pdesc'],
        'category_id':    p['cid'],
    }
    return render_template('admin/edit_product.html', product=product, categories=categories)

# ── Delete Product ───────────────────────────────────────────
@admin_bp.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    guard = admin_required()
    if guard: return guard
    oracle_execute("UPDATE products SET status = 'Inactive' WHERE product_id = :1", [product_id])
    flash('Product removed.', 'info')
    return redirect(url_for('admin.products'))

# ── Users ────────────────────────────────────────────────────
@admin_bp.route('/users')
def users():
    guard = admin_required()
    if guard: return guard

    # Use direct connection with positional access to avoid ALL reserved word issues
    from app.utils.db import get_oracle_connection
    conn = get_oracle_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_id, full_name, email, phone, status, "
        "TO_CHAR(created_at, 'Mon YYYY') FROM customers ORDER BY created_at DESC"
    )
    raw = cursor.fetchall()
    cursor.close()
    conn.close()

    all_users = []
    for row in raw:
        uid = row[0]
        count_rows = oracle_fetchall(
            "SELECT COUNT(*) AS cnt FROM orders WHERE customer_id = :1",
            [uid]
        )
        order_count = int(count_rows[0]['cnt']) if count_rows else 0
        all_users.append({
            'id':      row[0],
            'name':    row[1],
            'email':   row[2],
            'phone':   row[3] or '—',
            'address': '—',
            'status':  row[4],
            'joined':  row[5],
            'orders':  order_count,
        })

    return render_template('admin/users.html', users=all_users)

# ── Orders ───────────────────────────────────────────────────
@admin_bp.route('/orders')
def orders():
    guard = admin_required()
    if guard: return guard

    ord_raw = oracle_fetchall(
        "SELECT o.order_id AS oid, c.full_name AS cname, "
        "TO_CHAR(o.order_date,'Mon DD, YYYY') AS odate, "
        "o.total_amount AS ototal, o.status AS ostatus, "
        "d.status AS dstatus, pay.status AS paystatus, pay.method AS paymethod "
        "FROM orders o "
        "JOIN customers c ON o.customer_id = c.customer_id "
        "LEFT JOIN deliveries d ON o.order_id = d.order_id "
        "LEFT JOIN payments pay ON o.order_id = pay.order_id "
        "ORDER BY o.order_date DESC"
    )
    all_orders = []
    for o in ord_raw:
        items = oracle_fetchall(
            "SELECT pr.name AS pname FROM order_items oi "
            "JOIN products pr ON oi.product_id = pr.product_id "
            "WHERE oi.order_id = :1",
            [o['oid']]
        )
        all_orders.append({
            'id':             o['oid'],
            'user':           o['cname'],
            'date':           o['odate'],
            'total':          o['ototal'],
            'status':         o['ostatus'],
            'delivery':       o['dstatus'],
            'payment':        o['paystatus'],
            'payment_method': o['paymethod'],
            'products':       [i['pname'] for i in items],
        })
    return render_template('admin/orders.html', orders=all_orders)

# ── Update Order Status ──────────────────────────────────────
@admin_bp.route('/orders/update/<int:order_id>', methods=['POST'])
def update_order(order_id):
    guard = admin_required()
    if guard: return guard
    new_status = request.form.get('status')
    oracle_execute("UPDATE orders SET status = :1 WHERE order_id = :2", [new_status, order_id])
    oracle_execute("UPDATE deliveries SET status = :1 WHERE order_id = :2", [new_status, order_id])
    flash('Order status updated.', 'success')
    return redirect(url_for('admin.orders'))

# ── Ratings ──────────────────────────────────────────────────
@admin_bp.route('/ratings')
def ratings():
    guard = admin_required()
    if guard: return guard

    rv_raw = oracle_fetchall(
        "SELECT rv.review_id AS rid, c.full_name AS reviewer, p.name AS pname, "
        "rv.rating AS rrating, rv.review_comment AS rcomment, "
        "TO_CHAR(rv.review_date,'Mon DD, YYYY') AS rdate "
        "FROM reviews rv "
        "JOIN customers c ON rv.customer_id = c.customer_id "
        "JOIN products p ON rv.product_id = p.product_id "
        "ORDER BY rv.review_date DESC"
    )
    all_reviews = []
    for r in rv_raw:
        all_reviews.append({
            'id':      r['rid'],
            'user':    r['reviewer'],
            'product': r['pname'],
            'rating':  r['rrating'],
            'comment': r['rcomment'],
            'date':    r['rdate'],
        })
    return render_template('admin/ratings.html', reviews=all_reviews)

# ── Analytics ────────────────────────────────────────────────
@admin_bp.route('/analytics')
def analytics():
    guard = admin_required()
    if guard: return guard

    stats_rows = oracle_fetchall(
        "SELECT "
        "(SELECT COUNT(*) FROM products WHERE status='Active') AS total_products, "
        "(SELECT COUNT(*) FROM customers) AS total_users, "
        "(SELECT COUNT(*) FROM orders) AS total_orders, "
        "(SELECT NVL(SUM(amount),0) FROM payments WHERE status='Paid') AS revenue "
        "FROM DUAL"
    )
    stats = dict(stats_rows[0]) if stats_rows else {}

    monthly = oracle_fetchall(
        "SELECT TO_CHAR(paid_at,'Mon') AS mth, SUM(amount) AS mtotal "
        "FROM payments WHERE status = 'Paid' AND paid_at >= ADD_MONTHS(SYSDATE,-12) "
        "GROUP BY TO_CHAR(paid_at,'Mon'), TO_CHAR(paid_at,'YYYY-MM') "
        "ORDER BY TO_CHAR(paid_at,'YYYY-MM')"
    )
    stats['monthly_sales']  = [float(r['mtotal']) for r in monthly]
    stats['monthly_labels'] = [r['mth'] for r in monthly]

    cat_sales = oracle_fetchall(
        "SELECT c.name AS catname, SUM(oi.quantity) AS sold "
        "FROM order_items oi "
        "JOIN products p ON oi.product_id = p.product_id "
        "JOIN categories c ON p.category_id = c.category_id "
        "GROUP BY c.name ORDER BY sold DESC"
    )
    stats['category_sales'] = {r['catname']: int(r['sold']) for r in cat_sales}

    top_products = oracle_fetchall(
        "SELECT name AS pname, views AS pviews, image_url AS pimage "
        "FROM products WHERE status = 'Active' ORDER BY views DESC FETCH FIRST 5 ROWS ONLY"
    )
    stats['top_products'] = [
        {'name': p['pname'], 'views': p['pviews'], 'image': p['pimage']}
        for p in top_products
    ]

    mongo = get_mongo_db()

    peak_hours = list(mongo.activity_logs.aggregate([
        {"$group": {"_id": {"$hour": "$timestamp"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 6}
    ]))
    stats['peak_hours'] = [{"hour": p['_id'], "count": p['count']} for p in peak_hours]

    event_counts = list(mongo.activity_logs.aggregate([
        {"$group": {"_id": "$event_type", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]))
    stats['event_counts'] = {e['_id']: e['total'] for e in event_counts}

    failed = list(mongo.failed_transactions.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(10))
    stats['failed_transactions'] = failed

    recent_logins = list(mongo.activity_logs.find(
        {"event_type": "login"}, {"_id": 0}
    ).sort("timestamp", -1).limit(5))
    stats['recent_logins'] = recent_logins

    return render_template('admin/analytics.html', stats=stats)