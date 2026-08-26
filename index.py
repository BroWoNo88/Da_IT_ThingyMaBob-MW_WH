# matthews heart beat thingy
import time
import random
from machine import Pin
heart_rate = 80
led = Pin(0, Pin.OUT)
buzz = Pin(1, Pin.OUT)
def check_heart_rate(heart_rate):
    change = random.randint(-5, 5) 
    if heart_rate < 80:
        change += 2.0 
    elif heart_rate > 80:
        change -= 2.0
    heart_rate += change

while True:
    check_heart_rate
    print("Resting Heart rate is", round(heart_rate), "BPM")
    print(" \n \n \n \n ") 
    led.on()
    buzz.on()
    time.sleep(0.05)
    buzz.off()
    led.off()
    time.sleep(heart_rate/60)
    print heart rate
