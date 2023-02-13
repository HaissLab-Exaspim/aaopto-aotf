#!/usr/bin/env python3
"""Attach a log handler to print logs to stdout."""

from aaopto_aotf.aotf import MPDS
import pprint

DEV_NAME = '/dev/ttyUSB0'

aotf = MPDS(DEV_NAME)
print(f"Product id: {aotf.get_product_id()}")
status = aotf.get_lines_status()
pprint.pprint(status)
