import serial.rs485
ser=serial.rs485.RS485(port='/dev/ttySC0',baudrate=9600)
ser.rs485_mode = serial.rs485.RS485Settings(False,True)
ser.write('a test'.encode('utf-8'))

while True:
    c = ser.read(1)
    ser.write(c)
    print(c, end='')
