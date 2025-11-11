# 2-Day ML Model Implementation Plan

## 🎯 Goal
Build and deploy a cough classification model (Healthy/Mild/Severe) in 2 days

---

## 📅 Day 1: Model Training (TODAY)

### Morning (2-3 hours)
- [ ] **Upload notebook to Google Colab**
  - Go to https://colab.research.google.com
  - Upload `cough_classification_simple_cnn.ipynb`
  - Enable GPU: Runtime → Change runtime type → GPU

- [ ] **Setup Kaggle API**
  - Go to https://www.kaggle.com/settings
  - Click "Create New API Token"
  - Download `kaggle.json`
  - Upload to Colab when prompted

- [ ] **Download COUGHVID dataset**
  - Run cells 1-3 in notebook
  - Dataset download: ~10-15 minutes

### Afternoon (3-4 hours)
- [ ] **Data preprocessing**
  - Run cells 4-6 (dataset exploration and labeling)
  - Extract mel spectrograms
  - Expected time: 30-60 minutes for ~3000 samples

- [ ] **Model training**
  - Run cells 7-8 (build and train CNN)
  - Training time: 15-30 minutes with GPU
  - Monitor accuracy - target >85%

### Evening (1-2 hours)
- [ ] **Model evaluation**
  - Run cells 9 (evaluate performance)
  - Check confusion matrix
  - Verify accuracy on test set

- [ ] **Export model**
  - Run cells 10-12 (convert to TFLite)
  - Download files:
    - `cough_classifier.tflite`
    - `model_info.json`
    - `best_cough_model.h5`

### Day 1 Checklist
✅ Notebook runs successfully  
✅ Model trained with >85% accuracy  
✅ TFLite model generated (<5MB)  
✅ Files downloaded from Colab  

---

## 📅 Day 2: Backend Integration & Testing (TOMORROW)

### Morning (2-3 hours)

#### 1. Setup Backend for ML (30 mins)
```bash
# On your Mac backend folder
cd /path/to/backend

# Create models directory
mkdir models

# Copy downloaded files
cp /path/to/downloads/cough_classifier.tflite models/
cp /path/to/downloads/model_info.json models/

# Install dependencies
pip install tensorflow librosa pydub
```

#### 2. Create ML Module (1 hour)
Create file: `backend/ml_model.py`

```python
import tensorflow as tf
import numpy as np
import librosa
import json

class CoughClassifier:
    def __init__(self, model_path='models/cough_classifier.tflite', 
                 config_path='models/model_info.json'):
        # Load TFLite model
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.label_mapping = config['label_mapping']
        self.target_sr = config['target_sr']
        self.duration = config['duration']
        self.n_mels = config['n_mels']
        self.n_fft = config['n_fft']
        self.hop_length = config['hop_length']
    
    def preprocess_audio(self, audio_path):
        """Preprocess audio file"""
        # Load audio
        audio, sr = librosa.load(audio_path, sr=self.target_sr, duration=self.duration)
        audio = librosa.util.normalize(audio)
        
        # Trim silence
        audio, _ = librosa.effects.trim(audio, top_db=20)
        
        # Pad or truncate
        target_length = self.target_sr * self.duration
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]
        
        # Extract mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio, sr=sr, n_mels=self.n_mels,
            n_fft=self.n_fft, hop_length=self.hop_length
        )
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize
        mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / mel_spec_db.std()
        
        # Add dimensions for model input
        mel_spec_db = np.expand_dims(mel_spec_db, axis=-1)
        mel_spec_db = np.expand_dims(mel_spec_db, axis=0)
        
        return mel_spec_db.astype(np.float32)
    
    def predict(self, audio_path):
        """Predict cough classification"""
        try:
            # Preprocess
            input_data = self.preprocess_audio(audio_path)
            
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # Get results
            predicted_class = int(np.argmax(output_data[0]))
            confidence = float(output_data[0][predicted_class])
            
            return {
                'severity': self.label_mapping[str(predicted_class)],
                'confidence': confidence,
                'probabilities': {
                    self.label_mapping[str(i)]: float(prob)
                    for i, prob in enumerate(output_data[0])
                }
            }
        except Exception as e:
            raise Exception(f"Prediction failed: {str(e)}")
```

#### 3. Update Backend API (1 hour)
Update `backend/server.py`:

