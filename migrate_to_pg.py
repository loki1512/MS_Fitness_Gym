"""
One-time migration: SQLite → PostgreSQL

Usage:
  set DATABASE_URL=postgresql://user:pass@host/dbname
  python migrate_to_pg.py

Copies all rows from the local SQLite db to the PostgreSQL database
specified by DATABASE_URL. Skips if DATABASE_URL is not set.
"""

import os
import sys
from sqlalchemy import create_engine, text

SQLITE_URI = "sqlite:///instance/db.sqlite3"
PG_URI = os.environ.get("DATABASE_URL", "")

if not PG_URI:
    print("Set DATABASE_URL env var first.")
    sys.exit(1)

if PG_URI.startswith("postgres://"):
    PG_URI = PG_URI.replace("postgres://", "postgresql://", 1)

# Tables to migrate (in order to respect foreign keys)
TABLES = ["item", "role", "user", "roles_users", "bill", "bill_item"]

sqlite_eng = create_engine(SQLITE_URI)
pg_eng = create_engine(PG_URI)

# First, create all tables in PG via the app
from app import create_app
app = create_app()

with sqlite_eng.connect() as src:
    with pg_eng.connect() as dst:
        for table in TABLES:
            try:
                rows = src.execute(text(f"SELECT * FROM {table}")).fetchall()
            except Exception:
                print(f"  Skipping {table} (not in SQLite)")
                continue

            if not rows:
                print(f"  {table}: 0 rows (empty)")
                continue

            # Get column names
            cols = src.execute(text(f"SELECT * FROM {table} LIMIT 1")).keys()
            col_names = list(cols)
            placeholders = ", ".join(f":{c}" for c in col_names)
            col_list = ", ".join(col_names)

            insert_sql = text(
                f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
                f"ON CONFLICT DO NOTHING"
            )

            for row in rows:
                dst.execute(insert_sql, dict(zip(col_names, row)))

            dst.commit()
            print(f"  {table}: {len(rows)} rows migrated")

print("\nDone! All data migrated to PostgreSQL.")
