import RPi.GPIO as GPIO
import time

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set GPIO 22 as input, and enable internal pull-down resistor
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        # Check if shock detected
        if GPIO.input(22):
            print("Shock detected!")
        time.sleep(0.1) # Simple debounce
finally:
    GPIO.cleanup() # Clean up GPIO on exit