```python
# Add at top of file
from ml_model import CoughClassifier
import base64
import tempfile
import os

# Initialize ML model after Firebase
try:
    cough_classifier = CoughClassifier(
        model_path='models/cough_classifier.tflite',
        config_path='models/model_info.json'
    )
    print("✅ ML model loaded successfully!")
except Exception as e:
    print(f"⚠️  ML model not loaded: {e}")
    cough_classifier = None

# Update cough recording endpoint
@api_router.post("/cough-record")
async def save_cough_record(data: CoughRecordCreate):
    try:
        severity = 'unknown'
        diagnosis = 'No analysis available'
        
        # Decode audio and run ML prediction
        if data.audioData and cough_classifier:
            try:
                # Decode base64 audio
                audio_bytes = base64.b64decode(data.audioData)
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    temp_file.write(audio_bytes)
                    temp_path = temp_file.name
                
                # ML Prediction
                prediction = cough_classifier.predict(temp_path)
                severity = prediction['severity']
                confidence = prediction['confidence']
                diagnosis = f"ML Analysis: {severity} (confidence: {confidence:.1%})"
                
                # Clean up temp file
                os.unlink(temp_path)
                
                logger.info(f"ML prediction: {severity} ({confidence:.2f})")
                
            except Exception as e:
                logger.error(f"ML prediction error: {e}")
                severity = 'error'
                diagnosis = f"Analysis failed: {str(e)}"
        
        # Save to Firestore
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'severity': severity,
            'coughType': data.coughType or 'unknown',
            'diagnosis': diagnosis,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        db.collection('cough_records').document(record['id']).set(record)
        
        logger.info(f"Cough record saved: {severity}")
        
        return {
            'success': True,
            'message': 'Cough analysis complete',
            'data': record
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Afternoon (2-3 hours)

#### 4. Test Backend ML Integration (1 hour)
```bash
# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Should see:
# ✅ Firebase connected successfully!
# ✅ ML model loaded successfully!
```

Test with curl (create a test audio file first):
```bash
# Convert test audio to base64
BASE64_AUDIO=$(base64 -i test_cough.wav)

# Test API
curl -X POST http://localhost:8001/api/cough-record \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"test-user\",
    \"audioData\": \"$BASE64_AUDIO\",
    \"coughType\": \"dry\"
  }"
```

#### 5. Update Mobile App (30 mins)
Frontend already has the cough recording functionality. Just test it!

The existing code in `home.tsx` will automatically:
- Record audio
- Convert to base64
- Send to backend
- Display ML results

#### 6. End-to-End Testing (1 hour)
- [ ] Open app on Android Emulator
- [ ] Click "Record Cough"
- [ ] Record a cough sound (or any sound for testing)
- [ ] Click "Save"
- [ ] Verify alert shows ML analysis results
- [ ] Check Firebase to confirm data saved
- [ ] Check backend logs for ML prediction

### Evening (1 hour)

#### 7. Fine-tuning (if needed)
If accuracy is lower than expected:
- Adjust confidence threshold
- Add more preprocessing
- Collect more training data

#### 8. Documentation
- Document model performance
- Note any limitations
- Create user guide

### Day 2 Checklist
✅ Backend has ML integration  
✅ ML model loads successfully  
✅ Cough recording → ML analysis working  
✅ Results displayed in app  
✅ Data saved to Firebase  

---

## 📊 Success Metrics

### Model Performance
- ✅ Accuracy: >85%
- ✅ Model size: <5MB
- ✅ Inference time: <2 seconds

### Integration
- ✅ Backend loads model without errors
- ✅ App displays ML predictions
- ✅ Firebase stores results
- ✅ End-to-end flow works

---

## 🚨 Common Issues & Solutions

### Issue 1: Dataset Download Slow
**Solution**: Use smaller subset (~1000 samples per class)

### Issue 2: Low Accuracy (<80%)
**Solution**: 
- Check label distribution (balanced?)
- Increase training epochs
- Try data augmentation

### Issue 3: TFLite Model Too Large (>10MB)
**Solution**: Already optimized with float16

### Issue 4: Backend Can't Load Model
**Solution**:
```bash
pip install tensorflow librosa
# Check file paths
ls -la models/
```

### Issue 5: Audio Format Issues
**Solution**: Convert all audio to .wav format first
```python
from pydub import AudioSegment
audio = AudioSegment.from_file(file_path)
audio.export("output.wav", format="wav")
```

---

## 📁 Required Files at End of Day 2

```
backend/
├── models/
│   ├── cough_classifier.tflite    ← From Colab
│   └── model_info.json            ← From Colab
├── ml_model.py                     ← Created Day 2
├── server.py                       ← Updated Day 2
├── firebase-key.json              ← Already have
└── requirements.txt               ← Updated with ML deps
```

---

## ⏱️ Time Breakdown

| Task | Time | Day |
|------|------|-----|
| Colab setup + dataset download | 1 hour | 1 |
| Data preprocessing | 1 hour | 1 |
| Model training | 1 hour | 1 |
| Model evaluation + export | 1 hour | 1 |
| Backend ML integration | 2 hours | 2 |
| Testing & debugging | 2 hours | 2 |
| **Total** | **8 hours** | **2 days** |

---

## 🎉 Final Result

You'll have:
1. ✅ Trained ML model classifying cough as Healthy/Mild/Severe
2. ✅ TFLite model optimized for mobile
3. ✅ Backend API with ML predictions
4. ✅ Mobile app showing real-time analysis
5. ✅ All data saved to Firebase

**Good luck! You've got this! 🚀**

---

## 📞 Next Steps After Completion

1. Test with real cough recordings
2. Gather user feedback
3. Collect more data for model improvement
4. Add symptom detection (wheezing, dyspnea, etc.)
5. Deploy to production
