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

// Calculate AQI based on sensor readings
// This is a simplified calculation - actual AQI calculation is more complex
export const calculateAQI = (readings: SensorReadings): AQIResult => {
  // Weighted calculation based on different pollutants
  const pmWeight = 0.4;
  const coWeight = 0.25;
  const gasWeight = 0.25;
  const aqWeight = 0.1;

  // Normalize readings (example ranges - adjust based on sensor specs)
  const pmNorm = Math.min((readings.pm10 / 150) * 500, 500);
  const coNorm = Math.min((readings.co / 50) * 500, 500);
  const gasNorm = Math.min((readings.hazardousGas / 300) * 500, 500);
  const aqNorm = Math.min((readings.airQuality / 500) * 500, 500);

  // Calculate weighted AQI
  const aqi = Math.round(
    pmNorm * pmWeight +
    coNorm * coWeight +
    gasNorm * gasWeight +
    aqNorm * aqWeight
  );

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
