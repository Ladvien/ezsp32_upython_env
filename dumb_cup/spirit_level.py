# https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf
class SpiritLevel:

    def __init__(self, adxl345: ADXL345, callback, x_threshold: int, y_threshold: int, z_threshold: int):
        self.adxl345 = adxl345
        self.x_disturbance = 0
        self.y_disturbance = 0
        self.z_disturbance = 0

        self.x_threshold = x_threshold
        self.y_threshold = y_threshold
        self.z_threshold = z_threshold

        self.not_level_callback = callback

    def calculate(self):
        x, y, z = self.adxl345.readXYZ()
        if abs(x) > self.x_threshold or abs(y) > self.y_threshold or abs(z) > self.z_threshold:
            self.not_level_callback(x, y, z)