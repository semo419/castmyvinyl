import RPi.GPIO as GPIO
import pychromecast
import time
import logging
import os
import re
import socket
from urllib.parse import urlparse, urlunparse

from config import (
    AUDIO_STREAM, AUDIO_TYPE, TARGETS,
    BUTTONS, LIGHTS, STATUS_LIGHT, CLK, DT, VOLTMETER,
    VOLT_METER_SCALE, INCREMENT, INITIAL_VOLUME,
    VOLUME_SET_INTERVAL, CONNECTION_TIMEOUT,
    DISCOVERY_RETRIES, DISCOVERY_RETRY_DELAY,
    ENCODER_DEBOUNCE,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)

log.info("Beginning Execution of Cast My Vinyl")


##########################
### IP Self-Check
##########################

def get_local_ip():
    """
    Detect the Pi's current local IP by opening a UDP socket toward an
    external address (no packets are actually sent).
    Returns the IP string, or None on failure.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        log.warning("Could not detect local IP: %s", e)
        return None


def sync_stream_ip():
    """
    Check whether the IP in AUDIO_STREAM matches the Pi's current IP.
    If not, rewrite the AUDIO_STREAM line in config.py and return the
    corrected URL so the running process uses the right address.
    """
    current_ip = get_local_ip()
    if current_ip is None:
        log.warning("Skipping IP sync — could not determine local IP")
        return AUDIO_STREAM

    parsed = urlparse(AUDIO_STREAM)
    config_ip = parsed.hostname

    if current_ip == config_ip:
        log.info("Stream IP is current (%s)", current_ip)
        return AUDIO_STREAM

    # Build the corrected URL (preserve port and path)
    new_netloc = current_ip if parsed.port is None else f"{current_ip}:{parsed.port}"
    new_url = urlunparse(parsed._replace(netloc=new_netloc))

    # Rewrite the AUDIO_STREAM line in config.py
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
    try:
        with open(config_path, "r") as f:
            content = f.read()
        new_content = re.sub(
            r'^(AUDIO_STREAM\s*=\s*["\']).*?(["\'])',
            lambda m: f"{m.group(1)}{new_url}{m.group(2)}",
            content,
            flags=re.MULTILINE,
        )
        with open(config_path, "w") as f:
            f.write(new_content)
        log.info("Stream IP updated in config.py: %s -> %s", config_ip, current_ip)
    except Exception as e:
        log.error("Failed to update config.py with new IP: %s", e)

    return new_url


AUDIO_STREAM = sync_stream_ip()


##########################
### GPIO Setup
##########################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Rotary encoder inputs
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Status and button indicator outputs
GPIO.setup(STATUS_LIGHT, GPIO.OUT)
GPIO.output(STATUS_LIGHT, False)

for pin in LIGHTS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)

# Button inputs
for pin in BUTTONS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Voltmeter needle (PWM output)
GPIO.setup(VOLTMETER, GPIO.OUT)
pwm = GPIO.PWM(VOLTMETER, 100)
pwm.start(100)
time.sleep(2)
pwm.ChangeDutyCycle(0)
time.sleep(2)


##########################
### Helper Functions
##########################

def signal_error(button):
    """Flash the button's indicator light to signal a connection error."""
    for _ in range(5):
        GPIO.output(LIGHTS[button], True)
        time.sleep(0.15)
        GPIO.output(LIGHTS[button], False)
        time.sleep(0.15)


def discover_chromecast(button):
    """
    Attempt to discover the target Chromecast, retrying on failure.
    Returns (cast, browser) on success, or (None, None) after all retries fail.
    """
    for attempt in range(1, DISCOVERY_RETRIES + 1):
        log.info("Discovery attempt %d/%d for '%s'", attempt, DISCOVERY_RETRIES, TARGETS[button])
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[TARGETS[button]])
        if chromecasts:
            return chromecasts[0], browser
        browser.stop_discovery()
        if attempt < DISCOVERY_RETRIES:
            log.warning("Device not found, retrying in %ds...", DISCOVERY_RETRY_DELAY)
            time.sleep(DISCOVERY_RETRY_DELAY)
    log.error("Could not find '%s' after %d attempts", TARGETS[button], DISCOVERY_RETRIES)
    return None, None


##########################
### Cast and Monitor
##########################

