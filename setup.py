import os
import time

##############
# Parameters
##############
firmware_file_name          = 'tinypico-idf4-20200526-unstable-v1.12-464-gcae77daf0.bin'   

#################
# Install Script
#################

# Download tools
os.system('pip install esptool pyserial mpy-utils --quiet')
if not os.path.exists(firmware_file_name):
    os.system(f'wget https://micropython.org/resources/firmware/{firmware_file_name}')
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
print('# 3: MOUNT                                                     #')
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

if use_case == '2':
    # Flash the ESP32
    input('About Erasing EVERYTHING on the ESP32. Hit a key if you accept.')
    os.system(f'esptool.py --chip esp32 -p {port} erase_flash')

    # Install Micropython
    print('Installing Micropython!')
    print('Note: If you have problems connecting, try holding the BOOT button connected.')
    os.system(f'esptool.py --chip esp32 -p {port} write_flash -z 0x1000 {firmware_file_name}')
elif use_case == '1':
    # Connect
    print()
    print('Connecting to the device using "screen" terminal')
    print('To exit hit "CTRL+A" then "CTRL+D"')
    print('')
    input('Hit any key to connect then reset your ESP32....')
    os.system(f'screen {port} {115200}')
    print()

    # Debrief
    print()
    print('Huzzah! We are all done!')
    print()
elif use_case == '3':
    # Connect
    print()
    print('Mounting the ESP32 filesystem to "./esp32"')
    print('Keep this window open while manipulating the filesystem.')
    print(f'mpy-fuse --port {port} ')
else:
    print('Not a valid selection. Run once more to try again.')