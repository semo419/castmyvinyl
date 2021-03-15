import RPi.GPIO as GPIO
import sys
import pychromecast
import time


##########################
### Function to Cast to a chromecast target and monitor until playback stops or the button is pressed again
##########################

def cast_and_monitor(
    button, light, target="Office Speaker", 
    source="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",sourceaudiotype="vide/mp4"):
    #source="http://192.168.86.41:8000/rapi.mp3",sourceaudiotype="audio/mp3"):

    #Illuminate status indicator
    GPIO.output(light, True)
    print("Beginning Cast...")
    
    #Open connection to chromecast device
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[target])
    cast = chromecasts [0]
    
    #start worker thread and wait for cast device to be ready
    cast.wait()
    print("Casting to "+cast.device.friendly_name)

    #start media
    mc = cast.media_controller
    cast.set_volume(.2)
    mc.play_media(source,sourceaudiotype)
    mc.block_until_active()
    
    #wait for stream start
    time.sleep(10)
    print(mc.status.player_state)

    while mc.status.player_state=="PLAYING" and GPIO.input(button)==True:
         #print(mc.status.player_state)
         pass

    #End cast, close connection, and turn off light
    print("Closing Cast Session")
    GPIO.output(light, False)
    mc.stop()
    time.sleep(5)
    print(mc.status.player_state)
    pychromecast.discovery.stop_discovery(browser)
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

#Here, There, Everywhere
target1="Office Speaker"
target2="Office Speaker"
target3="Office Speaker"


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

GPIO.output(statuslight,False)
GPIO.output(light1,False)
GPIO.output(light2,False)
GPIO.output(light3,False)



##########################
### Continuous Loop Monitoring the 3 main buttons and beginning cast when they are pressed
#########################

#cast_and_monitor(button1,light1)

i=0
try:
    GPIO.output(statuslight,True)
    while i<4:
        if GPIO.input(button1)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button1,light1,target1)
            except:
                print("Function cast_and_monitor failed")
            i=i+1
            print(i)
            GPIO.output(statuslight, True)
        elif GPIO.input(button2)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button2,light2,target2)
            except:
                print("Function cast_and_monitor failed")
            i=i+1
            print(i)
            GPIO.output(statuslight, True)
        elif GPIO.input(button3)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button3,light3,target3)
            except:
                print("Function cast_and_monitor failed")
            i=i+1
            print(i)
            GPIO.output(statuslight, True)

except:
    print("there was an exception")
    GPIO.cleanup()

GPIO.cleanup()

