import sys
import time
import pychromecast 

# Define Chromecasts we're searching for
target_chromecasts=["Living Room Speaker","Kitchen display","Office Speaker"]
target = 2

# List chromecasts on the network, but don't connect
#services, browser = pychromecast.discovery.discover_chromecasts()
# Shut down discovery
#pychromecast.discovery.stop_discovery(browser)

# Discover and connect to chromecasts in target list
chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[target_chromecasts[target]])

cast = chromecasts[0]
# Start worker thread and wait for cast device to be ready
cast.wait()
print(cast.device.friendly_name)
print("Volume = "+str(cast.status.volume_level))
#print("")

mc = cast.media_controller
mc.play_media('http://192.168.86.41:8000/rapi.mp3','audio/mp3')
#mc.play_media('http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'video/mp4')
mc.block_until_active()
print(mc.status.player_state)

mc.pause()
time.sleep(5)
print(mc.status.player_state)

mc.play()
time.sleep(10)
print("Initialized! " + mc.status.player_state)

while mc.status.player_state=="PLAYING":
	time.sleep(5)
	print(mc.status.player_state)

#mc.stop()
print(mc.status.player_state)

# Shut down discovery
pychromecast.discovery.stop_discovery(browser)

