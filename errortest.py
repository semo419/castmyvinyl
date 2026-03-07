import RPi.GPIO as GPIO
import sys
import pychromecast
import time
import datetime

target="Office Speaker"

chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[target])

cast = chromecasts[0]
print(cast.device.friendly_name)

time.sleep(5)

