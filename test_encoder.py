import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        print('CLK(19)=%d  DT(26)=%d' % (GPIO.input(19), GPIO.input(26)))
        time.sleep(0.05)
except KeyboardInterrupt:
    GPIO.cleanup()
