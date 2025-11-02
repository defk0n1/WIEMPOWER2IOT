#!/usr/bin/env python3
import requests
import json
import time
import random
import os
from datetime import datetime

class NPKSensor:
    def __init__(self, gateway_url, zone_id="zone-1"):
        self.gateway_url = gateway_url  # Node-RED endpoint
        self.client_id = f"npk-sensor-{random.randint(1000, 9999)}"
        self.zone_id = zone_id
        
        # Sensor configuration
        self.base_nitrogen = 45.0
        self.base_phosphorus = 30.0
        self.base_potassium = 150.0
        self.noise_level = 2.0
        
    def read_npk(self):
        """Simulate NPK reading"""
        nitrogen = self.base_nitrogen + random.gauss(0, self.noise_level)
        phosphorus = self.base_phosphorus + random.gauss(0, self.noise_level)
        potassium = self.base_potassium + random.gauss(0, self.noise_level)
        
        return {
            'nitrogen': round(max(0, nitrogen), 2),
            'phosphorus': round(max(0, phosphorus), 2),
            'potassium': round(max(0, potassium), 2)
        }
    
    def send_to_gateway(self, nutrient_type, value):
        """Send data to Node-RED gateway via HTTP"""
        payload = {
            "sensor_id": self.client_id,
            "zone_id": self.zone_id,
            "nutrient": nutrient_type,
            "value": value,
            "unit": "mg/kg",
            "depth_cm": int(os.getenv("SENSOR_DEPTH_CM", "15")),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.gateway_url}/sensor/npk",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✓ Sent {nutrient_type}: {value} mg/kg to gateway")
                return True
            else:
                print(f"✗ Gateway error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error to gateway: {e}")
            return False
    
    def publish_reading(self):
        """Read and send NPK data"""
        npk = self.read_npk()
        
        success = True
        success &= self.send_to_gateway("nitrogen", npk['nitrogen'])
        success &= self.send_to_gateway("phosphorus", npk['phosphorus'])
        success &= self.send_to_gateway("potassium", npk['potassium'])
        
        if success:
            print(f"🌱 NPK: N={npk['nitrogen']:.2f}, P={npk['phosphorus']:.2f}, K={npk['potassium']:.2f} mg/kg")
        
        return success
    
    def run(self, interval=5):
        print(f"🌱 Starting NPK Sensor → Node-RED Gateway")
        print(f"📡 Gateway URL: {self.gateway_url}")
        
        while True:
            try:
                self.publish_reading()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n⏹ Stopping NPK sensor...")
                break

if __name__ == "__main__":
    gateway_url = os.getenv("GATEWAY_URL", "http://node-red-gateway:1880")
    zone_id = os.getenv("ZONE_ID", "zone-1")
    interval = int(os.getenv("SENSOR_INTERVAL", "5"))
    
    sensor = NPKSensor(gateway_url, zone_id)
    sensor.run(interval)