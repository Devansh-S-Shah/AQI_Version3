interface SensorReadings {
  co: number;
  hazardousGas: number;
  temperature: number;
  humidity: number;
  airQuality: number;
  pm10: number;
  pm25?: number;  // Optional PM2.5 sensor
}

interface AQIResult {
  aqi: number;
  category: string;
  color: string;
  message: string;
  recommendation: string;
}

/**
 * Calculate AQI based on sensor readings
 * 
 * FORMULA USED (Simplified Weighted Average):
 * ============================================
 * 
 * 1. NORMALIZATION (Convert sensor values to 0-500 scale):
 *    - PM2.5:  (value / 100) × 500  (Good: <35, Poor: >100 µg/m³)
 *    - PM10:   (value / 150) × 500  (Good: <50, Poor: >150 µg/m³)
 *    - CO:     (value / 50) × 500   (Good: <10, Poor: >50 ppm)
 *    - Gases:  (value / 300) × 500  (Good: <100, Poor: >300 ppm)
 *    - AQ:     (value / 500) × 500  (Direct SGP40 reading)
 * 
 * 2. WEIGHTED CALCULATION:
 *    AQI = (PM2.5 × 0.35) + (PM10 × 0.25) + (CO × 0.2) + (Gases × 0.15) + (AQ × 0.05)
 * 
 * 3. CATEGORIES:
 *    - 0-100:   Good (Green)
 *    - 101-200: Moderate (Yellow)
 *    - 201-300: Poor (Orange)
 *    - 301-400: Severe (Red)
 *    - 401+:    Danger (Purple)
 * 
 * NOTE: This is a simplified calculation. Official AQI uses EPA breakpoint formulas.
 * Location: /app/frontend/utils/aqiCalculator.ts
 */
export const calculateAQI = (readings: SensorReadings): AQIResult => {
  // Weighted calculation based on different pollutants
  const pm25Weight = 0.35;  // PM2.5 has highest impact on health
  const pm10Weight = 0.25;  // PM10 second most important
  const coWeight = 0.20;    // Carbon monoxide
  const gasWeight = 0.15;   // Hazardous gases (NOx, VOCs)
  const aqWeight = 0.05;    // Air quality index from SGP40

  // Normalize readings to 0-500 scale based on sensor ranges
  const pm25Norm = readings.pm25 
    ? Math.min((readings.pm25 / 100) * 500, 500) 
    : 0;
  const pm10Norm = Math.min((readings.pm10 / 150) * 500, 500);
  const coNorm = Math.min((readings.co / 50) * 500, 500);
  const gasNorm = Math.min((readings.hazardousGas / 300) * 500, 500);
  const aqNorm = Math.min((readings.airQuality / 500) * 500, 500);

  // Calculate weighted AQI
  const aqi = Math.round(
    pm25Norm * pm25Weight +
    pm10Norm * pm10Weight +
    coNorm * coWeight +
    gasNorm * gasWeight +
    aqNorm * aqWeight
  );

  console.log('AQI Calculation Details:', {
    pm25: readings.pm25?.toFixed(1),
    pm10: readings.pm10.toFixed(1),
    co: readings.co.toFixed(1),
    gas: readings.hazardousGas.toFixed(1),
    aq: readings.airQuality.toFixed(1),
    normalized: {
      pm25: pm25Norm.toFixed(0),
      pm10: pm10Norm.toFixed(0),
      co: coNorm.toFixed(0),
      gas: gasNorm.toFixed(0),
      aq: aqNorm.toFixed(0)
    },
    finalAQI: aqi
  });

  return getAQICategory(aqi);
};

export const getAQICategory = (aqi: number): AQIResult => {
  if (aqi <= 100) {
    return {
      aqi,
      category: 'GOOD',
      color: '#00E400',
      message: 'GOOD, YOU ARE SAFE!',
      recommendation: 'Air quality is excellent. Stay where you are - it\'s safe and healthy!',
    };
  } else if (aqi <= 200) {
    return {
      aqi,
      category: 'MODERATE',
      color: '#FFFF00',
      message: 'MODERATE SAFETY',
      recommendation: 'Air quality is acceptable. Consider moving if you have respiratory issues.',
    };
  } else if (aqi <= 300) {
    return {
      aqi,
      category: 'POOR',
      color: '#FF7E00',
      message: 'POOR SAFETY',
      recommendation: 'Air quality is unhealthy. Relocate to a safer location with better air quality.',
    };
  } else if (aqi <= 400) {
    return {
      aqi,
      category: 'SEVERE',
      color: '#FF0000',
      message: 'SEVERE CONDITIONS',
      recommendation: 'Health alert! Immediately move to an area with lower and safer AQI values.',
    };
  } else {
    return {
      aqi,
      category: 'DANGER',
      color: '#8F3F97',
      message: 'DANGER!',
      recommendation: '⚠️ EXTREME DANGER! Move out immediately - your life is in severe danger!',
    };
  }
};

// Get comprehensive recommendation based on AQI and health metrics
export const getHealthRecommendation = (
  aqi: number,
  coughSeverity: 'none' | 'low' | 'medium' | 'high',
  oxygenLevel: number
): string => {
  const aqiResult = getAQICategory(aqi);
  let recommendation = aqiResult.recommendation;

  // Add health-specific recommendations
  if (oxygenLevel < 90) {
    recommendation += '\n\n⚠️ Low oxygen level detected! Seek medical attention immediately.';
  } else if (oxygenLevel < 95) {
    recommendation += '\n\nYour oxygen level is slightly low. Consider using supplemental oxygen if available.';
  }

  if (coughSeverity === 'high') {
    recommendation += '\n\nSevere cough detected. Please consult a healthcare provider.';
  } else if (coughSeverity === 'medium' && aqi > 150) {
    recommendation += '\n\nYour cough combined with poor air quality is concerning. Minimize outdoor activities.';
  }

  return recommendation;
};
