import time
from machine import I2C, Pin, Timer
from dumb_cup.v53l0x import VL53L0X
from dumb_cup.adxl345 import ADXL345
from dumb_cup.spirit_level import SpiritLevel

###############
# Constants
###############

OZ_FULL             = const(16)
INIT_SAMPES         = const(50)
NUM_SAMPLES         = const(15)
RND_PLCS            = const(1)
DE_BNC_DELAY        = const(250)

BTN                 = const(26)
DE_BNC_TMR          = const(0)
CHK_LVL_TMR         = const(1)

BTN_ACTION_IN_PRG   = const(99)
BTN_UNPRESSED       = const(0)
BTN_PRESSED         = const(1)
BTN_GOT_EMPTY       = const(2)
BTN_GOT_FULL        = const(3)
BTN_CALI_IN_PRG_3   = const(4)

SCL_PIN             = const(21)
SDA_PIN             = const(22)

X_THRESH            = const(300)
Y_THRESH            = const(300)
Z_THRESH            = const(300)

CALI_F_NAME         = "calibration.txt"
SETTINGS_DIR_NAME   = "/dumb_cup"

###############
# Methods
###############
def map_val(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def on_not_level(x: int, y: int, z: int):
    print("Not level")
    print('x:', x, 'y:', y, 'z:',z ,'uint:mg')


def measure(tof: ADXL345, num_samples: int, round_num: int) -> int:
    global vol_cof
    samples = []    
    # if len(samples) >= NUM_SAMPLES + 1: samples.pop(0)
    for i in range(num_samples):
        samples.append(tof.read())
        dist = sum(samples) / len(samples) * vol_cof
    dist = map_val(dist, empty_val, full_val, 0, OZ_FULL)
    return round(dist, round_num)

def blink(led, num: int = 1, delay: int = 200):
    for i in range(num):
        led.on()
        time.sleep_ms(delay)
        led.off()
        time.sleep_ms(delay)

################
# Initialization 
################

i2c = I2C(scl = Pin(SCL_PIN), sda = Pin(SDA_PIN), freq = 20000, timeout = 2000)

# Accelerometer
a345 = ADXL345(i2c)
dd = SpiritLevel(a345, on_not_level, X_THRESH, Y_THRESH, Z_THRESH)

# Time-of-Flight
tof = VL53L0X(i2c)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

tof.start()

# Blinker
led = Pin(2, Pin.OUT)

# Main button.
btn = Pin(BTN, Pin.IN, Pin.PULL_DOWN)

###############
# Calibration
###############

de_bnc_tmr = Timer(DE_BNC_TMR)
de_bnc_flag = False
def dnc_timer_expr(timer):
    global de_bnc_flag
    de_bnc_flag = False

def on_btn(pin):
    global tof
    global de_bnc_flag
    global cali_file
    global btn_state
    global btn
    global led

    if not de_bnc_flag:
        # Turn on debounce timer.
        de_bnc_flag = True
        de_bnc_tmr.init(mode=Timer.ONE_SHOT, period=DE_BNC_DELAY, callback=dnc_timer_expr)
        
        if btn_state == BTN_UNPRESSED:
            btn_state = BTN_ACTION_IN_PRG

            # Erase old file.
            erase_cali()
            
            # Let the user know we are getting the 
            # depth of the cup.
            print("Getting measurements when empty.")
            blink(led, 5, 300)
            empty = measure(tof, NUM_SAMPLES, RND_PLCS)
            fs_write_val("empty", empty)
            
            btn_state = BTN_GOT_EMPTY
        elif btn_state == BTN_GOT_EMPTY:
            btn_state = BTN_ACTION_IN_PRG

            # Let the user know we are getting the 
            # depth of the cup.
            print("Getting measurements when full.")
            blink(led, 5, 300)
            full = measure(tof, NUM_SAMPLES, RND_PLCS)
            fs_write_val("full", full)

            btn_state = BTN_UNPRESSED
        elif btn_state == BTN_ACTION_IN_PRG:
            print("Busy")


def erase_cali():
    import os
    filepath = SETTINGS_DIR_NAME + "/" + CALI_F_NAME
    try:
        with open(filepath) as f:
            os.remove(filepath)
    except:
        pass


def fs_write_val(key: str, value: str):
    import os
    filepath = SETTINGS_DIR_NAME + "/" + CALI_F_NAME
    write_type = "a"

    try:
        with open(filepath, write_type) as f:
            f.write("")
    except OSError:
        os.mkdir(SETTINGS_DIR_NAME)
        write_type = "w"
        
    try:
        with open(filepath, write_type) as f:
            s = "{}={}\n".format(key, value)
            f.write(s)
    except OSError:
        print("FS error.")

def fs_read_cali():
    import os
    
    filepath = SETTINGS_DIR_NAME + "/" + CALI_F_NAME

    with open(filepath, "r") as f:
        return f.readlines()
    return []

def uninstall():
    import os
    os.chdir("dumb_cup")
    for item in os.listdir():
        print(type(item))
        try:
            os.remove(item)
        except:
            os.rmdir(item)

btn_state = BTN_UNPRESSED
btn.irq(on_btn)

#####################
# Volume coefficient
#####################
def vol_cof():
    lines = fs_read_cali()
    for value in lines:       
        if "empty" in value: 
            empty_val = float(value.split("=")[1][0:-1])
        elif "full" in value:
            full_val = float(value.split("=")[1][0:-1])
    return (empty_val, full_val)
    
#####################
# Check Liquid Level
#####################
def chk_liq_lvl(timer):
    global old_lvl
    global cur_lvl
    global consumed
    global tof
    cur_lvl = measure(tof, NUM_SAMPLES, RND_PLCS)
    delta = round((cur_lvl - old_lvl), RND_PLCS)
    consumed += round(delta, RND_PLCS)
    print("Current: {} Delta: {} Consumed: {}".format(cur_lvl, delta, consumed))
    old_lvl = cur_lvl
    
###############
# Calibration
###############

empty_val, full_val = vol_cof()
volume = (full_val - empty_val) * -1
vol_cof = OZ_FULL / volume

print("Initializing liquid gauge...")
cur_lvl = measure(tof, INIT_SAMPES, RND_PLCS)
old_lvl = cur_lvl
consumed = 0

print("Initial liquid level: {}".format(cur_lvl))
chk_liq_lvl_tmr = Timer(CHK_LVL_TMR)
chk_liq_lvl_tmr.init(mode=Timer.PERIODIC, period=3000, callback=chk_liq_lvl)


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
