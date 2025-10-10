import json
import os
from datetime import datetime, timezone
import board, busio
from digitalio import DigitalInOut
from adafruit_bme280 import basic

# Load config
CONFIG_FILE = "/home/pi/beam_logger/config.json"
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Extract global and sensor settings
node_id = config["global"]["node_id"]
timezone_setting = config["global"]["timezone"]  # e.g., "UTC"
base_dir = config["global"]["base_dir"]

bme_config = config["bme280"]
directory = os.path.join(base_dir, bme_config["directory"])
file_name = bme_config["file_name"]
os.makedirs(directory, exist_ok=True)
file_path = os.path.join(directory, file_name)

# Setup SPI pins from config
CS_PIN = getattr(board, bme_config["spi"]["cs_pin"].split(".")[1])
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = DigitalInOut(CS_PIN)

# Initialize BME280 over SPI
sensor = basic.Adafruit_BME280_SPI(spi, cs, baudrate=bme_config["spi"]["baudrate"])

# Read sensor values
temperature = float(sensor.temperature)
humidity = float(sensor.humidity)
pressure = float(sensor.pressure)

# Handle timestamp according to config timezone
if timezone_setting.upper() == "UTC":
    timestamp = datetime.now(timezone.utc).isoformat()
else:
    timestamp = datetime.now().astimezone().isoformat()

# Create new record
env_json_data = {
    "timestamp": timestamp,
    "temperature_C": temperature,
    "humidity_percent": humidity,
    "pressure_hPa": pressure
}

# Load existing data or create new structure
try:
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            try:
                data = json.load(json_file)
                if not isinstance(data, dict) or "records" not in data:
                    data = {"node_id": node_id, "sensor": "bme280", "records": []}
            except Exception:
                data = {"node_id": node_id, "sensor": "bme280", "records": []}
    else:
        data = {"node_id": node_id, "sensor": "bme280", "records": []}

    # Append new reading and save
    data["records"].append(env_json_data)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Env data appended to {file_name} at {timestamp}")

except Exception as e:
    print(f"Error saving env data: {e}")
