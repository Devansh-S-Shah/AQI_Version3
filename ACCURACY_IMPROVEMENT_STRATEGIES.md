# Accuracy Improvement Strategies
## Current Status: 45-47% Accuracy

Looking at your confusion matrix, the model still has issues distinguishing between classes. Here are targeted strategies to improve:

---

## 🔍 Analysis of Your Results

From the confusion matrix, I can see:
- Model is predicting across all 3 classes (better than before!)
- But still significant confusion between Healthy/Mild/Severe
- **Root causes**: Features may not be discriminative enough OR data quality issues

---

## 🚀 Strategy 1: Feature Selection (Quick - 20 mins)

Not all 137 features are equally useful. Let's identify the most important ones.

### Add to Colab Notebook (After feature extraction):

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt

# Train a quick Random Forest to get feature importances
print("Finding most important features...")
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_features_scaled, y_encoded)

# Get feature importances
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]

# Plot top 30 features
plt.figure(figsize=(12, 8))
plt.title('Top 30 Most Important Features')
plt.bar(range(30), importances[indices[:30]])
plt.xlabel('Feature Index')
plt.ylabel('Importance')
plt.tight_layout()
plt.show()

print("\nTop 20 most important features:")
for i in range(20):
    print(f"{i+1}. Feature {indices[i]}: {importances[indices[i]]:.4f}")

# Select top K features
k = 60  # Keep only 60 most important features
selector = SelectKBest(f_classif, k=k)
X_selected = selector.fit_transform(X_features_scaled, y_encoded)

print(f"\n✅ Reduced from {X_features_scaled.shape[1]} to {X_selected.shape[1]} features")

# Now split and train with selected features
X_train, X_temp, y_train, y_temp = train_test_split(
    X_selected, y_categorical, test_size=0.3, random_state=42, stratify=y_encoded
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)
```

**Expected improvement**: 45% → 60-70%

---

## 🚀 Strategy 2: Better Model Architecture (30 mins)

Try an ensemble approach or deeper network:

### Option A: Random Forest (Classical ML - Sometimes Better!)

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Train Random Forest
print("Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, np.argmax(y_train, axis=1))

# Evaluate
y_pred_rf = rf_model.predict(X_test)
y_test_labels = np.argmax(y_test, axis=1)

accuracy = accuracy_score(y_test_labels, y_pred_rf)
print(f"\nRandom Forest Accuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(classification_report(y_test_labels, y_pred_rf, target_names=label_encoder.classes_))

# Save model
import joblib
joblib.dump(rf_model, 'cough_rf_model.pkl')
print("✅ Random Forest model saved")
```

**Advantages:**
- Often performs better than neural networks on small datasets
- No need for normalization
- Built-in feature importance
- Fast training
- **Can achieve 65-80% accuracy**

### Option B: Deeper Neural Network with Dropout

```python
def build_deeper_model(input_dim, num_classes=3):
    model = keras.Sequential([
        keras.layers.Dense(512, activation='relu', input_dim=input_dim),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.5),
        
        keras.layers.Dense(256, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.4),
        
        keras.layers.Dense(128, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.4),
        
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.3),
        
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    return model

model = build_deeper_model(X_train.shape[1])
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0005),  # Lower LR
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
```

---

## 🚀 Strategy 3: Data Augmentation (15 mins)

Enhance training with more variations:

