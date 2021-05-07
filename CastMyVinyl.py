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
target1="Downstairs Speakers"
target2="Upstairs Speakers"
target3="All Devices"
audiostream="http://192.168.86.32:8000/mystream.mp3"

##########################
### Setup GPIO and naming of buttons and lights
##########################

button1=22
button2=27
button3=17

light1=25
light2=24
light3=23
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
GPIO.setup(light1,GPIO.OUT)
GPIO.setup(light2,GPIO.OUT)
GPIO.setup(light3,GPIO.OUT)

GPIO.setup(button1,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button3,GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(statuslight,False)
GPIO.output(light1,False)
GPIO.output(light2,False)
GPIO.output(light3,False)

#initialize PWM and cycle to show startup
pwm = GPIO.PWM(voltmeter,100)
pwm.start(100)
time.sleep(2)
pwm.ChangeDutyCycle(0)
time.sleep(2)

#set volume control parameters
VoltMeterScale=1 #adjustment factor for output voltage vs. max of voltmeter
increment=2 #bigger increment makes the volume knob more sensitive
initialVolume=40 #initial volume level when casting
setVolumeInterval=300 #counter to control how frequently volume change requests are sent to google
connectiontimeout=10

##########################
### Function to kill cast session
##########################

def kill(self, idle_only=False, force=False):
        """
        Kills current Chromecast session.

        :param idle_only: If set, session is only killed if the active Chromecast app
                          is idle. Use to avoid killing an active streaming session
                          when catt fails with certain invalid actions (such as trying
                          to cast an empty playlist).
        :type idle_only: bool
        :param force: If set, a dummy chromecast app is launched before killing the session.
                      This is a workaround for some devices that do not respond to this
                      command under certain circumstances.
        :type force: bool
        """

        if idle_only and not self._is_idle:
            return
        # The Google cloud app which is launched by the workaround is functionally
        # identical to the Default Media Receiver.
        if force:
            listener = CastStatusListener(CLOUD_APP_ID)
            self._cast.register_status_listener(listener)
            self._cast.start_app(CLOUD_APP_ID)
            listener.app_ready.wait()
        self._cast.quit_app() 

##########################
### Function to Cast to a chromecast target and monitor until playback stops or the button is pressed again
##########################

def cast_and_monitor(
    button, light, target="Office Speaker", 
    #source="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",sourceaudiotype="vide/mp4"):
    source=audiostream,sourceaudiotype="audio/mp3"):

    #Illuminate status indicator
    GPIO.output(light, True)
    setVolumeCounter=1
    priorVolume=initialVolume
    print("Attempting Cast...")
    
    #Open connection to chromecast device
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[target])
    print("db 3")
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
    
    #start PWM and volume control
    counter=initialVolume
    clkLastState=GPIO.input(clk)
    
    #wait for stream start
    time.sleep(5)
    timeout=5
    while mc.status.player_state!="PLAYING" and timeout<connectiontimeout:
        time.sleep(1)
        timeout=timeout+1
        print(timeout)

    print(mc.status.player_state)
    print(GPIO.input(button))

    pwm.ChangeDutyCycle(counter*VoltMeterScale)
    
    while (mc.status.player_state=="PLAYING" or mc.status.player_state=="BUFFERING") and GPIO.input(button)==True:
    #while GPIO.input(button)==True:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        if clkState != clkLastState:
            if dtState == clkState and counter < 100:
                counter += increment
            elif counter > 0:
                counter -= increment
            print(counter)
            pwm.ChangeDutyCycle(counter*VoltMeterScale)
        setVolumeCounter=(setVolumeCounter+1)%setVolumeInterval
        if setVolumeCounter == 0 and priorVolume!=counter:
            print("Set Volume")
            cast.set_volume(counter/100)
            priorVolume=counter
        clkLastState = clkState
        time.sleep(.002)
        #print(mc.status.player_state)
        #print(GPIO.input(button))

    #End cast, close connection, and turn off light and volume
    print("Closing Cast Session")
    GPIO.output(light, False)
    pwm.ChangeDutyCycle(0)
    mc.stop()
    time.sleep(5)
    print(mc.status.player_state)
    pychromecast.discovery.stop_discovery(browser)
    kill(cast)
    time.sleep(1)


#cast_and_monitor(button1,light1,target1)

##########################
### Continuous Loop Monitoring the 3 main buttons and beginning cast when they are pressed
#########################

#cast_and_monitor(button1,light1)

try:
    GPIO.output(statuslight,True)
    while True:
        if GPIO.input(button1)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button1,light1,target1)
            except:
                print("Function cast_and_monitor failed")
                GPIO.output(light1, False)
                pwm.ChangeDutyCycle(0)
            GPIO.output(statuslight, True)
        elif GPIO.input(button2)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button2,light2,target2)
            except:
                print("Function cast_and_monitor failed")
                GPIO.output(light2, False)
                pwm.ChangeDutyCycle(0)
            GPIO.output(statuslight, True)
        elif GPIO.input(button3)==False:
            GPIO.output(statuslight, False)
            try:
                cast_and_monitor(button3,light3,target3)
            except:
                print("Function cast_and_monitor failed")
                GPIO.output(light3, False)
                pwm.ChangeDutyCycle(0)
            GPIO.output(statuslight, True)
        time.sleep(.05)

except:
    print("there was an exception")
    pwm.ChangeDutyCycle(0)
    GPIO.cleanup()

GPIO.cleanup()

