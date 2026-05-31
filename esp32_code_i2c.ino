#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_SHT4x.h>
#include <Adafruit_SGP40.h>
#include "Adafruit_PM25AQI.h"  // <-- NEW: I2C PM2.5 library

// ========== WiFi Configuration ==========
//const char* ssid = "VDShome";
//const char* password = "Vinodshah9797";
const char* ssid = "Sim_Hotspot";
const char* password = "simonishah";

// ========== Web Server ==========
WebServer server(80);

// ========== Sensor Objects ==========
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_SGP40 sgp;
Adafruit_PM25AQI aqi = Adafruit_PM25AQI();  // <-- NEW: PM25 I2C object

// ========== Sensor Pins ==========
#define MQ7_PIN 36      // MQ-7 CO sensor (analog)
#define MQ135_PIN 34    // MQ-135 gas sensor (analog)
#define PULSE_OX_PIN 33 // Pulse oximeter signal pin

// I2C Pins for SHT4x + SGP40 + PMSA003I (all on same I2C bus)
#define I2C_SDA 21
#define I2C_SCL 22

// ========== Sensor Readings ==========
struct SensorData {
  float co;
  float hazardousGas;
  float temperature;
  float humidity;
  float airQuality;
  float pm25;
  float pm10;
  float oxygenLevel;
};

SensorData currentData;

bool pm25SensorFound = false;  // Track if PM sensor initialized

// ========== Setup Function ==========
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=================================");
  Serial.println("Air Quality Monitoring ESP32");
  Serial.println("=================================\n");

  // Initialize analog pins
  pinMode(MQ7_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  pinMode(PULSE_OX_PIN, INPUT);

  // Initialize I2C for ALL I2C sensors (SHT4x, SGP40, PMSA003I)
  Wire.begin(I2C_SDA, I2C_SCL);
  Serial.println("I2C initialized on pins:");
  Serial.print("  SDA: GPIO "); Serial.println(I2C_SDA);
  Serial.print("  SCL: GPIO "); Serial.println(I2C_SCL);

  // Initialize SHT4x (Temperature & Humidity)
  if (!sht4.begin()) {
    Serial.println("WARNING: SHT4x sensor not found!");
  } else {
    Serial.println("SHT4x sensor initialized");
    sht4.setPrecision(SHT4X_HIGH_PRECISION);
  }

  // Initialize SGP40 (Air Quality)
  if (!sgp.begin()) {
    Serial.println("WARNING: SGP40 sensor not found!");
  } else {
    Serial.println("SGP40 sensor initialized");
  }

  // ===== NEW: Initialize PMSA003I via I2C =====
  delay(1000);  // Give PM sensor time to boot up
  if (!aqi.begin_I2C()) {
    Serial.println("WARNING: PMSA003I not found on I2C!");
    Serial.println("  Check wiring: SDA->GPIO21, SCL->GPIO22");
    Serial.println("  Sensor needs 5V power");
    pm25SensorFound = false;
  } else {
    Serial.println("PMSA003I sensor initialized (I2C)");
    pm25SensorFound = true;
  }

  // Connect to WiFi
  connectToWiFi();

  // Setup web server routes
  server.on("/", handleRoot);
  server.on("/sensor-data", handleSensorData);
  server.on("/oxygen-level", handleOxygenLevel);
  server.onNotFound(handleNotFound);

  // Start server
  server.begin();
  Serial.println("\nWeb server started!");
  Serial.println("=================================\n");
}

// ========== Main Loop ==========
void loop() {
  server.handleClient();

  // Update sensor readings every 2 seconds
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 2000) {
    readAllSensors();
    lastUpdate = millis();
  }
}

// ========== WiFi Connection ==========
void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("\nEnter this IP in the app Settings: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi Connection Failed!");
    Serial.println("Please check your SSID and password");
  }
}

