import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "pumpsmart.db"
STATIONS_JSON = Path(__file__).parent.parent / "data" / "mock_stations.json"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER,
            fuel_type TEXT NOT NULL CHECK(fuel_type IN ('GASOLINE', 'DIESEL')),
            km_per_liter REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            origin_lat REAL,
            origin_lng REAL,
            dest_lat REAL,
            dest_lng REAL,
            is_recurring INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS fuel_stations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            gasoline_price_php REAL NOT NULL,
            diesel_price_php REAL NOT NULL,
            last_updated TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS trip_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            route_label TEXT,
            departure_time TEXT,
            distance_km REAL,
            predicted_cost_php REAL,
            predicted_duration_min REAL,
            traffic_factor REAL,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)

    # Seed stations if empty
    row = cur.execute("SELECT COUNT(*) FROM fuel_stations").fetchone()
    if row[0] == 0:
        stations = json.loads(STATIONS_JSON.read_text())
        cur.executemany(
            """INSERT INTO fuel_stations
               (id, name, brand, lat, lng, gasoline_price_php, diesel_price_php)
               VALUES (:id, :name, :brand, :lat, :lng, :gasoline_price_php, :diesel_price_php)""",
            stations,
        )

    conn.commit()
    conn.close()


def get_all_stations() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM fuel_stations ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_vehicle(make: str, model: str, year: int, fuel_type: str, km_per_liter: float) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO vehicles (make, model, year, fuel_type, km_per_liter) VALUES (?,?,?,?,?)",
        (make, model, year, fuel_type, km_per_liter),
    )
    conn.commit()
    vehicle_id = cur.lastrowid
    conn.close()
    return vehicle_id


def get_vehicles() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM vehicles ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_prediction(
    vehicle_id: int,
    route_label: str,
    departure_time: str,
    distance_km: float,
    predicted_cost_php: float,
    predicted_duration_min: float,
    traffic_factor: float,
) -> None:
    conn = get_conn()
    conn.execute(
        """INSERT INTO trip_predictions
           (vehicle_id, route_label, departure_time, distance_km,
            predicted_cost_php, predicted_duration_min, traffic_factor)
           VALUES (?,?,?,?,?,?,?)""",
        (vehicle_id, route_label, departure_time, distance_km,
         predicted_cost_php, predicted_duration_min, traffic_factor),
    )
    conn.commit()
    conn.close()


def get_recent_predictions(limit: int = 10) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM trip_predictions ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
