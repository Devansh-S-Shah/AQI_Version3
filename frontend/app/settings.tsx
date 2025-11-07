import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  TextInput,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useESP32Store } from '../store/esp32Store';

export default function Settings() {
  const router = useRouter();
  const { esp32IP, setESP32IP } = useESP32Store();
  const [ipInput, setIpInput] = useState(esp32IP);
  const [notifications, setNotifications] = useState(true);
  const [autoSync, setAutoSync] = useState(true);
  const [darkMode, setDarkMode] = useState(true);

  const handleSaveIP = () => {
    // Basic IP validation
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (ipRegex.test(ipInput)) {
      console.log('Saving ESP32 IP:', ipInput);
      setESP32IP(ipInput);
      Alert.alert(
        'Success', 
        `ESP32 IP address saved successfully!\n\nIP: ${ipInput}\n\nPlease restart the app for changes to take effect.`
      );
    } else {
      Alert.alert('Error', 'Please enter a valid IP address');
    }
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
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content}>
        {/* ESP32 Configuration */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Device Connection</Text>
          
          <View style={styles.card}>
            <Text style={styles.label}>ESP32 IP Address</Text>
            <TextInput
              style={styles.input}
              placeholder="192.168.1.100"
              placeholderTextColor="#888"
              value={ipInput}
              onChangeText={setIpInput}
              keyboardType="numeric"
            />
            <TouchableOpacity
              style={styles.saveButton}
              onPress={handleSaveIP}
            >
              <Text style={styles.saveButtonText}>Save IP Address</Text>
            </TouchableOpacity>
            
            <Text style={styles.helpText}>
              Enter the IP address of your ESP32 device. You can find this in
              your ESP32's serial monitor or router's connected devices list.
            </Text>
          </View>
        </View>

        {/* Notifications */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Ionicons name="notifications-outline" size={24} color="#4A90E2" />
              <View style={styles.settingItemText}>
                <Text style={styles.settingItemTitle}>Push Notifications</Text>
                <Text style={styles.settingItemDescription}>
                  Get alerts for poor air quality
                </Text>
              </View>
            </View>
            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{ false: '#2A2E4B', true: '#4A90E2' }}
              thumbColor={notifications ? '#fff' : '#888'}
            />
          </View>
        </View>

        {/* Data & Sync */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Data & Sync</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Ionicons name="sync-outline" size={24} color="#4A90E2" />
              <View style={styles.settingItemText}>
                <Text style={styles.settingItemTitle}>Auto-Sync</Text>
                <Text style={styles.settingItemDescription}>
                  Automatically sync data with cloud
                </Text>
              </View>
            </View>
            <Switch
              value={autoSync}
              onValueChange={setAutoSync}
              trackColor={{ false: '#2A2E4B', true: '#4A90E2' }}
              thumbColor={autoSync ? '#fff' : '#888'}
            />
          </View>

          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="cloud-download-outline" size={24} color="#4A90E2" />
            <Text style={styles.actionItemText}>Export Data</Text>
            <Ionicons name="chevron-forward" size={24} color="#888" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="trash-outline" size={24} color="#FF4444" />
            <Text style={[styles.actionItemText, { color: '#FF4444' }]}>
              Clear All Data
            </Text>
            <Ionicons name="chevron-forward" size={24} color="#888" />
          </TouchableOpacity>
        </View>

        {/* Appearance */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Appearance</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Ionicons name="moon-outline" size={24} color="#4A90E2" />
              <View style={styles.settingItemText}>
                <Text style={styles.settingItemTitle}>Dark Mode</Text>
                <Text style={styles.settingItemDescription}>
                  Use dark theme
                </Text>
              </View>
            </View>
            <Switch
              value={darkMode}
              onValueChange={setDarkMode}
              trackColor={{ false: '#2A2E4B', true: '#4A90E2' }}
              thumbColor={darkMode ? '#fff' : '#888'}
            />
          </View>
        </View>

        {/* Units */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Units</Text>
          
          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="thermometer-outline" size={24} color="#4A90E2" />
            <Text style={styles.actionItemText}>Temperature Unit: °C</Text>
            <Ionicons name="chevron-forward" size={24} color="#888" />
          </TouchableOpacity>
        </View>

        {/* About */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          
          <TouchableOpacity
            style={styles.actionItem}
            onPress={() => router.push('/about')}
          >
            <Ionicons name="information-circle-outline" size={24} color="#4A90E2" />
            <Text style={styles.actionItemText}>About the App</Text>
            <Ionicons name="chevron-forward" size={24} color="#888" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="document-text-outline" size={24} color="#4A90E2" />
            <Text style={styles.actionItemText}>Terms & Privacy</Text>
            <Ionicons name="chevron-forward" size={24} color="#888" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="help-circle-outline" size={24} color="#4A90E2" />
            <Text style={styles.actionItemText}>Help & Support</Text>
            <Ionicons name="chevron-forward" size={24} color="#888" />
          </TouchableOpacity>
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
  },
  section: {
    marginTop: 24,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#888',
    marginBottom: 12,
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: '#1A1E3B',
    borderRadius: 12,
    padding: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#0A0E27',
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#2A2E4B',
    marginBottom: 12,
  },
  saveButton: {
    backgroundColor: '#4A90E2',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  helpText: {
    fontSize: 12,
    color: '#888',
    lineHeight: 18,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1A1E3B',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  settingItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  settingItemText: {
    flex: 1,
  },
  settingItemTitle: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 4,
  },
  settingItemDescription: {
    fontSize: 13,
    color: '#888',
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1E3B',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    gap: 12,
  },
  actionItemText: {
    flex: 1,
    fontSize: 16,
    color: '#fff',
  },
});