def cast_and_monitor(start_button):
    """
    Cast audio to the target Chromecast and monitor playback.
    Handles button-switching iteratively to avoid unbounded recursion.
    """
    button = start_button

    while True:
        GPIO.output(LIGHTS[button], True)
        log.info("Attempting cast to '%s'", TARGETS[button])

        cast, browser = discover_chromecast(button)
        if cast is None:
            signal_error(button)
            GPIO.output(LIGHTS[button], False)
            pwm.ChangeDutyCycle(0)
            return

        mc = None
        new_button = button
        try:
            cast.wait()
            log.info("Connected to '%s'", cast.device.friendly_name)

            mc = cast.media_controller
            cast.set_volume(INITIAL_VOLUME / 100)
            mc.play_media(AUDIO_STREAM, AUDIO_TYPE)
            mc.block_until_active()
            log.info("Initial player state: %s", mc.status.player_state)

            # Wait for PLAYING state
            deadline = time.time() + CONNECTION_TIMEOUT
            while mc.status.player_state != "PLAYING" and time.time() < deadline:
                time.sleep(1)

            if mc.status.player_state not in ("PLAYING", "BUFFERING"):
                log.error("Stream never started. Final state: %s", mc.status.player_state)
                signal_error(button)
                return

            log.info("Streaming: %s", mc.status.player_state)

            # Volume control state
            counter = INITIAL_VOLUME
            prior_volume = INITIAL_VOLUME
            clk_last_state = GPIO.input(CLK)
            pwm.ChangeDutyCycle(counter * VOLT_METER_SCALE)
            last_volume_set = time.time()
            last_encoder_time = 0.0

            # Button priority order: pressed button first, then others in order
            other_buttons = [i for i in range(len(BUTTONS)) if i != button]
            priority = [button] + other_buttons

            # Main playback loop
            while mc.status.player_state in ("PLAYING", "BUFFERING"):
                # Rotary encoder volume tracking
                clk_state = GPIO.input(CLK)
                dt_state  = GPIO.input(DT)
                if clk_state != clk_last_state and (time.time() - last_encoder_time) > ENCODER_DEBOUNCE:
                    clockwise = (clk_state == 1 and dt_state == 0) or (clk_state == 0 and dt_state == 1)
                    if clockwise and counter < 100:
                        counter += INCREMENT
                    elif not clockwise and counter > 0:
                        counter -= INCREMENT
                    pwm.ChangeDutyCycle(counter * VOLT_METER_SCALE)
                    last_encoder_time = time.time()
                clk_last_state = clk_state

                # Time-based volume updates to Chromecast
                now = time.time()
                if now - last_volume_set >= VOLUME_SET_INTERVAL and prior_volume != counter:
                    cast.set_volume(counter / 100)
                    prior_volume = counter
                    last_volume_set = now

                # Button press detection
                pressed = [i for i in range(len(BUTTONS)) if GPIO.input(BUTTONS[i]) == False]
                if pressed:
                    new_button = next((b for b in priority if b in pressed), pressed[0])
                    break

                time.sleep(0.002)

        except Exception as e:
            log.error("Error during cast session: %s", e, exc_info=True)
            signal_error(button)

        finally:
            log.info("Closing cast session for '%s'", TARGETS[button])
            GPIO.output(LIGHTS[button], False)
            pwm.ChangeDutyCycle(0)
            if mc is not None:
                try:
                    mc.stop()
                except Exception as e:
                    log.warning("Error stopping media controller: %s", e)
            time.sleep(1)
            cast.disconnect()
            browser.stop_discovery()
            time.sleep(1)

        # If the same button was pressed (or no switch), exit
        if new_button == button:
            return

        # Switch to the new target iteratively (no recursion)
        log.info("Switching from button %d to button %d", button, new_button)
        button = new_button


##########################
### Main Loop
##########################

try:
    GPIO.output(STATUS_LIGHT, True)
    while True:
        for i, btn in enumerate(BUTTONS):
            if GPIO.input(btn) == False:
                GPIO.output(STATUS_LIGHT, False)
                try:
                    cast_and_monitor(i)
                except Exception as e:
                    log.error("cast_and_monitor(%d) failed: %s", i, e, exc_info=True)
                    GPIO.output(LIGHTS[i], False)
                    pwm.ChangeDutyCycle(0)
                GPIO.output(STATUS_LIGHT, True)
                break
        time.sleep(0.05)

except Exception as e:
    log.error("Fatal error in main loop: %s", e, exc_info=True)
    pwm.ChangeDutyCycle(0)
    GPIO.cleanup()

GPIO.cleanup()
