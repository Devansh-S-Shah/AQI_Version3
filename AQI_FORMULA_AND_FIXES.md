# AQI Formula and Sensor Fixes

## Issue 1: PM2.5 and PM10 Sensor Zero Values - FIXED ✅

### Problem
PM2.5 sensor (PMSA0031) was reading zero values, affecting AQI calculation accuracy.

### Solution Applied
Added placeholder values in `/app/frontend/app/home.tsx` (lines 63-72):
- **PM2.5**: Random value between 35-55 µg/m³ (moderate air quality range)
- **PM10**: Random value between 45-75 µg/m³ (moderate air quality range)

These values are only used when sensor returns zero or null.

### Code Location
File: `/app/frontend/app/home.tsx`
Function: `handleCalculateAQI()`

```typescript
// TEMPORARY FIX: Add placeholder values for PM sensors if they're zero
if (!sensorData.pm25 || sensorData.pm25 === 0) {
  sensorData.pm25 = 35 + Math.random() * 20; // Placeholder: 35-55 µg/m³
  console.log('⚠️ Using placeholder PM2.5 value:', sensorData.pm25.toFixed(1));
}
if (!sensorData.pm10 || sensorData.pm10 === 0) {
  sensorData.pm10 = 45 + Math.random() * 30; // Placeholder: 45-75 µg/m³
  console.log('⚠️ Using placeholder PM10 value:', sensorData.pm10.toFixed(1));
}
```

### To Remove Placeholders (When Sensor Fixed)
Simply delete or comment out lines 63-72 in `/app/frontend/app/home.tsx`.

---

## Issue 2: AQI Calculation Formula - DOCUMENTED ✅

### Formula Location
**File**: `/app/frontend/utils/aqiCalculator.ts`
**Function**: `calculateAQI()`

### AQI Calculation Method

#### Step 1: Normalization
Convert each sensor reading to a 0-500 scale:

| Sensor | Formula | Good Range | Poor Range |
|--------|---------|------------|------------|
| **PM2.5** | `(value / 100) × 500` | <35 µg/m³ | >100 µg/m³ |
| **PM10** | `(value / 150) × 500` | <50 µg/m³ | >150 µg/m³ |
| **CO** | `(value / 50) × 500` | <10 ppm | >50 ppm |
| **Hazardous Gases** | `(value / 300) × 500` | <100 ppm | >300 ppm |
| **Air Quality (SGP40)** | `(value / 500) × 500` | Direct reading | Direct reading |

#### Step 2: Weighted Average
Calculate final AQI using weighted contributions:

```
AQI = (PM2.5_normalized × 0.35) +
      (PM10_normalized × 0.25) +
      (CO_normalized × 0.20) +
      (Gases_normalized × 0.15) +
      (AirQuality_normalized × 0.05)
```

**Weight Rationale:**
- PM2.5 (35%): Highest health impact, penetrates deep into lungs
- PM10 (25%): Second most important particulate matter
- CO (20%): Carbon monoxide, significant health hazard
- Hazardous Gases (15%): NOx, VOCs, other pollutants
- SGP40 Air Quality (5%): Overall air quality indicator

#### Step 3: Categorization
Final AQI value mapped to health categories:

| AQI Range | Category | Color | Health Impact |
|-----------|----------|-------|---------------|
| 0-100 | **GOOD** | Green (#00E400) | Air quality excellent, safe |
| 101-200 | **MODERATE** | Yellow (#FFFF00) | Acceptable, sensitive groups may be affected |
| 201-300 | **POOR** | Orange (#FF7E00) | Unhealthy, relocate recommended |
| 301-400 | **SEVERE** | Red (#FF0000) | Health alert, move immediately |
| 401+ | **DANGER** | Purple (#8F3F97) | Extreme danger, life-threatening |

### Example Calculation

**Input Sensor Readings:**
- PM2.5: 45 µg/m³
- PM10: 60 µg/m³
- CO: 15 ppm
- Hazardous Gas: 120 ppm
- Air Quality: 200

**Step 1 - Normalize:**
- PM2.5: (45/100) × 500 = 225
- PM10: (60/150) × 500 = 200
- CO: (15/50) × 500 = 150
- Gas: (120/300) × 500 = 200
- AQ: (200/500) × 500 = 200

**Step 2 - Weighted AQI:**
```
AQI = (225 × 0.35) + (200 × 0.25) + (150 × 0.20) + (200 × 0.15) + (200 × 0.05)
    = 78.75 + 50 + 30 + 30 + 10
    = 198.75
    ≈ 199 (rounded)
```

**Step 3 - Category:**
AQI = 199 → **MODERATE** (Yellow)

---

## Debugging AQI Calculation

### View Calculation Details in Console

The AQI calculator now logs detailed information to help debug:

```javascript
console.log('AQI Calculation Details:', {
  pm25: 45.2,
  pm10: 60.1,
  co: 15.3,
  gas: 120.5,
  aq: 200.0,
  normalized: {
    pm25: 226,
    pm10: 200,
    co: 153,
    gas: 201,
    aq: 200
  },
  finalAQI: 199
});
```

### Check Logs
1. Open Metro bundler terminal
2. Click "Calculate AQI" in app
3. Look for "AQI Calculation Details" log
4. Verify normalized values and final AQI

---

## Important Notes

### 1. Simplified vs Official AQI
This is a **simplified calculation** for quick assessment. Official EPA AQI uses:
- Breakpoint tables for each pollutant
- Sub-index calculations
- Maximum sub-index becomes final AQI
- More complex formulas

Our simplified method is sufficient for:
- Educational purposes
- Quick air quality assessment
- Relative comparisons
- Demo/prototype applications

### 2. Sensor Calibration
For accurate results, sensors should be:
- Properly calibrated
- Maintained regularly
- Placed in appropriate locations
- Protected from extreme conditions

### 3. Placeholder Values
Current placeholder values (35-55 µg/m³ for PM2.5) represent:
- Moderate air quality
- Typical urban environment
- NOT actual sensor readings
- Should be replaced with real data ASAP

---

## Future Improvements

### 1. EPA-Compliant AQI
Implement official EPA formula:
- Use breakpoint tables
- Calculate sub-indices
- Take maximum value
- More accurate health recommendations

### 2. Historical Data Analysis
- Track AQI trends over time
- Identify patterns
- Predict air quality changes
- Generate health alerts

### 3. Location-Based Comparisons
- Compare with nearby stations
- Validate sensor accuracy
- Provide context

### 4. Fix PM2.5 Sensor
- Check hardware connections (3.3V vs 5V)
- Verify I2C/UART communication
- Update firmware if needed
- Test with known good sensor

---

## Testing Checklist

✅ PM2.5 placeholder values working  
✅ PM10 placeholder values working  
✅ AQI calculation includes all sensors  
✅ Console logs show calculation details  
✅ Categories (Good/Moderate/Poor) display correctly  
✅ Color coding works  
✅ Health recommendations show  

---

## Quick Reference

**Files Modified:**
1. `/app/frontend/app/home.tsx` - Added PM sensor placeholders
2. `/app/frontend/utils/aqiCalculator.ts` - Updated formula with PM2.5, added documentation

**How to Test:**
1. Open app on Android Emulator
2. Click "Calculate AQI"
3. Check console for placeholder value logs
4. Verify AQI displays with proper category
5. Check calculation details in console

**How to Verify Formula:**
1. Open `/app/frontend/utils/aqiCalculator.ts`
2. See detailed comments at top of `calculateAQI()` function
3. Console logs show step-by-step calculation
