#!/usr/bin/env python3
"""
NPK Sensor Emulator
Simulates a soil NPK (Nitrogen, Phosphorus, Potassium) sensor
with Modbus RTU/RS485 protocol characteristics
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import os
import math
from datetime import datetime

class NPKSensor:
    def __init__(self, broker, port=1883, username=None, password=None):
        self.broker = broker
        self.port = port
        self.client_id = f"npk-sensor-{random.randint(1000, 9999)}"
        self.topic = "sensors/npk"
        self.status_topic = "sensors/npk/status"
        
        # Realistic NPK ranges (mg/kg)
        self.nitrogen_base = 45.0  # 20-80 mg/kg typical
        self.phosphorus_base = 30.0  # 10-50 mg/kg typical
        self.potassium_base = 150.0  # 80-250 mg/kg typical
        
        # Sensor characteristics
        self.accuracy = 0.95  # 95% accuracy
        self.drift_rate = 0.001  # Slow environmental drift
        self.noise_level = 2.0  # ±2 mg/kg noise
        
        # Connection simulation
        self.connection_stability = 0.95  # 95% uptime
        self.connected = False
        self.reconnect_delay = 5
        
        # Modbus simulation
        self.modbus_address = 0x01
        self.register_delay = 0.1  # 100ms read delay
        
        # Setup MQTT client
        self.client = mqtt.Client(self.client_id)
        if username and password:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✓ NPK Sensor connected to MQTT broker at {self.broker}:{self.port}")
            status = {
                "sensor": "NPK",
                "status": "online",
                "modbus_address": hex(self.modbus_address),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.client.publish(self.status_topic, json.dumps(status), qos=1, retain=True)
        else:
            print(f"✗ Connection failed with code {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"✗ NPK Sensor disconnected (rc: {rc})")
        
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
        return True
        
    def simulate_connection_drop(self):
        """Simulate realistic connection drops"""
        if random.random() > self.connection_stability:
            print("⚠ Simulating connection drop...")
            self.client.disconnect()
            time.sleep(self.reconnect_delay)
            self.connect()
            
    def read_npk_values(self):
        """Simulate realistic NPK sensor readings with Modbus delay"""
        time.sleep(self.register_delay)  # Modbus read delay
        
        # Add temporal variation (slow changes)
        time_factor = time.time() / 10000
        
        # Nitrogen reading with drift and noise
        n_drift = math.sin(time_factor) * 5
        nitrogen = self.nitrogen_base + n_drift + random.gauss(0, self.noise_level)
        nitrogen = max(0, min(100, nitrogen))  # Clamp to valid range
        
        # Phosphorus reading
        p_drift = math.cos(time_factor * 0.7) * 3
        phosphorus = self.phosphorus_base + p_drift + random.gauss(0, self.noise_level)
        phosphorus = max(0, min(60, phosphorus))
        
        # Potassium reading
        k_drift = math.sin(time_factor * 0.5) * 10
        potassium = self.potassium_base + k_drift + random.gauss(0, self.noise_level)
        potassium = max(0, min(300, potassium))
        
        # Apply sensor accuracy
        if random.random() > self.accuracy:
            nitrogen *= random.uniform(0.9, 1.1)
            phosphorus *= random.uniform(0.9, 1.1)
            potassium *= random.uniform(0.9, 1.1)
            
        return {
            "nitrogen": round(nitrogen, 2),
            "phosphorus": round(phosphorus, 2),
            "potassium": round(potassium, 2)
        }
        
    def publish_reading(self):
        """Publish sensor reading to MQTT"""
        if not self.connected:
            return False
            
        npk_values = self.read_npk_values()
        
        payload = {
            "sensor_id": self.client_id,
            "sensor_type": "NPK",
            "modbus_address": hex(self.modbus_address),
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "nitrogen_mg_kg": npk_values["nitrogen"],
                "phosphorus_mg_kg": npk_values["phosphorus"],
                "potassium_mg_kg": npk_values["potassium"]
            },
            "unit": "mg/kg",
            "protocol": "Modbus RTU (RS485)"
        }
        
        result = self.client.publish(self.topic, json.dumps(payload), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"📊 NPK Reading: N={{npk_values['nitrogen']:.2f}}, "
                  f"P={{npk_values['phosphorus']:.2f}}, "
                  f"K={{npk_values['potassium']:.2f}} mg/kg")
            return True
        else:
            print(f"✗ Publish failed: {result.rc}")
            return False
            
    def run(self, interval=5):
        """Main sensor loop"""
        print(f"🌱 Starting NPK Sensor (Modbus Address: {{hex(self.modbus_address)}})")
        
        if not self.connect():
            print("✗ Failed to connect to MQTT broker")
            return
            
        try:
            while True:
                if self.connected:
                    self.publish_reading()
                    self.simulate_connection_drop()
                else:
                    print("⚠ Reconnecting...")
                    self.connect()
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹ Stopping NPK sensor...")
            status = {
                "sensor": "NPK",
                "status": "offline",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.client.publish(self.status_topic, json.dumps(status), qos=1, retain=True)
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    interval = int(os.getenv("SENSOR_INTERVAL", "5"))
    username = os.getenv("MQTT_USER", None)
    password = os.getenv("MQTT_PASSWORD", None)
    
    sensor = NPKSensor(broker, port, username, password)
    sensor.run(interval)