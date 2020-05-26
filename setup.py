import os

##############
# Parameters
##############
firmware_file_name          = 'tinypico-idf4-20200526-unstable-v1.12-464-gcae77daf0.bin'   

#################
# Install Script
#################

# Download tools
os.system('pip install esptool pyserial glob')
os.system(f'wget https://micropython.org/resources/firmware/{firmware_file_name}')
os.system('wget https://raw.githubusercontent.com/Ladvien/ramps_controller/master/ramps_controller/serial_util.py')

# Grab some code I wrote (or stole?) for a different project.
from serial_util import *

# Get the port from the user.
print('########################################################')
print('# Welcome to Ladvien\'s ESP32 Micropython setup script #')
print('# First, select the port your ESP32 is on.             #')
print('########################################################')
port = get_write_port()
print()
print()

# Flash the ESP32
input('About Erasing EVERYTHING on the ESP32. Hit a key if you accept.')
os.system(f'esptool.py --chip esp32 -p {port} erase_flash')

# Install Micropython
print()
print()
print('Installing Micropython!')
os.system(f'esptool.py --chip esp32 -p {port} write_flash -z 0x1000 {firmware_file_name}')

# Debrief
print()
print('Huzzah! We are all done!')
print()