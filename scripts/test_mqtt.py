import paho.mqtt.client as mqtt
import time

# Callback when a message is received

def on_message(client, userdata, message):
    print(f"{time.ctime()}: {message.topic} {message.payload.decode()}")

# Create MQTT client
client = mqtt.Client()

# Assign the on_message callback
client.on_message = on_message

# Connect to the broker
client.connect("mqtt-broker-address", 1883, 60)

# Subscribe to the topic
client.subscribe("sensors/#")

# Start the loop
client.loop_start()

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()