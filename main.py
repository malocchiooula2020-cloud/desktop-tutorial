from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI(
    title="Correspondence & Workflow Management API",
    description="Automated reference generation, department routing, and audit trail logging.",
    version="1.0.0"
)

DB_NAME = "workflow.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS correspondence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref_number TEXT UNIQUE,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                assigned_unit TEXT NOT NULL,
                status TEXT DEFAULT 'OPEN',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref_number TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

init_db()

class IncomingRecord(BaseModel):
    sender: str
    subject: str
    assigned_unit: str

@app.post("/records/")
def log_correspondence(item: IncomingRecord):
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM correspondence")
        seq = cursor.fetchone()[0] + 1
        ref_number = f"REF-{datetime.utcnow().year}-{seq:04d}"

        cursor.execute(
            "INSERT INTO correspondence (ref_number, sender, subject, assigned_unit, created_at) VALUES (?, ?, ?, ?, ?)",
            (ref_number, item.sender, item.subject, item.assigned_unit, now)
        )
        cursor.execute(
            "INSERT INTO audit_log (ref_number, action, timestamp) VALUES (?, ?, ?)",
            (ref_number, f"Logged & routed to {item.assigned_unit}", now)
        )
    return {"reference_number": ref_number, "status": "OPEN", "routed_to": item.assigned_unit}

@app.get("/records/")
def list_records():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM correspondence ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

@app.patch("/records/{ref_number}/close")
def close_record(ref_number: str):
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE correspondence SET status = 'CLOSED' WHERE ref_number = ?", (ref_number,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reference number not found")
        cursor.execute(
            "INSERT INTO audit_log (ref_number, action, timestamp) VALUES (?, ?, ?)",
            (ref_number, "Marked as CLOSED", now)
        )
    return {"reference_number": ref_number, "status": "CLOSED"}
