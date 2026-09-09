import time
import random
from machine import Pin
heart_rate = 80
led = Pin(0, Pin.OUT)
buzz = Pin(1, Pin.OUT)
red = Pin(2, Pin.OUT)
green = Pin(3, Pin.OUT)
def check_heart_rate():
    global heart_rate
    change = random.randint(-10, 10) 
    if heart_rate < 80:
        change += 2.0 
        heart_rate += change
    elif heart_rate > 80:
        change -= 2.0
        heart_rate += change
    else:
        heart_rate += change

while True:
    check_heart_rate()
    if heart_rate > 110 or heart_rate < 50:
        red.on()
        green.off()
    else:
        red.off()
        green.on()
    print("Resting Heart rate is", round(heart_rate), "BPM")
    led.on()
    buzz.on()
    time.sleep(0.05)
    buzz.off()
    led.off()
    time.sleep(60/heart_rate) #currently has a check based on heart rate, so bad`

