import busio
import board
import digitalio
from datetime import datetime
import adafruit_max31855
from time import sleep

### INITIALIZE SENSORS ###
# Set up SPI buses
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Thermocouple digital interface pins setup
cs_pins = [board.D17, board.D27, board.D22]  # Define the pins
cs_objects = [digitalio.DigitalInOut(pin) for pin in cs_pins]  # Create DigitalInOut objects
for cs in cs_objects:
    cs.direction = digitalio.Direction.OUTPUT
    cs.value = True  # Set all CS high initially

### DATA GATHERING LOOP ###
while True:
    data_list = [datetime.now()]  # Start data list with the current date and time

    # Read temperatures using MAX31855 sensors
    for cs in cs_objects:
        cs.value = False  # Set CS low to enable the corresponding sensor
        temp_sensor = adafruit_max31855.MAX31855(spi, cs)
        temperature = temp_sensor.temperature
        data_list.append(temperature)
        cs.value = True  # Set CS high to disable the sensor

    print(data_list)  # Print only the date-time and temperatures
    sleep(0.1)
