import random
import time
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = 'mqtt.example.com'  # Replace with your broker address
MQTT_PORT = 1883
MQTT_TOPIC = 'sensors/water_level'

# Function to simulate water level
def simulate_water_level():
    return random.uniform(0.0, 1.0)  # Simulating water level between 0 and 1

# Callback for MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# Setup MQTT Client
client = mqtt.Client()
client.on_connect = on_connect

# Connect to the MQTT Broker
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print("Could not connect to MQTT Broker:", e)

# Main loop to publish water level data
while True:
    water_level = simulate_water_level()
    client.publish(MQTT_TOPIC, water_level)
    print(f"Published water level: {water_level}")
    time.sleep(5)  # Publish every 5 seconds
