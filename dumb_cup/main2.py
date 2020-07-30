
import time
from machine import I2C, Pin
from dumb_cup.v53l0x import VL53L0X
from dumb_cup.adxl345 import ADXL345
from dumb_cup.spirit_level import SpiritLevel

def on_not_level(x: int, y: int, z: int):
    print("Not level")
    print('x:', x, 'y:', y, 'z:',z ,'uint:mg')

i2c = I2C(scl = Pin(21), sda = Pin(22), freq = 20000, timeout = 2000)

print(i2c.scan())

a345 = ADXL345(i2c)
dd = SpiritLevel(a345, on_not_level, 300, 300, 300)

tof = VL53L0X(i2c)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

tof.start()
NUM_SAMPLES = 32245

while True:
    dd.calculate()
    # x, y, z = a345.readXYZ()
    # print('x:', x, 'y:', y, 'z:',z ,'uint:mg')
    samples = []
    if len(samples) >= NUM_SAMPLES + 1: samples.pop(0)
    samples.append(tof.read())
    dist = sum(samples) / len(samples)
    print(round(dist, 3))
