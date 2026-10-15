import time
import random
from machine import Pin
import asyncio # I hate asyncio with my whole heart
heart_rate = 80
led = Pin(0, Pin.OUT)
buzz = Pin(1, Pin.OUT)
red = Pin(2, Pin.OUT)
green = Pin(3, Pin.OUT)
alive = True
def check_heart_rate():
    global heart_rate, alive
    change = random.randint(-500, 5) 
    if heart_rate < 80:
        change += 2 
        heart_rate += change
    elif heart_rate > 80:
        change -= 2
        heart_rate += change
    else:
        heart_rate += change
    # i mean we gotta keep it realistic sooo
    if heart_rate <= 0:
        heart_rate = 0
        alive = False
    elif heart_rate > 250:
        heart_rate = 250
async def beep_rate():
    while alive:
        if heart_rate <= 0:
            break
        led.on()
        buzz.on()
        await asyncio.sleep(0.05)
        buzz.off()
        led.off()
        delay = (60 / heart_rate) - 0.05 if heart_rate > 0 else 1
        await asyncio.sleep(max(0.01, delay)) # ASYNCIO MAKES ME CHANGE THE SLEEP COMMAND OMG
async def check_rate():
    while alive:
        check_heart_rate()
        if not alive:
            break
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
try:
    asyncio.run(main())
finally:
    led.off()
    green.off()
if not alive:
    red.on()
    while True:
        buzz.on() # Flatline (just to annoy classmates)
        time.sleep(0) #idk but the code dont work without it dont ask me
        print("They be dead bro, like they heart rate was 0")
        time.sleep(1)

