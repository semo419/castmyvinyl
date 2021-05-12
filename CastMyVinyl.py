import RPi.GPIO as GPIO
import sys
import pychromecast
import time
import datetime

print(datetime.datetime.now())
print("Beginning Execution of Cast My Vinyl")


##########################
### Define Chromecast Targets
#########################

#Here, There, Everywhere
targets=["Downstairs Speakers","Upstairs Speakers","All Devices"]
#targets[0]="Downstairs Speakers"
#targets[1]="Upstairs Speakers"
#targets[2]="All Devices"
audiostream="http://192.168.86.32:8000/mystream.mp3"

##########################
### Setup GPIO and naming of buttons and lights
##########################

buttons=[22,27,17]
#buttons[0]=22
#buttons[1]=27
#buttons[2]=17

lights=[25,24,23]
#lights[0]=25
#lights[1]=24
#lights[2]=23
statuslight=16

clk=19
dt=26
voltmeter=21

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(voltmeter,GPIO.OUT)
GPIO.setup(clk,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(statuslight,GPIO.OUT)
GPIO.setup(lights[0],GPIO.OUT)
GPIO.setup(lights[1],GPIO.OUT)
GPIO.setup(lights[2],GPIO.OUT)

GPIO.setup(buttons[0],GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttons[1],GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttons[2],GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(statuslight,False)
GPIO.output(lights[0],False)
GPIO.output(lights[1],False)
GPIO.output(lights[2],False)

#initialize PWM and cycle to show startup
pwm = GPIO.PWM(voltmeter,100)
pwm.start(100)
time.sleep(2)
pwm.ChangeDutyCycle(0)
time.sleep(2)

#set volume control parameters
VoltMeterScale=1 #adjustment factor for output voltage vs. max of voltmeter
increment=2 #bigger increment makes the volume knob more sensitive
initialVolume=50 #initial volume level when casting
setVolumeInterval=300 #counter to control how frequently volume change requests are sent to google
connectiontimeout=10


##########################
### Function to Cast to a chromecast target and monitor until playback stops or the button is pressed again
##########################

def cast_and_monitor(
    button, 
    #source="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",sourceaudiotype="vide/mp4"):
    source=audiostream,sourceaudiotype="audio/mp3"):

    #define button order
    if button==0: fbuttons=[0,1,2]
    if button==1: fbuttons=[1,0,2]
    if button==2: fbuttons=[2,0,1]
    newbutton=button

    #Illuminate status indicator
    GPIO.output(lights[button], True)
    print("Attempting Cast...")
    
    #Open connection to chromecast device
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[targets[button]])
    cast = chromecasts [0]

    #start worker thread and wait for cast device to be ready
    cast.wait()
    print("Casting to "+cast.device.friendly_name)

    #start media
    mc = cast.media_controller
    cast.set_volume(initialVolume/100)
    mc.play_media(source,sourceaudiotype)
    mc.block_until_active()
    print(mc.status.player_state)
    
    #wait for stream start
    time.sleep(5)
    timeout=5
    while mc.status.player_state!="PLAYING" and timeout<connectiontimeout:
        time.sleep(1)
        timeout=timeout+1
        print(timeout)
    print(mc.status.player_state)
 
    #start PWM and volume control
    setVolumeCounter=1
    priorVolume=initialVolume
    counter=initialVolume
    clkLastState=GPIO.input(clk)
    pwm.ChangeDutyCycle(counter*VoltMeterScale)
    
    #Loop to control volume and monitor for button presses
    while (mc.status.player_state=="PLAYING" or mc.status.player_state=="BUFFERING"):
    #while GPIO.input(button)==True:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        if clkState != clkLastState:
            if dtState == clkState and counter < 100:
                counter += increment
            elif counter > 0:
                counter -= increment
            #print(counter)
            pwm.ChangeDutyCycle(counter*VoltMeterScale)
        setVolumeCounter=(setVolumeCounter+1)%setVolumeInterval
        if setVolumeCounter == 0 and priorVolume!=counter:
            #print("Set Volume")
            cast.set_volume(counter/100)
            priorVolume=counter
        clkLastState = clkState
        if (GPIO.input(buttons[0])==False or GPIO.input(buttons[1])==False or GPIO.input(buttons[2])==False):
            if GPIO.input(buttons[fbuttons[1]])==False: newbutton=fbuttons[1]
            if GPIO.input(buttons[fbuttons[2]])==False: newbutton=fbuttons[2]
            break
        time.sleep(.002)
        #print(mc.status.player_state)
        #print(GPIO.input(button))

    #End cast, close connection, and turn off light and volume
    print("Closing Cast Session")
    GPIO.output(lights[button], False)
    pwm.ChangeDutyCycle(0)
    mc.stop()
    time.sleep(1)
    #print(mc.status.player_state)
    #cast.disconnect()
    pychromecast.discovery.stop_discovery(browser)
    time.sleep(1)

    print(button)
    print(newbutton)
    if newbutton==button: return

    print("didn't leave")
    cast_and_monitor(newbutton)


#Testing line - runs function without try to surface exceptions in testing
#cast_and_monitor(button=0)

##########################
### Continuous Loop Monitoring the 3 main buttons and beginning cast when they are pressed
#########################


try:
    GPIO.output(statuslight,True)
    while True:
        if GPIO.input(buttons[0])==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button=0)
            except:
                print("Function cast_and_monitor failed")
                GPIO.output(lights[0], False)
                pwm.ChangeDutyCycle(0)
            GPIO.output(statuslight, True)
        elif GPIO.input(buttons[1])==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button=1)
            except:
                print("Function cast_and_monitor failed")
                GPIO.output(lights[1], False)
                pwm.ChangeDutyCycle(0)
            GPIO.output(statuslight, True)
        elif GPIO.input(buttons[2])==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button=2)
            except:
                print("Function cast_and_monitor failed")
                GPIO.output(lights[2], False)
                pwm.ChangeDutyCycle(0)
            GPIO.output(statuslight, True)
        time.sleep(.05)

except:
    print("there was an exception")
    pwm.ChangeDutyCycle(0)
    GPIO.cleanup()

GPIO.cleanup()

