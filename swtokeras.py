import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D

# Đăng ký lớp tùy chỉnh
@tf.keras.utils.register_keras_serializable()
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, groups=1, **kwargs):
        super().__init__(**kwargs)

# Tải mô hình với custom_objects
model = load_model("mask_detector_trained.h5", 
                  custom_objects={"DepthwiseConv2D": CustomDepthwiseConv2D}, 
                  compile=False)
model.save("mask_detector_trained.keras")