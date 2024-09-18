import adafruit_rfm9x
import busio
import board
import time
import digitalio
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from busio import I2C
from adafruit_lis3mdl import LIS3MDL
from adafruit_debouncer import Debouncer

# BOARD
i2c = I2C(board.SCL, board.SDA)  # Create library object using our Bus I2C port
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

# LORA
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D9)
reset = digitalio.DigitalInOut(board.D10)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0, baudrate=1000000)

# Var Inits
on = True
acceleration = [0, 0, 0]
ax_bias = 0
ay_bias = 0
az_bias = 0
gyro = [0, 0, 0]
gx_bias = 0
gy_bias = 0
gz_bias = 0

# Button 1
pin1 = digitalio.DigitalInOut(board.D6)
pin1.direction = digitalio.Direction.INPUT
pin1.pull = digitalio.Pull.UP
switch1 = Debouncer(pin1)

# Button 2
pin2 = digitalio.DigitalInOut(board.D5)
pin2.direction = digitalio.Direction.INPUT
pin2.pull = digitalio.Pull.UP
switch2 = Debouncer(pin2)


def button_1_short_press():
    print("on_off()")
    rfm9x.send('on_off()')
    global on
    on = not on


def button_1_long_press():
    print("reset()")
    rfm9x.send('reset()')


def button_2_short_press():
    print("start()")
    rfm9x.send('start()')


def button_2_long_press():
    global ax_bias, ay_bias, az_bias, gx_bias, gy_bias, gz_bias
    acceleration = accel_gyro.acceleration
    ax_bias = acceleration[0]
    ay_bias = acceleration[1]
    az_bias = acceleration[2]
    gyro = accel_gyro.gyro
    gx_bias = gyro[0]
    gy_bias = gyro[1]
    gz_bias = gyro[2]
    print("Bias Calculated.")
    print(
        "Acceleration Bias: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2".format(
            ax_bias, ay_bias, az_bias
        )
    )
    print(
        "Gyro Bias: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2".format(
            gx_bias, gy_bias, gz_bias
        )
    )


# BIAS CACLULATION
print()
print("Calculating Bias")
print("Center the position and tilt of your glove")
print("Hit Start once ready")
start = False
while start is False:
    switch1.update()
    if switch1.fell:
        button_1_short_press()
    if on:
        switch2.update()
        if switch2.fell:
            button_2_long_press()
            start = True

# MAIN EXECUTE LOOP
dT = 0.0166  # Clock Speed: 16.6ms / 60 hz / 60 times a second
cooldown = 0
position = 7
tilt_cooldown = 0
rotation = 0
S1Timer = 0
S2Timer = 0
while True:
    # Update
    switch1.update()
    S1Timer += 1
    if switch1.fell:
        S1Timer = 0
    if switch1.rose:
        if S1Timer > 60:
            button_1_long_press()
        else:
            button_1_short_press()

    if on:
        gyro = accel_gyro.gyro
        gx = gyro[0] - gx_bias
        gy = gyro[1] - gy_bias
        gz = gyro[2] - gz_bias
        acceleration = accel_gyro.acceleration
        ax = acceleration[0] - ax_bias
        ay = acceleration[1] - ay_bias
        az = acceleration[2] - az_bias

        S2Timer += 1
        switch2.update()
        if switch2.fell:
            S2Timer = 0
        if switch2.rose:
            if S2Timer > 60:
                button_2_long_press()
            else:
                button_2_short_press()

        x_tilt = (
            abs(ay) > 1.5
            or abs(az) > 1.5
            or abs(gz) > 0.5
            or abs(gy) > 0.5
            or abs(gx) > 0.5
        )
        cooldown -= 1
        tilt_cooldown -= 1

        if not x_tilt and cooldown < 0:
            if ax < -1.0:
                print("move_right()")
                rfm9x.send('move_right()')
                position += 1
                if position > 15:
                    position = 15

                if ax < -2.0:
                    cooldown = 8
                else:
                    cooldown = 16

            if ax > 1.0:
                print("move_left()")
                rfm9x.send('move_left()')
                position -= 1
                if position < 0:
                    position = 0
                if ax > 2.0:
                    cooldown = 8
                else:
                    cooldown = 16

        if tilt_cooldown < 0:
            if ay > 2.5:
                print("rotation()")
                rfm9x.send('rotation()')
                rotation += 1
                if rotation > 3:
                    rotation = 0

                if ay > 4:
                    tilt_cooldown = 20
                else:
                    tilt_cooldown = 40

            if ay < -6.0:
                print("hard_drop()")
                rfm9x.send('hard_drop()')
                tilt_cooldown = 30

            elif ay < -3.0:
                print("soft_drop()")
                rfm9x.send('soft_drop()')
                tilt_cooldown = 5

    time.sleep(dT)
