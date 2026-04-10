# Local Development Environment Fix

## Problem
After downloading from GitHub and running locally, you get "Network Error" at signup because the frontend is trying to connect to the Emergent platform URL instead of your local backend.

## Quick Fix for Local Development on Mac

### Step 1: Update `.env` File

In your downloaded project, navigate to `frontend/.env` and change:

**FROM:**
```
EXPO_PUBLIC_BACKEND_URL=https://aqi-respiratory-app.preview.emergentagent.com
```

**TO:**
```
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8001
```

### Complete `.env` File Should Look Like:
```
EXPO_TUNNEL_SUBDOMAIN=aqi-respiratory-app
EXPO_PACKAGER_HOSTNAME=https://aqi-respiratory-app.preview.emergentagent.com
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8001
EXPO_USE_FAST_RESOLVER="1"
METRO_CACHE_ROOT=/app/frontend/.metro-cache
```

**Note:** `10.0.2.2` is the special IP address that Android Emulator uses to access your Mac's localhost.

### Step 2: Restart Frontend

After changing `.env`:
```bash
# Stop the running frontend (Ctrl+C)
# Then start again
cd frontend
npx expo start
```

### Step 3: Reload App on Emulator

In the Android Emulator:
- Press `Ctrl+M` (or `Cmd+M` on Mac)
- Tap "Reload"

Or completely close and reopen the app.

---

## Different Scenarios

### Scenario 1: Running Everything Locally (Current)
- Backend: `uvicorn server:app --host 0.0.0.0 --port 8001 --reload` on Mac
- Frontend: `npx expo start` on Mac
- Device: Android Emulator on Mac

**Frontend .env:**
```
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8001
```

### Scenario 2: Local Backend + Physical Android Device
- Backend: Running on Mac
- Device: Physical Android phone on same WiFi

**Frontend .env:**
```
EXPO_PUBLIC_BACKEND_URL=http://YOUR_MAC_IP:8001
```

Find your Mac's IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```
Example: `192.168.1.100`

### Scenario 3: Running on Emergent Platform
- Backend: Emergent container
- Frontend: Emergent container
- Device: Any (connects via tunnel)

**Frontend .env:**
```
EXPO_PUBLIC_BACKEND_URL=https://aqi-respiratory-app.preview.emergentagent.com
```

---

## Testing the Fix

### 1. Check Backend is Running
```bash
curl http://localhost:8001/api/health
```
Should return: `{"status":"healthy", ...}`

### 2. Test Backend from Android Emulator Perspective
From your Mac terminal:
```bash
curl http://10.0.2.2:8001/api/health
```
Should also work (this is how emulator sees it)

### 3. Try Signup Again
- Open app on emulator
- Try to sign up
- Should now work!

---

## Troubleshooting

### Still Getting "Network Error"?

**Check 1: Backend is Running**
```bash
ps aux | grep uvicorn
```
Should show the running process.

**Check 2: Backend Port 8001 is Listening**
```bash
lsof -i :8001
```
Should show uvicorn listening.

**Check 3: Frontend Read New .env**
- Make sure you restarted frontend after changing .env
- Check Metro bundler terminal, should show no errors
- Try clearing cache:
  ```bash
  cd frontend
  npx expo start -c
  ```

**Check 4: App Reloaded on Emulator**
- Close app completely (swipe away)
- Reopen from launcher

**Check 5: Check Frontend Console**
Look for this log in Metro bundler:
```
🔍 Backend URL being used: http://10.0.2.2:8001
```

If it shows the old URL, the .env wasn't reloaded.

---

## Quick Checklist

When running locally:
- [ ] Backend running: `uvicorn server:app --host 0.0.0.0 --port 8001 --reload`
- [ ] Backend shows: "✅ ML Cough Classifier loaded successfully!"
- [ ] Frontend .env has: `EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8001`
- [ ] Frontend restarted after .env change
- [ ] App reloaded on emulator
- [ ] Console shows correct backend URL

---

## Alternative: Create Local .env

Create a separate `.env.local` file for local development:

**frontend/.env.local:**
```
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8001
```

Then run:
```bash
REACT_NATIVE_PACKAGER_HOSTNAME=localhost npx expo start
```

---

## For Firebase Connection

Don't forget to add your `firebase-key.json` to the backend folder:
```
backend/
├── firebase-key.json  ← Add this
├── server.py
├── ml_model.py
└── ...
```

Then restart backend to see:
```
✅ Firebase connected successfully!
```

---

## Summary

**The Issue:** .env file from GitHub has Emergent platform URL
**The Fix:** Change `EXPO_PUBLIC_BACKEND_URL` to `http://10.0.2.2:8001`
**Time to Fix:** 2 minutes
**After Fix:** Signup should work immediately

Try this and let me know if it works! 🚀
