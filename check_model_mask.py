import time
import cv2
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import os
import glob

# Load model khẩu trang
mask_model = load_model("mask_detector_trained.h5")

def check_mask(image):
    """ Kiểm tra có đeo khẩu trang không """
    image_resized = cv2.resize(image, (224, 224))
    image_array = np.expand_dims(image_resized, axis=0) / 255.0
    prediction = mask_model.predict(image_array)
    print("Prediction: ", prediction)

    if prediction.shape[-1] == 2:  # Nếu model output 2 class (softmax)
        predicted_class = np.argmax(prediction[0])
        return predicted_class == 0  #0 = Mask, 1 = No Mask
    elif prediction.shape[-1] == 1:  # Nếu output 1 class (sigmoid)
        return prediction[0][0] < 0.45
    else:
        raise ValueError(f"Unexpected model output shape: {prediction.shape}")



def evaluate_mask_model(dataset_path, output_file="mask_model_performance.xlsx"):
    """ Kiểm tra performance của model khẩu trang trên tập dữ liệu. """
    results = []
    total_images = 0
    correct_predictions = 0
    failed_images = 0

    image_files = glob.glob(os.path.join(dataset_path, "*.[jpJP][pnPN]*"))  #  .jpg, .png

    if not image_files:
        print(f"❌ Không tìm thấy ảnh hợp lệ trong thư mục: {dataset_path}")
        return

    print(f"🔍 Đang kiểm tra {len(image_files)} ảnh...")

    start_eval_time = time.perf_counter()

    for idx, image_path in enumerate(image_files, start=1):
        filename = os.path.basename(image_path)
        image = cv2.imread(image_path)

        if image is None:
            print(f"⚠️ Lỗi đọc ảnh: {filename} (Bỏ qua)")
            failed_images += 1
            continue

        total_images += 1

        ground_truth = "mask" if filename.lower().startswith("m") else "no_mask"

        start_time = time.perf_counter()
        predicted_mask = check_mask(image)
        inference_time = time.perf_counter() - start_time

        predicted_label = "mask" if predicted_mask else "no_mask"
        correct = predicted_label == ground_truth
        correct_predictions += int(correct)

        results.append([filename, ground_truth, predicted_label, correct, inference_time])

        if idx % 10 == 0 or idx == len(image_files):
            print(f"✅ Đã xử lý {idx}/{len(image_files)} ảnh...")

    total_time = time.perf_counter() - start_eval_time

    if total_images == 0:
        print("❌ Không có ảnh hợp lệ để đánh giá.")
        return

    accuracy = correct_predictions / total_images

    df = pd.DataFrame(results, columns=["Filename", "Ground Truth", "Predicted", "Correct", "Inference Time (s)"])
    df.to_excel(output_file, index=False)

    print(f"\n Accuracy: {accuracy:.2%}")
    print(f"Tổng thời gian đánh giá: {total_time:.2f} giây")
    print(f" Kết quả đã lưu tại: {output_file}")
    print(f"Bỏ qua {failed_images} ảnh không hợp lệ.")

# Đường dẫn đến thư mục chứa ảnh kiểm tra
DATASET_PATH = "dataset/valid"
evaluate_mask_model(DATASET_PATH)