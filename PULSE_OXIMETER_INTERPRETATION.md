# Pulse Oximeter Sensor - Interpretation and Classification

## Overview

The application uses a pulse oximeter sensor connected to the ESP32 microcontroller to measure blood oxygen saturation levels (SpO₂). This document provides comprehensive details on how the sensor readings are interpreted, classified, and displayed.

---

## 1. Sensor Specifications

### Sensor Type
**MAX30100 / MAX30102 Pulse Oximeter Sensor**

**Measurement Parameters:**
- **SpO₂ (Oxygen Saturation)**: Percentage of oxygenated hemoglobin in blood
- **Range**: 0-100%
- **Accuracy**: ±2% (in range 70-100%)
- **Resolution**: 0.1%
- **Measurement Method**: Photoplethysmography (PPG)

**Physical Principle:**
- Uses two LEDs (Red: 660nm, Infrared: 880nm)
- Measures light absorption through skin/tissue
- Oxygenated and deoxygenated blood absorb different wavelengths differently
- Calculates SpO₂ ratio based on absorption difference

---

## 2. Data Flow Architecture

### 2.1 Hardware Connection
```
Pulse Oximeter Sensor → ESP32 Microcontroller → WiFi → Mobile App
```

**Connection Details:**
- Interface: I2C or Serial (UART)
- Power: 3.3V or 5V (depending on sensor model)
- Pins: SDA, SCL, VCC, GND

### 2.2 Data Retrieval Process

**Step 1: Request from App**
```javascript
// App sends GET request to ESP32
GET http://<ESP32_IP>/oxygen-level
Accept: application/json
```

**Step 2: ESP32 Response**
```json
{
  "oxygenLevel": 98.5,
  "heartRate": 72,  // Optional
  "timestamp": "2025-11-15T10:30:45Z"
}
```

**Step 3: App Processing**
```javascript
const oxygenReading = data.oxygenLevel;  // Extract SpO₂ value
setOxygenLevel(oxygenReading);  // Update display
```

**Step 4: Backend Storage**
```javascript
// Save to backend/Firebase
POST /api/oxygen-level
{
  "userId": "user-id",
  "level": 98.5,
  "timestamp": "ISO-8601"
}
```

---

## 3. Classification System

### 3.1 SpO₂ Ranges and Categories

The application uses a **3-tier classification system** based on clinical standards:

| SpO₂ Range | Category | Color Code | Status Indicator | Health Interpretation |
|------------|----------|------------|------------------|----------------------|
| **≥95%** | **Normal** | Green (#00E400) | ✅ Normal Range | Healthy oxygen levels |
| **90-94%** | **Low** | Yellow (#FFFF00) | ⚠️ Low | Mild hypoxemia, monitor closely |
| **<90%** | **Critical** | Red (#FF4444) | ❌ Critical | Severe hypoxemia, seek medical help |

### 3.2 Classification Logic (Code Implementation)

**Location:** `/app/frontend/app/home.tsx` (lines 419-425)

```javascript
// Color coding based on oxygen level
backgroundColor: oxygenLevel >= 95 ? '#00E400'    // Green (Normal)
                : oxygenLevel >= 90 ? '#FFFF00'   // Yellow (Low)
                : '#FF4444'                        // Red (Critical)

// Status text based on oxygen level
statusText: oxygenLevel >= 95 ? '✅ Normal Range'  // ≥95%
           : oxygenLevel >= 90 ? '⚠️ Low'          // 90-94%
           : '❌ Critical'                         // <90%
```

### 3.3 Mathematical Expression

```
Category = {
  "Normal"    if SpO₂ ≥ 95%
  "Low"       if 90% ≤ SpO₂ < 95%
  "Critical"  if SpO₂ < 90%
}

Color = {
  Green (#00E400)   if SpO₂ ≥ 95%
  Yellow (#FFFF00)  if 90% ≤ SpO₂ < 95%
  Red (#FF4444)     if SpO₂ < 90%
}
```

---

## 4. Clinical Interpretation

### 4.1 Normal Range (≥95%)

**SpO₂: 95-100%**

**Clinical Significance:**
- Optimal oxygen saturation
- Sufficient oxygen delivery to tissues
- Normal respiratory and circulatory function

**Display:**
- **Value**: "98%" (example)
- **Status**: "✅ Normal Range"
- **Color**: Green indicator
- **Recommendation**: None required

**Medical Context:**
- Healthy individuals typically maintain 95-100%
- Athletes and young adults often 98-100%
- Sea level normal: 96-100%
- High altitude normal: 90-95% (adjusted)

---

### 4.2 Low Range (90-94%)

**SpO₂: 90-94%**

**Clinical Significance:**
- **Mild Hypoxemia**: Below normal oxygen saturation
- May indicate respiratory issues
- Requires monitoring and possible intervention

**Display:**
- **Value**: "92%" (example)
- **Status**: "⚠️ Low"
- **Color**: Yellow indicator
- **Recommendation**: "Your oxygen level is slightly low. Consider using supplemental oxygen if available."

**Possible Causes:**
- Respiratory infections (pneumonia, bronchitis)
- Chronic obstructive pulmonary disease (COPD)
- Asthma exacerbation
- Poor air quality exposure
- High altitude
- Cardiovascular issues

**Action Required:**
- Monitor continuously
- Consider supplemental oxygen
- Consult healthcare provider if persistent
- Avoid strenuous activity

---

### 4.3 Critical Range (<90%)

**SpO₂: Below 90%**

**Clinical Significance:**
- **Severe Hypoxemia**: Dangerously low oxygen levels
- Medical emergency requiring immediate attention
- Risk of organ damage and life-threatening complications

**Display:**
- **Value**: "87%" (example)
- **Status**: "❌ Critical"
- **Color**: Red indicator
- **Recommendation**: "⚠️ Low oxygen level detected! Seek medical attention immediately."

**Immediate Risks:**
- Brain hypoxia (oxygen deprivation)
- Heart strain
- Organ failure
- Loss of consciousness
- Death (if prolonged)

**Action Required:**
- **IMMEDIATE MEDICAL ATTENTION**
- Call emergency services
- Administer supplemental oxygen
- Hospital evaluation necessary
- Do NOT delay

---

## 5. Display Implementation

### 5.1 UI Components

**Oxygen Level Card Structure:**

```
┌─────────────────────────────────────┐
│  ❤️  Blood Oxygen Level             │  ← Header with heart icon
├─────────────────────────────────────┤
│           98%                       │  ← Large oxygen value
│          SpO₂                       │  ← Label
├─────────────────────────────────────┤
│  🟢 ✅ Normal Range                 │  ← Status with color indicator
├─────────────────────────────────────┤
│  From Pulse Oximeter Sensor (ESP32) │  ← Source information
└─────────────────────────────────────┘
```

### 5.2 Visual Elements

**1. Header Section:**
- Icon: ❤️ (Heart icon, size 32, color #FF4444)
- Title: "Blood Oxygen Level"
- Font: Bold, size 20

**2. Value Display:**
- Oxygen Level: Large font (size 48), bold
- Unit: "SpO₂" (subscript 2)
- Color: White on dark background for contrast

**3. Status Indicator:**
- **Circular Dot**: 10×10 pixels
  - Green for Normal
  - Yellow for Low
  - Red for Critical
- **Status Text**: 
  - "✅ Normal Range"
  - "⚠️ Low"
  - "❌ Critical"

**4. Source Label:**
- Text: "From Pulse Oximeter Sensor (ESP32)"
- Font: Small, gray color
- Indicates data source

### 5.3 Conditional Rendering

The oxygen card only appears after a reading is taken:

```javascript
{oxygenLevel !== null && (
  <View style={styles.oxygenCard}>
    {/* Display components */}
  </View>
)}
```

**Before Measurement:** Card is hidden  
**After Measurement:** Card appears with reading and classification

---

## 6. Integration with Health Recommendations

### 6.1 Combined Health Assessment

The oxygen level is integrated with other health metrics for comprehensive recommendations:

**Function:** `getHealthRecommendation(aqi, coughSeverity, oxygenLevel)`

**Location:** `/app/frontend/utils/aqiCalculator.ts`

```javascript
if (oxygenLevel < 90) {
  recommendation += '\n\n⚠️ Low oxygen level detected! Seek medical attention immediately.';
} else if (oxygenLevel < 95) {
  recommendation += '\n\nYour oxygen level is slightly low. Consider using supplemental oxygen if available.';
}
```

### 6.2 Multi-Factor Analysis

**Scenario 1: Low Oxygen + Poor AQI**
```
Oxygen: 92% (Low)
AQI: 250 (Poor)
→ Recommendation: "Air quality is unhealthy. Your oxygen level is slightly low. 
                   Relocate immediately to area with better air quality."
```

**Scenario 2: Critical Oxygen + Severe Cough**
```
Oxygen: 88% (Critical)
Cough: Severe
→ Recommendation: "⚠️ Low oxygen level detected! Seek medical attention immediately.
                   Severe cough detected. Please consult a healthcare provider."
```

**Scenario 3: Normal Oxygen + Good AQI**
```
Oxygen: 98% (Normal)
AQI: 75 (Good)
→ Recommendation: "Air quality is excellent. Stay where you are - it's safe and healthy!"
```

---

## 7. Data Storage and History

### 7.1 Backend Storage Structure

**Collection:** `oxygen_levels` (Firebase Firestore)

```json
{
  "id": "uuid-v4",
  "userId": "user-id",
  "level": 98.5,
  "timestamp": "2025-11-15T10:30:45.123Z"
}
```

**Fields:**
- **id**: Unique identifier (UUID)
- **userId**: Reference to user
- **level**: SpO₂ percentage (float, 0-100)
- **timestamp**: ISO-8601 timestamp

### 7.2 Historical Tracking

Users can view oxygen level history to track trends:

```javascript
// API endpoint
GET /api/oxygen-levels/{userId}

// Returns last 50 readings, sorted by timestamp (descending)
```

**Use Cases:**
- Track improvement after treatment
- Identify patterns (time of day, activity correlation)
- Monitor chronic conditions
- Provide data to healthcare providers

---

## 8. Measurement Best Practices

### 8.1 Proper Sensor Usage

**For Accurate Readings:**

1. **Clean Sensor**: Ensure sensor surface is clean
2. **Proper Placement**: Typically on fingertip or earlobe
3. **Stay Still**: Avoid movement during measurement
4. **Warm Fingers**: Cold fingers can give false low readings
5. **Remove Nail Polish**: Can interfere with readings
6. **Wait Time**: Allow 10-30 seconds for stabilization

**Avoid:**
- Measuring immediately after exercise
- Using on dirty or wet skin
- Movement during measurement
- Poor sensor contact
- Low battery in sensor

### 8.2 Environmental Factors

**Factors Affecting Readings:**

| Factor | Effect | Correction |
|--------|--------|------------|
| **Cold Temperature** | Lower reading | Warm hands first |
| **High Altitude** | Lower normal | Adjust baseline |
| **Nail Polish** | Inaccurate | Remove before measuring |
| **Motion** | Unstable reading | Stay still |
| **Poor Circulation** | Lower reading | Warm extremities |
| **Anemia** | May be inaccurate | Clinical correlation needed |

---

## 9. Error Handling

### 9.1 Common Errors and Solutions

**Error 1: ESP32 Connection Failed**
```
Error: "Failed to connect to ESP32"
Causes:
- ESP32 not powered on
- Wrong IP address
- Not on same WiFi network
- Sensor disconnected

Solution: Check connections and network settings
```

**Error 2: Invalid Reading (>100% or <0%)**
```
Sensor malfunction or connection issue
Action: Retry measurement, check sensor connection
```

**Error 3: Unstable Reading (fluctuating)**
```
Cause: Movement or poor sensor contact
Action: Keep still, ensure proper finger placement
```

### 9.2 Validation Logic

```javascript
function validateOxygenReading(reading) {
  // Valid range check
  if (reading < 0 || reading > 100) {
    throw new Error("Invalid oxygen reading: out of range");
  }
  
  // Realistic range check
  if (reading < 50) {
    console.warn("Extremely low reading - verify sensor");
  }
  
  return reading;
}
```

---

## 10. Technical Specifications Summary

### Quick Reference Table

| Parameter | Value/Range |
|-----------|-------------|
| **Measurement** | SpO₂ (Blood Oxygen Saturation) |
| **Unit** | Percentage (%) |
| **Range** | 0-100% |
| **Normal** | ≥95% |
| **Low** | 90-94% |
| **Critical** | <90% |
| **Sensor** | MAX30100/MAX30102 |
| **Communication** | ESP32 WiFi HTTP |
| **Update Rate** | On-demand (user initiated) |
| **Display Format** | Large value + status indicator |
| **Storage** | Firebase Firestore |
| **History** | Last 50 readings |

---

## 11. Medical Disclaimer

**IMPORTANT NOTICE:**

This application and pulse oximeter sensor are for:
- ✅ Educational purposes
- ✅ General health monitoring
- ✅ Fitness tracking
- ✅ Air quality impact assessment

**NOT intended for:**
- ❌ Medical diagnosis
- ❌ Clinical decision making
- ❌ Emergency medical assessment
- ❌ Replacement for professional medical devices

**Always consult qualified healthcare professionals for:**
- Medical diagnosis
- Treatment decisions
- Persistent low oxygen levels
- Any concerning symptoms

---

## 12. References and Standards

### Clinical Guidelines
- **WHO Guidelines**: Normal SpO₂ ≥95% at sea level
- **American Thoracic Society**: Hypoxemia defined as SpO₂ <90%
- **Pulse Oximetry Standards**: ISO 80601-2-61

### Technical Standards
- **MAX30100/MAX30102 Datasheet**: Maxim Integrated
- **PPG Measurement Principles**: Photoplethysmography standards
- **Medical Device Accuracy**: ±2% for SpO₂ 70-100%

---

## Conclusion

The pulse oximeter integration in the Air Quality Monitoring application provides real-time blood oxygen saturation measurements with clear, color-coded classification. The three-tier system (Normal/Low/Critical) enables quick interpretation and appropriate action, while integration with AQI and cough data provides comprehensive health assessment in relation to air quality exposure.

The system balances simplicity for end users with clinical accuracy, providing actionable health information while maintaining appropriate disclaimers about medical use limitations.

---

**Document Version**: 1.0  
**Date**: November 15, 2025  
**File Location**: `/app/PULSE_OXIMETER_INTERPRETATION.md`
