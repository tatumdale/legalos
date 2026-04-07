"""
legal_os/billing.py — Acme Dale Legal Services Legal OS Billing Service
Time tracking, disbursements, and invoice management.
"""
import uuid
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".openclaw/workspace-ad-shared/db/ad_matters.db"
DEFAULT_RATE = 15000  # pence per 6-min unit (£150/hr)

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def log_time(matter_id, agent_id, description, duration_minutes, rate_effective=None, entry_date=None):
    """Log a time entry against a matter."""
    now = datetime.now().isoformat()
    rate = rate_effective or DEFAULT_RATE
    units = duration_minutes / 6.0
    fee_amount = int(units * rate)

    db = get_db()
    entry_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO time_entries (id, matter_id, agent_id, description, duration_minutes, "
        "rate_effective, fee_amount, entry_date, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (entry_id, matter_id, agent_id, description, duration_minutes, rate, fee_amount,
         entry_date or now[:10], now)
    )
    db.commit()
    db.close()
    return entry_id

def get_time_entries(matter_id):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM time_entries WHERE matter_id=? ORDER BY created_at DESC",
        (matter_id,)
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]

def get_billing_summary(matter_id):
    db = get_db()
    time_rows = db.execute(
        "SELECT SUM(duration_minutes) as total_mins, SUM(fee_amount) as total_fees "
        "FROM time_entries WHERE matter_id=?", (matter_id,)
    ).fetchone()
    disbursement_rows = db.execute(
        "SELECT SUM(amount) as total_disb FROM disbursements WHERE matter_id=?", (matter_id,)
    ).fetchone()
    db.close()
    return {
        "total_minutes": time_rows["total_mins"] or 0,
        "total_fees": time_rows["total_fees"] or 0,
        "total_disbursements": disbursement_rows["total_disb"] or 0,
        "total_due": (time_rows["total_fees"] or 0) + (disbursement_rows["total_disb"] or 0)
    }

def add_disbursement(matter_id, description, amount, disbursement_type="other"):
    db = get_db()
    disbursement_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db.execute(
        "INSERT INTO disbursements (id, matter_id, description, amount, disbursement_type, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (disbursement_id, matter_id, description, amount, disbursement_type, now)
    )
    db.commit()
    db.close()
    return disbursement_id

def get_disbursements(matter_id):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM disbursements WHERE matter_id=? ORDER BY created_at DESC",
        (matter_id,)
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]

def create_invoice(matter_id):
    """Create a draft invoice from all unbilled time entries and disbursements."""
    db = get_db()
    matter = db.execute("SELECT * FROM matters WHERE id=?", (matter_id,)).fetchone()
    if not matter:
        db.close()
        raise ValueError(f"Matter {matter_id} not found")

    # Compute summary inline using same connection to avoid SQLite lock
    time_row = db.execute(
        "SELECT SUM(fee_amount) as tf, SUM(duration_minutes) as tm FROM time_entries WHERE matter_id=? AND billing_status='unbilled'",
        (matter_id,)
    ).fetchone()
    disb_row = db.execute(
        "SELECT SUM(amount) as td FROM disbursements WHERE matter_id=?",
        (matter_id,)
    ).fetchone()
    total_due = (time_row["tf"] or 0) + (disb_row["td"] or 0)
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{matter['ref'] or matter_id[:6]}"

    invoice_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    due_at = (datetime.now() + timedelta(days=30)).isoformat()

    db.execute(
        "INSERT INTO invoices (id, matter_id, client_name, client_email, invoice_number, "
        "total_amount, status, issued_at, due_at, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (invoice_id, matter_id, matter["client_name"], matter["client_email"],
         invoice_number, total_due, "draft", now, due_at, now)
    )

    db.execute(
        "UPDATE time_entries SET billing_status='invoiced', invoice_id=? "
        "WHERE matter_id=? AND billing_status='unbilled'",
        (invoice_id, matter_id)
    )

    db.commit()
    db.close()
    return invoice_id

def get_invoices(matter_id=None, status=None):
    db = get_db()
    q = "SELECT * FROM invoices WHERE 1=1"
    args = []
    if matter_id:
        q += " AND matter_id=?"
        args.append(matter_id)
    if status:
        q += " AND status=?"
        args.append(status)
    q += " ORDER BY created_at DESC"
    rows = db.execute(q, args).fetchall()
    db.close()
    return [dict(r) for r in rows]

def update_invoice_status(invoice_id, status):
    db = get_db()
    now = datetime.now().isoformat()
    if status == "paid":
        db.execute("UPDATE invoices SET status=?, paid_at=? WHERE id=?", (status, now, invoice_id))
    else:
        db.execute("UPDATE invoices SET status=? WHERE id=?", (status, invoice_id))
    db.commit()
    db.close()
