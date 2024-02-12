import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)  # Use GPIO numbering
GPIO.setwarnings(False)

# Pin Definition
servo_pin = 17  # Change this to your GPIO pin number

# GPIO Setup
GPIO.setup(servo_pin, GPIO.OUT)

# PWM Setup
pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz (20 ms PWM period)
pwm.start(0)

def set_servo_angle(angle):
    duty_cycle = angle / 18.0 + 2.5  # Angle to duty cycle conversion
    pwm.ChangeDutyCycle(duty_cycle)

try:
    while True:
        set_servo_angle(0)   # 0 degrees
        time.sleep(1)
        set_servo_angle(90)  # 90 degrees
        time.sleep(1)
        set_servo_angle(180) # 180 degrees
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

