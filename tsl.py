import json
import os
from datetime import datetime, timezone
import board
import adafruit_tsl2591

# Load config
CONFIG_FILE = "/home/pi/beam_logger/config.json"
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Extract global and sensor settings
node_id = config["global"]["node_id"]
timezone_setting = config["global"]["timezone"]
base_dir = config["global"]["base_dir"]

tsl_config = config["tsl2591"]
directory = os.path.join(base_dir, tsl_config["directory"])
file_name = tsl_config["file_name"]
os.makedirs(directory, exist_ok=True)
file_path = os.path.join(directory, file_name)

# Initialize sensor on I2C bus (optional bus from config)
i2c_bus = tsl_config.get("i2c_bus", 1)  # default to 1
i2c = board.I2C()  # You could extend to select bus dynamically
sensor = adafruit_tsl2591.TSL2591(i2c)

# Read sensor value
lux = float(sensor.lux)

# Handle timestamp according to config timezone
if timezone_setting.upper() == "UTC":
    timestamp = datetime.now(timezone.utc).isoformat()
else:
    timestamp = datetime.now().astimezone().isoformat()

# New record
lux_json_data = {
    "timestamp": timestamp,
    "lux": lux
}

# Load existing data or create new structure
try:
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            try:
                data = json.load(json_file)
                if not isinstance(data, dict) or "records" not in data:
                    data = {"node_id": node_id, "sensor": "tsl2591", "records": []}
            except Exception:
                data = {"node_id": node_id, "sensor": "tsl2591", "records": []}
    else:
        data = {"node_id": node_id, "sensor": "tsl2591", "records": []}

    # Append new reading and save
    data["records"].append(lux_json_data)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Lux data appended to {file_name} at {timestamp}")

except Exception as e:
    print(f"Error saving lux data: {e}")
