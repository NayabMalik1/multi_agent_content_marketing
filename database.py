import sqlite3
import json
from datetime import datetime

DB_PATH = "contentflow.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            status TEXT DEFAULT 'running',
            started_at TEXT,
            completed_at TEXT,
            final_content TEXT,
            metadata TEXT
        );

        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            agent_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            input_data TEXT,
            output_data TEXT,
            iterations INTEGER DEFAULT 0,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY (run_id) REFERENCES pipeline_runs(id)
        );

        CREATE TABLE IF NOT EXISTS content_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            version_number INTEGER DEFAULT 1,
            agent_name TEXT,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY (run_id) REFERENCES pipeline_runs(id)
        );
    """)
    conn.commit()
    conn.close()

def create_run(topic):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO pipeline_runs (topic, status, started_at) VALUES (?, ?, ?)",
        (topic, "running", datetime.now().isoformat())
    )
    run_id = c.lastrowid
    conn.commit()
    conn.close()
    return run_id

def log_agent(run_id, agent_name, status, input_data=None, output_data=None, iterations=0):
    conn = get_connection()
    c = conn.cursor()
    # Check if log exists
    c.execute("SELECT id FROM agent_logs WHERE run_id=? AND agent_name=?", (run_id, agent_name))
    row = c.fetchone()
    now = datetime.now().isoformat()
    if row:
        c.execute("""
            UPDATE agent_logs SET status=?, output_data=?, iterations=?, completed_at=?
            WHERE run_id=? AND agent_name=?
        """, (status, json.dumps(output_data), iterations, now, run_id, agent_name))
    else:
        c.execute("""
            INSERT INTO agent_logs (run_id, agent_name, status, input_data, output_data, iterations, started_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (run_id, agent_name, status, json.dumps(input_data), json.dumps(output_data), iterations, now, now))
    conn.commit()
    conn.close()

def save_version(run_id, agent_name, content, version_number=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO content_versions (run_id, agent_name, content, version_number, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (run_id, agent_name, content, version_number, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def complete_run(run_id, final_content, metadata=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE pipeline_runs SET status='completed', completed_at=?, final_content=?, metadata=?
        WHERE id=?
    """, (datetime.now().isoformat(), final_content, json.dumps(metadata or {}), run_id))
    conn.commit()
    conn.close()

def get_all_runs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM pipeline_runs ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_run_logs(run_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM agent_logs WHERE run_id=? ORDER BY id", (run_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
