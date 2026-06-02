import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    location TEXT NOT NULL,
    price NUMERIC(18,2) NOT NULL,
    beds INTEGER NOT NULL,
    baths INTEGER NOT NULL,
    area TEXT NOT NULL,
    description TEXT NOT NULL,
    sale_type TEXT NOT NULL,
    image_url TEXT NOT NULL,
    rental_type TEXT
);

CREATE TABLE IF NOT EXISTS inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    property_name TEXT,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DEFAULT_LISTINGS = [
    (
        "Pristine 4BHK Villa",
        "22 Rosewood Avenue, Bengaluru",
        8400000.00,
        4,
        3,
        "2560 sqft",
        "A beautifully finished villa designed for modern family living with premium finishes.",
        "Outright",
        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=900&q=80",
        None,
    ),
    (
        "City Center 2BHK Apartment",
        "9 Lotus Street, Mumbai",
        4500000.00,
        2,
        2,
        "1150 sqft",
        "An elegant apartment located in the heart of the city, close to shopping and transit.",
        "Outright",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=900&q=80",
        None,
    ),
    (
        "Lakeview 3BHK Cottage",
        "18 Amber Lake Road, Pune",
        6850000.00,
        3,
        2,
        "1320 sqft",
        "A serene cottage with lake views, spacious interiors, and a lush outdoor area.",
        "Outright",
        "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80",
        None,
    ),
    (
        "Luxury 3BHK Rental",
        "7 Park Lane, Hyderabad",
        45000.00,
        3,
        3,
        "1400 sqft",
        "Premium rental home with park-facing views and concierge style amenities.",
        "Rental",
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=900&q=80",
        "Monthly",
    ),
    (
        "Cozy 2BHK Rental",
        "5 Jasmine Street, Chennai",
        28000.00,
        2,
        2,
        "900 sqft",
        "A comfortable rental apartment in a quiet neighborhood with excellent connectivity.",
        "Rental",
        "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=900&q=80",
        "Monthly",
    ),
    (
        "Studio Rental Suite",
        "12 Palm Grove, Delhi",
        18000.00,
        1,
        1,
        "550 sqft",
        "Smartly designed studio perfect for young professionals seeking city convenience.",
        "Rental",
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=900&q=80",
        "Monthly",
    ),
    (
        "Boys PG Near IIT",
        "4 Scholar Street, Bengaluru",
        10500.00,
        1,
        1,
        "180 sqft",
        "Affordable and secure PG accommodation for boys with meals and Wi-Fi included.",
        "PG",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=900&q=80",
        "Monthly",
    ),
    (
        "Girls PG with Food Facility",
        "16 Rose Avenue, Pune",
        12000.00,
        1,
        1,
        "200 sqft",
        "Comfortable girls PG with housekeeping, food facility, and a friendly community.",
        "PG",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80",
        "Monthly",
    ),
]


def get_db_connection(database_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(database_path: str) -> None:
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    conn = get_db_connection(database_path)
    with conn:
        conn.executescript(SCHEMA)
        
        existing_titles = {row[0] for row in conn.execute("SELECT title FROM listings").fetchall()}
        missing_rows = [row for row in DEFAULT_LISTINGS if row[0] not in existing_titles]
        if missing_rows:
            conn.executemany(
                """
                INSERT INTO listings (title, location, price, beds, baths, area, description, sale_type, image_url, rental_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                missing_rows,
            )
    conn.close()


def get_listings(database_path: str):
    conn = get_db_connection(database_path)
    listings = conn.execute(
        "SELECT title, location, price, beds, baths, area, description, sale_type, image_url, rental_type FROM listings"
    ).fetchall()
    conn.close()
    return listings


def get_listings_by_type(database_path: str, sale_type: str):
    conn = get_db_connection(database_path)
    listings = conn.execute(
        "SELECT title, location, price, beds, baths, area, description, sale_type, image_url, rental_type FROM listings WHERE sale_type = ?",
        (sale_type,),
    ).fetchall()
    conn.close()
    return listings


def save_inquiry(database_path: str, name: str, email: str, phone: str, property_name: str, message: str) -> None:
    conn = get_db_connection(database_path)
    with conn:
        conn.execute(
            "INSERT INTO inquiries (name, email, phone, property_name, message) VALUES (?, ?, ?, ?, ?)",
            (name, email, phone, property_name, message),
        )
    conn.close()


def get_inquiries(database_path: str, limit: int = 10, offset: int = 0, date_from: str | None = None, date_to: str | None = None):
    """Return enquiries with optional date filtering, pagination ordered by newest first.

    date_from/date_to should be strings in YYYY-MM-DD format (date only).
    """
    conn = get_db_connection(database_path)
    params = []
    where_clauses = []
    if date_from:
        where_clauses.append("date(created_at) >= date(?)")
        params.append(date_from)
    if date_to:
        where_clauses.append("date(created_at) <= date(?)")
        params.append(date_to)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"SELECT id, name, email, phone, property_name, message, created_at FROM inquiries {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    inquiries = conn.execute(sql, params).fetchall()
    conn.close()
    return inquiries


def get_inquiries_count(database_path: str, date_from: str | None = None, date_to: str | None = None) -> int:
    """Return total count of enquiries matching optional date filters."""
    conn = get_db_connection(database_path)
    params = []
    where_clauses = []
    if date_from:
        where_clauses.append("date(created_at) >= date(?)")
        params.append(date_from)
    if date_to:
        where_clauses.append("date(created_at) <= date(?)")
        params.append(date_to)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    sql = f"SELECT COUNT(*) FROM inquiries {where_sql}"
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return int(row[0] or 0)
