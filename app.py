from flask import Flask, request, jsonify
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from tensorflow.keras.models import load_model
from ultralytics import YOLO  

app = Flask(__name__)

# Load model khẩu trang
mask_model = load_model("mask_detector.model")

# Load model nhận diện khuôn mặt (ArcFace)
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))

# Load model nhận diện kệ
shelf_model = YOLO("yolov8n.pt")  # Model YOLOv8 Pretrained


@app.route("/verify-identity", methods=["POST"])
def verify_identity():
    try:
        # Nhận ảnh từ request
        file1 = request.files.get("image1")
        file2 = request.files.get("image2")

        if not file1 or not file2:
            return jsonify({"error": "Thiếu ảnh đầu vào"}), 400

        # Đọc ảnh
        image1 = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_COLOR)
        image2 = cv2.imdecode(np.frombuffer(file2.read(), np.uint8), cv2.IMREAD_COLOR)

        # Kiểm tra khẩu trang
        if check_mask(image1) or check_mask(image2):
            return jsonify({"error": "Không thể xác minh vì có khẩu trang"}), 400

        # Kiểm tra có kệ trong ảnh 2 không
        if not detect_shelf(image2):
            return jsonify({"error": "Không tìm thấy kệ trong ảnh thứ hai"}), 400

        # So sánh khuôn mặt
        result = compare_faces(image1, image2)

        if result == "Không tìm thấy khuôn mặt":
            return jsonify({"error": result}), 400
        elif result == "Hai người khác nhau":
            return jsonify({"error": result}), 400
        else:
            return jsonify({"message": "Hai khuôn mặt giống nhau"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/simple-check", methods=["POST"])
def simple_check():
    try:
        # Nhận ảnh từ request
        file1 = request.files.get("image")

        if not file1:
            return jsonify({"error": "Thiếu ảnh đầu vào"}), 400

        # Đọc ảnh
        image1 = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_COLOR)

        # Kiểm tra khẩu trang
        if check_mask(image1):
            return jsonify({"error": "Không thể xác minh vì có khẩu trang"}), 400

        # Kiểm tra có kệ
        if not detect_shelf(image1):
            return jsonify({"error": "Không tìm thấy kệ"}), 400

        # Nếu không có lỗi, trả về thành công
        return jsonify({"message": "Ảnh hợp lệ"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def check_mask(image):
    """ Kiểm tra có đeo khẩu trang không """
    image_resized = cv2.resize(image, (224, 224))
    image_array = np.expand_dims(image_resized, axis=0) / 255.0
    (mask, no_mask) = mask_model.predict(image_array)[0]
    return mask > no_mask  # True nếu có khẩu trang


def compare_faces(image1, image2):
    """ So sánh khuôn mặt bằng ArcFace """
    faces1 = face_app.get(image1)
    faces2 = face_app.get(image2)

    if len(faces1) == 0 or len(faces2) == 0:
        return "Không tìm thấy khuôn mặt"

    # Lấy đặc trưng khuôn mặt đầu tiên
    embedding1 = faces1[0].normed_embedding
    embedding2 = faces2[0].normed_embedding

    # Tính cosine similarity
    similarity = np.dot(embedding1, embedding2)

    # Ngưỡng xác minh: ArcFace thường dùng 0.5-0.6
    return "Hai khuôn mặt giống nhau" if similarity > 0.6 else "Hai người khác nhau"


def detect_shelf(image):
    """ Kiểm tra ảnh có kệ hay không bằng YOLOv8 """
    results = shelf_model(image)
    
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])  # Lấy class ID của vật thể
            if class_id in [73, 74]:  # chưa có ID chờ train
                return True  # Có kệ
    return False  # Không tìm thấy kệ


if __name__ == "__main__":
    app.run(debug=True)
