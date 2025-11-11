# ML Model Development Plan - Cough Classification

## Project Goal
Create a custom ML model to classify cough recordings with:
- **Primary Classification**: Healthy, Mild, Severe
- **Secondary Detection**: Wheezing, Dyspnea, Nasal Congestion
- **Dataset**: COUGHVID V3 from Kaggle
- **Deployment**: TensorFlow Lite for mobile integration

---

## Phase 1: Dataset Preparation & Exploration

### 1.1 Download COUGHVID Dataset
```bash
# Install Kaggle CLI
pip install kaggle

# Download dataset (requires Kaggle API credentials)
kaggle datasets download -d orvile/coughvid-v3
unzip coughvid-v3.zip -d data/coughvid
```

### 1.2 Explore Dataset Structure
```python
import pandas as pd
import json

# Load metadata
metadata = pd.read_csv('data/coughvid/metadata.csv')

# Explore columns
print(metadata.columns)
print(metadata['status'].value_counts())  # healthy, symptomatic, COVID
print(metadata['cough_detected'].describe())

# Expert labels analysis
# Check expert_labels_1, expert_labels_2, expert_labels_3 columns
```

### 1.3 Data Preprocessing
- Filter high-quality recordings (SNR > threshold)
- Extract only recordings with cough_detected > 0.8
- Parse expert labels for severity and symptoms
- Create custom labels for: healthy/mild/severe
- Map expert annotations to wheezing, dyspnea, congestion

### Key Files:
- `audio_files/` - .webm or .ogg audio files
- `metadata.csv` - Metadata with labels
- Expert labels contain diagnosis information

---

## Phase 2: Feature Engineering

### 2.1 Audio Preprocessing
```python
import librosa
import numpy as np

def preprocess_audio(file_path, target_sr=22050, duration=10):
    """Load and preprocess audio file"""
    # Load audio
    audio, sr = librosa.load(file_path, sr=target_sr, duration=duration)
    
    # Normalize
    audio = librosa.util.normalize(audio)
    
    # Trim silence
    audio, _ = librosa.effects.trim(audio, top_db=20)
    
    # Pad or truncate to fixed length
    target_length = target_sr * duration
    if len(audio) < target_length:
        audio = np.pad(audio, (0, target_length - len(audio)))
    else:
        audio = audio[:target_length]
    
    return audio, sr
```

### 2.2 Feature Extraction - Mel Spectrograms
```python
def extract_mel_spectrogram(audio, sr, n_mels=128, n_fft=2048, hop_length=512):
    """Extract Mel spectrogram features"""
    mel_spec = librosa.feature.melspectrogram(
        y=audio, 
        sr=sr, 
        n_mels=n_mels,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    # Convert to log scale (dB)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    return mel_spec_db
```

### 2.3 Additional Features (Optional)
- **MFCC** (Mel-frequency cepstral coefficients)
- **Chroma features** (pitch class profiles)
- **Spectral contrast**
- **Zero-crossing rate**

---

## Phase 3: Model Architecture

### Approach 1: CNN Model (Recommended for Mobile)
```python
import tensorflow as tf
from tensorflow import keras

def build_cnn_model(input_shape=(128, 216, 1), num_classes=3):
    """
    Lightweight CNN for cough classification
    input_shape: (n_mels, time_steps, channels)
    """
    model = keras.Sequential([
        # Conv Block 1
        keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', 
                           input_shape=input_shape),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Dropout(0.25),
        
        # Conv Block 2
        keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Dropout(0.25),
        
        # Conv Block 3
        keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Dropout(0.25),
        
        # Dense layers
        keras.layers.Flatten(),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model
```

### Approach 2: CNN-LSTM Hybrid (Better Accuracy)
```python
def build_cnn_lstm_model(input_shape=(128, 216, 1), num_classes=3):
    """
    CNN-LSTM hybrid for temporal pattern recognition
    """
    model = keras.Sequential([
        # CNN layers for feature extraction
        keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same',
                           input_shape=input_shape),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        
        keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        
        # Reshape for LSTM
        keras.layers.Reshape((-1, 64)),  # Flatten spatial dimensions
        
        # LSTM layers for temporal patterns
        keras.layers.LSTM(128, return_sequences=True),
        keras.layers.Dropout(0.3),
        keras.layers.LSTM(64),
        keras.layers.Dropout(0.3),
        
        # Classification
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model
```

### Approach 3: Transfer Learning with MobileNetV3
```python
def build_mobilenet_model(input_shape=(128, 128, 3), num_classes=3):
    """
    Transfer learning using MobileNetV3 Small (optimized for mobile)
    """
    base_model = keras.applications.MobileNetV3Small(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    model = keras.Sequential([
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model
```

---

