import sys
import time
import pychromecast 

# Define Chromecasts we're searching for
target_chromecasts=["Living Room Speaker","Kitchen display"]

# List chromecasts on the network, but don't connect
#services, browser = pychromecast.discovery.discover_chromecasts()
# Shut down discovery
#pychromecast.discovery.stop_discovery(browser)

# Discover and connect to chromecasts in target list
chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=target_chromecasts[1])
#chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Living Room Speaker"])

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
print(mc.status)

mc.pause()
time.sleep(5)
mc.play()
time.sleep(5)
mc.stop()

# Shut down discovery
pychromecast.discovery.stop_discovery(browser)

