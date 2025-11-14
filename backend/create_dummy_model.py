"""
Create a dummy TFLite model for testing ML integration
This creates a simple model that classifies audio as Healthy/Mild/Severe
"""
import tensorflow as tf
import numpy as np
import json

print("Creating dummy TFLite model for testing...")

# Create a very simple model (just for testing integration)
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(128, 216, 1)),  # Mel spectrogram shape
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')  # 3 classes: Healthy, Mild, Severe
])

# Compile (not training, just for structure)
model.compile(optimizer='adam', loss='categorical_crossentropy')

print("Model summary:")
model.summary()

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save TFLite model
model_path = 'models/cough_classifier_dummy.tflite'
with open(model_path, 'wb') as f:
    f.write(tflite_model)

model_size_mb = len(tflite_model) / (1024 * 1024)
print(f"\n✅ Dummy TFLite model saved: {model_path}")
print(f"Model size: {model_size_mb:.2f} MB")

# Create model info
model_info = {
    'label_mapping': {
        '0': 'Healthy',
        '1': 'Mild',
        '2': 'Severe'
    },
    'input_shape': [128, 216, 1],
    'target_sr': 22050,
    'duration': 10,
    'n_mels': 128,
    'n_fft': 2048,
    'hop_length': 512,
    'test_accuracy': 0.0,  # Dummy model, no real accuracy
    'test_precision': 0.0,
    'test_recall': 0.0,
    'model_size_mb': float(model_size_mb),
    'is_dummy': True,
    'note': 'This is a DUMMY model for testing integration only. Predictions are random!'
}

config_path = 'models/model_info_dummy.json'
with open(config_path, 'w') as f:
    json.dump(model_info, f, indent=2)

print(f"✅ Model config saved: {config_path}")
print("\n⚠️  NOTE: This is a DUMMY model!")
print("Predictions will be essentially random, but integration will work.")
print("\nNext steps:")
print("1. Run the ml_model.py to test loading")
print("2. Start backend and test cough recording endpoint")
print("3. Replace with real trained model when ready")
