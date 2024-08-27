import os
import sys, getopt
import csv
import busio
import board
import digitalio
from time import sleep
import minimalmodbus
from datetime import datetime, date
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


### SENSOR FUNCTIONS ###
def read_data(spi_bus, cs_pin, sensor_baudrate, sensor_phase, sensor_polarity, result):
    while not spi_bus.try_lock():
        pass
    spi_bus.configure(baudrate=sensor_baudrate, phase=sensor_phase, polarity=sensor_polarity)
    cs_pin.value=False
    spi_bus.readinto(result)
    cs_pin.value=True
    spi_bus.unlock()

def conv_temp(sensor_bytes):
    temp=int.from_bytes(sensor_bytes,"big")
    temp = (temp & 0x7ff8)>>3
    temp=32+temp*9/5*.25
    return temp

def conv_pressure(voltage):
    return round((voltage-0.5)/4*300,4)

def conv_flowRate(voltage):
    return round((voltage*23),3)

def read_modbus_float(register):
    for i in range(10):
        try:
            value = instr.read_float(register)
            return round(value,4)
        except:
            value = None
    return value


### GET COMMAND LINE ARGUMENTS ###
vibration, runSignal, kaeser = 0,0,0
location = "Unspecified"
run_charge_time = [0, 0]    #first number stores time, second number determines if compressor is running or idle. 0 for idle, 1 for running
opts, args = getopt.getopt(sys.argv[1:], "kvrl:", ["kaeser","vibration","runSignal","location"])
for opt, arg in opts:
    if opt in ("-v","--vibration"):
        vibration=1
    elif opt in ("-r","--runSignal"):
        runSignal=1
    elif opt in ("-k","--kaeser"):
        kaeser=1
        vibration=1
    elif opt in ("-l","--location"):
        location = arg


### OPEN CSV FILE ###
datafile = "{}-data.csv".format(date.today().strftime("%m-%d-%Y"))
runtimes = "{}-runtime.csv".format(date.today().strftime("%m-%d-%Y"))
open_datafile = open(datafile,"a+")
open_runtimes = open(runtimes,"a+")
new_writer = csv.writer(open_datafile)
runtimes_writer = csv.writer(open_runtimes)
old_day = date.today()


### INITIALIZE SENSORS ###
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Initialize Oil Temp
cs1 = digitalio.DigitalInOut(board.D22)
cs1.direction = digitalio.Direction.OUTPUT
cs1.value = True

# Initialize Compressor Cooler Temp
cs2 = digitalio.DigitalInOut(board.D27)
cs2.direction = digitalio.Direction.OUTPUT
cs2.value = True

# Initialize Motor Temp
cs3 = digitalio.DigitalInOut(board.D17)
cs3.direction = digitalio.Direction.OUTPUT
cs3.value = True

# Initialize ADC Sensor
cs4 = digitalio.DigitalInOut(board.D23)
mcp = MCP.MCP3008(spi,cs4)

# Initialize Oil Pressure Channel
chan0 = AnalogIn(mcp,MCP.P0)

# Initialize Air Pressure Channel
chan1 = AnalogIn(mcp,MCP.P1)

# Initialize Flow Rate Channel
chan2 = AnalogIn(mcp,MCP.P2)

# Initialize Vibration
if(vibration):
    chan3 = AnalogIn(mcp,MCP.P3)

# Initialize Run Signal
if(runSignal):
    chan4 = AnalogIn(mcp,MCP.P4)

# Initialize Modbus Reader
instr = minimalmodbus.Instrument('/dev/ttyS0',1)
instr.serial.baudrate = 9600
instr.handle_local_echo = True


### DATA GATHERING LOOP ###
result = bytearray(2)
runtime_headers = ["start_time", "stop_time","Duration(seconds)","Running_or_Compressing","Trusted"]
headers = ["datetime", "Compressor_Type", "Location", "Oil_Temp_(F)","Cooler_Temp_(F)","Motor_Temp_(F)","Oil_Pressure_(PSI)",
           "Air_Pressure_(PSI)","Flow_Rate_(L/min)", "Phase_A_Current_(A)", "Phase_B_Current_(A)", 
           "Phase_C_Current_(A)", "Phase_A_Voltage_(V)", "Phase_B_Voltage_(V)", "Phase_C_Voltage_(V)", 
           "Vibration_(V)", "Run_Signal_(V)", "Trusted"]
