# app/utils/db.py
import oracledb as cx_Oracle
from pymongo import MongoClient
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import config

# ── Oracle Client Init ───────────────────────────────────────
try:
    cx_Oracle.init_oracle_client(lib_dir=config.ORACLE_CLIENT_PATH)
except Exception:
    pass

# ── Oracle Connection ────────────────────────────────────────
def get_oracle_connection():
    return cx_Oracle.connect(
        user=config.ORACLE_USER,
        password=config.ORACLE_PASSWORD,
        dsn=config.ORACLE_DSN
    )

def oracle_fetchall(query, params=None):
    """Run a SELECT query and return list of dicts.
    - Normalizes whitespace to fix missing-space bugs from string concatenation
    - Reads CLOB/BLOB values while connection is still open
    """
    conn = get_oracle_connection()
    cursor = conn.cursor()
    # Fix missing spaces from Python multiline string concatenation
    clean_query = ' '.join(query.split())
    cursor.execute(clean_query, params or [])
    columns = [col[0].lower() for col in cursor.description]
    raw_rows = cursor.fetchall()
    rows = []
    for row in raw_rows:
        d = {}
        for col, val in zip(columns, row):
            # Read LOB objects (CLOB/BLOB) while connection is still open
            if hasattr(val, 'read'):
                try:
                    d[col] = val.read()
                except Exception:
                    d[col] = ''
            else:
                d[col] = val
        rows.append(d)
    cursor.close()
    conn.close()
    return rows

def oracle_execute(query, params=None):
    """Run INSERT/UPDATE/DELETE with commit."""
    conn = get_oracle_connection()
    cursor = conn.cursor()
    clean_query = ' '.join(query.split())
    cursor.execute(clean_query, params or [])
    conn.commit()
    cursor.close()
    conn.close()

def oracle_callproc(proc_name, params):
    """Call a PL/SQL stored procedure."""
    conn = get_oracle_connection()
    cursor = conn.cursor()
    cursor.callproc(proc_name, params)
    conn.commit()
    cursor.close()
    conn.close()

# ── MongoDB Connection ───────────────────────────────────────
_mongo_client = None

def get_mongo_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(config.MONGO_URI)
    return _mongo_client[config.MONGO_DB]

# ── MongoDB Loggers ──────────────────────────────────────────
def log_activity(event_type, data: dict):
    db = get_mongo_db()
    db.activity_logs.insert_one({
        "event_type": event_type,
        "timestamp": datetime.utcnow(),
        **data
    })

def log_search(user_id, query, results_count):
    db = get_mongo_db()
    db.search_logs.insert_one({
        "user_id": user_id,
        "query": query,
        "results_count": results_count,
        "timestamp": datetime.utcnow()
    })

def log_failed_transaction(user_id, order_id, amount, method, reason):
    db = get_mongo_db()
    db.failed_transactions.insert_one({
        "user_id": user_id,
        "order_id": order_id,
        "amount": amount,
        "method": method,
        "reason": reason,
        "timestamp": datetime.utcnow()
    })