## Phase 4: Multi-Task Learning (Optional Advanced)

For detecting multiple conditions simultaneously:

```python
def build_multitask_model(input_shape=(128, 216, 1)):
    """
    Multi-task model for:
    - Severity classification (healthy/mild/severe)
    - Symptom detection (wheezing, dyspnea, congestion)
    """
    inputs = keras.Input(shape=input_shape)
    
    # Shared CNN backbone
    x = keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.MaxPooling2D((2, 2))(x)
    
    x = keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.MaxPooling2D((2, 2))(x)
    
    x = keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.MaxPooling2D((2, 2))(x)
    
    x = keras.layers.Flatten()(x)
    x = keras.layers.Dense(256, activation='relu')(x)
    x = keras.layers.Dropout(0.5)(x)
    
    # Task 1: Severity classification
    severity_output = keras.layers.Dense(3, activation='softmax', name='severity')(x)
    
    # Task 2: Symptom detection (multi-label)
    symptoms_output = keras.layers.Dense(3, activation='sigmoid', name='symptoms')(x)
    
    model = keras.Model(inputs=inputs, outputs=[severity_output, symptoms_output])
    
    return model
```

---

## Phase 5: Training Strategy

### 5.1 Data Split
```python
from sklearn.model_selection import train_test_split

# 70% train, 15% validation, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp)
```

### 5.2 Data Augmentation
```python
def augment_audio(audio, sr):
    """Audio augmentation techniques"""
    augmentations = [
        lambda x: librosa.effects.pitch_shift(x, sr=sr, n_steps=2),  # Pitch shift
        lambda x: librosa.effects.time_stretch(x, rate=0.9),  # Time stretch
        lambda x: x + 0.005 * np.random.randn(len(x)),  # Add noise
    ]
    
    aug_func = np.random.choice(augmentations)
    return aug_func(audio)
```

### 5.3 Training Configuration
```python
# Compile model
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy', 'precision', 'recall', 'AUC']
)

# Callbacks
callbacks = [
    keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
    keras.callbacks.ModelCheckpoint('best_model.h5', save_best_only=True)
]

# Train
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=32,
    callbacks=callbacks
)
```

---

## Phase 6: Model Evaluation

### 6.1 Performance Metrics
```python
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Predictions
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_test_classes = np.argmax(y_test, axis=1)

# Classification report
print(classification_report(y_test_classes, y_pred_classes, 
                          target_names=['Healthy', 'Mild', 'Severe']))

# Confusion matrix
cm = confusion_matrix(y_test_classes, y_pred_classes)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()
```

### 6.2 Target Metrics
- **Accuracy**: > 90%
- **Precision/Recall**: > 85% for each class
- **AUC**: > 0.90
- **Model Size**: < 10 MB (for mobile)

---

## Phase 7: TensorFlow Lite Conversion

### 7.1 Convert to TFLite
```python
# Convert model to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Optimization for mobile
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]  # Use FP16 for smaller size

# Convert
tflite_model = converter.convert()

# Save
with open('cough_classifier.tflite', 'wb') as f:
    f.write(tflite_model)

print(f"Model size: {len(tflite_model) / 1024 / 1024:.2f} MB")
```

### 7.2 Test TFLite Model
```python
# Load TFLite model
interpreter = tf.lite.Interpreter(model_path='cough_classifier.tflite')
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Test inference
interpreter.set_tensor(input_details[0]['index'], X_test[0:1])
interpreter.invoke()
prediction = interpreter.get_tensor(output_details[0]['index'])
print(f"Prediction: {prediction}")
```

---

## Phase 8: Backend Integration

### 8.1 Add ML Prediction Endpoint (FastAPI)
```python
# backend/ml_model.py
import tensorflow as tf
import numpy as np
import librosa

class CoughClassifier:
    def __init__(self, model_path='cough_classifier.tflite'):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.labels = ['Healthy', 'Mild', 'Severe']
    
    def preprocess_audio(self, audio_path):
        """Preprocess audio file for prediction"""
        audio, sr = librosa.load(audio_path, sr=22050, duration=10)
        audio = librosa.util.normalize(audio)
        
        mel_spec = librosa.feature.melspectrogram(
            y=audio, sr=sr, n_mels=128, n_fft=2048, hop_length=512
        )
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize and reshape
        mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / mel_spec_db.std()
        mel_spec_db = np.expand_dims(mel_spec_db, axis=-1)
        mel_spec_db = np.expand_dims(mel_spec_db, axis=0)
        
        return mel_spec_db.astype(np.float32)
    
    def predict(self, audio_path):
        """Predict cough classification"""
        # Preprocess
        input_data = self.preprocess_audio(audio_path)
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # Get prediction
        predicted_class = np.argmax(output_data[0])
        confidence = float(output_data[0][predicted_class])
        
        return {
            'severity': self.labels[predicted_class],
            'confidence': confidence,
            'probabilities': {
                label: float(prob) 
                for label, prob in zip(self.labels, output_data[0])
            }
        }
```

