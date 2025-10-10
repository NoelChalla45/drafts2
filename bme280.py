import board
import adafruit_bme280

# Automatically uses SDA/SCL (I²C)
i2c = board.I2C()  
sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)

print(sensor.temperature)
print(sensor.humidity)
print(sensor.pressure)
