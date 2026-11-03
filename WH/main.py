from machine import ADC, PWM, Pin
from time import sleep_ms, ticks_diff, ticks_ms
import dht

BUZZER_PIN = 16
BUTTON_PIN = 14
POT_PIN = 26 # ADC0
HUMIDITY_PIN = 0
HEARTBEAT_INTERVAL_MS = 1000
BUTTON_DEBOUNCE_MS = 30
GREEN_FLASH_MS = 300 # limit-adjusting flash speed
WARNING_FREQUENCY = 1000
ALARM_LOW_FREQUENCY = 1000
ALARM_HIGH_FREQUENCY = 2000
ALARM_TONE_MS = 150 # alarm alternates between these two tones at this rate
BEEP_DURATION_MS = 100 # duration for warning and close warning beeps
WARNING_INTERVAL_MS = 1000
CLOSE_WARNING_INTERVAL_MS = 500
WARNING_RATIO = 0.90 # within 1-x% of the limit
CLOSE_WARNING_RATIO = 0.95 # within 1-x% of the limit but scarier beeping

DHT11 = dht.DHT11(Pin(HUMIDITY_PIN))
LEDS = tuple(PWM(Pin(gpio)) for gpio in range(2, 12))
for led in LEDS:
    led.freq(1000)
GAMMA = 2.2
MAX_DUTY = 65535
POT = ADC(POT_PIN)
BUTTON = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
BUZZER = PWM(Pin(BUZZER_PIN), freq=WARNING_FREQUENCY, duty_u16=0)
limit = POT.read_u16() / MAX_DUTY
adjusting = False
button_raw = BUTTON.value()
button_stable = button_raw
button_changed = ticks_ms()
flash_started = button_changed
humidity = None
last_read = 0
last_beep = 0
last_heartbeat = 0
previous_interval = None


def bar(percent):
    # gamma correction function
    level = min(100, max(0, percent)) / 20
    return tuple(min(1.0, max(0.0, level - i)) ** GAMMA for i in range(5))


def buzzer_interval(level, limit):
    # return None for silence, 0 for alarm, or the beep interval in ms
    if level is None:
        return None
    if level > limit:
        return 0
    if level >= limit * CLOSE_WARNING_RATIO:
        return CLOSE_WARNING_INTERVAL_MS
    if level >= limit * WARNING_RATIO:
        return WARNING_INTERVAL_MS
    return None


try:
    while True:
        now = ticks_ms()
        if ticks_diff(now, last_read) >= 2000:
            try:
                DHT11.measure()
                humidity = DHT11.humidity() / 100
                print("Humidity: {:.0f}%".format(humidity * 100))
            except OSError as e:
                print("DHT11 read failed:", e)
            last_read = now

        raw = BUTTON.value()
        if raw != button_raw:
            button_raw = raw
            button_changed = now
        if raw != button_stable and ticks_diff(now, button_changed) >= BUTTON_DEBOUNCE_MS:
            button_stable = raw
            if raw == 0:
                adjusting = not adjusting
                flash_started = now
                if not adjusting:
                    limit = POT.read_u16() / MAX_DUTY

        displayed_limit = POT.read_u16() / MAX_DUTY if adjusting else limit
        red = bar((humidity or 0) * 100)
        green = bar(displayed_limit * 100)
        if adjusting:
            if ticks_diff(now, flash_started) >= GREEN_FLASH_MS * 2:
                flash_started = now
            if ticks_diff(now, flash_started) >= GREEN_FLASH_MS:
                green = (0, 0, 0, 0, 0)
        for led, brightness in zip(LEDS[:5], red):
            led.duty_u16(round(brightness * MAX_DUTY))
        for led, brightness in zip(LEDS[5:], green):
            led.duty_u16(round(brightness * MAX_DUTY))

        interval = buzzer_interval(humidity, limit)
        if interval != previous_interval:
            last_beep = now
        if interval is not None and interval > 0:
            if ticks_diff(now, last_beep) >= interval:
                last_beep = now
        if interval == 0:
            if ticks_diff(now, last_beep) >= ALARM_TONE_MS * 2:
                last_beep = now
            BUZZER.freq(
                ALARM_LOW_FREQUENCY
                if ticks_diff(now, last_beep) < ALARM_TONE_MS
                else ALARM_HIGH_FREQUENCY
            )
        else:
            BUZZER.freq(WARNING_FREQUENCY)
        sounding = interval == 0 or (
            interval is not None and ticks_diff(now, last_beep) < BEEP_DURATION_MS
        )
        BUZZER.duty_u16(32768 if sounding else 0)
        previous_interval = interval
        if ticks_diff(now, last_heartbeat) >= HEARTBEAT_INTERVAL_MS:
            print("HEARTBEAT ticks_ms={}".format(now))
            last_heartbeat = now
        sleep_ms(10)
finally:
    BUZZER.duty_u16(0)
    BUZZER.deinit()
    Pin(BUZZER_PIN, Pin.OUT, value=0)
