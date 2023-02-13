# AA OptoElectronics MPDSnCxx AOTF Driver

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

python driver to control [MPDSnCxx AOTF devices](http://www.aaoptoelectronic.com/our-products/multi-channels-drivers-for-polychromatic-modulators/).


## Installation
To install this package from [PyPI](https://pypi.org/project/aaopto-aotf/), invoke: `pip install aaopto-aotf`

To install this package from the Github in editable mode, from this directory invoke: `pip install -e .`

To install this package in editable mode with dependencies for building the docs, invoke: `pip install -e .[dev]`

## Intro and Basic Usage
````python
from aaopto_aotf.aotf import MPDS

aotf = MPDS("COM3")
````

Before writing values, you must first set the global blanking mode, and each channel's frequency, mode, and whether it is driven by external input or internal (software controlled) input.
````python
from aaopto_aotf.aotf import MPDS, MAX_POWER_DBM
from aaopto_aotf.device_codes import DriverMode, BlankingMode, VoltageRange

aotf.set_blanking(BlankingMode.INTERNAL)  # disable blanking control from external input pin.
aotf.set_external_input_voltage_range(VoltageRange.ZERO_TO_FIVE_VOLTS)

# Note: device channels are 1-indexed to be consistent with the datasheet.
for channel in range(1, aotf.num_channels + 1):
    aotf.set_frequency(channel, 110.5)
    aotf.set_driver_mode(DriverMode.EXTERNAL)
````

If the driver mode is set to `DriverMode.EXTERNAL`, the device will take its output setpoint from the external input pin.

If set to `DriverMode.INTERNAL`, you can control the output with software settings:
````python
for channel in range(1, aotf.num_channels + 1):
    aotf.set_driver_mode(DriverMode.INTERNAL)
    aotf.set_power_dbm(channel, MAX_POWER_DBM)
    aotf.enable_channel(channel)
````

At this point, you might want to save the values set above to the current profile.
````python
aotf.save_profile()  # Now, calling an aotf.reset() will start with the saved settings.
````

## What's missing?
Here are the minor dangling features that are not implemented.
* changing laser channel profiles at runtime. (These must be changed with the external input pins.)
* automatic sweeping mode
    * automatic self-sweeping is a somewhat out-of-the-ordinary feature for most users.

## Examples:
Have a look at the examples folder to see other examples and make use of a [useful calibration script](https://github.com/AllenNeuralDynamics/aaopto-aotf/blob/main/examples/calibration_sweep.py).
