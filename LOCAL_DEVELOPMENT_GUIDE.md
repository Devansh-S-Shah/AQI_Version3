# Local Development Guide - Air Quality Monitoring App

## Running on Mac with Android Emulator

### Quick Start

1. **Start Backend (on your Mac terminal):**
   ```bash
   cd /path/to/backend
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```
   ✅ Look for: "Firebase connected successfully!" message

2. **Start Frontend (on Emergent platform OR locally):**
   - The app is already configured to connect to your local backend
   - Backend URL is set to: `http://10.0.2.2:8001`

3. **Launch Android Emulator:**
   - Open Android Studio
   - Start your Android Emulator device
   - Open the app in the emulator

### Important IP Addresses

| Environment | Backend URL | Use Case |
|------------|-------------|----------|
| Android Emulator | `http://10.0.2.2:8001` | ✅ Current setup |
| Physical Android Device | `http://YOUR_MAC_IP:8001` | If using real phone |
| iOS Simulator | `http://localhost:8001` | If using iOS |
| Emergent Platform | `https://clearbreathe-app.preview.emergentagent.com` | When deploying |

### Configuration Files

**Frontend Environment Variables** (`/app/frontend/.env`):
```
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8001
```

**Backend Environment Variables** (`/app/backend/.env`):
```
# Your backend .env should have Firebase configurations
# Make sure firebase-key.json is in /app/backend/
```

### Testing the Connection

1. **Test Backend API:**
   ```bash
   curl http://localhost:8001/api/health
   ```
   Should return JSON with status information

2. **Test from Android Emulator:**
   - Open app on emulator
   - Try to sign up with a test user
   - ✅ Should successfully create user and log in
   - ❌ If you get "Network Error", check:
     - Backend is running on port 8001
     - EXPO_PUBLIC_BACKEND_URL is set to `http://10.0.2.2:8001`
     - Frontend has been restarted after .env changes

### ESP32 Configuration

For ESP32 to work with Android Emulator:
1. ESP32 and Mac must be on the same WiFi network
2. In app Settings, set ESP32 IP to its local network IP (e.g., `192.168.1.100`)
3. The app will connect directly to ESP32 over WiFi

### Troubleshooting

#### "Network Error" on Signup/Login
- ✅ **Solution:** Backend URL updated to `http://10.0.2.2:8001`
- Restart frontend: `sudo supervisorctl restart expo` (on Emergent platform)

#### "Firebase not configured" in backend
- ✅ **Solution:** Add `firebase-key.json` to `/app/backend/`
- Download from Firebase Console → Project Settings → Service Accounts

#### ESP32 Connection Error (but data shows)
- ✅ **Solution:** Already fixed! Error handling improved in `home.tsx`

#### Can't see login page after logout
- ✅ **Solution:** Already fixed! Auth state handling improved in `index.tsx`

### Development Workflow

```
┌─────────────────────────────────────────────────────────┐
│                     Your Mac                              │
│                                                           │
│  ┌─────────────┐        ┌──────────────┐                │
│  │   Backend   │◄───────│  Android     │                │
│  │ localhost   │  HTTP  │  Emulator    │                │
│  │   :8001     │  via   │              │                │
│  │             │ 10.0.2.2│              │                │
│  └──────┬──────┘        └──────────────┘                │
│         │                                                 │
│         │ Firestore                                       │
│         ▼                                                 │
│  ┌─────────────┐                                         │
│  │  Firebase   │                                         │
│  │  Cloud      │                                         │
│  └─────────────┘                                         │
└─────────────────────────────────────────────────────────┘

                    WiFi Network
                         │
                         ▼
                  ┌─────────────┐
                  │   ESP32     │
                  │   Sensors   │
                  └─────────────┘
```

### Common Commands

```bash
# Check if backend is running
ps aux | grep uvicorn

# View backend logs
tail -f backend.log  # Or wherever your logs are

# Restart Expo (if running on Emergent)
sudo supervisorctl restart expo

# Test backend health
curl http://localhost:8001/api/health

# View Firebase data (requires firebase-tools)
firebase firestore:data
```

### Next Steps After Basic Setup

1. ✅ Test user signup/login
2. ✅ Connect ESP32 and test sensor readings
3. ✅ Test AQI calculation
4. ✅ Test oxygen level recording
5. ✅ Test cough recording
6. ⏳ Integrate ML model for cough analysis
7. ⏳ Add Google Maps API key for heatmap

### Notes

- **Port 8001** is for your local backend
- **Port 3000** is for Expo Metro bundler (if needed)
- Android Emulator's `10.0.2.2` always points to host machine's localhost
- Physical devices need your Mac's actual IP (find with `ifconfig`)

### Getting Your Mac's IP Address

```bash
# On Mac terminal
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Use this IP if connecting from a physical Android device on the same WiFi network.

---

## Summary

✅ **Backend URL for Android Emulator:** `http://10.0.2.2:8001`
✅ **Firebase:** Add `firebase-key.json` to backend folder
✅ **ESP32:** Set local network IP in app Settings
✅ **All fixes applied:** Login page, Firebase integration, ESP32 error handling

Your app should now work smoothly with Android Emulator! 🚀
