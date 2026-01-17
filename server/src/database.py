import sqlite3
import os
import json

from contextlib import contextmanager

db_path = os.environ["DB_PATH"] + "data.db"
max_stations = int(os.environ["MAX_STATIONS"])

def add_stations_to_db():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("DROP TABLE IF EXISTS stations")
    conn.execute("""CREATE TABLE stations(
                    id INTEGER PRIMARY KEY,
                    station_id TEXT
                    )"""
    )

    for i in range(max_stations):
        conn.execute("INSERT INTO stations (station_id) VALUES (?)", (f"station_{i+1}",))
    
    try:
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS metrics(
                    id INTEGER PRIMARY KEY,
                    station_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data JSON
                    )""")
    
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        pass
    finally:
        conn.close()


def store_data(station_id : str, timestamp : str, data : dict[str, dict[str, float]]):
    with get_db() as conn:
        conn.execute("INSERT INTO metrics (station_id, timestamp, data) VALUES (?, ?, json_insert(?))", (station_id, timestamp, json.dumps(data)))
    