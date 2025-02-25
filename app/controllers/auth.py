from flask import jsonify, request
from ..db import get_db
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta

def register(data):
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password:
        return jsonify({"error": "Thiếu email hoặc mật khẩu"}), 400

    conn = get_db()
    cur = conn.cursor()

    # Kiểm tra email đã tồn tại chưa
    cur.execute("SELECT * FROM accounts WHERE email = %s", (email,))
    if cur.fetchone():
        return jsonify({"error": "Email đã được sử dụng"}), 400

    # Hash mật khẩu
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Thêm vào bảng accounts
    cur.execute("INSERT INTO accounts (email, password) VALUES (%s, %s) RETURNING id",
                (email, hashed_password))
    account_id = cur.fetchone()[0]  # Truy cập tuple bằng chỉ số 0

    # Thêm vào bảng users
    cur.execute("INSERT INTO users (account_id, name) VALUES (%s, %s)",
                (account_id, name or "Unknown"))

    conn.commit()

    return jsonify({"message": "Đăng ký thành công", "account_id": account_id}), 201

def login(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Thiếu email hoặc mật khẩu"}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM accounts WHERE email = %s", (email,))
    account = cur.fetchone()

    if not account or not bcrypt.checkpw(password.encode('utf-8'), account[1].encode('utf-8')):
        return jsonify({"error": "Email hoặc mật khẩu không đúng"}), 401

    account_id = account[0]
    access_token = create_access_token(identity=str(account_id))
    refresh_token = create_refresh_token(identity=str(account_id))
    expires = datetime.utcnow() + timedelta(hours=1)

    cur.execute("""
        INSERT INTO sessions (account_id, token, expires) 
        VALUES (%s, %s, %s)
    """, (account_id, access_token, expires))
    conn.commit()

    return jsonify({"token": access_token, "refresh_token": refresh_token, "expires": expires.isoformat()}), 200