import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../store/authStore';
import { useESP32Store } from '../store/esp32Store';
import { calculateAQI, getHealthRecommendation } from '../utils/aqiCalculator';
import { diseases } from '../constants/diseases';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function Home() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { sensorData, esp32IP } = useESP32Store();
  const [loading, setLoading] = useState<string | null>(null);
  const [menuVisible, setMenuVisible] = useState(false);
  const [aqiResult, setAqiResult] = useState<any>(null);

  const handleCalculateAQI = async () => {
    setLoading('aqi');
    try {
      // Fetch data from ESP32
      const response = await fetch(`http://${esp32IP}/sensor-data`);
      
      if (!response.ok) {
        // Use mock data for demonstration
        const mockData = {
          co: 12.5,
          hazardousGas: 150,
          temperature: 25.5,
          humidity: 60,
          airQuality: 180,
          pm10: 45,
          timestamp: new Date().toISOString(),
        };
        
        const result = calculateAQI(mockData);
        setAqiResult(result);
        
        // Save to backend
        await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/sensor-data`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: user?.id,
            readings: mockData,
            aqi: result.aqi,
            location: { latitude: 0, longitude: 0 }, // TODO: Get actual location
          }),
        });
        
        Alert.alert('AQI Calculated', `${result.message}\n\nAQI: ${result.aqi}`);
      }
    } catch (error) {
      console.error('Error calculating AQI:', error);
      Alert.alert('Error', 'Failed to fetch sensor data. Using mock data.');
      
      // Fallback to mock data
      const mockData = {
        co: 12.5,
        hazardousGas: 150,
        temperature: 25.5,
        humidity: 60,
        airQuality: 180,
        pm10: 45,
        timestamp: new Date().toISOString(),
      };
      
      const result = calculateAQI(mockData);
      setAqiResult(result);
    } finally {
      setLoading(null);
    }
  };

  const handleRecordCough = async () => {
    setLoading('cough');
    try {
      // TODO: Implement audio recording and ML analysis
      await new Promise(resolve => setTimeout(resolve, 1000));
      Alert.alert(
        'Cough Recorded',
        'Cough analysis will be implemented with ML model.\n\nPlaceholder: Medium severity detected.'
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to record cough');
    } finally {
      setLoading(null);
    }
  };

  const handleRecordOxygen = async () => {
    setLoading('oxygen');
    try {
      // Mock oxygen level - in real app, this would come from pulse oximeter
      const oxygenLevel = 96;
      
      await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/oxygen-level`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: user?.id,
          oxygenLevel,
          timestamp: new Date().toISOString(),
        }),
      });
      
      Alert.alert('Oxygen Level Recorded', `Your oxygen level: ${oxygenLevel}%`);
    } catch (error) {
      Alert.alert('Error', 'Failed to record oxygen level');
    } finally {
      setLoading(null);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>[TBD - App Name]</Text>
        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => setMenuVisible(!menuVisible)}
        >
          <Ionicons name="menu" size={28} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Hamburger Menu */}
      {menuVisible && (
        <View style={styles.menu}>
          <TouchableOpacity
            style={styles.menuItem}
            onPress={() => {
              setMenuVisible(false);
              router.push('/history');
            }}
          >
            <Ionicons name="time-outline" size={20} color="#fff" />
            <Text style={styles.menuText}>Check History</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.menuItem}
            onPress={() => {
              setMenuVisible(false);
              router.push('/about');
            }}
          >
            <Ionicons name="information-circle-outline" size={20} color="#fff" />
            <Text style={styles.menuText}>About</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.menuItem}
            onPress={() => {
              setMenuVisible(false);
              router.push('/heatmap');
            }}
          >
            <Ionicons name="map-outline" size={20} color="#fff" />
            <Text style={styles.menuText}>Heat Map</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.menuItem}
            onPress={() => {
              setMenuVisible(false);
              router.push('/settings');
            }}
          >
            <Ionicons name="settings-outline" size={20} color="#fff" />
            <Text style={styles.menuText}>Settings</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.menuItem}
            onPress={() => {
              setMenuVisible(false);
              router.push('/profile');
            }}
          >
            <Ionicons name="person-outline" size={20} color="#fff" />
            <Text style={styles.menuText}>Profile</Text>
          </TouchableOpacity>
        </View>
      )}

      <ScrollView style={styles.content}>
        {/* Current AQI Display */}
        {aqiResult && (
          <View style={[styles.aqiCard, { borderColor: aqiResult.color }]}>
            <Text style={styles.aqiTitle}>Current Air Quality</Text>
            <Text style={[styles.aqiValue, { color: aqiResult.color }]}>
              {aqiResult.aqi}
            </Text>
            <Text style={[styles.aqiCategory, { color: aqiResult.color }]}>
              {aqiResult.message}
            </Text>
            <Text style={styles.aqiRecommendation}>
              {aqiResult.recommendation}
            </Text>
          </View>
        )}

        {/* Disease Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Related Health Information</Text>
          {diseases.slice(0, 2).map((disease) => (
            <View key={disease.id} style={styles.diseaseCard}>
              <Text style={styles.diseaseName}>{disease.name}</Text>
              <Text style={styles.diseaseDescription}>
                {disease.description}
              </Text>
              <Text style={styles.diseaseSubtitle}>Key Symptoms:</Text>
              {disease.symptoms.slice(0, 3).map((symptom, idx) => (
                <Text key={idx} style={styles.diseaseItem}>
                  • {symptom}
                </Text>
              ))}
            </View>
          ))}
        </View>
      </ScrollView>

      {/* Action Buttons */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleCalculateAQI}
          disabled={loading === 'aqi'}
        >
          {loading === 'aqi' ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="analytics" size={24} color="#fff" />
              <Text style={styles.buttonText}>Calculate AQI</Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleRecordCough}
          disabled={loading === 'cough'}
        >
          {loading === 'cough' ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="mic" size={24} color="#fff" />
              <Text style={styles.buttonText}>Record Cough</Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleRecordOxygen}
          disabled={loading === 'oxygen'}
        >
          {loading === 'oxygen' ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="fitness" size={24} color="#fff" />
              <Text style={styles.buttonText}>Record Oxygen Level</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2A2E4B',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4A90E2',
  },
  menuButton: {
    padding: 8,
  },
  menu: {
    position: 'absolute',
    top: 60,
    right: 16,
    backgroundColor: '#1A1E3B',
    borderRadius: 12,
    padding: 8,
    zIndex: 1000,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    gap: 12,
  },
  menuText: {
    color: '#fff',
    fontSize: 16,
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  aqiCard: {
    backgroundColor: '#1A1E3B',
    borderRadius: 16,
    padding: 24,
    marginTop: 16,
    marginBottom: 24,
    borderWidth: 2,
  },
  aqiTitle: {
    fontSize: 18,
    color: '#888',
    marginBottom: 8,
  },
  aqiValue: {
    fontSize: 64,
    fontWeight: 'bold',
    marginVertical: 8,
  },
  aqiCategory: {
    fontSize: 24,
    fontWeight: '600',
    marginBottom: 16,
  },
  aqiRecommendation: {
    fontSize: 16,
    color: '#ccc',
    lineHeight: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  diseaseCard: {
    backgroundColor: '#1A1E3B',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  diseaseName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#4A90E2',
    marginBottom: 8,
  },
  diseaseDescription: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 12,
    lineHeight: 20,
  },
  diseaseSubtitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 8,
  },
  diseaseItem: {
    fontSize: 13,
    color: '#aaa',
    marginBottom: 4,
    paddingLeft: 8,
  },
  buttonContainer: {
    padding: 16,
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: '#2A2E4B',
  },
  actionButton: {
    backgroundColor: '#000',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    minHeight: 56,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
