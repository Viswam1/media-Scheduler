"""SQLite database layer for the Church Media Scheduler."""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "scheduler.db"
DB_PATH.parent.mkdir(exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            skills TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            start_time TEXT,
            location TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            task_type TEXT,
            assigned_member_id INTEGER,
            notes TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_member_id) REFERENCES members(id) ON DELETE SET NULL
        );
        """)
        conn.commit()


# ---------- Members ----------
def add_member(name, email, phone, skills):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO members (name, email, phone, skills) VALUES (?, ?, ?, ?)",
            (name, email, phone, skills),
        )
        conn.commit()


def get_members(active_only=True):
    with get_conn() as conn:
        q = "SELECT * FROM members"
        if active_only:
            q += " WHERE active = 1"
        q += " ORDER BY name"
        return [dict(r) for r in conn.execute(q).fetchall()]


def update_member(member_id, name, email, phone, skills, active):
    with get_conn() as conn:
        conn.execute(
            """UPDATE members SET name=?, email=?, phone=?, skills=?, active=?
               WHERE id=?""",
            (name, email, phone, skills, active, member_id),
        )
        conn.commit()


def delete_member(member_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))
        conn.commit()


# ---------- Events ----------
def add_event(title, event_date, start_time, location, description):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO events (title, event_date, start_time, location, description)
               VALUES (?, ?, ?, ?, ?)""",
            (title, event_date, start_time, location, description),
        )
        conn.commit()
        return cur.lastrowid


def get_events():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM events ORDER BY event_date DESC"
        ).fetchall()]


def get_event(event_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        return dict(row) if row else None


def update_event(event_id, title, event_date, start_time, location, description):
    with get_conn() as conn:
        conn.execute(
            """UPDATE events SET title=?, event_date=?, start_time=?, location=?, description=?
               WHERE id=?""",
            (title, event_date, start_time, location, description, event_id),
        )
        conn.commit()


def delete_event(event_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM events WHERE id=?", (event_id,))
        conn.commit()


# ---------- Tasks ----------
def add_task(event_id, task_name, task_type, assigned_member_id, notes, status="Pending"):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO tasks (event_id, task_name, task_type, assigned_member_id, notes, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event_id, task_name, task_type, assigned_member_id, notes, status),
        )
        conn.commit()


def get_tasks_for_event(event_id):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT t.*, m.name AS member_name
            FROM tasks t
            LEFT JOIN members m ON t.assigned_member_id = m.id
            WHERE t.event_id = ?
            ORDER BY t.id
        """, (event_id,)).fetchall()
        return [dict(r) for r in rows]


def get_all_tasks():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT t.*, m.name AS member_name, e.title AS event_title, e.event_date
            FROM tasks t
            LEFT JOIN members m ON t.assigned_member_id = m.id
            LEFT JOIN events e ON t.event_id = e.id
            ORDER BY e.event_date DESC, t.id
        """).fetchall()
        return [dict(r) for r in rows]


def update_task(task_id, task_name, task_type, assigned_member_id, notes, status):
    with get_conn() as conn:
        conn.execute(
            """UPDATE tasks SET task_name=?, task_type=?, assigned_member_id=?,
               notes=?, status=? WHERE id=?""",
            (task_name, task_type, assigned_member_id, notes, status, task_id),
        )
        conn.commit()


def delete_task(task_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
