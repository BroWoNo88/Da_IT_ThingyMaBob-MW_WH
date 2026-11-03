# IoT device - Predictive Maintenance in Machinery

This program reads a DHT11 sensor, displays humidity and an adjustable limit on two LED bars, and uses a buzzer with two warnings and an alarm when the humidity reaches or exceeds the limit.

## Hardware

- Raspberry Pi Pico W
- DHT11 temperature humidity sensor on GP0
- Buzzer (passive, not active) on GP16
- Button on GP14, connected to ground when pressed
- Potentiometer with middle leg on ADC0 (GP26) and side legs on 3V3 Out and Ground
- 5 red LEDS on GP2-GP6 for humidity with a ~330 ohms resistor for each
- 5 green LEDS on GP7-GP11 for limit with a ~330 ohms resistor for each

## Run it

Ensure the Pico W has MicroPython and the `dht` module installed.

Run `main.py` on the board. Press the button to preview and adjust the limit with the potentiometer, then press it again to set the limit.

When humidity is close to the limit, the buzzer beeps at intervals. When it reaches the limit or goes above it, an alarm sounds between two alternating tones. Humidity readings and a heartbeat (to ensure the device has not been disconnected) are printed to the serial console.

Pins, and warning and alarm sounds and timings can be adjusted at the top of the script with the constant variables.
