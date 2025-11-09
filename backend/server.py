from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
import bcrypt
import uuid
import logging

# Firebase Admin
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Firebase Admin
try:
    cred = credentials.Certificate(str(ROOT_DIR / 'firebase-key.json'))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected successfully!")
except Exception as e:
    print(f"⚠️  Firebase not configured: {e}")
    db = None

# Create the main app
app = FastAPI()
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class SensorDataCreate(BaseModel):
    userId: str
    readings: Dict
    aqi: int
    location: Optional[Dict[str, float]] = None

class CoughRecordCreate(BaseModel):
    userId: str
    audioData: Optional[str] = None
    severity: str
    coughType: Optional[str] = None
    diagnosis: Optional[str] = None

class OxygenLevelCreate(BaseModel):
    userId: str
    oxygenLevel: float
    timestamp: Optional[str] = None

# Authentication Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Firebase not configured")
        
        users_ref = db.collection('users')
        existing = users_ref.where('username', '==', user_data.username).limit(1).get()
        
        if len(list(existing)) > 0:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = str(uuid.uuid4())
        user_doc = {
            'id': user_id,
            'username': user_data.username,
            'password': hashed_password,
            'created_at': datetime.utcnow().isoformat()
        }
        
        users_ref.document(user_id).set(user_doc)
        logger.info(f"User registered: {user_data.username}")
        
        return {
            'success': True,
            'message': 'User registered successfully',
            'user': {'id': user_id, 'username': user_data.username}
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Firebase not configured")
        
        users_ref = db.collection('users')
        users = users_ref.where('username', '==', user_data.username).limit(1).get()
        users_list = list(users)
        
        if len(users_list) == 0:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_doc = users_list[0].to_dict()
        
        if not bcrypt.checkpw(user_data.password.encode('utf-8'), user_doc['password'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"User logged in: {user_data.username}")
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': {'id': user_doc['id'], 'username': user_doc['username']}
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.post("/sensor-data")
async def save_sensor_data(data: SensorDataCreate):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Firebase not configured")
        
        record = {
            'userId': data.userId,
            'readings': data.readings,
            'aqi': data.aqi,
            'location': data.location,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        doc_ref = db.collection('sensor_data').document()
        doc_ref.set(record)
        logger.info(f"Sensor data saved for user: {data.userId}, AQI: {data.aqi}")
        
        return {'success': True, 'message': 'Sensor data saved successfully', 'data': record}
    except Exception as e:
        logger.error(f"Error saving sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save sensor data")

@api_router.post("/cough-record")
async def save_cough_record(data: CoughRecordCreate):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Firebase not configured")
        
        record = {
            'userId': data.userId,
            'audioData': data.audioData,
            'severity': data.severity,
            'coughType': data.coughType,
            'diagnosis': data.diagnosis,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        doc_ref = db.collection('cough_records').document()
        doc_ref.set(record)
        logger.info(f"Cough record saved for user: {data.userId}")
        
        return {'success': True, 'message': 'Cough record saved successfully', 'data': record}
    except Exception as e:
        logger.error(f"Error saving cough record: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save cough record")

@api_router.post("/oxygen-level")
async def save_oxygen_level(data: OxygenLevelCreate):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Firebase not configured")
        
        record = {
            'userId': data.userId,
            'oxygenLevel': data.oxygenLevel,
            'timestamp': data.timestamp or datetime.utcnow().isoformat()
        }
        
        doc_ref = db.collection('oxygen_levels').document()
        doc_ref.set(record)
        logger.info(f"Oxygen level saved: {data.oxygenLevel}%")
        
        return {'success': True, 'message': 'Oxygen level saved successfully', 'data': record}
    except Exception as e:
        logger.error(f"Error saving oxygen level: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save oxygen level")

@api_router.get("/history/{user_id}")
async def get_user_history(user_id: str):
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Firebase not configured")
        
        sensor_data = db.collection('sensor_data').where('userId', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).get()
        
        history = []
        for doc in sensor_data:
            data = doc.to_dict()
            history.append({
                '_id': doc.id,
                'userId': data['userId'],
                'aqi': data['aqi'],
                'timestamp': data['timestamp'],
                'location': data.get('location')
            })
        
        return {'success': True, 'history': history}
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "firebase_connected": db is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

app.include_router(api_router)
