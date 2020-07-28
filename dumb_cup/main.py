import time
from .adxl345 import ADXL345
from .spirit_level import SpiritLevel

def on_not_level(x: int, y: int, z: int):
    print("Not level")
    print('x:', x, 'y:', y, 'z:',z ,'uint:mg')

a345 = ADXL345(5, 4, 0)
dd = SpiritLevel(a345, on_not_level, 300, 300, 300)
while True:
    dd.calculate()
    # x, y, z = a345.readXYZ()
    # print('x:', x, 'y:', y, 'z:',z ,'uint:mg')
    time.sleep(0.1)

from dumb_cup.v53l0x import VL53L0X
from machine import I2C, Pin
i2c = I2C(scl = Pin(21), sda = Pin(22), freq = 20000, timeout = 2000)
print(i2c.scan())

tof = VL53L0X(i2c)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
