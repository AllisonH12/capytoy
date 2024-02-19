import subprocess

# Function to get Raspberry Pi's power status
def get_throttled():
    try:
        # Run the vcgencmd command to get the status
        result = subprocess.run(['vcgencmd', 'get_throttled'], stdout=subprocess.PIPE)
        # Decode the result from bytes to string
        result_string = result.stdout.decode('utf-8')
        # Extract the throttled status from the command output
        throttled_status = result_string.split('=')[1].strip()
        return int(throttled_status, 0)
    except Exception as e:
        print(f"Error getting throttled status: {e}")
        return None

# Function to check for under-voltage
def check_for_undervoltage():
    throttled = get_throttled()
    if throttled is not None:
        # Check for under-voltage warnings
        under_voltage_detected = throttled & 0x1
        if under_voltage_detected:
            print("Under-voltage detected! Check your power supply and cables.")
        else:
            print("Power supply is OK.")
    else:
        print("Could not get throttled status.")

# Check for under-voltage
check_for_undervoltage()

