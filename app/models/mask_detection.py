import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D
import tensorflow as tf

# Đăng ký lớp tùy chỉnh
@tf.keras.utils.register_keras_serializable()
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, groups=1, **kwargs):
        super().__init__(**kwargs)

# Tải mô hình với custom_objects
mask_model = load_model("mask_detector_trained.keras", 
                  custom_objects={"DepthwiseConv2D": CustomDepthwiseConv2D})

def check_mask(image):
    image_resized = cv2.resize(image, (224, 224))
    image_array = np.expand_dims(image_resized, axis=0) / 255.0
    (mask, no_mask) = mask_model.predict(image_array)[0]
    return mask > no_mask