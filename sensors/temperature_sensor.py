#!/usr/bin/env python3
import requests
import json
import time
import random
import os
from datetime import datetime

class TemperatureSensor:
    def __init__(self, gateway_url, zone_id="zone-1"):
        self.gateway_url = gateway_url
        self.client_id = f"temp-sensor-{random.randint(1000, 9999)}"
        self.zone_id = zone_id
        self.rom_code = f"28-{random.randint(100000000000, 999999999999):012X}"
        
        self.base_temp = 22.0
        self.resolution = 0.0625
        
    def read_temperature(self):
        """Simulate DS18B20 reading"""
        variation = random.gauss(0, 0.5)
        temperature = self.base_temp + variation
        temperature = round(temperature / self.resolution) * self.resolution
        return temperature
    
    def send_to_gateway(self):
        """Send temperature to Node-RED gateway"""
        temperature = self.read_temperature()
        
        payload = {
            "sensor_id": self.client_id,
            "sensor_type": "DS18B20",
            "rom_code": self.rom_code,
            "zone_id": self.zone_id,
            "value": round(temperature, 4),
            "unit": "°C",
            "depth_cm": int(os.getenv("SENSOR_DEPTH_CM", "10")),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.gateway_url}/sensor/temperature",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"🌡️  Temperature: {temperature:.4f}°C → Gateway")
                return True
            else:
                print(f"✗ Gateway error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def run(self, interval=3):
        print(f"🌡️  Starting Temperature Sensor → Node-RED Gateway")
        print(f"📡 Gateway URL: {self.gateway_url}")
        
        while True:
            try:
                self.send_to_gateway()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n⏹ Stopping Temperature sensor...")
                break

if __name__ == "__main__":
    gateway_url = os.getenv("GATEWAY_URL", "http://node-red-gateway:1880")
    zone_id = os.getenv("ZONE_ID", "zone-1")
    interval = int(os.getenv("SENSOR_INTERVAL", "3"))
    
    sensor = TemperatureSensor(gateway_url, zone_id)
    sensor.run(interval)