import smbus2
import time

# HYT939 default I2C address (Check your sensor datasheet for the address)
I2C_ADDRESS = 0x28

# Create an instance of the I2C bus
i2c_bus = smbus2.SMBus(1)

def read_humidity_temperature():
    # Reading data (4 bytes: Humidity 2 bytes, Temperature 2 bytes)
    data = i2c_bus.read_i2c_block_data(I2C_ADDRESS, 0x00, 4)
    
    # Convert the data to humidity
    humidity_raw = ((data[0] & 0x3F) << 8) | data[1]
    humidity = (humidity_raw * 100.0) / 16384.0

    # Convert the data to temperature
    temperature_raw = ((data[2] << 8) | (data[3] & 0xFC)) >> 2
    temperature = (temperature_raw * 165.0 / 16383.0) - 40.0
    
    return humidity, temperature

# Read and print humidity and temperature
humidity, temperature = read_humidity_temperature()
if humidity is not None and temperature is not None:
    print("Humidity: {:.2f}% RH".format(humidity))
    print("Temperature: {:.2f}°C".format(temperature))
else:
    print("Failed to read sensor data.")
