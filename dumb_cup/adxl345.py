# https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf
from machine import Pin
from machine import I2C
import time
import ustruct

class ADXL345:

    EXPECTED_ADXL345_ADDR = 0xE5
    DEVICE_ADDR           = 0x53
    DATA_FORMAT           = 0x31

    BW_RATE               = 0x2c
    POWER_CTL             = 0x2d
    INT_ENABLE            = 0x2E
    OFSX                  = 0x1e
    OFSY                  = 0x1f
    OFSZ                  = 0x20

    def __init__(self, scl, sda, cs):
        self.scl = Pin(scl)
        self.sda = Pin(sda)
        self.cs = Pin(cs)
        self.i2c = I2C(scl = self.scl, sda = self.sda, freq = 20000, timeout = 2000)
        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0

        dev = self.i2c.scan()
        print(dev)

        for s in dev:
            buf = self.i2c.readfrom_mem(s, 0, 1)
            if(buf[0] == self.EXPECTED_ADXL345_ADDR):
                self.slvAddr = s
                print('ADXL345 found.')
                break

        # self.writeByte(POWER_CTL,0x00)  #sleep
        # time.sleep(0.001)

        # Low-level interrupt output
        # 13-bit full resolution
        # output data right-justified, 16g range
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.DATA_FORMAT, b'\x2B')

        # Data output speed is 100Hz
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.BW_RATE, b'\x0A')

        # No interrupts
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.INT_ENABLE, b'\x00')

        self.i2c.writeto_mem(self.DEVICE_ADDR, self.OFSX, b'\x00')
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.OFSY, b'\x00')
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.OFSZ, b'\x00')

        # Link enable, measurement mode
        self.i2c.writeto_mem(self.DEVICE_ADDR, self.POWER_CTL, b'\x28')
        print("Warming up...")
        time.sleep(1)
        print("Ready.")

        self.x_offset, self.y_offset, self.z_offset = self.calibrate()

    def calibrate(self):
        x, y, z = self.readXYZ()
        return (x*-1, y*-1, z*-1)

    def readXYZ(self, round_err = 2):
        fmt = '<h' #little-endian
        buf1 = self.readByte(0x32)
        buf2 = self.readByte(0x33)
        buf = bytearray([buf1[0], buf2[0]])
        x, = ustruct.unpack(fmt, buf)
        x = round(x * 3.9 + self.x_offset, round_err)

        buf1 = self.readByte(0x34)
        buf2 = self.readByte(0x35)
        buf = bytearray([buf1[0], buf2[0]])
        y, = ustruct.unpack(fmt, buf)
        y = round(y * 3.9 + self.y_offset, round_err)

        buf1 = self.readByte(0x36)
        buf2 = self.readByte(0x37)
        buf = bytearray([buf1[0], buf2[0]])
        z, = ustruct.unpack(fmt, buf)
        z = round(z * 3.9 + self.z_offset, round_err)
        return (x,y,z)

    def writeByte(self, addr, data):
        d = bytearray([data])
        self.i2c.writeto_mem(self.slvAddr, addr, d)

    def readByte(self, addr):
        return self.i2c.readfrom_mem(self.slvAddr, addr, 1)