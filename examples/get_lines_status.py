#!/usr/bin/env python3
"""Attach a log handler to print logs to stdout."""

from aaopto_aotf.aotf import MPDS
from aaopto_aotf.device_codes import InputMode, BlankingMode
import logging
import pprint

## Send log messages to stdout so we can see every outgoing/incoming tiger msg.
#class LogFilter(logging.Filter):
#    def filter(self, record):
#        return record.name.split(".")[0].lower() in ['aaopto_aotf']
#
#fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())
#logger.handlers[-1].setFormatter(logging.Formatter(fmt=fmt))
#logger.handlers[-1].addFilter(LogFilter())  # Remove parse lib log messages.

aotf = MPDS('/dev/ttyUSB0')
print(f"Product id: {aotf.get_product_id()}")
status = aotf.get_lines_status()
pprint.pprint(status)
