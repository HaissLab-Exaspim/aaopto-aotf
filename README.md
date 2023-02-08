# AA OptoElectronics AOTF

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

python driver to control MPDS AOTF devices.


## Installation
<!--To install this package from [PyPI](https://pypi.org/project/aaopto_aotf), invoke: `pip install aaopto_aotf`.-->

To install this package from the Github in editable mode, from this directory invoke: `pip install -e .`

To install this package in editable mode with dependencies for building the docs, invoke: `pip install -e .[dev]`

## Intro and Basic Usage
````python
from aaopto_aotf.aotf import MPDS

aotf = MPDS("COM3")
````

The basic syntax looks like so:
````python
from aaopto_aotf.device_codes import DriverMode, BlankingMode

NUM_CHANNELS = 8

aotf.set_blanking(BlankingMode.INTERNAL)  # disable blanking control from external input pin.

# Note: device channels are 1-indexed to be consistent with the datasheet.
for channel in range(1, NUM_CHANNELS+1):
    aotf.set_frequency(channel, 110.5)
    aotf.set_power_dbm(channel, 15.0)
    aotf.set_driver_mode(DriverMode.INTERNAL)
    aotf.enable_channel(channel)
````

