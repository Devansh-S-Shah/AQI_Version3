# Quick Fix: Add Class Weights to Handle Imbalance
# Add this to your notebook in Step 8 (training)

from sklearn.utils.class_weight import compute_class_weight

# Compute class weights
class_weights_array = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(np.argmax(y_train, axis=1)),
    y=np.argmax(y_train, axis=1)
)

class_weights = {i: weight for i, weight in enumerate(class_weights_array)}

print("Class weights:", class_weights)
# Example output: {0: 1.5, 1: 2.5, 2: 0.7}
# Higher weights for underrepresented classes

# Update training with class weights
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=callbacks,
    class_weight=class_weights,  # ADD THIS LINE
    verbose=1
)

print("\n✅ Training with class weights to handle imbalance!")
