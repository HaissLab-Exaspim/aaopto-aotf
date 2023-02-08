#!/usr/bin/env python3
"""Attach a log handler to print logs to stdout."""

from aaopto_aotf.aotf import MPDS
from aaopto_aotf.device_codes import InputMode, BlankingMode
import logging
import pprint

# Send log messages to stdout so we can see every outgoing/incoming tiger msg.
class LogFilter(logging.Filter):
    def filter(self, record):
        return record.name.split(".")[0].lower() in ['aaopto_aotf']

fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(logging.Formatter(fmt=fmt))
logger.handlers[-1].addFilter(LogFilter())  # Remove parse lib log messages.

aotf = MPDS('/dev/ttyUSB0')
print(f"Product id: {aotf.get_product_id()}")
#for i in range(1,4):
#    print(f"Channel {i}:")
#    print(f"frequency: {aotf.get_frequency(i)}")
#    print(f"power (dBm): {aotf.get_power_dbm(i)}")
#    aotf.enable_channel(i)
#    print()

status = aotf.get_lines_status()
pprint.pprint(status)
print("Setting Blanking mode to INTERNAL.")
aotf.set_blanking_mode(BlankingMode.INTERNAL)
print(aotf.get_blanking_mode())
print("Setting Blanking mode to EXTERNAL.")
aotf.set_blanking_mode(BlankingMode.EXTERNAL)
print(aotf.get_blanking_mode())
status = aotf.get_lines_status()
pprint.pprint(status)

#status = aotf.get_lines_status()
#pprint.pprint(status)
#print("Setting modes to EXTERNAL")
#for i in range(1,4):
#    print(f"Channel {i}:")
#    aotf.set_channel_input_mode(i, InputMode.EXTERNAL)
#status = aotf.get_lines_status()
#pprint.pprint(status)
#print("Setting modes to INTERNAL")
#for i in range(1,4):
#    print(f"Channel {i}:")
#    aotf.set_channel_input_mode(i, InputMode.INTERNAL)
#status = aotf.get_lines_status()
#pprint.pprint(status)
