import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

# Tải mô hình đã được huấn luyện
base_model = load_model("mask_detector.model")



# Thêm các lớp mới vào mô hình
x = base_model.output
# x = Dropout(0.3, name="dropout_16")(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.001), name="dense_16")(x)
output = Dense(1, activation='sigmoid', name="output19", kernel_regularizer=l2(0.01))(x)

mask_model = tf.keras.models.Model(inputs=base_model.input, outputs=output)
for layer in base_model.layers[-10:]:
    layer.trainable = True
mask_model.compile(optimizer=Adam(learning_rate=0.00001), loss='binary_crossentropy', metrics=['accuracy'])

# Data Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2,
    brightness_range=[0.8, 1.2],  # chỉnh độ sáng
    channel_shift_range=20.0      # chỉnh kênh màu
)

test_datagen = ImageDataGenerator(rescale=1./255)

# Tạo bộ dữ liệu huấn luyện và kiểm tra
train_dir = 'dataset/train1'
test_dir = 'dataset/test'

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',
    subset='validation'
)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

# Biên dịch lại mô hình
mask_model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Callbacks
checkpoint = ModelCheckpoint(
    'mask_detector_trained.h5',
    monitor='val_loss',
    save_best_only=True,
    mode='min',
    verbose=1
)

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=5,
    min_lr=1e-6
)

# Huấn luyện mô hình
history = mask_model.fit(
    train_generator,
    steps_per_epoch=len(train_generator),
    epochs=100,
    validation_data=validation_generator,
    validation_steps=len(validation_generator),
    callbacks=[checkpoint, early_stopping, reduce_lr]
)

# Đánh giá mô hình trên tập test
test_loss, test_accuracy = mask_model.evaluate(test_generator)
print(f"Test accuracy: {test_accuracy:.2f}")

# Lưu mô hình
mask_model.save("mask_detector_final.h5")

print("Model training completed and saved.")

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.savefig('training_history.png')
plt.show()