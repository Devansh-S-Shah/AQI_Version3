"""
ML Model Integration for Cough Classification
Handles TFLite model loading and inference
"""
import tensorflow as tf
import numpy as np
import librosa
import json
import logging
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
    
    def preprocess_audio(self, audio_path):
        """
        Preprocess audio file for model input
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Preprocessed mel spectrogram ready for inference
        """
        try:
            # Get config parameters
            target_sr = self.config.get('target_sr', 22050)
            duration = self.config.get('duration', 10)
            n_mels = self.config.get('n_mels', 128)
            n_fft = self.config.get('n_fft', 2048)
            hop_length = self.config.get('hop_length', 512)
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=target_sr, duration=duration)
            
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
            
            # Extract mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=sr,
                n_mels=n_mels,
                n_fft=n_fft,
                hop_length=hop_length
            )
            
            # Convert to log scale (dB)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Normalize
            mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / (mel_spec_db.std() + 1e-6)
            
            # Get expected input shape from model
            expected_shape = self.input_details[0]['shape']
            expected_time_steps = expected_shape[2]  # Usually 216
            
            # Resize time dimension if needed
            if mel_spec_db.shape[1] != expected_time_steps:
                from scipy.ndimage import zoom
                zoom_factor = expected_time_steps / mel_spec_db.shape[1]
                mel_spec_db = zoom(mel_spec_db, (1, zoom_factor), order=1)
                logger.info(f"Resized spectrogram from {mel_spec.shape[1]} to {mel_spec_db.shape[1]} time steps")
            
            # Add dimensions for model input [batch, height, width, channels]
            mel_spec_db = np.expand_dims(mel_spec_db, axis=-1)  # Add channel dim
            mel_spec_db = np.expand_dims(mel_spec_db, axis=0)   # Add batch dim
            
            logger.info(f"Preprocessed audio shape: {mel_spec_db.shape}")
            
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
