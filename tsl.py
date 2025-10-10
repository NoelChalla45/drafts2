import board
import adafruit_tsl2591
import json
from datetime import datetime, timezone
import os

# Load config file
config_path = "/home/pi/drafts2/config.json"
with open(config_path, "r") as f:
    config = json.load(f)

# Extract TSL2591 config
tsl_config = config["tsl2591"]
global_config = config["global"]

# Node ID
node_id = global_config.get("node_id", "unknown-node")

# Directory and file
directory = os.path.join(global_config.get("base_dir", "/home/pi/data"), tsl_config.get("directory", "tsl2591"))
file_name = tsl_config.get("file_name", "lux_data.json")
file_path = os.path.join(directory, file_name)

# Create directory if needed
os.makedirs(directory, exist_ok=True)

# Initialize sensor
i2c_bus = tsl_config.get("i2c_bus", 1)  # optional
i2c = board.I2C()  # board.I2C() defaults to bus=1 on Pi
sensor = adafruit_tsl2591.TSL2591(i2c)

# Read lux
lux = sensor.lux

# Create new record
new_lux_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "lux": lux
}

# Append to JSON
try:
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "records" not in data:
                data = {"node_id": node_id, "sensor": "tsl2591", "records": []}
    else:
        data = {"node_id": node_id, "sensor": "tsl2591", "records": []}

    data["records"].append(new_lux_data)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    if global_config.get("print_debug", True):
        print(f"Lux data appended to {file_name} at {datetime.now(timezone.utc)}")
except Exception as e:
    print(f"Error saving lux data: {e}")
