#!/usr/bin/env python3


"""
Install uPython on ESP8266
esptool.py --port /dev/tty.usbserial-14340 --baud 460800 write_flash --flash_size=detect -fm dio 0 esp8266-20191220-v1.12.bin 
"""

import os
import time
import urllib
import time
import urllib.request

##############
# Parameters
##############
firmware_file_name          = 'esp32-idf4-20191220-v1.12.bin'   
esp32_mount_dir             = ''   
 
#################
# Install Script
#################

# Red Herring error: "failed to load calibration data" and crash was due to 
# input power problem.
# https://esp32.com/viewtopic.php?t=4097

# Ampy
# ampy -p /dev/ttyUSB0 -b 115200 run esp32/test.py

def get_firmware(url, filename):
    print('Beginning file download with urllib2...')
    print(url)
    urllib.request.urlretrieve(url, filename)

# Download tools
os.system('pip install esptool pyserial mpy-utils --quiet')
if not os.path.exists(firmware_file_name):
    print("here")
    get_firmware(f'https://micropython.org/resources/firmware/{firmware_file_name}', firmware_file_name)
if not os.path.exists('serial_util.py'):
    os.system('wget https://raw.githubusercontent.com/Ladvien/ramps_controller/master/ramps_controller/serial_util.py')

# Grab some code I wrote (or stole? I cant remember) for a different project.
from serial_util import *

# Get the port from the user.
print('########################################################')
print("# Welcome to Ladvien's ESP32 Micropython setup script  #")
print('# How can it help?                                     #')
print('#                                                      #')
print('# 1: CONNECT                                           #')
print('# 2: INSTALL                                           #')
print('# 3: MOUNT                                             #')
print('# 4: SYNC                                              #')
# print('# 5: RUN                                               #')
print('#                                                      #')
print('########################################################')
use_case = input(': ')
print()
print()
print('########################################################')
print('# Select your port:                                    #')
print('########################################################')
port = get_write_port()
print()
print()

#############
# Helping 
#############
def ensure_esp32_dir(esp32_mount_dir):
    if esp32_mount_dir == '':
        esp32_mount_dir = './esp32'
        if not os.path.exists(os.path.dirname(esp32_mount_dir)):
            try:
                os.makedirs(os.path.dirname(esp32_mount_dir))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
    return esp32_mount_dir

###########
# Uses
###########

def connect():
    print()
    print('Connecting to the device using "screen" terminal')
    print('To exit hit "CTRL+A" then "CTRL+D"')
    print('')
    input('Hit return to connect and then reset your ESP32....')
    os.system(f'screen {port} 115200')
    os.system('pkill screen')
    print()

def install():
    # Flash the ESP32
    input('About Erasing EVERYTHING on the ESP32. Hit a key if you accept.')
    os.system(f'esptool.py --chip esp32 -p {port} erase_flash')

    # Install Micropython
    print('Installing Micropython!')
    print('Note: If you have problems connecting, try holding the BOOT button connected.')
    os.system(f'esptool.py --chip esp32 -p {port} write_flash -z 0x1000 {firmware_file_name}')
    # Debrief
    print()
    print('Huzzah! We are all done!')
    print()

def mount():
    global esp32_mount_dir
    print()
    print('Mounting the ESP32 filesystem to "./esp32"')
    print('Keep this window open while manipulating the filesystem.')
    esp32_mount_dir = ensure_esp32_dir(esp32_mount_dir)
    os.system(f'mpy-fuse --port {port} --baud 115200 {esp32_mount_dir}')

def sync_fs():
    global esp32_mount_dir
    # Flash the ESP32
    esp32_mount_dir = ensure_esp32_dir(esp32_mount_dir)
    print(f'Syncing {esp32_mount_dir}')
    os.system(f'mpy-sync ./{esp32_mount_dir}')

if use_case == '1':
    connect()
elif use_case == '2':
    install()
elif use_case == '3':
    mount()
elif use_case == '4':
    sync_fs()

else:
    print('Not a valid selection. Run once more to try again.')