import RPi.GPIO as GPIO
import sys
import pychromecast
import time


##########################
### Function to Cast to a chromecast target and monitor until playback stops or the button is pressed again
##########################

def cast_and_monitor(
    button, light, target=["Office Speaker"], 
    source="http://192.168.86.41:8000/rapi.mp3",sourceaudiotype="audio/mp3"
):
    #Illuminate status indicator
    GPIO.output(light, True)
    print("Beginning Cast...")
    
    #Open connection to chromecast device
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=target)
    cast = chromecasts [0]
    
    #start worker thread and wait for cast device to be ready
    cast.wait()
    print("Casting to "+cast.device.friendly_name)

    #start media
    mc = cast.media_controller
    mc.set_volume(.5)
    mc.play_media(source,sourceaudiotype)
    time.sleep(1)
    
    print(mc.status)

    while GPIO.input(button)==True:
         pass
    
    #End cast, close connection, and turn off light
    mc.stop()
    pychromecast.discovery.stop_discovery(browser)
    GPIO.output(light, False)
    time.sleep(1)


##########################
### Function to monitor and play back volume
##########################

def volume_knob(
    button, light, target=["Living Room Speaker"], source="http://192.168.86.41:8000/rapi.mp3"
):
    pass



##########################
### Define Chromecast Targets
#########################

here="Office Speaker"
there="Bedroom speaker"
everywhere="Upstairs Speakers"
target_chromecasts=[here,there,everywhere]


##########################
### Setup GPIO and naming of buttons and lights
##########################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(16,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)

GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27,GPIO.IN, pull_up_down=GPIO.PUD_UP)

button1=22
button2=27
button3=17

light1=25
light2=24
light3=23
statuslight=16


##########################
### Continuous Loop Monitoring the 3 main buttons and beginning cast when they are pressed
#########################

i=0
try:
    GPIO.output(statuslight,True)
    while i<4:
        if GPIO.input(button1)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button1,light1)
            except:
                print("Function cast_and_monitor failed")
            i=i+1
            print(i)
            GPIO.output(statuslight, True)
        elif GPIO.input(button2)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button2,light2)
            except:
                print("Function cast_and_monitor failed")
            i=i+1
            print(i)
            GPIO.output(statuslight, True)
        elif GPIO.input(button3)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button3,light3)
            except:
                print("Function cast_and_monitor failed")
            i=i+1
            print(i)
            GPIO.output(statuslight, True)
except:
    print("there was an exception")
    GPIO.cleanup()

GPIO.cleanup()

