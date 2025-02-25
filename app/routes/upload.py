from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import get_db
from uuid import uuid4
from datetime import datetime
import os

upload_bp = Blueprint('upload', __name__)

# Thư mục lưu file upload
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@upload_bp.route('/api/upload/request-uuids', methods=['POST'])
@jwt_required()
def request_uuids():
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cur = conn.cursor()

        # Kiểm tra token trong sessions
        token = request.headers.get('Authorization').split()[1]
        cur.execute("SELECT expires FROM sessions WHERE account_id = %s AND token = %s", (user_id, token))
        session = cur.fetchone()

        if not session or session['expires'] < datetime.utcnow():
            return jsonify({"error": "Phiên đã hết hạn hoặc không hợp lệ"}), 401

        data = request.json
        valid_count = data.get('valid_count', 0)
        invalid_count = data.get('invalid_count', 0)

        if not isinstance(valid_count, int) or not isinstance(invalid_count, int) or valid_count < 0 or invalid_count < 0:
            return jsonify({"error": "Số lượng valid_count và invalid_count phải là số nguyên không âm"}), 400

        total_count = valid_count + invalid_count
        if total_count == 0:
            return jsonify({"error": "Cần ít nhất 1 ảnh để tạo UUID"}), 400

        # Tạo process
        cur.execute("INSERT INTO processes (status, created_time) VALUES (%s, %s) RETURNING id",
                    ('pending', datetime.utcnow()))
        process_id = cur.fetchone()['id']

        # Tạo danh sách UUID
        uuids = [str(uuid4()) for _ in range(total_count)]
        valid_uuids = uuids[:valid_count]
        invalid_uuids = uuids[valid_count:]

        conn.commit()
        return jsonify({
            "message": "UUIDs created successfully",
            "process_id": process_id,
            "valid_uuids": valid_uuids,
            "invalid_uuids": invalid_uuids
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

@upload_bp.route('/api/upload/files', methods=['POST'])
@jwt_required()
def upload_files():
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cur = conn.cursor()

        # Kiểm tra token trong sessions
        token = request.headers.get('Authorization').split()[1]
        cur.execute("SELECT expires FROM sessions WHERE account_id = %s AND token = %s", (user_id, token))
        session = cur.fetchone()

        if not session or session['expires'] < datetime.utcnow():
            return jsonify({"error": "Phiên đã hết hạn hoặc không hợp lệ"}), 401

        # Kiểm tra dữ liệu gửi lên
        if 'valid_images' not in request.files and 'invalid_images' not in request.files and 'excel' not in request.files:
            return jsonify({"error": "No files uploaded"}), 400

        process_id = request.form.get('process_id')
        valid_uuids = request.form.get('valid_uuids', '').split(',')
        invalid_uuids = request.form.get('invalid_uuids', '').split(',')

        if not process_id:
            return jsonify({"error": "Missing process_id"}), 400

        # Lưu file và cập nhật bảng documents
        saved_files = {'valid': [], 'invalid': [], 'excel': None}

        # Xử lý valid images
        valid_files = request.files.getlist('valid_images')
        for i, file in enumerate(valid_files):
            if file.filename and i < len(valid_uuids):
                uuid = valid_uuids[i]
                file_path = os.path.join(UPLOAD_FOLDER, f"{uuid}_{file.filename}")
                file.save(file_path)
                saved_files['valid'].append(file_path)
                cur.execute("""
                    INSERT INTO documents (uuid, type, process_id, time)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (uuid) DO NOTHING
                """, (uuid, 'valid', process_id, datetime.utcnow()))

        # Xử lý invalid images
        invalid_files = request.files.getlist('invalid_images')
        for i, file in enumerate(invalid_files):
            if file.filename and i < len(invalid_uuids):
                uuid = invalid_uuids[i]
                file_path = os.path.join(UPLOAD_FOLDER, f"{uuid}_{file.filename}")
                file.save(file_path)
                saved_files['invalid'].append(file_path)
                cur.execute("""
                    INSERT INTO documents (uuid, type, process_id, time)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (uuid) DO NOTHING
                """, (uuid, 'invalid', process_id, datetime.utcnow()))

        # Xử lý file Excel
        excel_file = request.files.get('excel')
        if excel_file and excel_file.filename:
            excel_path = os.path.join(UPLOAD_FOLDER, excel_file.filename)
            excel_file.save(excel_path)
            saved_files['excel'] = excel_path

        # Cập nhật process
        cur.execute("UPDATE processes SET status = %s, finish_time = %s WHERE id = %s",
                    ('completed', datetime.utcnow(), process_id))

        conn.commit()
        return jsonify({
            "message": "Files uploaded successfully",
            "saved_files": saved_files
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500