#!/bin/bash
# Navigate to the script directory
cd /home/pi/capytoy
# Activate the virtual environment
source /home/pi/capytoy/dev/bin/activate
# Run the Python script
python -u capy.py >/home/pi/capytoy/capy.log 2>/home/pi/capytoy/capyerror.log