// ========== Read All Sensors ==========
void readAllSensors() {
  // Read MQ-7 (Carbon Monoxide)
  int mq7_raw = analogRead(MQ7_PIN);
  currentData.co = mapToRange(mq7_raw, 0, 4095, 0, 100);

  // Read MQ-135 (Hazardous Gas)
  int mq135_raw = analogRead(MQ135_PIN);
  currentData.hazardousGas = mapToRange(mq135_raw, 0, 4095, 0, 500);

  // Read SHT4x (Temperature & Humidity)
  sensors_event_t humidity, temp;
  if (sht4.getEvent(&humidity, &temp)) {
    currentData.temperature = temp.temperature;
    currentData.humidity = humidity.relative_humidity;

    // Read SGP40 (Air Quality) - use temp and humidity from SHT4x
    int32_t voc_index = sgp.measureVocIndex(temp.temperature, humidity.relative_humidity);
    if (voc_index >= 0) {
      currentData.airQuality = voc_index;
    } else {
      uint16_t rawValue = sgp.measureRaw(temp.temperature, humidity.relative_humidity);
      currentData.airQuality = rawValue;
    }
  } else {
    currentData.temperature = 25.5;
    currentData.humidity = 60.0;
    uint16_t rawValue = sgp.measureRaw(25.5, 60.0);
    currentData.airQuality = rawValue > 0 ? rawValue : 180.0;
  }

  // ===== NEW: Read PMSA003I via I2C =====
  if (pm25SensorFound) {
    PM25_AQI_Data data;
    if (aqi.read(&data)) {
      // Use "standard" particle readings (CF=1)
      currentData.pm25 = data.pm25_standard;
      currentData.pm10 = data.pm100_standard;

      Serial.print("PM2.5: ");
      Serial.print(currentData.pm25);
      Serial.print(" ug/m3, PM10: ");
      Serial.print(currentData.pm10);
      Serial.println(" ug/m3");
    } else {
      Serial.println("WARNING: Failed to read PM sensor data");
    }
  }

  // Read Pulse Oximeter
  int pulseOx_raw = analogRead(PULSE_OX_PIN);
  currentData.oxygenLevel = mapToRange(pulseOx_raw, 0, 4095, 85, 100);

  // Print readings
  printSensorData();
}

// ========== Helper Function: Map Values ==========
float mapToRange(float value, float inMin, float inMax, float outMin, float outMax) {
  return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
}

// ========== Print Sensor Data ==========
void printSensorData() {
  Serial.println("\n========== Sensor Readings ==========");
  Serial.print("CO Level:      "); Serial.print(currentData.co, 2); Serial.println(" ppm");
  Serial.print("Hazardous Gas: "); Serial.print(currentData.hazardousGas, 2); Serial.println(" ppm");
  Serial.print("Temperature:   "); Serial.print(currentData.temperature, 2); Serial.println(" C");
  Serial.print("Humidity:      "); Serial.print(currentData.humidity, 2); Serial.println(" %");
  Serial.print("Air Quality:   "); Serial.println(currentData.airQuality, 2);
  Serial.print("PM2.5:         "); Serial.print(currentData.pm25, 2); Serial.println(" ug/m3");
  Serial.print("PM10:          "); Serial.print(currentData.pm10, 2); Serial.println(" ug/m3");
  Serial.print("Oxygen Level:  "); Serial.print(currentData.oxygenLevel, 2); Serial.println(" %");
  Serial.println("====================================\n");
}

// ========== Web Server Handlers ==========
void handleRoot() {
  String html = "<html><body style='font-family: Arial; padding: 20px;'>";
  html += "<h1>Air Quality Monitoring System</h1>";
  html += "<h2>ESP32 Web Server</h2>";
  html += "<p><strong>Sensor Status:</strong></p>";
  html += "<ul>";
  html += "<li>CO Level: " + String(currentData.co, 2) + " ppm</li>";
  html += "<li>Hazardous Gas: " + String(currentData.hazardousGas, 2) + " ppm</li>";
  html += "<li>Temperature: " + String(currentData.temperature, 2) + " C</li>";
  html += "<li>Humidity: " + String(currentData.humidity, 2) + " %</li>";
  html += "<li>Air Quality: " + String(currentData.airQuality, 2) + "</li>";
  html += "<li>PM2.5: " + String(currentData.pm25, 2) + " ug/m3</li>";
  html += "<li>PM10: " + String(currentData.pm10, 2) + " ug/m3</li>";
  html += "<li>Oxygen Level: " + String(currentData.oxygenLevel, 2) + " %</li>";
  html += "</ul>";
  html += "<p>PM Sensor (I2C): " + String(pm25SensorFound ? "Connected" : "NOT FOUND") + "</p>";
  html += "<p><a href='/sensor-data'>View JSON Data</a></p>";
  html += "<p><a href='/oxygen-level'>View Oxygen Level JSON</a></p>";
  html += "</body></html>";

  server.send(200, "text/html", html);
}

void handleSensorData() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");

  String json = "{";
  json += "\"co\":" + String(currentData.co, 2) + ",";
  json += "\"hazardousGas\":" + String(currentData.hazardousGas, 2) + ",";
  json += "\"temperature\":" + String(currentData.temperature, 2) + ",";
  json += "\"humidity\":" + String(currentData.humidity, 2) + ",";
  json += "\"airQuality\":" + String(currentData.airQuality, 2) + ",";
  json += "\"pm25\":" + String(currentData.pm25, 2) + ",";
  json += "\"pm10\":" + String(currentData.pm10, 2);
  json += "}";

  server.send(200, "application/json", json);
  Serial.println("Sensor data sent to app");
}

void handleOxygenLevel() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");

  String json = "{";
  json += "\"oxygenLevel\":" + String(currentData.oxygenLevel, 2);
  json += "}";

  server.send(200, "application/json", json);
  Serial.println("Oxygen level sent to app");
}

void handleNotFound() {
  server.send(404, "text/plain", "404: Not Found");
}
