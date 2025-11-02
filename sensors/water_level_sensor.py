#!/usr/bin/env python3
import requests
import json
import time
import random
import os
import math
from datetime import datetime

class WaterLevelSensor:
    def __init__(self, gateway_url):
        self.gateway_url = gateway_url
        self.client_id = f"water-sensor-{random.randint(1000, 9999)}"
        self.sensor_model = random.choice(["HC-SR04", "JSN-SR04T", "Capacitive"])
        
        self.tank_height_cm = 200.0
        self.current_level_percent = 60.0
        self.noise_level = 0.5
        
    def read_water_level(self):
        """Simulate water level reading"""
        # Simple variation
        self.current_level_percent += random.gauss(0, 0.5)
        self.current_level_percent = max(0, min(100, self.current_level_percent))
        
        water_height_cm = (self.current_level_percent / 100.0) * self.tank_height_cm
        
        return {
            "level_percent": round(self.current_level_percent, 2),
            "water_height_cm": round(water_height_cm, 2)
        }
    
    def send_to_gateway(self):
        """Send water level to Node-RED gateway"""
        reading = self.read_water_level()
        
        tank_radius_cm = float(os.getenv("TANK_RADIUS_CM", "50.0"))
        tank_capacity_liters = (math.pi * tank_radius_cm**2 * self.tank_height_cm) / 1000
        volume_liters = (math.pi * tank_radius_cm**2 * reading["water_height_cm"]) / 1000
        
        payload = {
            "sensor_id": self.client_id,
            "sensor_type": self.sensor_model,
            "level_percent": reading["level_percent"],
            "current_liters": round(volume_liters, 2),
            "capacity_liters": round(tank_capacity_liters, 2),
            "water_height_cm": reading["water_height_cm"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.gateway_url}/sensor/water",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"💧 Water: {reading['level_percent']:.2f}% ({volume_liters:.2f}L) → Gateway")
                return True
            else:
                print(f"✗ Gateway error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def run(self, interval=4):
        print(f"💧 Starting Water Level Sensor → Node-RED Gateway")
        print(f"📡 Gateway URL: {self.gateway_url}")
        
        while True:
            try:
                self.send_to_gateway()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n⏹ Stopping Water sensor...")
                break

if __name__ == "__main__":
    gateway_url = os.getenv("GATEWAY_URL", "http://node-red-gateway:1880")
    interval = int(os.getenv("SENSOR_INTERVAL", "4"))
    
    sensor = WaterLevelSensor(gateway_url)
    sensor.run(interval)