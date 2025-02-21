import psycopg2
from psycopg2.extras import RealDictCursor

# Kết nối database
conn = psycopg2.connect(
    dbname="authentication_python",
    user="postgres",
    password="password",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Tạo bảng nếu chưa có
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        code TEXT UNIQUE,
        name TEXT,
        password TEXT,
        token TEXT,
        fresh_token TEXT
    );
""")
conn.commit()
