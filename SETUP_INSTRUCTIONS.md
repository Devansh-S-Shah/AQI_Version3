# Air Quality Monitoring App - Setup Instructions

This document provides step-by-step instructions for setting up the Air Quality Monitoring native Android app.

## Table of Contents
1. [Firebase Setup](#firebase-setup)
2. [Google Maps Setup](#google-maps-setup)
3. [ESP32 Configuration](#esp32-configuration)
4. [ML Model Integration](#ml-model-integration)
5. [Running the App](#running-the-app)

---

## Firebase Setup

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter your project name (e.g., "Air Quality Monitor")
4. Follow the setup wizard

### Step 2: Enable Firestore Database

1. In your Firebase project, click "Firestore Database" in the left sidebar
2. Click "Create database"
3. Choose production mode or test mode:
   - **Test mode**: Good for development (open access for 30 days)
   - **Production mode**: Requires security rules
4. Select a region closest to your users
5. Click "Enable"

### Step 3: Get Firebase Configuration

1. In Firebase Console, go to Project Settings (gear icon)
2. Scroll down to "Your apps" section
3. Click the web icon (`</>`) to add a web app
4. Register your app with a nickname
5. Copy the `firebaseConfig` object

### Step 4: Update Frontend Configuration

Open `/app/frontend/firebase.config.ts` and replace the placeholder values:

```typescript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456"
};
```

### Step 5: Set Up Firestore Security Rules

In Firestore Database, go to "Rules" tab and add:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Sensor data collection
    match /sensor_data/{docId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.resource.data.userId == request.auth.uid;
    }
    
    // Cough records collection
    match /cough_records/{docId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.resource.data.userId == request.auth.uid;
    }
    
    // Oxygen levels collection
    match /oxygen_levels/{docId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.resource.data.userId == request.auth.uid;
    }
  }
}
```

---

## Google Maps Setup

### Step 1: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps SDK for Android
   - Maps SDK for iOS
   - Maps JavaScript API
4. Go to "Credentials" in the left sidebar
5. Click "Create Credentials" > "API key"
6. Copy your API key

### Step 2: Restrict Your API Key (Recommended)

1. Click on your API key to edit it
2. Under "Application restrictions":
   - For Android: Add your app's package name and SHA-1 certificate fingerprint
   - For iOS: Add your app's bundle identifier
3. Under "API restrictions":
   - Select "Restrict key"
   - Enable only the Maps APIs you're using

### Step 3: Configure API Key in Your App

For Expo apps, add the API key to `app.json`:

```json
{
  "expo": {
    "android": {
      "config": {
        "googleMaps": {
          "apiKey": "YOUR_GOOGLE_MAPS_API_KEY_HERE"
        }
      }
    },
    "ios": {
      "config": {
        "googleMapsApiKey": "YOUR_GOOGLE_MAPS_API_KEY_HERE"
      }
    }
  }
}
```

### Step 4: Update app.json

Open `/app/frontend/app.json` and add the Google Maps configuration under the appropriate platforms.

---

## ESP32 Configuration

### Step 1: Find Your ESP32 IP Address

1. Connect your ESP32 to the same Wi-Fi network as your mobile device
2. Open the Arduino IDE Serial Monitor
3. Look for the IP address in the serial output (usually displayed on startup)
4. Example: `192.168.1.100`

### Step 2: Configure IP in the App

1. Open the app on your device
2. Go to **Settings** (via hamburger menu)
3. Under "Device Connection", enter your ESP32 IP address
4. Click "Save IP Address"

### Step 3: Test Connection

1. Go to the main dashboard
2. Click "Calculate AQI"
3. The app will attempt to connect to your ESP32
4. If connection fails, verify:
   - ESP32 is powered on
   - ESP32 and phone are on the same network
   - IP address is correct

### ESP32 API Endpoints (Expected)

Your ESP32 should expose these endpoints:

- `GET /sensor-data` - Returns current sensor readings:
  ```json
  {
    "co": 12.5,
    "hazardousGas": 150,
    "temperature": 25.5,
    "humidity": 60,
    "airQuality": 180,
    "pm10": 45
  }
  ```

---

## ML Model Integration for Cough Analysis

### Overview

The app is designed to integrate a TensorFlow Lite model for cough audio classification. Here's how to add it:

### Step 1: Obtain a Cough Analysis Model

Option 1: **Use a Pre-trained Model**
- Search for open-source cough classification models
- Download a TensorFlow Lite (.tflite) model file
- Models should classify cough types and severity

Option 2: **Train Your Own Model**
- Collect cough audio samples
- Use TensorFlow to train an audio classification model
- Convert to TensorFlow Lite format
- Export the .tflite file

### Step 2: Add Model to Your App

1. Place your `.tflite` model file in `/app/frontend/assets/models/`
2. Install required packages:
   ```bash
   cd /app/frontend
   yarn add @tensorflow/tfjs @tensorflow/tfjs-react-native
   ```

### Step 3: Implement Model Inference

Create a new file `/app/frontend/utils/coughAnalysis.ts`:

```typescript
import * as tf from '@tensorflow/tfjs';
import { bundleResourceIO } from '@tensorflow/tfjs-react-native';

let model: tf.LayersModel | null = null;

export const loadCoughModel = async () => {
  try {
    const modelJson = require('../assets/models/cough_model.json');
    const modelWeights = require('../assets/models/cough_model.weights.bin');
    model = await tf.loadLayersModel(
      bundleResourceIO(modelJson, modelWeights)
    );
    console.log('Cough model loaded successfully');
  } catch (error) {
    console.error('Error loading cough model:', error);
  }
};

export const analyzeCough = async (audioData: Float32Array) => {
  if (!model) {
    await loadCoughModel();
  }
  
  // Preprocess audio data
  const inputTensor = tf.tensor(audioData).expandDims(0);
  
  // Run inference
  const prediction = model!.predict(inputTensor) as tf.Tensor;
  const results = await prediction.data();
  
  // Map results to severity and type
  return {
    severity: getSeverity(results),
    coughType: getCoughType(results),
    diagnosis: getDiagnosis(results)
  };
};
```

### Step 4: Update Recording Feature

Modify the "Record Cough" functionality in `/app/frontend/app/home.tsx` to use the ML model for analysis.

### Placeholder Implementation

Currently, the app uses a mock/placeholder for cough analysis. Replace this with actual ML integration once you have a model.

---

## Running the App

### Development Setup

1. **Install Dependencies**:
   ```bash
   cd /app/frontend
   yarn install
   ```

2. **Start Expo**:
   ```bash
   yarn start
   ```

3. **Run on Android**:
   - Option 1: Scan QR code with Expo Go app
   - Option 2: Use Android emulator
   - Option 3: Build APK for installation on physical device

### Build for Production

For Android Studio development:

1. **Prebuild**:
   ```bash
   npx expo prebuild --platform android
   ```

2. **Open in Android Studio**:
   - Open the `/app/frontend/android` folder in Android Studio
   - Build and run the project

### Testing the App

1. **User Authentication**:
   - Create a new account
   - Login with credentials

2. **AQI Calculation**:
   - Click "Calculate AQI" button
   - View sensor readings and recommendations

3. **Navigation**:
   - Use hamburger menu to access all pages
   - Test History, About, Heat Map, Settings, and Profile pages

---

## Troubleshooting

### Common Issues

1. **Firebase Connection Error**:
   - Verify firebaseConfig values are correct
   - Check internet connection
   - Ensure Firestore is enabled in Firebase Console

2. **Google Maps Not Loading**:
   - Verify API key is correct and has Maps APIs enabled
   - Check billing is enabled in Google Cloud Console
   - Ensure location permissions are granted

3. **ESP32 Connection Failed**:
   - Verify ESP32 and phone are on same network
   - Check ESP32 IP address is correct
   - Ensure ESP32 web server is running

4. **App Crashes on Start**:
   - Check all dependencies are installed
   - Clear Metro bundler cache: `yarn start --clear`
   - Reinstall node_modules: `rm -rf node_modules && yarn install`

---

## Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [TensorFlow Lite](https://www.tensorflow.org/lite)

---

## Support

For issues or questions, please refer to:
- Firebase Console for database/auth issues
- Google Cloud Console for Maps API issues
- ESP32 documentation for hardware connectivity
- App logs for debugging frontend issues

---

## Notes

- **App Name Placeholder**: Replace `[TBD - App Name]` throughout the app with your chosen name
- **Security**: Always use production-mode Firebase rules in production
- **API Keys**: Never commit API keys to public repositories
- **Testing**: Test thoroughly on real devices before production deployment
