import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load model nhận diện khẩu trang
model = load_model("mask_detector.model")

# Load ảnh và chuyển sang định dạng phù hợp
image = cv2.imread("nomask.jpg")
image_resized = cv2.resize(image, (224, 224))
image_array = np.expand_dims(image_resized, axis=0) / 255.0

# Dự đoán
(mask, no_mask) = model.predict(image_array)[0]

# Kết quả
if mask > no_mask:
    print("Người này có đeo khẩu trang.")
else:
    print("Người này KHÔNG đeo khẩu trang.")
