import os
import csv
from time import sleep
import busio
import board
from datetime import datetime, date
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

### SENSOR FUNCTIONS ###
def conv_pressure(voltage):
    return round((voltage - 0.5) / 4 * 300, 4)

def conv_pressure2(voltage):
    return round((voltage / 3.3 - 0.1) / 0.66667, 4)

### INITIALIZE SENSORS ###
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

oil_pressure = AnalogIn(ads, ADS.P0)
air_pressure = AnalogIn(ads, ADS.P1)
psi100_pressure = AnalogIn(ads, ADS.P2)

### SETUP CSV FILE ###
today = date.today()
header = ["Timestamp", "Oil Pressure", "Air Pressure", "PSI100 Pressure"]

### DATA GATHERING LOOP ###
while True:
    data_list = [datetime.now()]
    
    # Get Pressure readings
    data_list.append(conv_pressure(oil_pressure.voltage))
    data_list.append(conv_pressure(air_pressure.voltage))
    data_list.append(conv_pressure2(psi100_pressure.voltage))
    
    print(data_list)
    
    sleep(1)  # Sleep for 1 second to prevent too frequent sampling
