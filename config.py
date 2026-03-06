# =============================================================================
# CastMyVinyl Configuration
# Edit this file to adapt to your network/hardware without touching core logic.
# =============================================================================

# Audio stream URL (Raspberry Pi local stream server)
AUDIO_STREAM = "http://192.168.86.32:8000/mystream.mp3"
AUDIO_TYPE = "audio/mp3"

# Chromecast target friendly names — index must match BUTTONS and LIGHTS below
TARGETS = ["Downstairs Speakers", "Upstairs Speakers", "All Devices"]

# GPIO pin mapping (BCM numbering) — DO NOT CHANGE, pins are hardwired
BUTTONS      = [22, 27, 17]   # tactile push buttons (active low)
LIGHTS       = [25, 24, 23]   # indicator LEDs per button
STATUS_LIGHT = 16             # global status LED
CLK          = 19             # rotary encoder clock
DT           = 26             # rotary encoder data
VOLTMETER    = 21             # PWM-driven analog voltmeter needle

# Volume control
VOLT_METER_SCALE   = 1     # output duty cycle multiplier vs. counter value
INCREMENT          = 2     # encoder steps per volume unit
INITIAL_VOLUME     = 50   # volume (0–100) applied when casting starts
VOLUME_SET_INTERVAL = 0.3  # seconds between volume updates sent to Chromecast

# Connectivity
CONNECTION_TIMEOUT    = 10  # seconds to wait for PLAYING state before giving up
DISCOVERY_RETRIES     = 5   # number of Chromecast discovery attempts before failing
DISCOVERY_RETRY_DELAY = 3   # seconds between discovery retries
