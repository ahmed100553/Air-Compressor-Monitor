import os
import sys
import csv
import busio
import board
import digitalio
from time import sleep
import minimalmodbus
from datetime import datetime, date
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_max31855

### SENSOR FUNCTIONS ###
def read_temp_max31855(spi, cs):
    max31855 = adafruit_max31855.MAX31855(spi, cs)
    return max31855.temperature

def conv_pressure(voltage):
    return round((voltage - 0.5) / 4 * 300, 4)

def conv_pressure2(voltage):
    return round((voltage / 3.3 - 0.1) / 0.66667, 4)

def read_modbus_float(instr, register):
    for i in range(10):
        try:
            value = instr.read_float(register)
            return round(value, 4)
        except:
            continue
    return None

### INITIALIZE SENSORS ###
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs_pins = [digitalio.DigitalInOut(pin) for pin in [board.D17, board.D27, board.D22]]
for cs in cs_pins:
    cs.direction = digitalio.Direction.OUTPUT
    cs.value = True  # Initialize as high (inactive)

oil_pressure = AnalogIn(ads, ADS.P0)
air_pressure = AnalogIn(ads, ADS.P1)
psi100_pressure = AnalogIn(ads, ADS.P2)

instr = minimalmodbus.Instrument('/dev/ttySC0', 1)
instr.serial.baudrate = 115200
instr.handle_local_echo = False

### SETUP CSV FILE ###
today = date.today()
datafile = f"{today.strftime('%m-%d-%Y')}-data.csv"
header = ["Timestamp", "Temperature1", "Temperature2", "Temperature3", "Oil Pressure",
          "Air Pressure", "PSI100 Pressure", "Current (1016)", "Voltage (1018)",
          "Current (1020)", "Voltage (1000)", "Current (1002)", "Voltage (1004)"]
if not os.path.isfile(datafile):
    with open(datafile, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

### DATA GATHERING LOOP ###
while True:
    data_list = [datetime.now()]
    
    # Read temperatures using MAX31855
    for cs in cs_pins:
        cs.value = False  # Enable sensor
        temperature = read_temp_max31855(spi, cs)
        data_list.append(temperature)
        cs.value = True  # Disable sensor
    
    # Get Pressure readings
    data_list.append(conv_pressure(oil_pressure.voltage))
    data_list.append(conv_pressure(air_pressure.voltage))
    data_list.append(conv_pressure2(psi100_pressure.voltage))
    
    # Modbus data
    for register in [1016, 1018, 1020, 1000, 1002, 1004, 1006, 1008, 1010, 1012, 1014]:
        data_list.append(read_modbus_float(instr, register))
    
    # Write to CSV
    with open(datafile, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data_list)
    print(data_list)
    
    sleep(1)  # Sleep for 1 second to prevent too frequent sampling
