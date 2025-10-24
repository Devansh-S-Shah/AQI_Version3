import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

export default function About() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>About</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.title}>Air Quality Monitoring System</Text>
          <Text style={styles.description}>
            This application provides real-time air quality monitoring and health
            tracking to help you stay safe in various environmental conditions.
          </Text>
        </View>

        {/* Device Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Device Components</Text>
          
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Sensors Used</Text>
            
            <View style={styles.sensorItem}>
              <Ionicons name="radio-outline" size={20} color="#4A90E2" />
              <View style={styles.sensorInfo}>
                <Text style={styles.sensorName}>MQ-7</Text>
                <Text style={styles.sensorDescription}>Carbon Monoxide Sensor</Text>
              </View>
            </View>

            <View style={styles.sensorItem}>
              <Ionicons name="radio-outline" size={20} color="#4A90E2" />
              <View style={styles.sensorInfo}>
                <Text style={styles.sensorName}>MQ-135</Text>
                <Text style={styles.sensorDescription}>Hazardous Gas Sensor</Text>
              </View>
            </View>

            <View style={styles.sensorItem}>
              <Ionicons name="radio-outline" size={20} color="#4A90E2" />
              <View style={styles.sensorInfo}>
                <Text style={styles.sensorName}>EVE SHT4X+SGP40</Text>
                <Text style={styles.sensorDescription}>
                  Temperature and Humidity Sensor
                </Text>
              </View>
            </View>

            <View style={styles.sensorItem}>
              <Ionicons name="radio-outline" size={20} color="#4A90E2" />
              <View style={styles.sensorInfo}>
                <Text style={styles.sensorName}>PM10 Sensor</Text>
                <Text style={styles.sensorDescription}>Particulate Matter Sensor</Text>
              </View>
            </View>

            <View style={styles.sensorItem}>
              <Ionicons name="radio-outline" size={20} color="#4A90E2" />
              <View style={styles.sensorInfo}>
                <Text style={styles.sensorName}>Pulse Oximeter</Text>
                <Text style={styles.sensorDescription}>Blood Oxygen Level Sensor</Text>
              </View>
            </View>
          </View>
        </View>

        {/* How AQI is Calculated */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>How AQI is Calculated</Text>
          <View style={styles.card}>
            <Text style={styles.cardDescription}>
              The Air Quality Index (AQI) is calculated using a weighted formula that
              considers multiple pollutants:
            </Text>
            <Text style={styles.formula}>
              AQI = (PM10 × 0.4) + (CO × 0.25) + (Hazardous Gases × 0.25) + (Air Quality × 0.1)
            </Text>
            <Text style={styles.cardDescription}>
              Each sensor reading is normalized to a 0-500 scale, then weighted based on
              its health impact. The final AQI value determines the safety category:
            </Text>
            <View style={styles.aqiLegend}>
              <View style={styles.legendItem}>
                <View style={[styles.colorBox, { backgroundColor: '#00E400' }]} />
                <Text style={styles.legendText}>0-100: Good</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.colorBox, { backgroundColor: '#FFFF00' }]} />
                <Text style={styles.legendText}>101-200: Moderate</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.colorBox, { backgroundColor: '#FF7E00' }]} />
                <Text style={styles.legendText}>201-300: Poor</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.colorBox, { backgroundColor: '#FF0000' }]} />
                <Text style={styles.legendText}>301-400: Severe</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.colorBox, { backgroundColor: '#8F3F97' }]} />
                <Text style={styles.legendText}>401+: Danger</Text>
              </View>
            </View>
          </View>
        </View>

        {/* How It Works */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>How It Works</Text>
          <View style={styles.card}>
            <Text style={styles.stepTitle}>1. Data Collection</Text>
            <Text style={styles.stepDescription}>
              The ESP32 microcontroller continuously collects data from all connected
              sensors, measuring various air quality parameters.
            </Text>

            <Text style={styles.stepTitle}>2. Data Transmission</Text>
            <Text style={styles.stepDescription}>
              Sensor data is transmitted to the mobile app via Wi-Fi connection,
              ensuring real-time updates.
            </Text>

            <Text style={styles.stepTitle}>3. Processing & Analysis</Text>
            <Text style={styles.stepDescription}>
              The app processes sensor readings, calculates the AQI, and provides
              personalized health recommendations based on your location and health data.
            </Text>

            <Text style={styles.stepTitle}>4. Health Monitoring</Text>
            <Text style={styles.stepDescription}>
              In addition to environmental data, the app monitors your cough patterns
              and blood oxygen levels to provide comprehensive health insights.
            </Text>
          </View>
        </View>

        {/* Technical Details */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Technical Specifications</Text>
          <View style={styles.card}>
            <Text style={styles.specItem}>
              <Text style={styles.specLabel}>Microcontroller:</Text> ESP32
            </Text>
            <Text style={styles.specItem}>
              <Text style={styles.specLabel}>Communication:</Text> Wi-Fi (802.11 b/g/n)
            </Text>
            <Text style={styles.specItem}>
              <Text style={styles.specLabel}>Update Frequency:</Text> Real-time
            </Text>
            <Text style={styles.specItem}>
              <Text style={styles.specLabel}>Data Storage:</Text> Cloud-based (Firebase)
            </Text>
            <Text style={styles.specItem}>
              <Text style={styles.specLabel}>Platform:</Text> React Native (Expo)
            </Text>
          </View>
        </View>

        {/* Placeholder for device image */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Device Image</Text>
          <View style={styles.imagePlaceholder}>
            <Ionicons name="hardware-chip" size={64} color="#4A90E2" />
            <Text style={styles.placeholderText}>
              Device image will be added here
            </Text>
          </View>
        </View>
      </ScrollView>
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
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  section: {
    marginTop: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90E2',
    marginBottom: 12,
  },
  description: {
    fontSize: 16,
    color: '#ccc',
    lineHeight: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  card: {
    backgroundColor: '#1A1E3B',
    borderRadius: 12,
    padding: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  cardDescription: {
    fontSize: 14,
    color: '#ccc',
    lineHeight: 20,
    marginBottom: 12,
  },
  sensorItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 12,
  },
  sensorInfo: {
    flex: 1,
  },
  sensorName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  sensorDescription: {
    fontSize: 14,
    color: '#888',
  },
  formula: {
    backgroundColor: '#0A0E27',
    padding: 12,
    borderRadius: 8,
    color: '#4A90E2',
    fontFamily: 'monospace',
    fontSize: 12,
    marginVertical: 12,
  },
  aqiLegend: {
    marginTop: 12,
    gap: 8,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  colorBox: {
    width: 24,
    height: 24,
    borderRadius: 4,
  },
  legendText: {
    fontSize: 14,
    color: '#ccc',
  },
  stepTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4A90E2',
    marginTop: 12,
    marginBottom: 8,
  },
  stepDescription: {
    fontSize: 14,
    color: '#ccc',
    lineHeight: 20,
  },
  specItem: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 8,
  },
  specLabel: {
    fontWeight: '600',
    color: '#fff',
  },
  imagePlaceholder: {
    backgroundColor: '#1A1E3B',
    borderRadius: 12,
    padding: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  placeholderText: {
    fontSize: 14,
    color: '#888',
    marginTop: 16,
  },
});
