from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import uuid
import bcrypt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Air Quality Monitor API")
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    cred = credentials.Certificate('firebase-key.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("✅ Firebase connected successfully!")
except Exception as e:
    logger.warning(f"⚠️  Firebase not configured: {e}")
    logger.warning("Using in-memory storage as fallback")
    # Fallback to in-memory storage
    users_db: Dict[str, Any] = {}
    sensor_data_db: List[Dict[str, Any]] = []
    cough_records_db: List[Dict[str, Any]] = []
    oxygen_records_db: List[Dict[str, Any]] = []

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

# Pydantic models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class SensorDataCreate(BaseModel):
    userId: str
    readings: Dict[str, Any]
    aqi: int
    location: Dict[str, float]

class CoughRecordCreate(BaseModel):
    userId: str
    audioData: Optional[str] = None
    severity: Optional[str] = None
    coughType: Optional[str] = None
    diagnosis: Optional[str] = None

class OxygenLevelCreate(BaseModel):
    userId: str
    level: float
    timestamp: Optional[str] = None

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "firebase_connected": db is not None,
        "ml_model_loaded": cough_classifier is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@api_router.post("/auth/register")
async def register_user(user_data: UserRegister):
    """Register a new user"""
    try:
        # Hash password
        hashed_password = bcrypt.hashpw(
            user_data.password.encode('utf-8'),
            bcrypt.gensalt()
        )
        
        user_id = str(uuid.uuid4())
        user_doc = {
            'id': user_id,
            'username': user_data.username,
            'password': hashed_password.decode('utf-8'),
            'createdAt': datetime.utcnow().isoformat()
        }
        
        if db:
            # Firebase storage
            # Check if user already exists
            users_ref = db.collection('users')
            existing = users_ref.where('username', '==', user_data.username).limit(1).get()
            
            if len(list(existing)) > 0:
                raise HTTPException(status_code=400, detail="Username already exists")
            
            users_ref.document(user_id).set(user_doc)
            logger.info(f"User registered in Firebase: {user_data.username}")
        else:
            # In-memory storage
            if user_data.username in users_db:
                raise HTTPException(status_code=400, detail="Username already exists")
            users_db[user_data.username] = user_doc
            logger.info(f"User registered in memory: {user_data.username}")
        
        return {
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'username': user_data.username
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@api_router.post("/auth/login")
async def login_user(user_data: UserLogin):
    """Login user"""
    try:
        if db:
            # Firebase storage
            users_ref = db.collection('users')
            user_docs = users_ref.where('username', '==', user_data.username).limit(1).get()
            user_list = list(user_docs)
            
            if not user_list:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            user = user_list[0].to_dict()
        else:
            # In-memory storage
            if user_data.username not in users_db:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            user = users_db[user_data.username]
        
        # Verify password
        if not bcrypt.checkpw(
            user_data.password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"User logged in: {user_data.username}")
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username']
            },
            'token': 'dummy-jwt-token'
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# Sensor data endpoints
@api_router.post("/sensor-data")
async def save_sensor_data(data: SensorDataCreate):
    """Save sensor readings and AQI"""
    try:
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'readings': data.readings,
            'aqi': data.aqi,
            'location': data.location,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if db:
            # Firebase storage
            db.collection('sensor_data').document(record['id']).set(record)
            logger.info(f"Sensor data saved to Firebase: AQI {data.aqi}")
        else:
            # In-memory storage
            sensor_data_db.append(record)
            logger.info(f"Sensor data saved to memory: AQI {data.aqi}")
        
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
    """Get sensor data history for user"""
    try:
        if db:
            # Firebase storage
            docs = db.collection('sensor_data')\
                .where('userId', '==', user_id)\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(50)\
                .stream()
            
            records = [{'id': doc.id, **doc.to_dict()} for doc in docs]
        else:
            # In-memory storage
            records = [r for r in sensor_data_db if r['userId'] == user_id]
            records = sorted(records, key=lambda x: x['timestamp'], reverse=True)[:50]
        
        return {
            'success': True,
            'data': records
        }
    except Exception as e:
        logger.error(f"Error getting sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sensor data")

# Cough recording endpoints
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
                
                # Check if audio data is too small
                if len(audio_bytes) < 1000:
                    raise Exception(f"Audio data too small ({len(audio_bytes)} bytes). Recording might have failed.")
                
                # Save to temporary file
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
            severity = data.severity or 'unknown'
            diagnosis = data.diagnosis or 'No ML analysis available'
        
        # Save record
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'audioData': None,  # Don't store full audio
            'severity': severity,
            'coughType': data.coughType or 'dry',
            'diagnosis': diagnosis,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if db:
            # Firebase storage
            db.collection('cough_records').document(record['id']).set(record)
            logger.info(f"Cough record saved to Firebase: {severity}")
        else:
            # In-memory storage
            cough_records_db.append(record)
            logger.info(f"Cough record saved to memory: {severity}")
        
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
    """Get cough records for user"""
    try:
        if db:
            # Firebase storage
            docs = db.collection('cough_records')\
                .where('userId', '==', user_id)\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(50)\
                .stream()
            
            records = [{'id': doc.id, **doc.to_dict()} for doc in docs]
        else:
            # In-memory storage
            records = [r for r in cough_records_db if r['userId'] == user_id]
            records = sorted(records, key=lambda x: x['timestamp'], reverse=True)[:50]
        
        return {
            'success': True,
            'data': records
        }
    except Exception as e:
        logger.error(f"Error getting cough records: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cough records")

# Oxygen level endpoints
@api_router.post("/oxygen-level")
async def save_oxygen_level(data: OxygenLevelCreate):
    """Save oxygen level reading"""
    try:
        record = {
            'id': str(uuid.uuid4()),
            'userId': data.userId,
            'level': data.level,
            'timestamp': data.timestamp or datetime.utcnow().isoformat()
        }
        
        if db:
            # Firebase storage
            db.collection('oxygen_levels').document(record['id']).set(record)
            logger.info(f"Oxygen level saved to Firebase: {data.level}%")
        else:
            # In-memory storage
            oxygen_records_db.append(record)
            logger.info(f"Oxygen level saved to memory: {data.level}%")
        
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
    """Get oxygen level history for user"""
    try:
        if db:
            # Firebase storage
            docs = db.collection('oxygen_levels')\
                .where('userId', '==', user_id)\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(50)\
                .stream()
            
            records = [{'id': doc.id, **doc.to_dict()} for doc in docs]
        else:
            # In-memory storage
            records = [r for r in oxygen_records_db if r['userId'] == user_id]
            records = sorted(records, key=lambda x: x['timestamp'], reverse=True)[:50]
        
        return {
            'success': True,
            'data': records
        }
    except Exception as e:
        logger.error(f"Error getting oxygen levels: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get oxygen levels")

# History endpoint (combined data)
@api_router.get("/history/{user_id}")
async def get_history(user_id: str):
    """Get combined history for user"""
    try:
        # Get sensor data
        sensor_response = await get_sensor_data(user_id)
        sensor_history = sensor_response['data']
        
        # Get cough records
        cough_response = await get_cough_records(user_id)
        cough_history = cough_response['data']
        
        # Get oxygen levels
        oxygen_response = await get_oxygen_levels(user_id)
        oxygen_history = oxygen_response['data']
        
        return {
            'success': True,
            'data': {
                'sensorData': sensor_history,
                'coughRecords': cough_history,
                'oxygenLevels': oxygen_history
            }
        }
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get history")

# Heat map endpoint (for all users)
@api_router.get("/heatmap-data")
async def get_heatmap_data():
    """Get AQI data from all users for heat map"""
    try:
        if db:
            # Firebase storage - get recent data from all users
            docs = db.collection('sensor_data')\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(100)\
                .stream()
            
            records = []
            for doc in docs:
                data = doc.to_dict()
                records.append({
                    'location': data.get('location', {'latitude': 0, 'longitude': 0}),
                    'aqi': data.get('aqi', 0),
                    'timestamp': data.get('timestamp')
                })
        else:
            # In-memory storage
            records = [
                {
                    'location': r['location'],
                    'aqi': r['aqi'],
                    'timestamp': r['timestamp']
                }
                for r in sensor_data_db[-100:]  # Last 100 records
            ]
        
        return {
            'success': True,
            'data': records
        }
    except Exception as e:
        logger.error(f"Error getting heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get heatmap data")

# Register router
app.include_router(api_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Air Quality Monitor API starting up...")
    logger.info(f"Firebase: {'Connected' if db else 'Not connected'}")
    logger.info(f"ML Model: {'Loaded' if cough_classifier else 'Not loaded'}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
