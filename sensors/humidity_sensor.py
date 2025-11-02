#!/usr/bin/env python3
"""
Humidity Sensor Emulator
Simulates a DHT22 (AM2302) digital humidity and temperature sensor
Sends data to Node-RED gateway via HTTP
"""

import requests
import json
import time
import random
import os
from datetime import datetime

class HumiditySensor:
    def __init__(self, gateway_url, zone_id="zone-1"):
        self.gateway_url = gateway_url
        self.client_id = f"humidity-sensor-{random.randint(1000, 9999)}"
        self.zone_id = zone_id
        self.sensor_model = "DHT22"  # AM2302
        
        # DHT22 characteristics
        self.base_humidity = 65.0  # Base relative humidity %
        self.base_temp = 22.0      # DHT22 also reads temperature
        
        # DHT22 specifications
        self.humidity_range = (0.0, 100.0)
        self.temp_range = (-40.0, 80.0)
        self.humidity_accuracy = 2.0  # ±2% RH
        self.temp_accuracy = 0.5      # ±0.5°C
        self.humidity_resolution = 0.1  # 0.1% RH
        self.temp_resolution = 0.1      # 0.1°C
        
        # Environmental simulation
        self.time_of_day_factor = 0.0
        
    def simulate_environmental_conditions(self):
        """Simulate humidity changes based on time and weather"""
        # Simulate daily humidity cycle (higher at night, lower during day)
        hour = datetime.utcnow().hour
        
        # Night (0-6): Higher humidity
        if 0 <= hour < 6:
            self.time_of_day_factor = random.uniform(5, 10)
        # Morning (6-12): Decreasing humidity
        elif 6 <= hour < 12:
            self.time_of_day_factor = random.uniform(0, 5)
        # Afternoon (12-18): Lower humidity
        elif 12 <= hour < 18:
            self.time_of_day_factor = random.uniform(-10, -5)
        # Evening (18-24): Increasing humidity
        else:
            self.time_of_day_factor = random.uniform(-5, 0)
    
    def read_humidity(self):
        """Simulate DHT22 humidity reading"""
        self.simulate_environmental_conditions()
        
        # Base humidity with daily variation
        humidity = self.base_humidity + self.time_of_day_factor
        
        # Add random variations (weather changes, irrigation effects)
        humidity += random.gauss(0, 3.0)
        
        # Simulate irrigation impact (occasional spike)
        if random.random() < 0.05:  # 5% chance of irrigation event
            humidity += random.uniform(5, 15)
        
        # Apply resolution
        humidity = round(humidity / self.humidity_resolution) * self.humidity_resolution
        
        # Apply accuracy deviation
        if random.random() > 0.95:
            humidity += random.uniform(-self.humidity_accuracy, self.humidity_accuracy)
        
        # Clamp to sensor range
        humidity = max(self.humidity_range[0], min(self.humidity_range[1], humidity))
        
        return round(humidity, 1)
    
    def read_temperature(self):
        """DHT22 also reads air temperature"""
        # Temperature with small variation
        temperature = self.base_temp + random.gauss(0, 1.0)
        
        # Apply resolution
        temperature = round(temperature / self.temp_resolution) * self.temp_resolution
        
        # Apply accuracy deviation
        if random.random() > 0.95:
            temperature += random.uniform(-self.temp_accuracy, self.temp_accuracy)
        
        # Clamp to sensor range
        temperature = max(self.temp_range[0], min(self.temp_range[1], temperature))
        
        return round(temperature, 1)
    
    def calculate_heat_index(self, temperature_c, humidity):
        """Calculate heat index (feels like temperature)"""
        # Convert to Fahrenheit for calculation
        T = temperature_c * 9/5 + 32
        RH = humidity
        
        # Simplified heat index formula
        if T < 80:
            return temperature_c  # Heat index only relevant at higher temps
        
        HI = -42.379 + 2.04901523*T + 10.14333127*RH - 0.22475541*T*RH
        HI += -0.00683783*T*T - 0.05481717*RH*RH + 0.00122874*T*T*RH
        HI += 0.00085282*T*RH*RH - 0.00000199*T*T*RH*RH
        
        # Convert back to Celsius
        return round((HI - 32) * 5/9, 1)
    
    def calculate_dew_point(self, temperature_c, humidity):
        """Calculate dew point temperature"""
        # Magnus formula
        a = 17.27
        b = 237.7
        
        alpha = ((a * temperature_c) / (b + temperature_c)) + math.log(humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        return round(dew_point, 1)
    
    def send_to_gateway(self):
        """Send humidity data to Node-RED gateway"""
        humidity = self.read_humidity()
        temperature = self.read_temperature()
        
        # Calculate derived values
        heat_index = self.calculate_heat_index(temperature, humidity)
        
        # Use simple approximation for dew point (avoid math import)
        dew_point = temperature - ((100 - humidity) / 5.0)
        dew_point = round(dew_point, 1)
        
        payload = {
            "sensor_id": self.client_id,
            "sensor_type": self.sensor_model,
            "zone_id": self.zone_id,
            "humidity": humidity,
            "temperature": temperature,
            "heat_index": heat_index,
            "dew_point": dew_point,
            "unit": "%",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.gateway_url}/sensor/humidity",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"🌫️  Humidity: {humidity}% RH, Temp: {temperature}°C, Dew Point: {dew_point}°C → Gateway")
                return True
            else:
                print(f"✗ Gateway error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def run(self, interval=5):
        print(f"🌫️  Starting Humidity Sensor ({self.sensor_model}) → Node-RED Gateway")
        print(f"📡 Gateway URL: {self.gateway_url}")
        print(f"🏷️  Zone ID: {self.zone_id}")
        
        while True:
            try:
                self.send_to_gateway()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n⏹ Stopping Humidity sensor...")
                break

if __name__ == "__main__":
    gateway_url = os.getenv("GATEWAY_URL", "http://node-red-gateway:1880")
    zone_id = os.getenv("ZONE_ID", "zone-1")
    interval = int(os.getenv("SENSOR_INTERVAL", "5"))
    
    sensor = HumiditySensor(gateway_url, zone_id)
    sensor.run(interval)