```python
def advanced_augmentation(features, num_augmented=3):
    """Create multiple augmented versions of each sample"""
    augmented = [features]  # Original
    
    for _ in range(num_augmented):
        # Add Gaussian noise
        noise = np.random.normal(0, 0.02, features.shape)
        augmented.append(features + noise)
        
        # Scale features slightly
        scale = np.random.uniform(0.95, 1.05, features.shape)
        augmented.append(features * scale)
        
        # Small random perturbations
        mask = np.random.rand(*features.shape) < 0.1
        perturbed = features.copy()
        perturbed[mask] += np.random.normal(0, 0.05, np.sum(mask))
        augmented.append(perturbed)
    
    return np.array(augmented)

# Apply to training data
print("Augmenting training data...")
X_train_aug = []
y_train_aug = []

for i in range(len(X_train)):
    augs = advanced_augmentation(X_train[i], num_augmented=2)
    for aug in augs:
        X_train_aug.append(aug)
        y_train_aug.append(y_train[i])

X_train_aug = np.array(X_train_aug)
y_train_aug = np.array(y_train_aug)

print(f"Training set size: {len(X_train)} → {len(X_train_aug)} (after augmentation)")
```

**Expected improvement**: +5-10% accuracy

---

## 🚀 Strategy 4: Binary Classification (Practical - 30 mins)

Since 3-class classification is hard, try 2 classes:

### Approach A: Healthy vs Unhealthy

```python
# Combine Mild + Severe → Unhealthy
def create_binary_labels(y_original):
    y_binary = []
    for label in y_original:
        if label == 'Healthy':
            y_binary.append('Healthy')
        else:
            y_binary.append('Unhealthy')
    return np.array(y_binary)

y_binary = create_binary_labels(y)

# Re-encode
label_encoder_binary = LabelEncoder()
y_binary_encoded = label_encoder_binary.fit_transform(y_binary)
y_binary_categorical = keras.utils.to_categorical(y_binary_encoded)

print(f"Binary distribution:")
print(pd.Series(y_binary).value_counts())

# Train binary model (will be faster and more accurate)
```

**Expected accuracy**: 75-90% (much easier problem!)

### Approach B: Two-Stage Classification

1. **Stage 1**: Healthy vs Not Healthy (90% accuracy)
2. **Stage 2**: If Not Healthy → Mild vs Severe (70% accuracy)

```python
# Train two separate models
model_stage1 = build_model(input_dim, num_classes=2)  # Healthy/Unhealthy
model_stage2 = build_model(input_dim, num_classes=2)  # Mild/Severe

# Filter data for stage 2 (only Mild + Severe samples)
mask_unhealthy = (y != 'Healthy')
X_stage2 = X_features_scaled[mask_unhealthy]
y_stage2 = y[mask_unhealthy]

# Train both models separately
```

**Expected overall accuracy**: ~80%

---

## 🚀 Strategy 5: Check Data Quality (10 mins)

The COUGHVID dataset might have noisy labels. Let's verify:

```python
# Check if model is actually learning patterns
from sklearn.model_selection import cross_val_score

# 5-fold cross-validation
print("Performing cross-validation...")
rf_cv = RandomForestClassifier(n_estimators=100, random_state=42)
cv_scores = cross_val_score(rf_cv, X_features_scaled, y_encoded, cv=5, n_jobs=-1)

print(f"\nCross-validation scores: {cv_scores}")
print(f"Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std()*2:.2%})")

if cv_scores.mean() < 0.5:
    print("\n⚠️  WARNING: Low CV score suggests:")
    print("  1. Features are not discriminative enough")
    print("  2. Labels might be noisy in the dataset")
    print("  3. Classes might not be separable with current features")
    print("\n→ Recommendation: Try binary classification (Healthy vs Unhealthy)")
```

---

## 🚀 Strategy 6: Transfer Learning (Advanced - 60 mins)

Use pre-trained audio models:

```python
# YAMNet or VGGish for audio
# These models are pre-trained on AudioSet (millions of audio samples)

# Install
!pip install tensorflow-hub

import tensorflow_hub as hub

# Load pre-trained model
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

def extract_yamnet_features(audio, sr=16000):
    """Extract embeddings from YAMNet"""
    # YAMNet expects 16kHz
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    
    # Get embeddings
    scores, embeddings, spectrogram = yamnet_model(audio)
    
    # Use mean of embeddings as features
    features = np.mean(embeddings.numpy(), axis=0)
    return features  # 1024-dimensional vector

# Extract YAMNet features for all samples
# Then train classifier on top
```

