import RPi.GPIO as GPIO
import sys
import time

clk=19
dt=26
VoltMeterScale=1 #adjustment factor for output voltage vs. max of voltmeter
increment=2 #bigger increment makes the volume knob more sensitive

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(21,GPIO.OUT)
GPIO.setup(clk,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

pwm = GPIO.PWM(21,100)
pwm.start(100)

time.sleep(2)

pwm.ChangeDutyCycle(50)

time.sleep(2)

counter=50
clkLastState=GPIO.input(clk)

try:
    while True:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        if clkState != clkLastState:
            if dtState == clkState and counter < 100:
                counter += increment
            elif counter > 0:
                counter -= increment
            print(counter)
            pwm.ChangeDutyCycle(counter*VoltMeterScale)
        clkLastState = clkState
        #time.sleep(0.01)

except KeyboardInterrupt:
    print("Ctl C pressed - ending program")

pwm.ChangeDutyCycle(0)
GPIO.cleanup()

