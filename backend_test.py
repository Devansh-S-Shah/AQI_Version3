#!/usr/bin/env python3
"""
Air Quality Monitoring App Backend API Tests
Tests all backend endpoints for functionality and data integrity
"""

import requests
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from frontend environment
BACKEND_URL = "https://clearbreathe-app.preview.emergentagent.com/api"

# Test data
TEST_USER = {
    "username": "airquality_testuser",
    "password": "testpass123"
}

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_id = None
        self.session = requests.Session()
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response and not success:
            print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
        print()
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True, f"Service healthy with {data.get('users_count', 0)} users")
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid health response format", response)
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=TEST_USER
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "user" in data:
                    self.test_user_id = data["user"]["id"]
                    self.log_result("User Registration", True, f"User registered with ID: {self.test_user_id}")
                    return True
                else:
                    self.log_result("User Registration", False, "Invalid registration response", response)
            elif response.status_code == 400:
                # User might already exist, try to continue with login
                self.log_result("User Registration", True, "User already exists (continuing with login)")
                return True
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("User Registration", False, f"Error: {str(e)}")
        return False
    
    def test_user_login(self):
        """Test user login"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=TEST_USER
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "user" in data:
                    self.test_user_id = data["user"]["id"]
                    self.log_result("User Login", True, f"Login successful for user: {data['user']['username']}")
                    return True
                else:
                    self.log_result("User Login", False, "Invalid login response", response)
            else:
                self.log_result("User Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("User Login", False, f"Error: {str(e)}")
        return False
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            invalid_user = {"username": "nonexistent", "password": "wrongpass"}
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=invalid_user
            )
            
            if response.status_code == 401:
                self.log_result("Invalid Login Test", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_result("Invalid Login Test", False, f"Expected 401, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Invalid Login Test", False, f"Error: {str(e)}")
        return False
    
    def test_sensor_data_save(self):
        """Test saving sensor data"""
        if not self.test_user_id:
            self.log_result("Sensor Data Save", False, "No user ID available")
            return False
        
        try:
            sensor_data = {
                "userId": self.test_user_id,
                "readings": {
                    "co": 2.5,
                    "hazardousGas": 1.2,
                    "temperature": 25.5,
                    "humidity": 60.0,
                    "airQuality": 85.0,
                    "pm10": 15.5
                },
                "aqi": 85,
                "location": {
                    "latitude": 37.7749,
                    "longitude": -122.4194
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/sensor-data",
                json=sensor_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.log_result("Sensor Data Save", True, f"Sensor data saved with AQI: {data['data']['aqi']}")
                    return True
                else:
                    self.log_result("Sensor Data Save", False, "Invalid save response", response)
            else:
                self.log_result("Sensor Data Save", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Sensor Data Save", False, f"Error: {str(e)}")
        return False
    
    def test_sensor_data_get(self):
        """Test retrieving sensor data"""
        if not self.test_user_id:
            self.log_result("Sensor Data Get", False, "No user ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/sensor-data/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    records_count = len(data["data"])
                    self.log_result("Sensor Data Get", True, f"Retrieved {records_count} sensor records")
                    return True
                else:
                    self.log_result("Sensor Data Get", False, "Invalid get response", response)
            else:
                self.log_result("Sensor Data Get", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Sensor Data Get", False, f"Error: {str(e)}")
        return False
    
    def test_cough_record_save(self):
        """Test saving cough record"""
        if not self.test_user_id:
            self.log_result("Cough Record Save", False, "No user ID available")
            return False
        
        try:
            cough_data = {
                "userId": self.test_user_id,
                "audioData": "base64_encoded_audio_data_placeholder",
                "severity": "moderate",
                "coughType": "dry",
                "diagnosis": "possible respiratory irritation"
            }
            
            response = self.session.post(
                f"{self.base_url}/cough-record",
                json=cough_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.log_result("Cough Record Save", True, f"Cough record saved with severity: {data['data']['severity']}")
                    return True
                else:
                    self.log_result("Cough Record Save", False, "Invalid save response", response)
            else:
                self.log_result("Cough Record Save", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Cough Record Save", False, f"Error: {str(e)}")
        return False
    
    def test_cough_records_get(self):
        """Test retrieving cough records"""
        if not self.test_user_id:
            self.log_result("Cough Records Get", False, "No user ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/cough-records/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    records_count = len(data["data"])
                    self.log_result("Cough Records Get", True, f"Retrieved {records_count} cough records")
                    return True
                else:
                    self.log_result("Cough Records Get", False, "Invalid get response", response)
            else:
                self.log_result("Cough Records Get", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Cough Records Get", False, f"Error: {str(e)}")
        return False
    
    def test_oxygen_level_save(self):
        """Test saving oxygen level"""
        if not self.test_user_id:
            self.log_result("Oxygen Level Save", False, "No user ID available")
            return False
        
        try:
            oxygen_data = {
                "userId": self.test_user_id,
                "oxygenLevel": 98.5,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/oxygen-level",
                json=oxygen_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.log_result("Oxygen Level Save", True, f"Oxygen level saved: {data['data']['oxygenLevel']}%")
                    return True
                else:
                    self.log_result("Oxygen Level Save", False, "Invalid save response", response)
            else:
                self.log_result("Oxygen Level Save", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Oxygen Level Save", False, f"Error: {str(e)}")
        return False
    
    def test_oxygen_levels_get(self):
        """Test retrieving oxygen levels"""
        if not self.test_user_id:
            self.log_result("Oxygen Levels Get", False, "No user ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/oxygen-levels/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    records_count = len(data["data"])
                    self.log_result("Oxygen Levels Get", True, f"Retrieved {records_count} oxygen level records")
                    return True
                else:
                    self.log_result("Oxygen Levels Get", False, "Invalid get response", response)
            else:
                self.log_result("Oxygen Levels Get", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Oxygen Levels Get", False, f"Error: {str(e)}")
        return False
    
    def test_history_get(self):
        """Test retrieving user history"""
        if not self.test_user_id:
            self.log_result("History Get", False, "No user ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/history/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "history" in data:
                    history_count = len(data["history"])
                    self.log_result("History Get", True, f"Retrieved {history_count} history records")
                    return True
                else:
                    self.log_result("History Get", False, "Invalid history response", response)
            else:
                self.log_result("History Get", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("History Get", False, f"Error: {str(e)}")
        return False
    
    def test_heatmap_data_get(self):
        """Test retrieving heatmap data"""
        try:
            response = self.session.get(f"{self.base_url}/heatmap-data")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    data_points = len(data["data"])
                    self.log_result("Heatmap Data Get", True, f"Retrieved {data_points} heatmap data points")
                    return True
                else:
                    self.log_result("Heatmap Data Get", False, "Invalid heatmap response", response)
            else:
                self.log_result("Heatmap Data Get", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Heatmap Data Get", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("AIR QUALITY MONITORING APP - BACKEND API TESTS")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Invalid Login Test", self.test_invalid_login),
            ("Sensor Data Save", self.test_sensor_data_save),
            ("Sensor Data Get", self.test_sensor_data_get),
            ("Cough Record Save", self.test_cough_record_save),
            ("Cough Records Get", self.test_cough_records_get),
            ("Oxygen Level Save", self.test_oxygen_level_save),
            ("Oxygen Levels Get", self.test_oxygen_levels_get),
            ("History Get", self.test_history_get),
            ("Heatmap Data Get", self.test_heatmap_data_get)
        ]
        
        for test_name, test_func in tests:
            test_func()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)