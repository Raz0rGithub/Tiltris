import time
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from busio import I2C
import adafruit_bme680
from adafruit_lis3mdl import LIS3MDL
from analogio import AnalogIn
from adafruit_debouncer import Debouncer

i2c = I2C(board.SCL, board.SDA)  # Create library object using our Bus I2C port
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

dT = 0.1
cooldown = 0
while True:
    acceleration = accel_gyro.acceleration
    ax = acceleration[0] + 0.01
    ay = acceleration[1] - 0.11
    az = acceleration[2] - 9.89

    cooldown -= 1
    if (cooldown <= 0):
        if ax < -1.0:
            print("move_left()")
        if ax > 1.0:
            print("move_right()")

    # left

    # print(
    #    "Acceleration: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2".format(ax,ay,az)
    # )
    # print("")
    time.sleep(dT)
