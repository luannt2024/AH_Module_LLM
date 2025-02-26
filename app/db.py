import psycopg2
from psycopg2 import extras
from datetime import datetime

# Kết nối đến database mặc định 'postgres'
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="thanhluan1303",
    host="localhost",
    port=5432
)
conn.autocommit = True
cur = conn.cursor()

# Kiểm tra và tạo database
cur.execute("SELECT 1 FROM pg_database WHERE datname = 'authentication_python';")
if not cur.fetchone():
    cur.execute("CREATE DATABASE authentication_python;")
cur.close()
conn.close()

# Kết nối đến 'authentication_python'
conn = psycopg2.connect(
    dbname="authentication_python",
    user="postgres",
    password="thanhluan1303",
    host="localhost",
    port=5432,
    cursor_factory=extras.DictCursor
)
cur = conn.cursor()

# Xóa và tạo lại các bảng
cur.execute("DROP TABLE IF EXISTS documents;")
cur.execute("DROP TABLE IF EXISTS processes;")
cur.execute("DROP TABLE IF EXISTS sessions;")
cur.execute("DROP TABLE IF EXISTS users;")
cur.execute("DROP TABLE IF EXISTS accounts;")

cur.execute("""
    CREATE TABLE accounts (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    );
""")
cur.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        account_id INTEGER UNIQUE REFERENCES accounts(id),
        name TEXT
    );
""")
cur.execute("""
    CREATE TABLE sessions (
        id SERIAL PRIMARY KEY,
        account_id INTEGER REFERENCES accounts(id),
        token TEXT NOT NULL,
        expires TIMESTAMP NOT NULL
    );
""")
cur.execute("""
    CREATE TABLE processes (
        id SERIAL PRIMARY KEY,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        created_time TIMESTAMP NOT NULL,
        finish_time TIMESTAMP,
        is_locked BOOLEAN DEFAULT FALSE
    );
""")
cur.execute("""
    CREATE TABLE documents (
        uuid UUID PRIMARY KEY,
        type VARCHAR(50) NOT NULL CHECK (type IN ('valid', 'invalid')),
        process BOOLEAN DEFAULT FALSE,
        employee_number VARCHAR(50),
        time TIMESTAMP,
        ess_store VARCHAR(50),
        process_id INTEGER REFERENCES processes(id),
        created_username VARCHAR(100),
        user_role_code VARCHAR(50),
        last_updated_time TIMESTAMP,
        store_name VARCHAR(100),
        original_name VARCHAR(255) 
    );
""")
conn.commit()

def get_db():
    return conn

def init_db(app):
    pass