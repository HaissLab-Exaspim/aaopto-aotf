#!/usr/bin/env python3
"""Script to sample & plot a grid over power & frequency to find max output."""

import argparse
import time
from tqdm import tqdm
import pprint
import numpy as np
import matplotlib.pyplot as plt
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
    parser.add_argument("min_freq", type=float, default=0,
                        help="minimum frequency [dBm] to start the sweep.")
    parser.add_argument("max_freq", type=float, default=150,
                        help="maximum frequency [dBm] to stop the sweep.")
    parser.add_argument("freq_step", type=float, default=0.1,
                        help="frequency step size increment.")
    parser.add_argument("min_power", type=float, default=0,
                        help="minimum power [MHz] to start the sweep.")
    parser.add_argument("max_power", type=float, default=MAX_POWER_DBM,
                        help="minimum power [MHz] to stop the sweep.")
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

    # Setup
    inst = USBTMC(device=args.pm100_port)
    meter = ThorlabsPM100(inst=inst)
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

