import math
import serial
import config

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
        if config.justReseted == True:
            return
        
        config.points.clear()
        config.clusters.clear()
        
        config.minValue=math.inf
        config.maxValue=-math.inf
        # print("Reset")
        config.justReseted=True
        self.ser.write(b'RESET\n')