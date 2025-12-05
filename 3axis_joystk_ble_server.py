# 3axis_joystk_ble_server.py (aka main.py)

import struct
import asyncio
import aioble
import bluetooth
from machine import ADC, Pin
import time

# Set up onboard LED
led = Pin("LED", Pin.OUT, value=0)

# Set up pin to switch to tare mode
tare = Pin(15, Pin.IN, Pin.PULL_DOWN)

# Set up joystick on ADC pins
adc_x = ADC(Pin(26))
adc_y = ADC(Pin(27))
adc_z = ADC(Pin(28))

# BLE values
ble_name = "3axis_joystk"
ble_svc_uuid = bluetooth.UUID(0x1812)
ble_characteristic_uuid = bluetooth.UUID(0x2A4D)
ble_appearance = 0x03C3
ble_advertising_interval = 2000
ble_service = aioble.Service(ble_svc_uuid)
ble_characteristic = aioble.Characteristic(
    ble_service,
    ble_characteristic_uuid,
    read=True,
    notify=True)
aioble.register_services(ble_service)

def encode(x, y, z):
    return struct.pack("3i", x, y, z)

async def ble_task():
    while True:
        async with await aioble.advertise(
            ble_advertising_interval,
            name=ble_name,
            services=[ble_svc_uuid],
            appearance=ble_appearance) as connection:
            print("Connection from", connection.device)
            await connection.disconnected()

async def joystk_task():
    # Initial trim values for tare mode
    x_trim = 0
    y_trim = 0
    z_trim = 0
    while True:
        # get joystick axis values
        js_x = adc_x.read_u16()
        js_y = adc_y.read_u16()
        js_z = adc_z.read_u16()

        # convert to ints: -127 < value < 127
        x = round(js_x / 256) - 128 - x_trim
        y = round(js_y / 256) - 128 - y_trim
        z = round(js_z / 256) - 128 - z_trim

        # in tare mode?
        if tare.value():
            # adjust trim values to null output
            x_trim += x
            y_trim += y
            z_trim += z
            print(f"Trim values: {x_trim}, {y_trim}, {z_trim}")

        else:
            ble_characteristic.write(encode(x, y, z))
        led.toggle()
        await asyncio.sleep_ms(100)

async def main():
    task1 = asyncio.create_task(ble_task())
    task2 = asyncio.create_task(joystk_task())
    await asyncio.gather(task1, task2)

print("Launching BLE joystick server...")
asyncio.run(main())
