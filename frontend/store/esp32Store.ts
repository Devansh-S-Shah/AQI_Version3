import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ESP32_IP_KEY = 'esp32_ip_address';

interface SensorData {
  co: number; // MQ7 - Carbon Monoxide
  hazardousGas: number; // MQ-135
  temperature: number; // SHT4X
  humidity: number; // SHT4X
  airQuality: number; // SGP40
  pm10: number; // Particulate Matter
  timestamp: string;
}

interface ESP32State {
  esp32IP: string;
  isConnected: boolean;
  isIPLoaded: boolean;
  sensorData: SensorData | null;
  setESP32IP: (ip: string) => Promise<void>;
  setConnected: (status: boolean) => void;
  setSensorData: (data: SensorData) => void;
  loadESP32IP: () => Promise<void>;
}

export const useESP32Store = create<ESP32State>((set) => ({
  esp32IP: '192.168.1.100', // Default/placeholder IP
  isConnected: false,
  isIPLoaded: false,
  sensorData: null,

  setESP32IP: async (ip: string) => {
    try {
      await AsyncStorage.setItem(ESP32_IP_KEY, ip);
      console.log('✅ ESP32 IP persisted to AsyncStorage:', ip);
      set({ esp32IP: ip });
    } catch (error) {
      console.error('❌ Failed to persist ESP32 IP:', error);
      // Still update in-memory even if persistence fails
      set({ esp32IP: ip });
    }
  },

  loadESP32IP: async () => {
    try {
      const savedIP = await AsyncStorage.getItem(ESP32_IP_KEY);
      if (savedIP) {
        console.log('✅ Loaded ESP32 IP from AsyncStorage:', savedIP);
        set({ esp32IP: savedIP, isIPLoaded: true });
      } else {
        console.log('ℹ️ No saved ESP32 IP found, using default');
        set({ isIPLoaded: true });
      }
    } catch (error) {
      console.error('❌ Failed to load ESP32 IP:', error);
      set({ isIPLoaded: true });
    }
  },

  setConnected: (status: boolean) => set({ isConnected: status }),
  setSensorData: (data: SensorData) => set({ sensorData: data }),
}));
