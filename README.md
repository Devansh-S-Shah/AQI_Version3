# Air Quality Monitoring Native Android App

A comprehensive mobile application for monitoring air quality using ESP32 sensors, providing real-time AQI calculations, cough analysis, and health recommendations.

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure username/password login system
- **Real-time AQI Monitoring**: Connect to ESP32 device via WiFi to fetch sensor data
- **Multiple Sensors Support**:
  - MQ-7 Carbon Monoxide Sensor
  - MQ-135 Hazardous Gas Sensor
  - EVE SHT4X+SGP40 Temperature and Humidity Sensor
  - PM10 Particulate Matter Sensor
  - Pulse Oximeter for Blood Oxygen Level

### Health Monitoring
- **Cough Recording**: Record and analyze cough sounds (ML integration ready)
- **Oxygen Level Tracking**: Monitor blood oxygen saturation
- **Personalized Recommendations**: Get health suggestions based on AQI and health metrics

### Data Visualization
- **History Tracking**: View all past AQI readings with timestamps
- **Heat Map**: GPS-based visualization of air quality across different locations
- **Disease Information**: Learn about respiratory diseases related to air quality

### User Interface
- **Intuitive Navigation**: Hamburger menu for easy access to all features
- **Dark Mode**: Eye-friendly dark theme
- **Responsive Design**: Optimized for various Android device sizes

## 🚀 Getting Started

### Quick Setup

1. **Install Dependencies**:
   ```bash
   cd /app/frontend && yarn install
   cd /app/backend && pip install -r requirements.txt
   ```

2. **Configure Firebase**: Follow `/app/SETUP_INSTRUCTIONS.md`

3. **Run the App**:
   ```bash
   # Terminal 1 - Backend
   cd /app/backend && uvicorn server:app --host 0.0.0.0 --port 8001
   
   # Terminal 2 - Frontend
   cd /app/frontend && yarn start
   ```

## 📖 Documentation

- **Complete Setup Guide**: See `/app/SETUP_INSTRUCTIONS.md`
- **API Documentation**: All endpoints documented in backend code
- **ML Integration**: TensorFlow Lite guide in setup instructions

## 🔧 Configuration Required

Before deploying, configure:
1. Firebase credentials in `/app/frontend/firebase.config.ts`
2. Google Maps API key in `/app/frontend/app.json`
3. ESP32 IP address in app Settings page

## 📊 AQI Categories

| AQI Range | Category | Action |
|-----------|----------|--------|
| 0-100 | 🟩 Good | Safe |
| 101-200 | 🟨 Moderate | Consider moving |
| 201-300 | 🟧 Poor | Relocate |
| 301-400 | 🟥 Severe | Move immediately |
| 401+ | 🟪 Danger | Evacuate |

## 🤝 Note

This is a prototype application. Replace all placeholders before production use:
- `[TBD - App Name]` throughout the app
- Firebase configuration values
- Google Maps API keys
- Implement actual ML model for cough analysis
