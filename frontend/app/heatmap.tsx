import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';

interface HeatMapData {
  latitude: number;
  longitude: number;
  aqi: number;
  color: string;
}

export default function HeatMap() {
  const router = useRouter();
  const [location, setLocation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [heatMapData, setHeatMapData] = useState<HeatMapData[]>([]);

  useEffect(() => {
    requestLocationPermission();
  }, []);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      
      if (status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Location permission is needed to show the heat map'
        );
        setLoading(false);
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({});
      setLocation({
        latitude: currentLocation.coords.latitude,
        longitude: currentLocation.coords.longitude,
        latitudeDelta: 0.05,
        longitudeDelta: 0.05,
      });

      // Mock heat map data
      setHeatMapData([
        {
          latitude: currentLocation.coords.latitude + 0.01,
          longitude: currentLocation.coords.longitude + 0.01,
          aqi: 85,
          color: '#00E400',
        },
        {
          latitude: currentLocation.coords.latitude - 0.01,
          longitude: currentLocation.coords.longitude - 0.01,
          aqi: 150,
          color: '#FFFF00',
        },
        {
          latitude: currentLocation.coords.latitude + 0.02,
          longitude: currentLocation.coords.longitude - 0.01,
          aqi: 250,
          color: '#FF7E00',
        },
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Error', 'Failed to get your location');
      setLoading(false);
    }
  };

  const getMarkerColor = (aqi: number): string => {
    if (aqi <= 100) return '#00E400';
    if (aqi <= 200) return '#FFFF00';
    if (aqi <= 300) return '#FF7E00';
    if (aqi <= 400) return '#FF0000';
    return '#8F3F97';
  };

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
        <Text style={styles.headerTitle}>Air Quality Heat Map</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4A90E2" />
          <Text style={styles.loadingText}>Loading map...</Text>
        </View>
      ) : location ? (
        <View style={styles.mapContainer}>
          <MapView
            style={styles.map}
            provider={PROVIDER_GOOGLE}
            initialRegion={location}
            showsUserLocation
            showsMyLocationButton
          >
            {heatMapData.map((data, index) => (
              <Marker
                key={index}
                coordinate={{
                  latitude: data.latitude,
                  longitude: data.longitude,
                }}
                pinColor={data.color}
              >
                <View style={styles.markerContainer}>
                  <View
                    style={[
                      styles.markerCircle,
                      { backgroundColor: data.color },
                    ]}
                  >
                    <Text style={styles.markerText}>{data.aqi}</Text>
                  </View>
                </View>
              </Marker>
            ))}
          </MapView>

          {/* Legend */}
          <View style={styles.legend}>
            <Text style={styles.legendTitle}>AQI Legend</Text>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, { backgroundColor: '#00E400' }]} />
              <Text style={styles.legendText}>Good (0-100)</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, { backgroundColor: '#FFFF00' }]} />
              <Text style={styles.legendText}>Moderate (101-200)</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, { backgroundColor: '#FF7E00' }]} />
              <Text style={styles.legendText}>Poor (201-300)</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, { backgroundColor: '#FF0000' }]} />
              <Text style={styles.legendText}>Severe (301-400)</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, { backgroundColor: '#8F3F97' }]} />
              <Text style={styles.legendText}>Danger (401+)</Text>
            </View>
          </View>
        </View>
      ) : (
        <View style={styles.errorContainer}>
          <Ionicons name="location-outline" size={64} color="#888" />
          <Text style={styles.errorText}>
            Unable to load map. Please check location permissions.
          </Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={requestLocationPermission}
          >
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Instructions */}
      <View style={styles.instructions}>
        <Text style={styles.instructionsTitle}>Google Maps Setup Required</Text>
        <Text style={styles.instructionsText}>
          To enable the heat map feature:
        </Text>
        <Text style={styles.instructionsText}>
          1. Get a Google Maps API key from Google Cloud Console
        </Text>
        <Text style={styles.instructionsText}>
          2. Enable Maps SDK for Android and iOS
        </Text>
        <Text style={styles.instructionsText}>
          3. Add the API key to your app configuration
        </Text>
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
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#888',
    marginTop: 16,
    fontSize: 16,
  },
  mapContainer: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  markerContainer: {
    alignItems: 'center',
  },
  markerCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#fff',
  },
  markerText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 14,
  },
  legend: {
    position: 'absolute',
    top: 16,
    right: 16,
    backgroundColor: 'rgba(26, 30, 59, 0.95)',
    padding: 12,
    borderRadius: 8,
    gap: 8,
  },
  legendTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  legendColor: {
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  legendText: {
    fontSize: 12,
    color: '#ccc',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  errorText: {
    fontSize: 16,
    color: '#888',
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 24,
  },
  retryButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  instructions: {
    backgroundColor: '#1A1E3B',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#2A2E4B',
  },
  instructionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4A90E2',
    marginBottom: 8,
  },
  instructionsText: {
    fontSize: 13,
    color: '#ccc',
    marginBottom: 4,
  },
});