**Expected accuracy**: 70-85%

---

## 📊 Quick Comparison of Strategies

| Strategy | Time | Expected Accuracy | Complexity | Recommended |
|----------|------|-------------------|------------|-------------|
| Feature Selection | 20 min | 60-70% | Low | ✅ Yes |
| Random Forest | 30 min | 65-80% | Low | ✅ Yes |
| Binary Classification | 30 min | 75-90% | Low | ✅ **Highly Recommended** |
| Data Augmentation | 15 min | +5-10% | Medium | ✅ Yes |
| Deeper Network | 30 min | 50-65% | Medium | Maybe |
| Two-Stage | 45 min | ~80% | Medium | Yes |
| Transfer Learning | 60 min | 70-85% | High | If time permits |

---

## 🎯 Recommended Action Plan (1-2 hours)

### For Tomorrow (High Priority):

1. **Try Feature Selection** (20 min)
   - Reduce to 60 best features
   - Retrain model

2. **Try Random Forest** (30 min)
   - Often outperforms neural networks
   - Much simpler to deploy

3. **Switch to Binary Classification** (30 min)
   - Healthy vs Unhealthy
   - Much more practical
   - 75-90% accuracy achievable

### If Time Permits:

4. **Data Augmentation** (15 min)
   - Add to any approach above
   - Easy boost

5. **Two-Stage Classification** (45 min)
   - Best of both worlds
   - More complex but better accuracy

---

## 🔧 Practical Considerations

### For Demo/MVP:
- **Use Binary Classification** (Healthy vs Unhealthy)
- **OR Use Random Forest** with current features
- Both are simple and give 70-80% accuracy

### For Production:
- Feature Selection + Deep Learning
- Two-Stage Classification
- Transfer Learning with YAMNet

---

## 📝 Example: Quick Binary Classification Implementation

```python
# Complete code for binary classification

# 1. Create binary labels
def to_binary(label):
    return 'Healthy' if label == 'Healthy' else 'Unhealthy'

y_binary = np.array([to_binary(label) for label in y])

# 2. Encode
le = LabelEncoder()
y_bin_encoded = le.fit_transform(y_binary)
y_bin_cat = keras.utils.to_categorical(y_bin_encoded)

# 3. Split
X_train, X_temp, y_train, y_temp = train_test_split(
    X_features_scaled, y_bin_cat, test_size=0.3, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# 4. Build and train
model_binary = build_1d_cnn_model(input_dim=X_train.shape[1], num_classes=2)
model_binary.compile(
    optimizer=keras.optimizers.Adam(0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history = model_binary.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=callbacks
)

# 5. Evaluate
y_pred = np.argmax(model_binary.predict(X_test), axis=1)
y_true = np.argmax(y_test, axis=1)

accuracy = accuracy_score(y_true, y_pred)
print(f"\n✅ Binary Classification Accuracy: {accuracy:.2%}")
print(classification_report(y_true, y_pred, target_names=['Healthy', 'Unhealthy']))

# Expected: 75-90% accuracy!
```

---

## ✅ Summary

**Current**: 45% accuracy with 3 classes
**Target**: 70-90% accuracy

**Best Quick Fixes**:
1. ✅ Binary Classification (Healthy vs Unhealthy) - **EASIEST & MOST PRACTICAL**
2. ✅ Random Forest Classifier - **SIMPLE & EFFECTIVE**
3. ✅ Feature Selection + Current Model - **QUICK IMPROVEMENT**

**For Better Results**:
- Two-stage classification
- Transfer learning
- More data

**Recommendation for 2-day deadline:**
→ **Go with Binary Classification**
→ Achievable 75-90% accuracy
→ More practical use case
→ Faster training
→ Simpler to explain

Good luck! 🚀
