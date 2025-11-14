from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging
from pathlib import Path
import bcrypt
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize ML Model for Cough Classification
cough_classifier = None
try:
    from ml_model import CoughClassifier
    cough_classifier = CoughClassifier(
        model_path='models/cough_classifier_dummy.tflite',
        config_path='models/model_info_dummy.json'
    )
    logger.info("✅ ML Cough Classifier loaded successfully!")
except Exception as e:
    logger.warning(f"⚠️  ML model not loaded: {e}")
    logger.warning("Cough analysis will use placeholder values")

# In-memory storage (will be replaced with Firebase)
# For now, we'll use simple dictionaries to store data
users_db: Dict[str, Any] = {}
sensor_data_db: List[Dict[str, Any]] = []
cough_records_db: List[Dict[str, Any]] = []
oxygen_records_db: List[Dict[str, Any]] = []

# ==================== Models ====================

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class SensorReadings(BaseModel):
    co: float
    hazardousGas: float
    temperature: float
    humidity: float
    airQuality: float
    pm10: float

class SensorDataCreate(BaseModel):
    userId: str
    readings: SensorReadings
    aqi: int
    location: Optional[Dict[str, float]] = None

class CoughRecordCreate(BaseModel):
    userId: str
    audioData: Optional[str] = None  # base64 encoded audio
    severity: str
    coughType: Optional[str] = None
    diagnosis: Optional[str] = None

class OxygenLevelCreate(BaseModel):
    userId: str
    oxygenLevel: float
    timestamp: Optional[str] = None

