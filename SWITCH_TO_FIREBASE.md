# Switch to Firebase Backend

## Current Situation
You're using `server.py` which stores data in memory (RAM only). Data will be lost when server restarts.

You need to use `server_firebase.py` which saves data to Firebase Firestore permanently.

## Steps to Switch

### 1. Stop the Backend Server
In your backend terminal, press `Ctrl+C` to stop uvicorn

### 2. Backup Current Version (Optional)
```bash
cd /path/to/your/backend
mv server.py server_in_memory.py
```

### 3. Use Firebase Version
```bash
cp server_firebase.py server.py
```

### 4. Verify Firebase Key Exists
```bash
ls -la firebase-key.json
```
You should see the file listed. If not, add your firebase-key.json file.

### 5. Start Backend Again
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 6. Look for Success Message
You should now see:
```
✅ Firebase connected successfully!
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

If you see:
```
⚠️  Firebase not configured: [error message]
```
Then there's an issue with your firebase-key.json file.

## Verification

After switching:

1. **Test Registration:**
   - Open your app on Android Emulator
   - Sign up with a new user
   - Check Firebase Console → Firestore Database
   - You should see a new `users` collection

2. **Test Sensor Data:**
   - Click "Calculate AQI"
   - Check Firebase Console
   - You should see a `sensor_data` collection

3. **Data Persists:**
   - Restart your backend server (Ctrl+C then run uvicorn again)
   - Check app History page
   - Data should still be there (not lost)

## Troubleshooting

### "Firebase not configured" Error

**Check firebase-key.json location:**
```bash
# Should be in backend folder
ls -la firebase-key.json
```

**Check firebase-key.json format:**
```bash
# Should be valid JSON
head -5 firebase-key.json
```
Should show something like:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
```

**Check file permissions:**
```bash
chmod 644 firebase-key.json
```

### Server Won't Start

**Check Python dependencies:**
```bash
pip install firebase-admin
```

**Or reinstall all requirements:**
```bash
pip install -r requirements.txt
```

## Comparison

| Feature | server.py (in-memory) | server_firebase.py |
|---------|----------------------|-------------------|
| Data storage | RAM only | Firebase Firestore |
| Survives restart | ❌ No | ✅ Yes |
| Requires firebase-key.json | ❌ No | ✅ Yes |
| Works without internet | ✅ Yes | ❌ No |
| Good for testing | ✅ Yes | ✅ Yes |
| Good for production | ❌ No | ✅ Yes |

## Current Status

✅ App working with in-memory storage
⏳ Need to switch to Firebase for persistent storage

After switching, all your data will be saved to Firebase and won't be lost on server restart! 🚀
