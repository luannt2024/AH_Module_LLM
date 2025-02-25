from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..db import get_db
from datetime import datetime
import cv2
import numpy as np
from ..models.mask_detection import check_mask

def verify_identity():
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cur = conn.cursor()

        # Kiểm tra token trong sessions
        token = request.headers.get('Authorization').split()[1]
        cur.execute("SELECT expires FROM sessions WHERE account_id = %s AND token = %s", (user_id, token))
        session = cur.fetchone()

        if not session or session["expires"] < datetime.utcnow():
            return jsonify({"error": "Phiên đã hết hạn hoặc không hợp lệ"}), 401

        file1 = request.files.get("image1")
        file2 = request.files.get("image2")

        if not file1 or not file2:
            return jsonify({"error": "Thiếu ảnh đầu vào"}), 400

        image1 = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_COLOR)
        image2 = cv2.imdecode(np.frombuffer(file2.read(), np.uint8), cv2.IMREAD_COLOR)

        if check_mask(image1) or check_mask(image2):
            return jsonify({"error": "Không thể xác minh vì có khẩu trang"}), 400

        return jsonify({"message": "Xác minh thành công"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def simple_check():
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cur = conn.cursor()

        token = request.headers.get('Authorization').split()[1]
        cur.execute("SELECT expires FROM sessions WHERE account_id = %s AND token = %s", (user_id, token))
        session = cur.fetchone()

        if not session or session["expires"] < datetime.utcnow():
            return jsonify({"error": "Phiên đã hết hạn hoặc không hợp lệ"}), 401

        file1 = request.files.get("image")
        if not file1:
            return jsonify({"error": "Thiếu ảnh đầu vào"}), 400

        image1 = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_COLOR)

        if check_mask(image1):
            return jsonify({"error": "Không thể xác minh vì có khẩu trang"}), 400

        return jsonify({"message": "Ảnh hợp lệ"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500