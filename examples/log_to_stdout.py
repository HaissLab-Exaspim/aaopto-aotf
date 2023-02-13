#!/usr/bin/env python3
"""Attach a log handler to print logs to stdout."""

from aaopto_aotf.aotf import MPDS
from aaopto_aotf.device_codes import InputMode, BlankingMode
import pprint
import logging

DEV_NAME = "/dev/ttyUSB0"

# Send log messages to stdout so we can see every outgoing/incoming msg.
# Only display messages from this package.
class LogFilter(logging.Filter):
    def filter(self, record):
        return record.name.split(".")[0].lower() in ['aaopto_aotf']

fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(logging.Formatter(fmt=fmt))
logger.handlers[-1].addFilter(LogFilter())

aotf = MPDS(DEV_NAME)
print(f"Product id: {aotf.get_product_id()}")

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
