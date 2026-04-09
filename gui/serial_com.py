import math
import serial
from config import points

class SerialCom:
    def __init__(self):
        self.ser = serial.Serial("COM6", 115200, timeout=1)
    
    def Stop(self):
        self.ser.write(b'STOP\n')
        # print("Stop")

    def Start(self):
        self.ser.write(b'START\n')
        # print("Start")

    def Reset(self):
        global justReseted
        if justReseted == True:
            return
        
        points.clear()
        
        global minValue, maxValue
        minValue=math.inf
        maxValue=-math.inf
        self.ser.write(b'RESET\n')
        # print("Reset")
        justReseted=True