### 8.2 Update Cough Recording Endpoint
```python
# backend/server.py
from ml_model import CoughClassifier
import base64
import tempfile
import os

# Initialize classifier
cough_classifier = CoughClassifier('models/cough_classifier.tflite')

@api_router.post("/cough-record")
async def save_cough_record(data: CoughRecordCreate):
    try:
        # Decode base64 audio
        if data.audioData:
            audio_bytes = base64.b64decode(data.audioData)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            
            # ML Prediction
            try:
                prediction = cough_classifier.predict(temp_path)
                severity = prediction['severity']
                cough_type = 'dry' if 'type' in prediction else data.coughType
                diagnosis = f"ML Analysis: {prediction['severity']} (confidence: {prediction['confidence']:.2f})"
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")
                severity = data.severity
                diagnosis = f"ML prediction failed: {str(e)}"
            finally:
                os.unlink(temp_path)
        else:
            severity = data.severity
            diagnosis = "No audio data provided"
        
        # Save to Firestore
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'audioData': data.audioData[:100] + "...",  # Store sample only
            'severity': severity,
            'coughType': cough_type,
            'diagnosis': diagnosis,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        db.collection('cough_records').document(record['id']).set(record)
        
        return {
            'success': True,
            'message': 'Cough record saved with ML analysis',
            'data': record
        }
    except Exception as e:
        logger.error(f"Error saving cough record: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save cough record")
```

---

## Phase 9: Mobile App Integration

### 9.1 Update Frontend Cough Recording
```typescript
// frontend/app/home.tsx
const saveCoughRecording = async () => {
  if (!recording) {
    Alert.alert('Error', 'No recording to save');
    return;
  }

  try {
    await stopRecording();
    
    // Get audio URI
    const uri = recording.getURI();
    
    // Convert to base64
    const base64Audio = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    
    // Send to backend for ML analysis
    const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/cough-record`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: user?.id,
        audioData: base64Audio,
        severity: 'unknown',  // Will be determined by ML
        coughType: 'unknown',
        diagnosis: 'Processing...',
      }),
    });
    
    const result = await response.json();
    
    Alert.alert(
      '✅ Cough Analysis Complete',
      `Severity: ${result.data.severity}\n\n${result.data.diagnosis}`
    );
    
    setCoughModalVisible(false);
    setRecording(null);
  } catch (error) {
    console.error('Error saving cough recording:', error);
    Alert.alert('Error', 'Failed to analyze cough recording');
  }
};
```

---

## Phase 10: Testing & Validation

### 10.1 Backend Testing
```bash
# Test ML endpoint with sample audio
curl -X POST http://localhost:8001/api/cough-record \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-123",
    "audioData": "<base64_encoded_audio>",
    "severity": "unknown",
    "coughType": "unknown"
  }'
```

### 10.2 Mobile Testing
1. Record actual cough sounds
2. Verify ML predictions are displayed
3. Check Firebase for stored results
4. Test edge cases (no audio, corrupted audio)

---

## Timeline Estimate

| Phase | Task | Estimated Time |
|-------|------|----------------|
| 1 | Dataset download & exploration | 2-3 days |
| 2 | Feature engineering | 3-4 days |
| 3 | Model development | 5-7 days |
| 4 | Training & tuning | 3-5 days |
| 5 | Evaluation | 2-3 days |
| 6 | TFLite conversion | 1-2 days |
| 7 | Backend integration | 2-3 days |
| 8 | Mobile integration | 2-3 days |
| 9 | Testing | 2-3 days |
| **Total** | | **3-4 weeks** |

---

## Required Dependencies

### Python (Backend/Training)
```bash
pip install tensorflow==2.15.0
pip install librosa
pip install numpy pandas
pip install scikit-learn
pip install matplotlib seaborn
pip install kaggle
```

### React Native (Frontend)
```bash
npm install expo-file-system
npm install @react-native-async-storage/async-storage
```

---

## Next Steps

1. **Confirm approach**: Which model architecture do you prefer?
   - Simple CNN (fastest, smallest)
   - CNN-LSTM (better accuracy)
   - Transfer learning (MobileNet - balanced)

2. **Dataset access**: Do you have Kaggle API credentials?

3. **Development environment**: Where will you train the model?
   - Local machine (requires GPU recommended)
   - Google Colab (free GPU)
   - Cloud (AWS, GCP)

4. **Start with**: Dataset exploration or should I create the training notebook?

Let me know your preferences and we can start building! 🚀
