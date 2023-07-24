#!/usr/bin/env python3
"""Script to sample & plot a grid over power & frequency to find max output."""

import argparse
import time
from tqdm import tqdm
import pprint
import numpy as np
import matplotlib.pyplot as plt
from sys import platform as PLATFORM
if PLATFORM == "win32":
    from sys import modules
    from ctypes import byref, c_double, c_bool, c_int, c_int16, create_string_buffer, c_uint32
    import importlib
    try:
        # Import from the git submodule location.
        spec = importlib.util.spec_from_file_location("module.name", "./thorlabs_lib/Light_Analysis_Examples/Python/Thorlabs PMxxx Power Meters/TLPM.py")
        tlpm_mod = importlib.util.module_from_spec(spec)
        modules["module.name"] = tlpm_mod
        spec.loader.exec_module(tlpm_mod)

        # Mirror the same function signature as the ThorlabsPM100 package.
        class MyTLPM(tlpm_mod.TLPM):
            @property
            def read(self):
                p = c_double()
                meter.measPower(byref(p))
                return p.value

    except ImportError:
        raise ImportError("Cannot import TLPM. You may need to install the Thorlabs submodule first.")
else:
    from ThorlabsPM100 import ThorlabsPM100, USBTMC
from aaopto_aotf.aotf import MPDS, MAX_POWER_DBM
from aaopto_aotf.aotf import BlankingMode, InputMode


# Immutable Constants:
MEASUREMENT_SETTLING_TIME_S = 0.5


if __name__ == "__main__":
    description = """With a Thorlabs PM100 power meter installed at the output
        of the aotf, run a grid sweep of input commands over the specified
        frequency and power range, save the output to a CSV, plot the output,
        and print the settings that produce the maximum power output."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("channel", type=int, default=1,
                        help="the desired aotf channel.")
    parser.add_argument("wavelength", type=int, default=488,
                        help="the desired wavelength to set the power meter (in nanometers).")
    parser.add_argument("min_freq", type=float, default=0,
                        help="minimum frequency [MHz] to start the sweep.")
    parser.add_argument("max_freq", type=float, default=150,
                        help="maximum frequency [MHz] to stop the sweep.")
    parser.add_argument("freq_step", type=float, default=0.1,
                        help="frequency step size increment.")
    parser.add_argument("min_power", type=float, default=0,
                        help="minimum power [dBm] to start the sweep.")
    parser.add_argument("max_power", type=float, default=MAX_POWER_DBM,
                        help="minimum power [dBm] to stop the sweep.")
    parser.add_argument("power_step", type=float, default=0.1,
                        help="power step size increment.")
    parser.add_argument("--validate", default=False, action="store_true",
                        help="if True, check the hardware device to ensure "\
                             "that the desired settings have been set. " \
                             "Note that not all desired settings may be " \
                             "achievable.")
    parser.add_argument("--aotf_port", type=str, default="/dev/ttyUSB0",
                        help="name of the aotf port as it appears on the pc.")
    parser.add_argument("--pm100_port", type=str, default="/dev/usbtmc0",
                        help="name of the PM100 device as it appears on the pc.")
    parser.add_argument("--filename", type=str, default="data.csv",
                        help="the name of the CSV output file.")
    parser.add_argument("--overwrite", default=False, action="store_true",
                        help="allow overwriting data in preexisting output file.")
    parser.add_argument("--console_output", default=True,
                        help="whether or not to print to the console.")
    args = parser.parse_args()
    print("Running Calibration Sweep with the following settings:")
    for arg in vars(args):
        print(f"{arg}: {getattr(args, arg)}")
    print()

    # Setup Thorlabs power meter
    meter = None
    if PLATFORM == 'win32':
        # Duplicate the function signature of the USBTMC module.
        # FIXME: put the connection attempt in a try-except with software link:
        # https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=OPM
        resource_name = create_string_buffer(1024)
        meter = MyTLPM()
        deviceCount = c_uint32()
        meter.findRsrc(byref(deviceCount))  # We need to call this first.
        meter.getRsrcName(c_int(0), resource_name)  # get name of first device.
        meter.open(resource_name, c_bool(True), c_bool(True))
        meter.setPowerUnit(c_int16(0))  # 0 --> watts
        set_wavelength = c_double(0)
        meter.getWavelength(c_int16(tlpm_mod.TLPM_ATTR_SET_VAL), byref(set_wavelength))
        print(f"PM100 wavelength currently set to {set_wavelength.value}[nm].")
        if abs(set_wavelength.value - args.wavelength) < 0.001:
            print("PM100 already at correct wavelength. Skipping.")
        else:
            time.sleep(1.0) # Sleeping is necessary here.
            # Otherwise reading current setting will change the set value.
            print(f"Setting PM100 wavelength to {args.wavelength}[nm].")
            meter.setWavelength(c_double(args.wavelength))
    else:
        inst = USBTMC(device=args.pm100_port)
        meter = ThorlabsPM100(inst=inst)
        meter.sense.correction.wavelength = args.wavelength

    # for i in range(10):
    #     print(f"value from power meter is: {meter.read}")
    #     time.sleep(0.5)

    # Setup aotf.
    aotf = MPDS(args.aotf_port)
    aotf.set_blanking_mode(BlankingMode.INTERNAL)
    aotf.set_channel_input_mode(args.channel, InputMode.INTERNAL)
    aotf.enable_channel(args.channel)
    #print(aotf.get_lines_status())

    # Containers.
    power_xy = []
    freq_xy = []
    watts_xy = []
    max_watts = 0
    argmax_power = 0
    argmax_freq = 0
    # Take measurements with progress bar.
    try:
        with open(args.filename, 'w') as the_file:
            the_file.write("power [dbm], frequency [MHz], watts [w]\n")
            try:
                for power in tqdm(np.arange(args.min_power, args.max_power, args.power_step),
                        desc="Power Sweep:", leave=False):
                    aotf.set_power_dbm(args.channel, power, validate=args.validate)
                    for freq in tqdm(np.arange(args.min_freq, args.max_freq, args.freq_step),
                            desc="Frequency Sweep:", leave=False):
                        aotf.set_frequency(args.channel, freq, validate=args.validate)
                        time.sleep(MEASUREMENT_SETTLING_TIME_S)
                        watts = meter.read
                        power_xy.append(power)
                        freq_xy.append(freq)
                        watts_xy.append(watts)
                        the_file.write(f'{power}, {freq}, {watts}\n')
                        if watts > max_watts:  # Save best-so-far measurement.
                            max_watts = watts
                            argmax_power = power
                            argmax_freq = freq
            except Exception as e:  # Exception catch-all so that we save the data.
                print(e)
                import traceback
                traceback.print_exc()
    finally:
        print("Turning off aotf.")
        aotf.disable_channel(args.channel)
        if PLATFORM == 'win32':
            print("closing connection to power meter.")
            meter.close()
    print(f"The following settings: "
          f"({argmax_power:.2f}[dBm], {argmax_freq:.3f}[MHz]) "
          f"result in the highest measured output power of {max_watts:.6f}[w].")
    # Plot the results.
    fig = plt.figure()
    ax = plt.axes(projection ='3d')
    ax.scatter(power_xy, freq_xy, watts_xy)
    ax.set_xlabel('power [dBm]')
    ax.set_ylabel('frequency [MHz]')
    ax.set_zlabel('watts');
    plt.show()

