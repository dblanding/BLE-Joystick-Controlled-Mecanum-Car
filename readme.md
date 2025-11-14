# Replace IR remote control for [Adeept Mecanum Wheel Robotic Car](https://www.amazon.com/Adeept-Omni-Directional-Raspberry-Controlled-Educational/dp/B0BF5GVJK8?ref_=ast_sto_dp) with [3-axis Joystick](https://a.co/d/4GYH1ec) control.

![Addept Mecanum Car Kit + Joystick](imgs/Adeept_mecanum_car_+_joystick.png)

## Why replace the push-button IR remote with a Joystick?
* With the push-button IR remote controller, the robot car is only capable of moving in a single direction at a time.
    * For example, the robot can move forward / backward **or** right / left **or** spin CW / CCW. One at a time.
    * It can't do more than one of these things at the same time.
* With the joystick, it will be capable of much more graceful motion, simultaneously moving in all 3 degrees of freedom.
    * For example, it can move in **any direction** while spinning on its axis, if so directed.
* Pico microcontrollers have built-in BLE communication. Since the Adeept robot car uses a pico, it seems it should be possible to use this built-in BLE to send joystick axis values to it.
    * Let's do some research into how to proceed...

### The Picos come with built-in support for Bluetooth LE
* In chapter 12 of the book [Get Started with MicroPython on Raspberry Pi Pico](https://magazine.raspberrypi.com/books/get-started-micropython-pico-2ed) there is a well documented example showing how to send temperature values from one Pico W to another via Bluetooth LE.
* It's pretty strightforward to hook up a 3-axis joystick to the three ADC pins on the Pico and send the joystick axis values instead.
* The files `3axis_joystk_ble_server.py` and `3axis_joystk_client.py` show the details of this.
* The client code is adapted to operate the Mecanum Car in the file `mecanum_car.py`.

### How the Mecanum wheels work
* The image below shows the Adeept Mecanum Wheel Car overlaid on a diagram showing its *natural* X & Y axes.
    * If wheels 1 & 3 are driven forward, the car will move in the X direction. The rollers on wheels 2 & 4 will spin freely to allow this.
    * If wheels 2 & 4 are driven forward, the car will move in the Y direction. The rollers on wheels 1 & 3 will spin freely to allow this.
    * If the right wheels are driven forward and the left wheels are driven backward, the car will spin in place CCW.
    * These 3 degrees of freedom are independent, allowing them to be combined in any proportion without affecting each other. This allows the car to move gracefully in any direction, fast or slow, while also spinning about its axis, either CW or CCW.

![Natural Axes of Mecanum Wheel Car](imgs/mecanum_car_axes.jpeg)

* A 3-axis joystick, such as the one shown below, is a very *intuitive* interface for controlling the mecanum wheel car. In addition to the X & Y axes, the joystick has a knob that can be twisted (in theta-Z).

![Joystick Axes](imgs/joystick_axes.jpeg)

* To make the joystick even more intuitive, it can be arranged to have the Joystick Y axis aligned in the same direction as the front of the car. This can be accomplished quite simply by doing the following:
    1. Convert the joystick X, Y coordinates to polar coordinates (R, theta).
    2. Subtract pi/4 from theta.
    3. Convert back to rectangular coordinates.
    4. Use the new coordinates to drive the motors.

### Performance in operation
* The first thing I discovered is that the powerbank I am using to power the joystick remote shuts off spontaneously becasue the current draw from the pico is so low. It doesn't do trickle. So I plugged it into my laptop USB for power.
* The video below shows how the robot being controlled in all 3 DOF with **X**, **Y**, and **θz** all superimposed.

https://github.com/user-attachments/assets/002a17ee-53f1-4d82-afa3-9c98e6867681
