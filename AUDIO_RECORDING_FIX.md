# Audio Recording Issue Fix

## Problem
Backend showing: "Error opening ... Format not recognised" and audio is only 19 bytes.

## Root Cause
The audio recording from expo-av isn't being saved properly, or the file isn't in a readable format.

## Fixes Applied

### 1. Backend Changes (`server.py`):
- Added check for minimum audio size (1000 bytes)
- Changed temp file extension to `.m4a` (expo-av typical format)
- Better error messages showing actual byte count

### 2. Frontend Changes (`home.tsx`):
- Fixed `stopRecording()` to properly await and return URI
- Added audio file info logging
- Proper cleanup of audio mode after recording

## Debugging Steps

### On Your Mac (Local Development):

1. **Check Console Logs When Recording:**
   ```
   - "Reading audio file from: file://..."
   - "Audio file info: {exists: true, size: XXXXX}"
   ```

2. **Expected File Size:**
   - Minimum: >1000 bytes
   - Typical for 5-10 sec: 50KB - 500KB
   - If showing only 19 bytes → Recording failed

### Common Issues & Solutions:

#### Issue 1: Recording Returns Immediately (19 bytes)
**Cause**: Recording not actually capturing audio
**Solution**:
1. Check microphone permissions on device/emulator
2. Ensure you record for at least 2-3 seconds
3. Try on physical device (emulator mic can be finicky)

#### Issue 2: File Format Not Recognized
**Cause**: expo-av uses different formats on different platforms
**Solutions**:
- iOS: Produces .m4a or .caf
- Android: Produces .m4a or .3gp
- Backend needs to handle all these

Let's add pydub for format conversion:

```bash
# On your Mac backend
pip install pydub ffmpeg-python
```

Then update `ml_model.py`:

```python
from pydub import AudioSegment
import subprocess

def convert_to_wav(input_path, output_path):
    """Convert any audio format to WAV"""
    try:
        # Using pydub (requires ffmpeg)
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format='wav')
        return True
    except Exception as e:
        print(f"Conversion error: {e}")
        return False

# In preprocess_audio method:
def preprocess_audio(self, audio_path):
    # Convert to WAV first
    wav_path = audio_path.replace('.m4a', '.wav')
    if not convert_to_wav(audio_path, wav_path):
        raise Exception("Failed to convert audio format")
    
    # Now load WAV file
    audio, sr = librosa.load(wav_path, sr=target_sr, duration=duration)
    # ... rest of code
```

#### Issue 3: Microphone Permissions
**Check**:
- Android Emulator: Settings → Apps → Your App → Permissions → Microphone
- iOS Simulator: Doesn't have microphone access (use physical device)

## Quick Test

### Test 1: Check if Recording Works
```javascript
// In frontend, add after recording starts:
setTimeout(async () => {
  if (recording) {
    const status = await recording.getStatusAsync();
    console.log('Recording status:', status);
    // Should show: {isRecording: true, durationMillis: XXXX}
  }
}, 2000);
```

### Test 2: Manually Check Recorded File
```javascript
// After stopRecording():
const uri = await stopRecording();
const fileInfo = await FileSystem.getInfoAsync(uri);
console.log('File info:', fileInfo);
// Should show: {exists: true, size: >1000, uri: "..."}
```

## Alternative: Use Mock Data for Testing

If recording continues to fail, use mock audio for testing ML:

```javascript
// In saveCoughRecording():
// Instead of real recording, use a test audio file
const testAudioBase64 = "..." // Put a valid base64 encoded audio here

await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/cough-record`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    userId: user?.id,
    audioData: testAudioBase64,  // Use test data
    severity: 'unknown',
    coughType: 'test',
    diagnosis: 'Testing with mock data',
  }),
});
```

## Install ffmpeg on Mac (if needed)

```bash
brew install ffmpeg
pip install pydub
```

## Recommended Testing Flow

1. **First**: Test on physical Android device (not emulator)
   - Emulator microphone is unreliable
   - Physical device gives real audio

2. **Check Logs**:
   - Frontend console: Audio file size
   - Backend logs: Received bytes count

3. **If Still Failing**:
   - Use binary classification (easier problem)
   - Test with pre-recorded audio file
   - Focus on other features first

## Status After This Fix

✅ Backend handles small files (rejects <1000 bytes)
✅ Better error messages
✅ Support for .m4a format
✅ File info logging added

⏳ **Test on physical device for best results**
⏳ **May need ffmpeg for format conversion**

---

## Next Recommended Actions

1. Test recording on physical Android device
2. Check console logs for actual file size
3. If still failing, install ffmpeg/pydub for format conversion
4. Consider using pre-recorded test audio for development

The infrastructure is ready, just need proper audio input! 🎤
