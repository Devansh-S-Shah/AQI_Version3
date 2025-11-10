# Android Emulator Setup Guide

## Current Situation

You're running:
- **Backend**: Locally on your Mac using `uvicorn` command
- **Frontend**: On Emergent platform
- **Android Emulator**: On your Mac (Android Studio)

## The Network Error Issue

The Android Emulator app has the **old URL cached** in the JavaScript bundle. Simply changing the `.env` file and restarting Metro is not enough - the app needs to reload completely on the emulator.

## Solution: Force App Reload on Android Emulator

### Option 1: Shake to Reload (Easiest)
1. **In Android Emulator**, with your app open:
2. Press `Ctrl + M` (Windows/Linux) or `Cmd + M` (Mac) to open the dev menu
3. Tap **"Reload"** to reload the JavaScript bundle
4. The app will now use the new backend URL: `http://10.0.2.2:8001`

### Option 2: Complete Restart
1. Close the app completely (swipe away from recent apps)
2. Reopen the app from the launcher
3. The updated URL should now be active

### Option 3: Clear App Data
1. In Android Emulator, go to **Settings → Apps**
2. Find your app
3. Tap **Storage → Clear Data**
4. Reopen the app

## Verify It's Working

After reloading, when you try to sign up, you should see in your Mac terminal (where uvicorn is running):
```
INFO:     10.0.2.2:XXXXX - "POST /api/auth/register HTTP/1.1" 200 OK
```

This confirms the Android Emulator successfully reached your local backend.

## Current Configuration

**Frontend .env** (on Emergent):
```
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8001
```

**Your Local Mac Backend**:
- Running at: `localhost:8001`
- Android Emulator accesses it via: `10.0.2.2:8001`
- Has `firebase-key.json` ✅

## Troubleshooting

### Still Getting "Network Error"?

1. **Check if backend is actually running on your Mac:**
   ```bash
   curl http://localhost:8001/api/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Test registration endpoint:**
   ```bash
   curl -X POST http://localhost:8001/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass"}'
   ```
   Should return: `{"success":true,...}`

3. **Check your Mac's firewall:**
   - Make sure port 8001 is not blocked
   - Allow Python/uvicorn through firewall

4. **Verify the app is using the correct URL:**
   - Check the Metro bundler logs (should show the console.log output)
   - Look for: `🔍 Backend URL being used: http://10.0.2.2:8001`

### Check Console Logs

The app now logs the backend URL it's using. To see this:
1. Run Metro bundler with logs visible
2. When the app loads, you should see:
   ```
   🔍 Backend URL being used: http://10.0.2.2:8001
   ```

If it shows something else (like the old URL), the app hasn't reloaded with the new .env value.

## Important Notes

### Environment Variables in Expo/React Native
- Environment variables are **bundled at build time**
- Changing `.env` requires **app reload** on device
- Simply restarting Metro server is **not enough**
- Must reload the JavaScript bundle on the device/emulator

### The Magic of 10.0.2.2
- This is a **special IP address** in Android Emulator
- It always points to the host machine's `localhost`
- Equivalent to `127.0.0.1` or `localhost` on your Mac
- Only works in Android Emulator (not physical devices)

## Next Steps

1. ✅ **Reload the app** on Android Emulator (Ctrl+M → Reload)
2. ✅ Try signing up again
3. ✅ Check your Mac terminal for the API request log
4. ✅ If successful, you should be able to register and login

## If Everything is Working

Once signup works, all these should work too:
- ✅ User login
- ✅ Calculate AQI (ESP32 data)
- ✅ Record Oxygen Level (ESP32 data)
- ✅ Record Cough
- ✅ View History
- ✅ Data saved to Firebase (on your local backend)

The key is just getting the app to reload with the new backend URL! 🚀
