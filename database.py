"""
database.py
------------
Handles all SQLite persistence for the Logistics Cost Analyzer.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "logistics.db")
TABLE_NAME = "shipments"


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db_with_data(df: pd.DataFrame, force_reload: bool = False):
    """Create the shipments table and populate it if empty or force_reload."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}'"
    )
    exists = cursor.fetchone() is not None

    needs_load = force_reload or not exists
    if not needs_load:
        count = pd.read_sql(f"SELECT COUNT(*) as c FROM {TABLE_NAME}", conn)["c"][0]
        needs_load = count == 0

    if needs_load:
        df_to_save = df.copy()
        df_to_save["date"] = df_to_save["date"].astype(str)
        df_to_save.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        conn.commit()

    conn.close()


def load_data() -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
        df["date"] = pd.to_datetime(df["date"])
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


def record_count() -> int:
    conn = get_connection()
    try:
        count = pd.read_sql(f"SELECT COUNT(*) as c FROM {TABLE_NAME}", conn)["c"][0]
    except Exception:
        count = 0
    conn.close()
    return count


def reset_database(df: pd.DataFrame):
    """Force-overwrite the database with a fresh dataset."""
    init_db_with_data(df, force_reload=True)
