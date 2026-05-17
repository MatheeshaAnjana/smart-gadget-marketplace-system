# app/routes/auth_routes.py
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.utils.db import oracle_fetchall, oracle_execute, log_activity
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth_bp = Blueprint('auth', __name__)

# ── Helper ───────────────────────────────────────────────────
def is_logged_in():
    return 'user_id' in session

# ── Index ────────────────────────────────────────────────────
@auth_bp.route('/')
def index():
    # Everyone (logged-in or anonymous) goes straight to the marketplace homepage
    if is_logged_in():
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
    # Anonymous users also land on the public home page
    return redirect(url_for('user.home'))

# ── Login ────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('auth.index'))

    # Where to go after login — passed as ?next=/user/cart etc.
    next_url = request.args.get('next', '')
    error = None

    if request.method == 'POST':
        form_email    = request.form.get('email', '').strip().lower()
        form_password = request.form.get('password', '')
        form_role     = request.form.get('role', 'user')
        next_url      = request.form.get('next', '')

        if not form_email or not form_password:
            error = 'Please fill in all fields.'

        elif form_role == 'admin':
            rows = oracle_fetchall(
                "SELECT seller_id AS sid, shop_name AS sname, "
                "email AS semail, password_hash AS phash "
                "FROM sellers WHERE LOWER(email) = :1",
                [form_email]
            )
            if rows and check_password_hash(rows[0]['phash'], form_password):
                u = rows[0]
                session['user_id']   = u['sid']
                session['user_name'] = u['sname']
                session['email']     = u['semail']
                session['role']      = 'admin'
                log_activity('login', {
                    'user_id':   u['sid'],
                    'user_name': u['sname'],
                    'role':      'admin'
                })
                return redirect(url_for('admin.dashboard'))
            else:
                error = 'Invalid admin credentials.'

        else:
            rows = oracle_fetchall(
                "SELECT customer_id AS cid, full_name AS cname, "
                "email AS cemail, password_hash AS phash, status AS cstatus "
                "FROM customers WHERE LOWER(email) = :1",
                [form_email]
            )
            if not rows:
                error = 'No account found with that email.'
            elif rows[0]['cstatus'] == 'Inactive':
                error = 'Your account is inactive. Contact support.'
            elif not check_password_hash(rows[0]['phash'], form_password):
                error = 'Incorrect password.'
            else:
                u = rows[0]
                session['user_id']   = u['cid']
                session['user_name'] = u['cname']
                session['email']     = u['cemail']
                session['role']      = 'user'
                log_activity('login', {
                    'user_id':   u['cid'],
                    'user_name': u['cname'],
                    'role':      'user'
                })
                # Redirect to the page they were trying to reach, or home
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(url_for('user.home'))

    return render_template('auth/login.html', error=error, next_url=next_url)

# ── Register ─────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('auth.index'))

    error = None

    if request.method == 'POST':
        reg_name     = request.form.get('name', '').strip()
        reg_email    = request.form.get('email', '').strip().lower()
        reg_phone    = request.form.get('phone', '').strip()
        reg_address  = request.form.get('address', '').strip()
        reg_password = request.form.get('password', '')
        reg_confirm  = request.form.get('confirm_password', '')

        if not reg_name or not reg_email or not reg_password or not reg_confirm:
            error = 'Please fill in all required fields.'
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', reg_email):
            error = 'Invalid email address.'
        elif len(reg_password) < 6:
            error = 'Password must be at least 6 characters.'
        elif reg_password != reg_confirm:
            error = 'Passwords do not match.'
        else:
            existing = oracle_fetchall(
                "SELECT customer_id AS cid FROM customers WHERE LOWER(email) = :1",
                [reg_email]
            )
            if existing:
                error = 'An account with this email already exists.'
            else:
                hashed = generate_password_hash(reg_password)
                oracle_execute(
                    "INSERT INTO customers "
                    "(full_name, email, password_hash, phone, address, status) "
                    "VALUES (:1, :2, :3, :4, :5, 'Active')",
                    [reg_name, reg_email, hashed, reg_phone, reg_address]
                )
                log_activity('register', {
                    'user_name': reg_name,
                    'reg_email': reg_email
                })
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('auth.login'))

    return render_template('auth/register.html', error=error)

# ── Logout ───────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    if is_logged_in():
        log_activity('logout', {
            'user_id':   session.get('user_id'),
            'user_name': session.get('user_name'),
            'role':      session.get('role')
        })
    session.clear()
    # After logout, go back to public homepage (not login page)
    return redirect(url_for('user.home'))