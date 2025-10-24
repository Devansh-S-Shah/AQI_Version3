import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Modal,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { useAuthStore } from '../store/authStore';
import { useESP32Store } from '../store/esp32Store';
import { calculateAQI, getHealthRecommendation } from '../utils/aqiCalculator';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function Home() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { sensorData, esp32IP } = useESP32Store();
  const [loading, setLoading] = useState<string | null>(null);
  const [menuVisible, setMenuVisible] = useState(false);
  const [aqiResult, setAqiResult] = useState<any>(null);
  const [sensorReadings, setSensorReadings] = useState<any>(null);
  const [oxygenLevel, setOxygenLevel] = useState<number | null>(null);
  
  // Cough recording modal state
  const [coughModalVisible, setCoughModalVisible] = useState(false);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  const handleCalculateAQI = async () => {
    setLoading('aqi');
    try {
      // Use mock data for demonstration (ESP32 would provide real data)
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
      setSensorReadings(mockData);
      
      // Save to backend
      await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/sensor-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: user?.id,
          readings: mockData,
          aqi: result.aqi,
          location: { latitude: 0, longitude: 0 },
        }),
      });
      
      Alert.alert('AQI Calculated Successfully', `${result.message}\n\nAQI: ${result.aqi}\n\nSensor readings are now displayed below.`);
    } catch (error) {
      console.error('Error calculating AQI:', error);
      Alert.alert('Error', 'Failed to calculate AQI. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const startRecording = async () => {
    try {
      // Request microphone permissions
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert('Permission Required', 'Microphone access is needed to record cough.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording: newRecording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      setRecording(newRecording);
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    
    setIsRecording(false);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    console.log('Recording saved to:', uri);
  };

  const saveCoughRecording = async () => {
    if (!recording) {
      Alert.alert('Error', 'No recording to save');
      return;
    }

    try {
      await stopRecording();
      
      // Save to backend (placeholder for ML analysis)
      await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/cough-record`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: user?.id,
          audioData: 'base64_audio_data_placeholder',
          severity: 'moderate',
          coughType: 'dry',
          diagnosis: 'ML analysis placeholder - integrate TensorFlow Lite model',
        }),
      });

      Alert.alert(
        'Cough Recorded Successfully',
        'Recording saved. ML analysis will be available after model integration.'
      );
      
      setCoughModalVisible(false);
      setRecording(null);
    } catch (error) {
      console.error('Error saving cough recording:', error);
      Alert.alert('Error', 'Failed to save cough recording');
    }
  };

  const handleRecordCough = () => {
    setCoughModalVisible(true);
  };

  const handleRecordOxygen = async () => {
    setLoading('oxygen');
    try {
      // Use mock oxygen level for demonstration (ESP32 pulse oximeter would provide real data)
      const oxygenReading = 96;
      
      // Set the oxygen level to display on screen
      setOxygenLevel(oxygenReading);
      
      await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/oxygen-level`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: user?.id,
          oxygenLevel: oxygenReading,
          timestamp: new Date().toISOString(),
        }),
      });
      
      Alert.alert(
        'Oxygen Level Recorded',
        `Pulse oximeter reading saved successfully!\n\nOxygen Level: ${oxygenReading}%`
      );
    } catch (error) {
      console.error('Error recording oxygen level:', error);
      Alert.alert('Error', 'Failed to record oxygen level. Please try again.');
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

        {/* Sensor Readings Display */}
        {sensorReadings && (
          <View style={styles.sensorCard}>
            <Text style={styles.sensorTitle}>Sensor Readings</Text>
            <View style={styles.sensorGrid}>
              <View style={styles.sensorItem}>
                <Ionicons name="cloud-outline" size={24} color="#4A90E2" />
                <Text style={styles.sensorLabel}>CO Level</Text>
                <Text style={styles.sensorValue}>{sensorReadings.co} ppm</Text>
              </View>
              
              <View style={styles.sensorItem}>
                <Ionicons name="warning-outline" size={24} color="#FF7E00" />
                <Text style={styles.sensorLabel}>Hazardous Gas</Text>
                <Text style={styles.sensorValue}>{sensorReadings.hazardousGas} ppm</Text>
              </View>
              
              <View style={styles.sensorItem}>
                <Ionicons name="thermometer-outline" size={24} color="#00E400" />
                <Text style={styles.sensorLabel}>Temperature</Text>
                <Text style={styles.sensorValue}>{sensorReadings.temperature}°C</Text>
              </View>
              
              <View style={styles.sensorItem}>
                <Ionicons name="water-outline" size={24} color="#4A90E2" />
                <Text style={styles.sensorLabel}>Humidity</Text>
                <Text style={styles.sensorValue}>{sensorReadings.humidity}%</Text>
              </View>
              
              <View style={styles.sensorItem}>
                <Ionicons name="leaf-outline" size={24} color="#00E400" />
                <Text style={styles.sensorLabel}>Air Quality</Text>
                <Text style={styles.sensorValue}>{sensorReadings.airQuality}</Text>
              </View>
              
              <View style={styles.sensorItem}>
                <Ionicons name="analytics-outline" size={24} color="#8F3F97" />
                <Text style={styles.sensorLabel}>PM10</Text>
                <Text style={styles.sensorValue}>{sensorReadings.pm10} µg/m³</Text>
              </View>
            </View>
          </View>
        )}
      </ScrollView>

      {/* Cough Recording Modal */}
      <Modal
        visible={coughModalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setCoughModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Record Cough</Text>
            <Text style={styles.modalSubtitle}>
              Press the microphone button to start recording
            </Text>
            
            <TouchableOpacity
              style={[
                styles.recordButton,
                isRecording && styles.recordButtonActive,
              ]}
              onPress={isRecording ? stopRecording : startRecording}
            >
              <Ionicons
                name={isRecording ? 'stop-circle' : 'mic'}
                size={64}
                color="#fff"
              />
            </TouchableOpacity>
            
            {isRecording && (
              <Text style={styles.recordingText}>Recording...</Text>
            )}
            
            {recording && !isRecording && (
              <Text style={styles.readyText}>✓ Recording ready to save</Text>
            )}
            
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={styles.modalButtonCancel}
                onPress={() => {
                  setRecording(null);
                  setIsRecording(false);
                  setCoughModalVisible(false);
                }}
              >
                <Text style={styles.modalButtonText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[
                  styles.modalButtonSave,
                  !recording && styles.modalButtonDisabled,
                ]}
                onPress={saveCoughRecording}
                disabled={!recording}
              >
                <Text style={styles.modalButtonTextSave}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

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
  // Sensor readings styles
  sensorCard: {
    backgroundColor: '#1A1E3B',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  sensorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  sensorGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  sensorItem: {
    backgroundColor: '#0A0E27',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    width: '47%',
    minHeight: 120,
    justifyContent: 'center',
  },
  sensorLabel: {
    fontSize: 12,
    color: '#888',
    marginTop: 8,
    marginBottom: 4,
    textAlign: 'center',
  },
  sensorValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#1A1E3B',
    borderRadius: 20,
    padding: 32,
    width: '85%',
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  modalSubtitle: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    marginBottom: 32,
  },
  recordButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#4A90E2',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  recordButtonActive: {
    backgroundColor: '#FF4444',
  },
  recordingText: {
    fontSize: 16,
    color: '#FF4444',
    fontWeight: '600',
    marginBottom: 16,
  },
  readyText: {
    fontSize: 16,
    color: '#00E400',
    fontWeight: '600',
    marginBottom: 16,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
    width: '100%',
  },
  modalButtonCancel: {
    flex: 1,
    backgroundColor: '#2A2E4B',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  modalButtonSave: {
    flex: 1,
    backgroundColor: '#4A90E2',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  modalButtonDisabled: {
    opacity: 0.5,
  },
  modalButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  modalButtonTextSave: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
