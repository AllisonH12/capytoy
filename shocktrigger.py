import RPi.GPIO as GPIO
import time
import subprocess
import logging

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

try:
    print("Monitoring for shocks. Press CTRL+C to exit.")
    while True:
        if GPIO.input(22):
            print("Shock detected! Triggering capy.py")
            logging.info("Shock Detected.")
            trigger_script("/home/pi/capytoy/run_capy.sh")
            time.sleep(10)  # Simple debounce
        time.sleep(0.1)  # Simple debounce
finally:
    GPIO.cleanup()

