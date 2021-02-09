import RPi.GPIO as GPIO
import pychromecast
import time

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

#GPIO.setup(18,GPIO.OUT)
#GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("-- Discovering Devices\n")
available_devices = pychromecast.get_chromecasts()
print(available_devices)

for device in available_devices:
    #if device.friendly_name=='Office Speaker':
        time.sleep(1)
        print(str(device))
        print("- Current Volume: {0}%".format(int(device.status.volume_level*100)))
        
time.sleep(1)
        

"""
i=0
try:
    while i<10:
        button_state = GPIO.input(17)
        if button_state == False:
            GPIO.output(18, True)
            print("button pressed..")
            i=i+1
            print(i)
            time.sleep(.2)
        else:
            GPIO.output(18,False)
except:
    print("there was an exception")
    GPIO.cleanup()

GPIO.output(18,False)
"""
