import sys
import time
import pychromecast

from config import AUDIO_STREAM, AUDIO_TYPE, TARGETS

# Select which Chromecast to test (0=Downstairs, 1=Upstairs, 2=All Devices)
target = 2

chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[TARGETS[target]])
cast = chromecasts[0]

cast.wait()
print(cast.device.friendly_name)
print("Volume = " + str(cast.status.volume_level))

mc = cast.media_controller
mc.play_media(AUDIO_STREAM, AUDIO_TYPE)
mc.block_until_active()
print(mc.status.player_state)

mc.pause()
time.sleep(5)
print(mc.status.player_state)

mc.play()
time.sleep(10)
print("Initialized! " + mc.status.player_state)

while mc.status.player_state == "PLAYING":
    time.sleep(5)
    print(mc.status.player_state)

print(mc.status.player_state)

browser.stop_discovery()
