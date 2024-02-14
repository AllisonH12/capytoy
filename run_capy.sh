#!/bin/bash
# Navigate to the script directory
cd /home/pi/capytoy
# Activate the virtual environment
source /home/pi/capytoy/dev/bin/activate
export OPENAI_API_KEY='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'
# Run the Python script
python -u capy.py >/home/pi/capytoy/capy.log 2>/home/pi/capytoy/capyerror.log

