import RPi.GPIO as GPIO
import time
import subprocess
import logging
import wave
from time import sleep, time
import simpleaudio as sa 
import random

# Logging configuration
logging.basicConfig(filename='/home/pi/capytoy/shock_detectionshock.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')


def check_process_running(process_name):
    """Check if there is any running process that contains the given name process_name."""
    try:
        # This will throw an exception if the process isn't running
        output = subprocess.check_output(["pgrep", "-f", process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def trigger_script(script_path):
    """Run the specified shell script if 'capy.py' is not already running."""
    if not check_process_running("capy.py"):
        logging.info("starting a new capy.")
        subprocess.Popen(["/bin/bash", script_path])
    else:
        print("There is a capy running already")
        logging.info("There is a capy running already")

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Define the path to your WAV file
wav_path = "/home/pi/capytoy/snoring.wav"
# Load the WAV file
wave_obj = sa.WaveObject.from_wave_file(wav_path)
# Record the start time
# Set the interval for playing the sound (e.g., every 30 seconds)
play_interval = 30
next_play_time = time() + play_interval + random.randint(0, 5)
print(next_play_time)
play_obj = wave_obj.play()
play_obj.wait_done()  # Wait until sound has finished playing

try:
    print("Monitoring for shocks. Press CTRL+C to exit.")
    while True:
        current_time = time()
        if GPIO.input(22):
            print("Shock detected! Triggering capy.py")
            logging.info("Shock Detected.")
            trigger_script("/home/pi/capytoy/run_capy.sh")
            time.sleep(2)  # Simple debounce
        elif current_time >= next_play_time:
            print("Playing sound.")
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until sound has finished playing
            # Calculate the next play time
            next_play_time = current_time + play_interval + random.randint(0, 1600)
        sleep(0.1)  # Simple debounce
finally:
    GPIO.cleanup()

