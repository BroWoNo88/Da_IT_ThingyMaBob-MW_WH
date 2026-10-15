import time
import random
from machine import Pin
import asyncio
heart_rate = 80
led = Pin(0, Pin.OUT)
buzz = Pin(1, Pin.OUT)
red = Pin(2, Pin.OUT)
green = Pin(3, Pin.OUT)
alive = True
def check_heart_rate():
    global heart_rate
    change = random.randint(-10, 10) 
    if heart_rate < 80:
        change += 2 
        heart_rate += change
    elif heart_rate > 80:
        change -= 2
        heart_rate += change
    else:
        heart_rate += change
    # i mean we gotta keep it realistic sooo
    if heart_rate < 0:
        alive = False
    elif heart_rate > 250:
        heart_rate = 250

async def beep_rate():
    while True:
        led.on()
        buzz.on()
        await asyncio.sleep(0.05)
        buzz.off()
        led.off()
        await asyncio.sleep(60/heart_rate - -0.05) 

        
async def check_rate():
    while True:
        check_heart_rate()
        if heart_rate > 110 or heart_rate < 50:
            red.on()
            green.off()
        else:
            red.off()
            green.on()
        print("Resting Heart rate is", round(heart_rate), "BPM")
        await asyncio.sleep(1)

async def main():

        await asyncio.gather(
            beep_rate(),
            check_rate()
    )

while alive:
    actual_thing = asyncio.get_event_loop()
    actual_thing.create_task(main())
    actual_thing.run_forever()
if not alive:
    while True:
        buzz.on()
        time.sleep(1)
        print("They be dead bro, like they heart rate was 0")
