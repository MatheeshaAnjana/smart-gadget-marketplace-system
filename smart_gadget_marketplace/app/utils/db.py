# app/utils/db.py
import oracledb as cx_Oracle
from pymongo import MongoClient
from datetime import datetime
import sys, os

# Add project root to path so config.py is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import config

# ── Oracle Client Init ───────────────────────────────────────
try:
    cx_Oracle.init_oracle_client(lib_dir=config.ORACLE_CLIENT_PATH)
except Exception:
    pass  # Already initialized

# ── Oracle Connection ────────────────────────────────────────
def get_oracle_connection():
    """Returns a new Oracle DB connection."""
    return cx_Oracle.connect(
        user=config.ORACLE_USER,
        password=config.ORACLE_PASSWORD,
        dsn=config.ORACLE_DSN
    )

def oracle_fetchall(query, params=None):
    """Run a SELECT query and return list of dicts."""
    conn = get_oracle_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    columns = [col[0].lower() for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows

def oracle_execute(query, params=None):
    """Run INSERT/UPDATE/DELETE with commit."""
    conn = get_oracle_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or [])
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
    """Returns MongoDB database instance (singleton)."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(config.MONGO_URI)
    return _mongo_client[config.MONGO_DB]

# ── MongoDB Activity Logger ──────────────────────────────────
def log_activity(event_type, data: dict):
    """
    Log any activity event to MongoDB.
    Usage: log_activity("login", {"user_id": 1, "user_name": "Alex"})
    """
    db = get_mongo_db()
    doc = {
        "event_type": event_type,
        "timestamp": datetime.utcnow(),
        **data
    }
    db.activity_logs.insert_one(doc)

def log_search(user_id, query, results_count):
    """Log a search query to MongoDB."""
    db = get_mongo_db()
    db.search_logs.insert_one({
        "user_id": user_id,
        "query": query,
        "results_count": results_count,
        "timestamp": datetime.utcnow()
    })

def log_failed_transaction(user_id, order_id, amount, method, reason):
    """Log a failed payment to MongoDB."""
    db = get_mongo_db()
    db.failed_transactions.insert_one({
        "user_id": user_id,
        "order_id": order_id,
        "amount": amount,
        "method": method,
        "reason": reason,
        "timestamp": datetime.utcnow()
    })