# Enhanced Model Architecture for Multi-Feature Classification
# Replace Step 7 in your notebook with this

# OPTION 1: Simple Dense Network (Fastest, ~150 features)
def build_dense_model(input_dim, num_classes=3):
    """
    Dense neural network for feature vector classification
    Works well with comprehensive acoustic features
    """
    model = keras.Sequential([
        keras.layers.Dense(256, activation='relu', input_dim=input_dim),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.5),
        
        keras.layers.Dense(128, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.4),
        
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.3),
        
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


# OPTION 2: 1D CNN for Feature Patterns (Better, learns feature relationships)
def build_1d_cnn_model(input_dim, num_classes=3):
    """
    1D CNN that can learn patterns in the feature sequence
    """
    model = keras.Sequential([
        keras.layers.Reshape((input_dim, 1), input_shape=(input_dim,)),
        
        keras.layers.Conv1D(64, 3, activation='relu', padding='same'),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling1D(2),
        keras.layers.Dropout(0.3),
        
        keras.layers.Conv1D(128, 3, activation='relu', padding='same'),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling1D(2),
        keras.layers.Dropout(0.3),
        
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


# OPTION 3: Hybrid Model (Best, combines both approaches)
def build_hybrid_model(input_dim, num_classes=3):
    """
    Hybrid model combining 1D CNN and dense layers
    """
    inputs = keras.Input(shape=(input_dim,))
    
    # Branch 1: 1D CNN
    x1 = keras.layers.Reshape((input_dim, 1))(inputs)
    x1 = keras.layers.Conv1D(64, 3, activation='relu', padding='same')(x1)
    x1 = keras.layers.BatchNormalization()(x1)
    x1 = keras.layers.MaxPooling1D(2)(x1)
    x1 = keras.layers.Conv1D(128, 3, activation='relu', padding='same')(x1)
    x1 = keras.layers.BatchNormalization()(x1)
    x1 = keras.layers.GlobalMaxPooling1D()(x1)
    
    # Branch 2: Dense
    x2 = keras.layers.Dense(128, activation='relu')(inputs)
    x2 = keras.layers.BatchNormalization()(x2)
    x2 = keras.layers.Dropout(0.4)(x2)
    
    # Combine branches
    combined = keras.layers.Concatenate()([x1, x2])
    x = keras.layers.Dense(128, activation='relu')(combined)
    x = keras.layers.Dropout(0.5)(x)
    outputs = keras.layers.Dense(num_classes, activation='softmax')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    return model


# ============================================================
# BUILD AND COMPILE MODEL
# ============================================================

# Choose one of the architectures
# For 2-day timeline, I recommend Option 2 (1D CNN)

print("Building 1D CNN model for enhanced features...")
input_dim = X_features_scaled.shape[1]  # Number of features
model = build_1d_cnn_model(input_dim=input_dim, num_classes=3)

# Compile
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
)

print("\nModel architecture:")
model.summary()

print(f"\nInput features: {input_dim}")
print(f"Output classes: 3 (Healthy, Mild, Severe)")


# ============================================================
# DATA PREPARATION
# ============================================================

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = keras.utils.to_categorical(y_encoded)

print(f"\nLabel mapping:")
for i, label in enumerate(label_encoder.classes_):
    count = np.sum(y_encoded == i)
    print(f"  {i}: {label} ({count} samples)")

# Split dataset
X_train, X_temp, y_train, y_temp = train_test_split(
    X_features_scaled, y_categorical, 
    test_size=0.3, random_state=42, stratify=y_encoded
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

print(f"\nTraining set: {X_train.shape}")
print(f"Validation set: {X_val.shape}")
print(f"Test set: {X_test.shape}")


# ============================================================
# TRAINING WITH DATA AUGMENTATION (Optional)
# ============================================================

# Simple data augmentation for features
def augment_features(features, noise_level=0.01):
    """Add small Gaussian noise to features"""
    noise = np.random.normal(0, noise_level, features.shape)
    return features + noise

# Create augmented training data
X_train_augmented = []
y_train_augmented = []

for i in range(len(X_train)):
    # Original sample
    X_train_augmented.append(X_train[i])
    y_train_augmented.append(y_train[i])
    
    # Augmented sample (add noise)
    X_train_augmented.append(augment_features(X_train[i]))
    y_train_augmented.append(y_train[i])

X_train_augmented = np.array(X_train_augmented)
y_train_augmented = np.array(y_train_augmented)

print(f"\nAugmented training set: {X_train_augmented.shape}")
print("✅ Data augmentation complete")


# ============================================================
# CALLBACKS
# ============================================================

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=7,
        min_lr=1e-6,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        'best_cough_model_enhanced.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

print("\n✅ Ready to train!")
print("\nExpected improvements over mel spectrogram only:")
print("  - Previous accuracy: ~32%")
print("  - Expected with enhanced features: 70-90%")
print("  - Training time: 15-25 minutes")
