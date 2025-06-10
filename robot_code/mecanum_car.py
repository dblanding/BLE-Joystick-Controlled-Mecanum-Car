# mecanum_car.py (aka main.py)

import aioble
import asyncio
import bluetooth
import struct
from machine import Pin
from math import pi
from pico_car import Motor
from geom2d import r2p, p2r

# setup onboard LED
led = Pin("LED", Pin.OUT, value=0)

# BLE values
ble_name = "3axis_joystk"
ble_svc_uuid = bluetooth.UUID(0x1812)
ble_characteristic_uuid = bluetooth.UUID(0x2A4D)
ble_scan_length = 5000
ble_interval = 30000
ble_window = 30000

async def ble_scan():
    print("Scanning for BLE beacon named", ble_name, "...")
    async with aioble.scan(
    ble_scan_length,
    interval_us=ble_interval,
    window_us=ble_window,
    active=True) as scanner:
        async for result in scanner:
            if result.name() == ble_name and \
               ble_svc_uuid in result.services():
                return result.device
    return None

def decode(data):
    return struct.unpack("3i", data)

# Use the Motor class provided by Adeept
motor = Motor()

# individual motors
m1 = motor.motor_left_front
m2 = motor.motor_right_front
m3 = motor.motor_right_back
m4 = motor.motor_left_back

def mtr1(spd):
    """Run motor1 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m1(1, direction, abs(spd))

def mtr2(spd):
    """Run motor2 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m2(1, direction, abs(spd))

def mtr3(spd):
    """Run motor3 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m3(1, direction, abs(spd))

def mtr4(spd):
    """Run motor4 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m4(1, direction, abs(spd))

def drive_motors(joyvals):
    x, y, z = joyvals
    
    # scale x & y to +/- 100, z to +/- 50
    x = int(x * 100/127)
    y = int(y * 100/127)
    z = int(z * 50/127)
    
    # rotate 45 deg so joystk Y aligns w/ front of car
    r, theta = r2p(x, y)
    theta -= pi/4
    x, y = p2r(r, theta)

    # superimpose all DOF to get correct spd of each mtr
    m1_spd = x-z
    m2_spd = y+z
    m3_spd = x+z
    m4_spd = y-z

    # drive the motors
    mtr1(m1_spd)
    mtr2(m2_spd)
    mtr3(m3_spd)
    mtr4(m4_spd)

async def main():
    while True:
        device = await ble_scan()
        if not device:
            print("BLE beacon not found.")
            continue

        try:
            print("Connecting to", device)
            connection = await device.connect()
        except asyncio.TimeoutError:
            print("Connection timed out.")
            continue

        async with connection:
            try:
                ble_service = await connection.service(ble_svc_uuid)
                ble_characteristic = await \
                  ble_service.characteristic(ble_characteristic_uuid)
            except (asyncio.TimeoutError, AttributeError):
                print("Timeout discovering services/characteristics.")
                continue

            while True:
                try:
                    data = decode(await ble_characteristic.read())
                    print(f"Joystick Values: {data}")
                    drive_motors(data)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Error: {e}")
                    continue

asyncio.run(main())
