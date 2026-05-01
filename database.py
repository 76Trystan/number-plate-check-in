import logging
import os
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anpr.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate           TEXT NOT NULL,
                actual_checkin_time     TEXT NOT NULL,
                booked_checkin_time     TEXT,
                scheduled_checkout_time TEXT,
                actual_checkout_time    TEXT,
                image_path              TEXT
            )
        """)
        conn.commit()
    logger.info("Database initialised at %s", DB_PATH)


def log_checkin(license_plate, booked_checkin_time=None, scheduled_checkout_time=None, image_path=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO vehicles
               (license_plate, actual_checkin_time, booked_checkin_time, scheduled_checkout_time, image_path)
               VALUES (?, ?, ?, ?, ?)""",
            (license_plate, now, booked_checkin_time, scheduled_checkout_time, image_path),
        )
        conn.commit()
    logger.info("Checked in: %s at %s (id=%d)", license_plate, now, cur.lastrowid)
    return cur.lastrowid


def log_checkout(vehicle_id):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_connection() as conn:
        conn.execute(
            "UPDATE vehicles SET actual_checkout_time = ? WHERE id = ?",
            (now, vehicle_id),
        )
        conn.commit()
    logger.info("Checked out vehicle id=%d at %s", vehicle_id, now)


def get_all_vehicles():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM vehicles ORDER BY actual_checkin_time DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_current_vehicles():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM vehicles WHERE actual_checkout_time IS NULL ORDER BY actual_checkin_time DESC"
        ).fetchall()
    return [dict(row) for row in rows]
