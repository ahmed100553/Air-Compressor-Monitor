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
import smbus2

I2C_ADDRESS = 0x28
i2c_bus = smbus2.SMBus(1)

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
def read_humidity_temperature():
    # Sending a read measurement request to the sensor
    # The HYT939 doesn't require a specific command to start measurement in its default mode
    # Reading data (4 bytes: Humidity 2 bytes, Temperature 2 bytes)
    data = i2c_bus.read_i2c_block_data(I2C_ADDRESS, 0x00, 4)
    # Convert the data to humidity
    humidity_raw = ((data[0] & 0x3F) << 8) | data[1]
    humidity = (humidity_raw * 100.0) / 16384.0
    # Convert the data to temperature
    temperature_raw = ((data[2] << 8) | (data[3] & 0xFC)) >> 2
    temperature = (temperature_raw * 165.0 / 16383.0) - 40.0
    return humidity

'''
def adc_to_voltage(adc_value):
    # Assuming the gain is set to 1 for maximum voltage range of +/- 4.096V
    voltage = (adc_value * 4.096) / 32767
    return voltage

def conv_pressure(adc_value):
    voltage = adc_to_voltage(adc_value)
    return round((voltage - 0.5) / 4 * 300, 4)

def conv_pressure2(adc_value):
    voltage = adc_to_voltage(adc_value)
    return round((voltage / 3.3 - 0.1) / 0.66667, 4)
'''

### INITIALIZE SENSORS ###
i2c = busio.I2C(board.SCL, board.SDA)
ads1 = ADS.ADS1115(i2c)
ads2 = ADS.ADS1115(i2c, address=0x49)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs_pins = [digitalio.DigitalInOut(pin) for pin in [board.D17, board.D27, board.D22]]
for cs in cs_pins:
    cs.direction = digitalio.Direction.OUTPUT
    cs.value = True  # Initialize as high (inactive)

oil_pressure = AnalogIn(ads1, ADS.P0)
air_pressure = AnalogIn(ads1, ADS.P1)
psi100_pressure = AnalogIn(ads1, ADS.P2)

'''oil_pressure = ads1.read_adc(0)
air_pressure = ads1.read_adc(1)
psi100_pressure = ads1.read_adc(2)'''


instr = minimalmodbus.Instrument('/dev/ttySC0', 1)
instr.serial.baudrate = 9600
instr.handle_local_echo = False
instr.mode = minimalmodbus.MODE_RTU  
instr.clear_buffers_before_each_transaction = True
#instr.debug = True

### SETUP CSV FILE ###
today = date.today()
datafile = f"{today.strftime('%m-%d-%Y')}-data.csv"
header = ["Timestamp", "Motor Temp", "Cooler Temp", "Oil Temp", "Oil Pressure",
          "Air Pressure", "PSI100 Pressure", "Phase_A_Current_(A)", "Phase_B_Current_(A)", 
           "Phase_C_Current_(A)", "Phase_A_Voltage_(V)", "Phase_B_Voltage_(V)", "Phase_C_Voltage_(V)", "Total Active Power(W)", "Humditiy", "E-Shutdown"]
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
    for register in [1000, 1002, 1004, 1010, 1012, 1014, 1034]:
        data_list.append(read_modbus_float(instr, register))
    data_list.append(read_humidity_temperature())
    # E-Shutdown logic
    channel_value = AnalogIn(ads2, ADS.P0).value
    if channel_value < 60:
        e_shutdown = "E-Shutdown has been pressed"
    elif 200 <= channel_value <= 300:
        e_shutdown = "E-Shutdown is"
    else:
        e_shutdown = "Normal"
    data_list.append(e_shutdown)
    
    # Write to CSV
    with open(datafile, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data_list)
    print(data_list)
    
    sleep(1)  # Sleep for 1 second to prevent too frequent sampling