if (os.path.getsize(str(datafile))==0):
    new_writer.writerow(headers)
if (os.path.getsize(str(runtimes))==0):
    runtimes_writer.writerow(runtime_headers)

# Gather Data for Samachurlsama
while 1:
    data_list = []
    runtime_list = []
    today = date.today()
    data_list.append(datetime.now())
    
    if(kaeser):
        data_list.append("Kaeser")
    else:
        data_list.append("Ingersoll Rand")

    data_list.append(location)    
    
    # Change CSV file that is written to
    if(old_day!=today):
        old_day = today
        datafile = "{}-data.csv".format(date.today().strftime("%m-%d-%Y"))
        runtimes = "{}-runtime.csv".format(date.today().strftime("%m-%d-%Y"))
        open_datafile = open(datafile,"a+")
        open_runtimes = open(runtimes,"a+")
        runtimes_writer = csv.writer(open_runtimes)
        new_writer = csv.writer(open_datafile)
        new_writer.writerow(headers)
        runtimes_writer.writerow(runtime_headers)

    if(not kaeser):
        # Get Oil, Cooler and Motor temperature. (Gathered in order listed)
        read_data(spi,cs1,4000000,0,0,result)
        oil_temperature = conv_temp(result)
        data_list.append(oil_temperature)
        
        read_data(spi,cs2,4000000,0,0,result)
        cooler_temperature = conv_temp(result)
        data_list.append(cooler_temperature)

        read_data(spi,cs3,4000000,0,0,result)
        motor_temperature = conv_temp(result)
        data_list.append(motor_temperature)

        # Get Oil Pressure, Air Pressure, and Flow Rate
        data_list.append(conv_pressure(chan0.voltage))
        data_list.append(conv_pressure(chan1.voltage))
        data_list.append(conv_flowRate(chan2.voltage))

        # Get current and voltage of power supply
        data_list.append(read_modbus_float(1016))
        data_list.append(read_modbus_float(1018))
        data_list.append(read_modbus_float(1020))
        data_list.append(read_modbus_float(1000))
        data_list.append(read_modbus_float(1002))
        data_list.append(read_modbus_float(1004))
    else:
        for i in range(12):
            data_list.append(None)
    

    # Get vibration, run Signal
    if(vibration):
        data_list.append(chan3.voltage)
    else:
        data_list.append(None)
    
    if(runSignal):
        data_list.append(chan4.voltage)
    else:
        data_list.append(None)

    
    # Calculate run time or charge time
    if(run_charge_time[0]==0 or ((data_list[9]!=None and data_list[9]<1) or (data_list[10]!=None and data_list[10]<1) or (data_list[11]!=None and data_list[11]<1) and data_list[7]<5)):
        run_charge_time[0] = datetime.now()
        run_charge_time[1] = 1

    if((data_list[6] != None and data_list[6]>70) or (data_list[7] != None and data_list[7]<=100)):
        if(run_charge_time[1] == 0):
            runtime_list.append(run_charge_time[0])
            runtime_list.append(data_list[0])
            runtime_list.append((data_list[0]-run_charge_time[0]).total_seconds())
            runtime_list.append("Running")
            if(runtime_list[2] < 0):
                runtime_list.append(0)
            else:
                runtime_list.append(1)
            run_charge_time[0] = datetime.now()
            runtimes_writer.writerow(runtime_list)
        run_charge_time[1] = 1
    elif((data_list[6] != None and data_list[6]<=70)):
        if(run_charge_time[1] == 1):
            runtime_list.append(run_charge_time[0])
            runtime_list.append(data_list[0])
            runtime_list.append((data_list[0]-run_charge_time[0]).total_seconds())
            runtime_list.append("Compressing")
            if(runtime_list[2] < 0):
                runtime_list.append(0)
            else:
                runtime_list.append(1)
            run_charge_time[0] = datetime.now()
            runtimes_writer.writerow(runtime_list)
        run_charge_time[1] = 0

    # Check if data has any gaps (Invalid if there are) (check if correct data types)
    if(None in data_list[8:15] or (data_list[14]==None and vibration)):
        data_list.append(0)
    else:
        data_list.append(1)
   
    new_writer.writerow(data_list)
    sleep(1)