# Enhanced Feature Extraction for Cough Classification
# Replace Step 5 in your notebook with this comprehensive feature extraction

import numpy as np
import librosa
from scipy import signal
from scipy.stats import kurtosis, skew

def extract_comprehensive_features(audio, sr, n_mfcc=20, n_mels=128):
    """
    Extract comprehensive acoustic features for cough classification
    
    Features extracted:
    1. MFCCs (Mel-frequency cepstral coefficients)
    2. Mel Spectrogram
    3. Spectral features (centroid, bandwidth, contrast, rolloff)
    4. Zero-crossing rate
    5. Chroma features
    6. Formant frequencies
    7. Energy features (RMS, log energy)
    8. Higher-order statistics (kurtosis, skewness)
    9. Pitch features
    
    Returns:
        Combined feature vector
    """
    
    # 1. MFCCs (20 coefficients) - VERY IMPORTANT for speech/cough
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    mfccs_delta = librosa.feature.delta(mfccs)  # First derivative
    mfccs_delta2 = librosa.feature.delta(mfccs, order=2)  # Second derivative
    
    # 2. Mel Spectrogram
    mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=n_mels)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # 3. Spectral Features
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
    spectral_flatness = librosa.feature.spectral_flatness(y=audio)
    
    # 4. Zero-crossing rate (indicates pitch and noisiness)
    zcr = librosa.feature.zero_crossing_rate(audio)
    
    # 5. Chroma features (pitch class profiles)
    chroma_stft = librosa.feature.chroma_stft(y=audio, sr=sr)
    chroma_cqt = librosa.feature.chroma_cqt(y=audio, sr=sr)
    
    # 6. Energy features
    rms = librosa.feature.rms(y=audio)
    energy = np.array([
        np.sum(audio ** 2) / len(audio)  # Average energy
    ])
    log_energy = np.log(energy + 1e-10)
    
    # 7. Pitch features
    try:
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
        pitch_std = np.std(pitches[pitches > 0]) if np.any(pitches > 0) else 0
    except:
        pitch_mean = 0
        pitch_std = 0
    
    # 8. Higher-order statistics
    audio_kurtosis = kurtosis(audio)
    audio_skewness = skew(audio)
    
    # 9. Formant frequencies (approximate using LPC)
    try:
        # Linear Predictive Coding for formants
        lpc_order = 12
        a = librosa.lpc(audio, order=lpc_order)
        roots = np.roots(a)
        roots = roots[np.imag(roots) >= 0]
        
        # Convert to frequencies
        formants = sorted(np.angle(roots) * (sr / (2 * np.pi)))[:4]  # First 4 formants
        while len(formants) < 4:
            formants.append(0)
    except:
        formants = [0, 0, 0, 0]
    
    # 10. Temporal features
    temporal_centroid = np.sum(np.arange(len(audio)) * np.abs(audio)) / (np.sum(np.abs(audio)) + 1e-10)
    
    # Compute statistics for time-varying features (mean, std, max, min)
    def compute_stats(feature):
        return np.array([
            np.mean(feature),
            np.std(feature),
            np.max(feature),
            np.min(feature)
        ])
    
    # Combine all features
    feature_vector = np.concatenate([
        # MFCCs and derivatives (20 * 3 = 60 values)
        np.mean(mfccs, axis=1),
        np.std(mfccs, axis=1),
        np.mean(mfccs_delta, axis=1),
        np.mean(mfccs_delta2, axis=1),
        
        # Spectral features (7 * 4 = 28 values)
        compute_stats(spectral_centroid),
        compute_stats(spectral_bandwidth),
        compute_stats(spectral_rolloff),
        compute_stats(spectral_flatness),
        np.mean(spectral_contrast, axis=1),  # 7 contrast bands
        
        # Chroma features (12 + 12 = 24 values)
        np.mean(chroma_stft, axis=1),
        np.mean(chroma_cqt, axis=1),
        
        # Zero-crossing rate (4 values)
        compute_stats(zcr),
        
        # Energy features (5 values)
        compute_stats(rms),
        log_energy,
        
        # Pitch features (2 values)
        np.array([pitch_mean, pitch_std]),
        
        # Higher-order statistics (2 values)
        np.array([audio_kurtosis, audio_skewness]),
        
        # Formant frequencies (4 values)
        np.array(formants),
        
        # Temporal features (1 value)
        np.array([temporal_centroid])
    ])
    
    return feature_vector, mel_spec_db  # Return both for visualization


def extract_features_from_audio_file(file_path, target_sr=22050, duration=10):
    """
    Load audio file and extract comprehensive features
    """
    try:
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
        
        # Extract features
        feature_vector, mel_spec = extract_comprehensive_features(audio, sr)
        
        return feature_vector, mel_spec
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None, None


# ============================================================
# USAGE IN YOUR NOTEBOOK
# ============================================================

# REPLACE Step 6 in your notebook with this:

print("Processing audio files with comprehensive feature extraction...")
X_features = []  # Feature vectors
X_spectrograms = []  # Mel spectrograms (for visualization/backup)
y = []
failed = 0

for idx, row in tqdm(working_metadata.iterrows(), total=len(working_metadata)):
    # Get audio file path
    uuid = row['uuid']
    
    # Try different extensions
    audio_file = None
    for ext in ['.wav', '.webm', '.ogg']:
        potential_path = os.path.join(audio_dir, f"{uuid}{ext}")
        if os.path.exists(potential_path):
            audio_file = potential_path
            break
    
    if audio_file is None:
        failed += 1
        continue
    
    # Extract features
    feature_vector, mel_spec = extract_features_from_audio_file(audio_file)
    
    if feature_vector is None:
        failed += 1
        continue
    
    X_features.append(feature_vector)
    X_spectrograms.append(mel_spec)
    y.append(row['severity'])

print(f"\n✅ Processed: {len(X_features)} files")
print(f"❌ Failed: {failed} files")

# Convert to numpy arrays
X_features = np.array(X_features)
X_spectrograms = np.array(X_spectrograms)
y = np.array(y)

print(f"\nFeature vector shape: {X_features.shape}")
print(f"Example: {X_features.shape[1]} features per sample")
print(f"Spectrogram shape: {X_spectrograms.shape}")

# Normalize features (IMPORTANT!)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_features_scaled = scaler.fit_transform(X_features)

print(f"\n✅ Features normalized")

# Save scaler for later use
import joblib
joblib.dump(scaler, 'feature_scaler.pkl')
print("✅ Scaler saved for deployment")
