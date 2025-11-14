"""
ML Model Integration for Cough Classification
Handles TFLite model loading and inference
"""
import tensorflow as tf
import numpy as np
import librosa
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class CoughClassifier:
    def __init__(self, model_path='models/cough_classifier_dummy.tflite', 
                 config_path='models/model_info_dummy.json'):
        """
        Initialize cough classifier with TFLite model
        
        Args:
            model_path: Path to TFLite model file
            config_path: Path to model configuration JSON
        """
        self.model_path = model_path
        self.config_path = config_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.config = None
        
        try:
            # Load TFLite model
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Load configuration
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            logger.info(f"✅ ML Model loaded successfully from {model_path}")
            logger.info(f"   Input shape: {self.input_details[0]['shape']}")
            logger.info(f"   Output shape: {self.output_details[0]['shape']}")
            
            if self.config.get('is_dummy'):
                logger.warning("⚠️  Using DUMMY model - predictions will be random!")
            
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            raise
    
    def extract_comprehensive_features(self, audio, sr):
        """Extract 137 comprehensive acoustic features"""
        from scipy.stats import kurtosis, skew
        
        n_mfcc = 20
        n_mels = 128
        
        # 1. MFCCs and derivatives (80 features)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        mfccs_delta = librosa.feature.delta(mfccs)
        mfccs_delta2 = librosa.feature.delta(mfccs, order=2)
        
        # 2. Spectral features (28 features)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        spectral_flatness = librosa.feature.spectral_flatness(y=audio)
        
        # 3. Zero-crossing rate (4 features)
        zcr = librosa.feature.zero_crossing_rate(audio)
        
        # 4. Chroma features (24 features)
        chroma_stft = librosa.feature.chroma_stft(y=audio, sr=sr)
        chroma_cqt = librosa.feature.chroma_cqt(y=audio, sr=sr)
        
        # 5. Energy features (5 features)
        rms = librosa.feature.rms(y=audio)
        energy = np.sum(audio ** 2) / len(audio)
        log_energy = np.log(energy + 1e-10)
        
        # 6. Pitch features (2 features)
        try:
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            pitch_std = np.std(pitches[pitches > 0]) if np.any(pitches > 0) else 0
        except:
            pitch_mean = 0
            pitch_std = 0
        
        # 7. Higher-order statistics (2 features)
        audio_kurtosis = kurtosis(audio)
        audio_skewness = skew(audio)
        
        # 8. Formant frequencies (4 features)
        try:
            lpc_order = 12
            a = librosa.lpc(audio, order=lpc_order)
            roots = np.roots(a)
            roots = roots[np.imag(roots) >= 0]
            formants = sorted(np.angle(roots) * (sr / (2 * np.pi)))[:4]
            while len(formants) < 4:
                formants.append(0)
        except:
            formants = [0, 0, 0, 0]
        
        # 9. Temporal features (1 feature)
        temporal_centroid = np.sum(np.arange(len(audio)) * np.abs(audio)) / (np.sum(np.abs(audio)) + 1e-10)
        
        # Compute statistics for time-varying features
        def compute_stats(feature):
            return np.array([
                np.mean(feature),
                np.std(feature),
                np.max(feature),
                np.min(feature)
            ])
        
        # Combine all features (137 total)
        feature_vector = np.concatenate([
            np.mean(mfccs, axis=1),  # 20
            np.std(mfccs, axis=1),  # 20
            np.mean(mfccs_delta, axis=1),  # 20
            np.mean(mfccs_delta2, axis=1),  # 20
            compute_stats(spectral_centroid),  # 4
            compute_stats(spectral_bandwidth),  # 4
            compute_stats(spectral_rolloff),  # 4
            compute_stats(spectral_flatness),  # 4
            np.mean(spectral_contrast, axis=1),  # 7
            np.mean(chroma_stft, axis=1),  # 12
            np.mean(chroma_cqt, axis=1),  # 12
            compute_stats(zcr),  # 4
            compute_stats(rms),  # 4
            np.array([log_energy]),  # 1
            np.array([pitch_mean, pitch_std]),  # 2
            np.array([audio_kurtosis, audio_skewness]),  # 2
            np.array(formants),  # 4
            np.array([temporal_centroid])  # 1
        ])
        
        return feature_vector
    
    def preprocess_audio(self, audio_path):
        """
        Preprocess audio file for model input
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Preprocessed features ready for inference
        """
        try:
            # Get config parameters
            target_sr = self.config.get('target_sr', 22050)
            duration = self.config.get('duration', 10)
            
            # Check if model expects features or spectrogram
            expected_shape = self.input_details[0]['shape']
            num_dims = len(expected_shape)
            
            logger.info(f"Model expects {num_dims}D input with shape: {expected_shape}")
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=target_sr, duration=duration)
            audio = librosa.util.normalize(audio)
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Pad or truncate to fixed length
            target_length = target_sr * duration
            if len(audio) < target_length:
                audio = np.pad(audio, (0, target_length - len(audio)))
            else:
                audio = audio[:target_length]
            
            # Extract features based on model type
            if num_dims == 2:
                # Enhanced features model (batch, features)
                logger.info("Extracting enhanced features (137 features)")
                feature_vector = self.extract_comprehensive_features(audio, sr)
                
                # Load scaler if available
                scaler_path = self.config.get('scaler_path', 'models/feature_scaler.pkl')
                try:
                    import joblib
                    if os.path.exists(scaler_path):
                        scaler = joblib.load(scaler_path)
                        feature_vector = scaler.transform(feature_vector.reshape(1, -1))
                        logger.info("Applied feature scaling")
                    else:
                        # Normalize manually if no scaler
                        feature_vector = (feature_vector - feature_vector.mean()) / (feature_vector.std() + 1e-6)
                        feature_vector = feature_vector.reshape(1, -1)
                except:
                    feature_vector = feature_vector.reshape(1, -1)
                
                logger.info(f"Preprocessed features shape: {feature_vector.shape}")
                return feature_vector.astype(np.float32)
                
            else:
                # Mel spectrogram model (batch, height, width, channels)
                logger.info("Extracting mel spectrogram")
                n_mels = self.config.get('n_mels', 128)
                n_fft = self.config.get('n_fft', 2048)
                hop_length = self.config.get('hop_length', 512)
                
                mel_spec = librosa.feature.melspectrogram(
                    y=audio, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length
                )
                mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
                mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / (mel_spec_db.std() + 1e-6)
                
                # Resize to match expected shape
                expected_time_steps = expected_shape[2]
                if mel_spec_db.shape[1] != expected_time_steps:
                    from scipy.ndimage import zoom
                    zoom_factor = expected_time_steps / mel_spec_db.shape[1]
                    mel_spec_db = zoom(mel_spec_db, (1, zoom_factor), order=1)
                
                mel_spec_db = np.expand_dims(mel_spec_db, axis=-1)
                mel_spec_db = np.expand_dims(mel_spec_db, axis=0)
                
                logger.info(f"Preprocessed spectrogram shape: {mel_spec_db.shape}")
                return mel_spec_db.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            raise
    
    def predict(self, audio_path):
        """
        Predict cough classification from audio file
        
        Args:
            audio_path: Path to audio file (.wav, .mp3, etc.)
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Preprocess audio
            input_data = self.preprocess_audio(audio_path)
            
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # Get results
            predicted_class = int(np.argmax(output_data[0]))
            confidence = float(output_data[0][predicted_class])
            
            label_mapping = self.config.get('label_mapping', {
                '0': 'Healthy',
                '1': 'Mild',
                '2': 'Severe'
            })
            
            severity = label_mapping.get(str(predicted_class), 'Unknown')
            
            result = {
                'severity': severity,
                'confidence': confidence,
                'probabilities': {
                    label_mapping.get(str(i), f'Class{i}'): float(prob)
                    for i, prob in enumerate(output_data[0])
                },
                'is_dummy_model': self.config.get('is_dummy', False)
            }
            
            logger.info(f"Prediction: {severity} (confidence: {confidence:.2%})")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise Exception(f"Prediction failed: {str(e)}")
    
    def test_model(self):
        """Test if model is working with dummy data"""
        try:
            # Create dummy input
            input_shape = self.input_details[0]['shape']
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
            
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], dummy_input)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            logger.info(f"✅ Model test successful. Output shape: {output_data.shape}")
            return True
        except Exception as e:
            logger.error(f"❌ Model test failed: {e}")
            return False


# Test the model loading
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Testing ML Model Integration")
    print("=" * 60)
    
    try:
        # Initialize classifier
        classifier = CoughClassifier()
        
        # Test with dummy data
        if classifier.test_model():
            print("\n✅ ML model integration is working!")
            print(f"\nModel details:")
            print(f"  - Classes: {list(classifier.config['label_mapping'].values())}")
            print(f"  - Input shape: {classifier.input_details[0]['shape']}")
            print(f"  - Is dummy: {classifier.config.get('is_dummy', False)}")
        else:
            print("\n❌ Model test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
