import { create } from 'zustand';

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
  sensorData: SensorData | null;
  setESP32IP: (ip: string) => void;
  setConnected: (status: boolean) => void;
  setSensorData: (data: SensorData) => void;
}

export const useESP32Store = create<ESP32State>((set) => ({
  esp32IP: '192.168.1.100', // Default/placeholder IP
  isConnected: false,
  sensorData: null,

  setESP32IP: (ip: string) => set({ esp32IP: ip }),
  setConnected: (status: boolean) => set({ isConnected: status }),
  setSensorData: (data: SensorData) => set({ sensorData: data }),
}));
