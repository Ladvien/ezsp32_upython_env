
import time

from machine import I2C, Pin, Timer
from dumb_cup.v53l0x import VL53L0X
from dumb_cup.adxl345 import ADXL345
from dumb_cup.spirit_level import SpiritLevel

###############
# Methods
###############
def on_not_level(x: int, y: int, z: int):
    print("Not level")
    print('x:', x, 'y:', y, 'z:',z ,'uint:mg')


def measure(tof: ADXL345, num_samples: int, round_num: int) -> int:
    samples = []    
    # if len(samples) >= NUM_SAMPLES + 1: samples.pop(0)
    for i in range(num_samples):
        samples.append(tof.read())
        dist = sum(samples) / len(samples)
    return round(dist, round_num)

#####################
# Check Liquid Level
#####################
def chk_liq_lvl(timer):
    NUM_SAMPLES = 100
    global old_lvl
    global cur_lvl
    global tof
    cur_lvl = measure(tof, NUM_SAMPLES, 3) * -1
    delta = cur_lvl - old_lvl
    print("Current: {} Delta: {}".format(cur_lvl, delta))
    old_lvl = cur_lvl

###############
# Initialize
###############
i2c = I2C(scl = Pin(21), sda = Pin(22), freq = 20000, timeout = 2000)

a345 = ADXL345(i2c)
dd = SpiritLevel(a345, on_not_level, 300, 300, 300)

tof = VL53L0X(i2c)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

tof.start()

print("Initializing liquid gauge...")
cur_lvl = measure(tof, 40, 3) * -1
old_lvl = cur_lvl

print("Initial liquid level: {}".format(cur_lvl))
chk_liq_lvl_tmr = Timer(0)
chk_liq_lvl_tmr.init(mode=Timer.PERIODIC, period=1000, callback=chk_liq_lvl)

# To begin conversion we need a calibration sequence.
#   1. Have the user empty the cup and level it on counter.
#   2. Have the user fill the cup.
#   
#   We could use the empty_reading (-137) and full_reading (-63) to
#   calculate the linear volume of the cup (74).
#
#   abs(empty_reading) - abs(full_reading) = linear_volume
#
#   Then, we have two routes, we can convert linear_volume into
#   millimeters.  This would become linear_volume_mm.
#
#   We can then get the cup diameter in millimeters (80mm)
#   and multiply it by the linear_volume_mm, which should give
#   us total volume.
#
#   V = πr^2h
#   cubic_mm = (cup_diameter / 2)^2  * π * linear_volume_mm 
#   cubic_mm = (40)^2 * π * 74
#   cubic_mm = 1600 * π * 74
#   cubic_mm = 5026.54 * 74
#   cubic_mm = 371964.57
#
#   To get ounces, multiply mm3 by 3.3814e-5.
#
#   ounces = 12.5776184143
#

###############
# Main Loop
###############
while True:
    dd.calculate()
