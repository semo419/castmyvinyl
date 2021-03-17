import RPi.GPIO as GPIO
import sys
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(21,GPIO.OUT)


pwm = GPIO.PWM(21,100)
pwm.start(100)

time.sleep(2)

pwm.ChangeDutyCycle(0)

time.sleep(2)

v=0
print(v)

try:
    while True:
        for v in range (0,100,1):
            pwm.ChangeDutyCycle(v)
            print(v)
            time.sleep(.05)
        for v in range (100,0,-20):
            pwm.ChangeDutyCycle(v)
            print(v)
            time.sleep(.5)
except KeyboardInterrupt:
    print("Ctl C pressed - ending program")

pwm.ChangeDutyCycle(0)
GPIO.cleanup()

