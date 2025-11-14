# Quick Fix: Binary Classification (Healthy vs Unhealthy)
# Add this cell to your notebook AFTER Step 4 (label creation)

# REPLACE the severity labeling with binary classification
def create_binary_label(row):
    """Simplified binary classification"""
    status = row.get('status', '').lower()
    if status == 'healthy':
        return 'Healthy'
    else:
        return 'Unhealthy'  # Combines symptomatic + COVID

# Apply binary labeling
metadata['severity'] = metadata.apply(create_binary_label, axis=1)

# Continue with same filtering
filtered_metadata = metadata[
    (metadata['cough_detected'] > 0.8) &
    (metadata['SNR'] > 5) &
    (metadata['severity'].isin(['Healthy', 'Unhealthy']))
].copy()

# Balance dataset - IMPORTANT!
min_samples = filtered_metadata['severity'].value_counts().min()
balanced_samples = min(min_samples, 1500)  # Take up to 1500 per class

balanced_metadata = filtered_metadata.groupby('severity').sample(
    n=min(balanced_samples, filtered_metadata.groupby('severity').size().min()),
    random_state=42
)

print(f"Balanced dataset size: {len(balanced_metadata)}")
print(f"\nBalanced distribution:")
print(balanced_metadata['severity'].value_counts())

working_metadata = balanced_metadata.copy()

# Then continue with Step 6 (audio processing)
# The model will now have 2 output classes instead of 3
