# Quick Diagnostic Checks for Low Model Accuracy
# Add these cells to your notebook BEFORE continuing to Step 9

# Cell 1: Check label distribution in training data
print("=" * 50)
print("DIAGNOSTIC CHECK 1: Label Distribution")
print("=" * 50)
import numpy as np

y_train_labels = np.argmax(y_train, axis=1)
unique, counts = np.unique(y_train_labels, axis=0, return_counts=True)

print("\nTraining set distribution:")
for label_idx, count in zip(unique, counts):
    label_name = label_encoder.classes_[label_idx]
    percentage = (count / len(y_train_labels)) * 100
    print(f"  {label_name}: {count} samples ({percentage:.1f}%)")

print("\nClass balance check:")
if max(counts) / min(counts) > 2:
    print("⚠️  WARNING: Significant class imbalance detected!")
else:
    print("✅ Classes are reasonably balanced")

# Cell 2: Check if model is predicting anything
print("\n" + "=" * 50)
print("DIAGNOSTIC CHECK 2: Model Predictions")
print("=" * 50)

# Get predictions on a small sample
sample_predictions = model.predict(X_train[:100])
predicted_classes = np.argmax(sample_predictions, axis=1)

print("\nFirst 20 predictions:")
print(predicted_classes[:20])

unique_preds, pred_counts = np.unique(predicted_classes, return_counts=True)
print("\nPrediction distribution on 100 samples:")
for pred_idx, count in zip(unique_preds, pred_counts):
    print(f"  Class {pred_idx} ({label_encoder.classes_[pred_idx]}): {count} predictions")

if len(unique_preds) == 1:
    print("❌ ERROR: Model is only predicting ONE class! This is the problem.")
elif len(unique_preds) == 2:
    print("⚠️  WARNING: Model is only predicting TWO classes")
else:
    print("✅ Model is predicting all classes")

# Cell 3: Check a few samples to ensure data is correct
print("\n" + "=" * 50)
print("DIAGNOSTIC CHECK 3: Data Sanity Check")
print("=" * 50)

print(f"\nFeature shape: {X_train[0].shape}")
print(f"Feature min: {X_train[0].min():.2f}")
print(f"Feature max: {X_train[0].max():.2f}")
print(f"Feature mean: {X_train[0].mean():.2f}")
print(f"Feature std: {X_train[0].std():.2f}")

if np.isnan(X_train).any():
    print("❌ ERROR: NaN values found in features!")
else:
    print("✅ No NaN values in features")

if np.isinf(X_train).any():
    print("❌ ERROR: Infinite values found in features!")
else:
    print("✅ No infinite values in features")

# Cell 4: Visualize some spectrograms with labels
print("\n" + "=" * 50)
print("DIAGNOSTIC CHECK 4: Visualize Samples")
print("=" * 50)

import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for i in range(6):
    idx = np.random.randint(0, len(X_train))
    spec = X_train[idx][:, :, 0]  # Remove channel dimension
    true_label = label_encoder.classes_[np.argmax(y_train[idx])]
    
    axes[i].imshow(spec, aspect='auto', origin='lower', cmap='viridis')
    axes[i].set_title(f'Sample {i+1}: {true_label}')
    axes[i].axis('off')

plt.tight_layout()
plt.show()

print("\n✅ Check if spectrograms look reasonable")
print("   - Should show patterns (not uniform noise)")
print("   - Different samples should look different")

# Cell 5: Print recommendations
print("\n" + "=" * 50)
print("RECOMMENDATIONS")
print("=" * 50)
print("""
Based on the diagnostics above:

1. If model predicts only ONE class:
   → Problem: Severe class imbalance or labeling issue
   → Solution: Check label creation logic in Step 4

2. If spectrograms look uniform/empty:
   → Problem: Audio preprocessing issue
   → Solution: Check audio file loading

3. If labels seem wrong:
   → Problem: Label mapping issue
   → Solution: Verify severity label creation

4. If data looks fine but accuracy is low:
   → Solution: Try simpler 2-class problem (Healthy vs Not Healthy)
   → Or collect better quality samples
""")
