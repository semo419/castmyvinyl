import RPi.GPIO as GPIO
import time
import os

# All BCM GPIO pins available on the Pi
PINS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
        19, 20, 21, 22, 23, 24, 25, 26, 27]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

prev = {}

try:
    print("Monitoring all GPIO pins. Turn the knob, press buttons, etc.")
    print("Only changes are printed. Ctrl+C to exit.\n")
    while True:
        current = {pin: GPIO.input(pin) for pin in PINS}
        for pin, val in current.items():
            if val != prev.get(pin):
                print("GPIO %2d changed: %d -> %d" % (pin, prev.get(pin, -1), val))
        prev = current
        time.sleep(0.005)
except KeyboardInterrupt:
    GPIO.cleanup()
