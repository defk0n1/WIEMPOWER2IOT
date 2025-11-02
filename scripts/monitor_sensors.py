import time

class SensorMonitor:
    def __init__(self, npk_sensor, temperature_sensor, water_level_sensor):
        self.npk_sensor = npk_sensor
        self.temperature_sensor = temperature_sensor
        self.water_level_sensor = water_level_sensor

    def monitor(self):
        while True:
            npk_value = self.npk_sensor.read_value()
            temperature = self.temperature_sensor.read_value()
            water_level = self.water_level_sensor.read_value()
            print(f"NPK: {npk_value}, Temperature: {temperature}, Water Level: {water_level}")
            time.sleep(5)  # Delay for 5 seconds

# Initialize sensors and start monitoring
# npk_sensor = NPKSensor()
# temperature_sensor = TemperatureSensor()
# water_level_sensor = WaterLevelSensor()
# monitor = SensorMonitor(npk_sensor, temperature_sensor, water_level_sensor)
# monitor.monitor()