# ==================== Authentication Routes ====================

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Check if user already exists
        if user_data.username in users_db:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            user_data.password.encode('utf-8'), 
            bcrypt.gensalt()
        )
        
        # Create user
        user_id = str(uuid.uuid4())
        users_db[user_data.username] = {
            'id': user_id,
            'username': user_data.username,
            'password': hashed_password,
            'created_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"User registered: {user_data.username}")
        
        return {
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'username': user_data.username
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    """Login user"""
    try:
        # Check if user exists
        if user_data.username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = users_db[user_data.username]
        
        # Verify password
        if not bcrypt.checkpw(
            user_data.password.encode('utf-8'), 
            user['password']
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"User logged in: {user_data.username}")
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# ==================== Sensor Data Routes ====================

@api_router.post("/sensor-data")
async def save_sensor_data(data: SensorDataCreate):
    """Save sensor data and AQI reading"""
    try:
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'readings': data.readings.dict(),
            'aqi': data.aqi,
            'location': data.location,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        sensor_data_db.append(record)
        
        logger.info(f"Sensor data saved for user: {data.userId}, AQI: {data.aqi}")
        
        return {
            'success': True,
            'message': 'Sensor data saved successfully',
            'data': record
        }
    except Exception as e:
        logger.error(f"Error saving sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save sensor data")

@api_router.get("/sensor-data/{user_id}")
async def get_sensor_data(user_id: str):
    """Get all sensor data for a user"""
    try:
        user_data = [
            record for record in sensor_data_db 
            if record['userId'] == user_id
        ]
        
        return {
            'success': True,
            'data': user_data
        }
    except Exception as e:
        logger.error(f"Error fetching sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sensor data")

# ==================== Cough Recording Routes ====================

@api_router.post("/cough-record")
async def save_cough_record(data: CoughRecordCreate):
    """Save cough recording and perform ML analysis"""
    import base64
    import tempfile
    
    severity = 'unknown'
    diagnosis = 'No analysis available'
    confidence = 0.0
    
    try:
        # Decode audio and run ML prediction
        if data.audioData and cough_classifier:
            try:
                # Clean and decode base64 audio
                # Remove data URI prefix if present (e.g., "data:audio/wav;base64,")
                audio_data = data.audioData
                if ',' in audio_data:
                    audio_data = audio_data.split(',')[1]
                
                # Add padding if needed
                missing_padding = len(audio_data) % 4
                if missing_padding:
                    audio_data += '=' * (4 - missing_padding)
                
                # Decode base64
                audio_bytes = base64.b64decode(audio_data)
                logger.info(f"Decoded audio: {len(audio_bytes)} bytes")
                
                # Check if audio data is too small (likely invalid)
                if len(audio_bytes) < 1000:  # Minimum reasonable audio size
                    raise Exception(f"Audio data too small ({len(audio_bytes)} bytes). Recording might have failed.")
                
                # Save to temporary file (expo-av typically produces m4a/caf format)
                # Try different extensions to help librosa identify format
                with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a', mode='wb') as temp_file:
                    temp_file.write(audio_bytes)
                    temp_path = temp_file.name
                
                logger.info(f"Saved temp audio file: {temp_path} ({len(audio_bytes)} bytes)")
                
                # Run ML Prediction
                prediction = cough_classifier.predict(temp_path)
                severity = prediction['severity']
                confidence = prediction['confidence']
                
                # Build diagnosis message
                diagnosis = f"ML Analysis: {severity}"
                if prediction.get('is_dummy_model'):
                    diagnosis += " (⚠️ DUMMY MODEL - Random prediction for testing)"
                else:
                    diagnosis += f" (Confidence: {confidence:.1%})"
                
                # Clean up temp file
                import os
                os.unlink(temp_path)
                
                logger.info(f"✅ ML prediction: {severity} (confidence: {confidence:.2%})")
                
            except Exception as e:
                import traceback
                logger.error(f"ML prediction error: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                severity = data.severity or 'error'
                diagnosis = f"Analysis failed: {str(e)}"
        else:
            # No ML model or no audio data
            severity = data.severity or 'unknown'
            diagnosis = data.diagnosis or 'No ML analysis available'
        
        # Save record
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'audioData': None,  # Don't store full audio in memory
            'severity': severity,
            'coughType': data.coughType or 'dry',
            'diagnosis': diagnosis,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        cough_records_db.append(record)
        
        logger.info(f"Cough record saved: {severity} for user {data.userId}")
        
        return {
            'success': True,
            'message': 'Cough analysis complete',
            'data': record
        }
    except Exception as e:
        logger.error(f"Error saving cough record: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/cough-records/{user_id}")
async def get_cough_records(user_id: str):
    """Get all cough records for a user"""
    try:
        user_records = [
            record for record in cough_records_db 
            if record['userId'] == user_id
        ]
        
        return {
            'success': True,
            'data': user_records
        }
    except Exception as e:
        logger.error(f"Error fetching cough records: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cough records")

# ==================== Oxygen Level Routes ====================

@api_router.post("/oxygen-level")
async def save_oxygen_level(data: OxygenLevelCreate):
    """Save oxygen level reading"""
    try:
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'oxygenLevel': data.oxygenLevel,
            'timestamp': data.timestamp or datetime.utcnow().isoformat()
        }
        
        oxygen_records_db.append(record)
        
        logger.info(f"Oxygen level saved for user: {data.userId}, Level: {data.oxygenLevel}%")
        
        return {
            'success': True,
            'message': 'Oxygen level saved successfully',
            'data': record
        }
    except Exception as e:
        logger.error(f"Error saving oxygen level: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save oxygen level")

@api_router.get("/oxygen-levels/{user_id}")
async def get_oxygen_levels(user_id: str):
    """Get all oxygen level readings for a user"""
    try:
        user_records = [
            record for record in oxygen_records_db 
            if record['userId'] == user_id
        ]
        
        return {
            'success': True,
            'data': user_records
        }
    except Exception as e:
        logger.error(f"Error fetching oxygen levels: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch oxygen levels")

# ==================== History Routes ====================

@api_router.get("/history/{user_id}")
async def get_user_history(user_id: str):
    """Get complete history for a user"""
    try:
        # Get all sensor data (AQI readings)
        history = [
            {
                '_id': record['id'],
                'userId': record['userId'],
                'aqi': record['aqi'],
                'timestamp': record['timestamp'],
                'location': record.get('location')
            }
            for record in sensor_data_db 
            if record['userId'] == user_id
        ]
        
        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'success': True,
            'history': history
        }
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

# ==================== Heat Map Routes ====================

@api_router.get("/heatmap-data")
async def get_heatmap_data():
    """Get all AQI readings for heat map"""
    try:
        # Get all sensor data with location
        heatmap_data = [
            {
                'latitude': record['location']['latitude'],
                'longitude': record['location']['longitude'],
                'aqi': record['aqi'],
                'timestamp': record['timestamp']
            }
            for record in sensor_data_db 
            if record.get('location')
        ]
        
        return {
            'success': True,
            'data': heatmap_data
        }
    except Exception as e:
        logger.error(f"Error fetching heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch heatmap data")

# ==================== Health Check ====================

@api_router.get("/")
async def root():
    return {
        "message": "Air Quality Monitoring API",
        "version": "1.0.0",
        "status": "running"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "users_count": len(users_db),
        "sensor_readings_count": len(sensor_data_db),
        "cough_records_count": len(cough_records_db),
        "oxygen_records_count": len(oxygen_records_db)
    }

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
