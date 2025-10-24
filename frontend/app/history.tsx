import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { FlashList } from '@shopify/flash-list';
import { format } from 'date-fns';
import { useAuthStore } from '../store/authStore';
import { getAQICategory } from '../utils/aqiCalculator';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface HistoryItem {
  _id: string;
  userId: string;
  aqi: number;
  timestamp: string;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export default function History() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch(
        `${EXPO_PUBLIC_BACKEND_URL}/api/history/${user?.id}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setHistory(data.history || []);
      } else {
        // Use mock data if API fails
        setHistory(generateMockData());
      }
    } catch (error) {
      console.error('Error fetching history:', error);
      // Use mock data as fallback
      setHistory(generateMockData());
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const generateMockData = (): HistoryItem[] => {
    const mockData: HistoryItem[] = [];
    const now = new Date();
    
    for (let i = 0; i < 10; i++) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      date.setHours(date.getHours() - (i * 2));
      
      mockData.push({
        _id: `mock-${i}`,
        userId: user?.id || 'mock-user',
        aqi: Math.floor(Math.random() * 400) + 50,
        timestamp: date.toISOString(),
        location: {
          latitude: 0,
          longitude: 0,
        },
      });
    }
    
    return mockData;
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchHistory();
  };

  const renderHistoryItem = ({ item }: { item: HistoryItem }) => {
    const aqiCategory = getAQICategory(item.aqi);
    const date = new Date(item.timestamp);

    return (
      <TouchableOpacity style={styles.historyCard}>
        <View style={styles.historyHeader}>
          <View
            style={[
              styles.aqiBadge,
              { backgroundColor: aqiCategory.color + '20' },
            ]}
          >
            <Text style={[styles.aqiValue, { color: aqiCategory.color }]}>
              {item.aqi}
            </Text>
          </View>
          <View style={styles.historyInfo}>
            <Text style={styles.historyCategory}>
              {aqiCategory.category}
            </Text>
            <Text style={styles.historyDate}>
              {format(date, 'MMM dd, yyyy')}
            </Text>
            <Text style={styles.historyTime}>
              {format(date, 'hh:mm a')}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#888" />
        </View>
      </TouchableOpacity>
    );
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
        <Text style={styles.headerTitle}>History</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4A90E2" />
        </View>
      ) : history.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="time-outline" size={64} color="#888" />
          <Text style={styles.emptyText}>No history yet</Text>
          <Text style={styles.emptySubtext}>
            Your air quality readings will appear here
          </Text>
        </View>
      ) : (
        <View style={styles.listContainer}>
          <FlashList
            data={history}
            renderItem={renderHistoryItem}
            estimatedItemSize={100}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                tintColor="#4A90E2"
              />
            }
            contentContainerStyle={styles.listContent}
          />
        </View>
      )}

      {/* Stats Summary */}
      {!loading && history.length > 0 && (
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Total Readings</Text>
            <Text style={styles.statValue}>{history.length}</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Average AQI</Text>
            <Text style={styles.statValue}>
              {Math.round(
                history.reduce((sum, item) => sum + item.aqi, 0) / history.length
              )}
            </Text>
          </View>
        </View>
      )}
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#888',
    marginTop: 8,
    textAlign: 'center',
  },
  listContainer: {
    flex: 1,
  },
  listContent: {
    padding: 16,
  },
  historyCard: {
    backgroundColor: '#1A1E3B',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  historyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  aqiBadge: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  aqiValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  historyInfo: {
    flex: 1,
  },
  historyCategory: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  historyDate: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 2,
  },
  historyTime: {
    fontSize: 12,
    color: '#888',
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#1A1E3B',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#2A2E4B',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statDivider: {
    width: 1,
    backgroundColor: '#2A2E4B',
  },
  statLabel: {
    fontSize: 13,
    color: '#888',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90E2',
  },
});
