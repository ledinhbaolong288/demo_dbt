import json
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data_src"

def get_connection():
    # print("Connecting to PostgreSQL...", DB_CONFIG)
    return psycopg2.connect(**DB_CONFIG)


def load_json(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_raw_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            create schema if not exists raw;
        """)

        cur.execute("""
            create table if not exists raw.orders_raw (
                order_id bigint,
                user_id bigint,
                total_amount numeric(18,2),
                created_at timestamp,
                etl_time timestamp default current_timestamp
            );
        """)

        cur.execute("""
            create table if not exists raw.users_raw (
                user_id bigint,
                user_name text,
                email text,
                created_at timestamp,
                updated_at timestamp,
                etl_time timestamp default current_timestamp
            );
        """)

    conn.commit()


def truncate_raw_tables(conn):
    with conn.cursor() as cur:
        cur.execute("truncate table raw.orders_raw;")
        cur.execute("truncate table raw.users_raw;")
    conn.commit()


def insert_orders(conn, orders):
    rows = [
        (
            item.get("order_id"),
            item.get("user_id"),
            item.get("total_amount"),
            item.get("created_at")
        )
        for item in orders
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            insert into raw.orders_raw (order_id, user_id, total_amount,created_at)
            values %s
            """,
            rows
        )
    conn.commit()


def insert_users(conn, users):
    rows = [
        (
            item.get("user_id"),
            item.get("username"),
            item.get("email"),
            item.get("created_at"),
            item.get("updated_at")
        )
        for item in users
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            insert into raw.users_raw (user_id, user_name, email,created_at,updated_at)
            values %s
            """,
            rows
        )
    conn.commit()


def main():
    orders = load_json(DATA_DIR / "orders.json")
    users = load_json(DATA_DIR / "users.json")

    conn = get_connection()
    try:
        create_raw_tables(conn)
        truncate_raw_tables(conn)
        insert_orders(conn, orders)
        insert_users(conn, users)
        print("Loaded JSON data into raw.orders_raw and raw.users_raw successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()