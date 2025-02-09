import torch
import os
import time
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score
from ultralytics import YOLO
import cv2

# Đường dẫn đến thư mục chứa ảnh
input_folder = "dataset_shelf"  # Thay đổi đường dẫn thư mục của bạn
with_shelf_folder = os.path.join(input_folder, "with_shelf")
without_shelf_folder = os.path.join(input_folder, "without_shelf")

# Tải mô hình YOLOv8n
model = YOLO("yolo11n.pt")  # Đảm bảo đường dẫn chính xác đến file yolo11
model.eval() 

def predict(image_path):
    img = cv2.imread(image_path)
    results = model(img)  # Dự đoán

    print("Prediction Results:", results)
    
    if results and len(results[0].boxes) > 0: 
        for result in results[0].boxes:
            if result.cls == 0:  # Giả sử có "shelf" => này không có cần train 
                return True
    return False


# Hàm tính toán accuracy và thời gian
def evaluate_model():
    y_true = []
    y_pred = []
    times = []

    # Đọc ảnh trong thư mục with_shelf và without_shelf
    for img_name in os.listdir(with_shelf_folder):
        img_path = os.path.join(with_shelf_folder, img_name)
        start_time = time.time()
        has_shelf = predict(img_path)
        end_time = time.time()
        times.append(end_time - start_time)
        
        y_true.append(1)  # Ghi nhận kết quả  (có kệ)
        y_pred.append(1 if has_shelf else 0)

    for img_name in os.listdir(without_shelf_folder):
        img_path = os.path.join(without_shelf_folder, img_name)
        start_time = time.time()
        has_shelf = predict(img_path)
        end_time = time.time()
        times.append(end_time - start_time)

        y_true.append(0)  # Ghi nhận kết quả (không có kệ)
        y_pred.append(1 if has_shelf else 0)

    # Tính toán độ chính xác
    accuracy = accuracy_score(y_true, y_pred)
    
    # Thời gian trung bình
    avg_time = sum(times) / len(times)

    # Ghi kết quả vào file Excel
    df = pd.DataFrame({
        'Image': os.listdir(with_shelf_folder) + os.listdir(without_shelf_folder),
        'True_Label': y_true,
        'Predicted_Label': y_pred,
        'Time_Per_Image': times
    })
    
    df.to_excel("evaluation_results.xlsx", index=False)

    return accuracy, avg_time

# Đánh giá mô hình
accuracy, avg_time = evaluate_model()
print(f"Accuracy: {accuracy:.4f}")
print(f"Average Inference Time: {avg_time:.4f} seconds per image")
