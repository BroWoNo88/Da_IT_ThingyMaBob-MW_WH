import time
import random
from machine import Pin
heart_rate = 80
led = Pin(0, Pin.OUT)
buzz = Pin(1, Pin.OUT)
while True:
  buzz.on()
  led.on()
  sleep(0.5)
  buzz.off()
  led.off()
