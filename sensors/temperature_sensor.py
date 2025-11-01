#!/usr/bin/env python3
"""
Temperature Sensor Emulator
Simulates a DS18B20-style 1-Wire digital temperature sensor
with realistic environmental behavior
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import os
import math
from datetime import datetime

class TemperatureSensor:
    def __init__(self, broker, port=1883, username=None, password=None):
        self.broker = broker
        self.port = port
        self.client_id = f"temp-sensor-{random.randint(1000, 9999)}"
        self.topic = "sensors/temperature"
        self.status_topic = "sensors/temperature/status"
        
        self.base_temp = 22.0
        self.daily_variation = 5.0
        self.sensor_resolution = 0.0625
        self.accuracy = 0.5
        self.response_time = 0.75
        self.noise_level = 0.1
        self.thermal_mass = 0.95
        self.current_temp = self.base_temp
        self.connection_stability = 0.97
        self.connected = False
        self.reconnect_delay = 3
        self.rom_code = f"28-{random.randint(100000000000, 999999999999):012X}"
        
        self.client = mqtt.Client(self.client_id)
        if username and password:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✓ Temperature Sensor connected to MQTT broker at {self.broker}:{self.port}")
            status = {"sensor": "Temperature", "status": "online", "rom_code": self.rom_code, "protocol": "1-Wire", "timestamp": datetime.utcnow().isoformat()}
            self.client.publish(self.status_topic, json.dumps(status), qos=1, retain=True)
        else:
            print(f"✗ Connection failed with code {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"✗ Temperature Sensor disconnected (rc: {rc})")
        
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
        return True
        
    def simulate_connection_drop(self):
        if random.random() > self.connection_stability:
            print("⚠ Simulating connection drop...")
            self.client.disconnect()
            time.sleep(self.reconnect_delay)
            self.connect()
            
    def read_temperature(self):
        time.sleep(self.response_time)
        time_of_day = (time.time() % 86400) / 86400
        daily_cycle = math.sin(2 * math.pi * time_of_day) * self.daily_variation
        target_temp = self.base_temp + daily_cycle
        self.current_temp = (self.thermal_mass * self.current_temp + (1 - self.thermal_mass) * target_temp)
        temp_reading = self.current_temp + random.gauss(0, self.noise_level)
        temp_reading = round(temp_reading / self.sensor_resolution) * self.sensor_resolution
        if random.random() > 0.9:
            temp_reading += random.uniform(-self.accuracy, self.accuracy)
        return round(temp_reading, 4)
        
    def publish_reading(self):
        if not self.connected:
            return False
        temperature = self.read_temperature()
        temp_fahrenheit = round(temperature * 9/5 + 32, 2)
        payload = {"sensor_id": self.client_id, "sensor_type": "DS18B20", "rom_code": self.rom_code, "timestamp": datetime.utcnow().isoformat(), "data": {"temperature_celsius": temperature, "temperature_fahrenheit": temp_fahrenheit}, "unit": "°C", "protocol": "1-Wire", "resolution": f"{self.sensor_resolution}°C"}
        result = self.client.publish(self.topic, json.dumps(payload), qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"🌡️  Temperature: {temperature:.4f}°C ({temp_fahrenheit:.2f}°F)")
            return True
        else:
            print(f"✗ Publish failed: {result.rc}")
            return False
            
    def run(self, interval=3):
        print(f"🌡️  Starting Temperature Sensor (ROM: {self.rom_code})")
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
            print("\n⏹ Stopping Temperature sensor...")
            status = {"sensor": "Temperature", "status": "offline", "timestamp": datetime.utcnow().isoformat()}
            self.client.publish(self.status_topic, json.dumps(status), qos=1, retain=True)
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    interval = int(os.getenv("SENSOR_INTERVAL", "3"))
    username = os.getenv("MQTT_USER", None)
    password = os.getenv("MQTT_PASSWORD", None)
    sensor = TemperatureSensor(broker, port, username, password)
    sensor.run(interval)