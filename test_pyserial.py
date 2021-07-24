import serial
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
    # print("{}: {} [{}]".format(port, desc, hwid))
    print("{}".format(port))
ser = serial.Serial('COM1', baudrate = 9600, timeout = 1)
def getValues():
    
    ser.write(b'g')
    arduinoData = ser.readline().decode('ascii')
    return arduinoData

# while(1):

#     userInput = input('Get data point?')

#     if userInput == 'y':
#         print(getValues())