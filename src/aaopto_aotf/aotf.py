"""Python driver for an AA OptoElectronics AOTF device."""

import logging
import time

from parse import parse
from serial import Serial, SerialException
from aaopto_aotf.device_codes import *
from functools import wraps
from typing import Union


def channel_range_check(func):
    """Check that the channel is within range."""
    @wraps(func)  # Required for sphinx doc generation.
    def inner(self, channel, *args, **kwds):
        if channel < 1 or channel > self.num_channels:
            raise IndexError("Requested channel value is out of range.")
        return func(self, channel, *args, **kwds)
    return inner


MAX_POWER_DBM = 22.0

BAUDRATE = 57600
TIMEOUT = 0.5

RESET_BOOT_TIME_S = 0.005


class MPDS:

    def __init__(self, com_port: str):
        self.ser = None
        self.log = logging.getLogger(f"{__name__}.{com_port}")
        try:
            self.ser = Serial(com_port, BAUDRATE, timeout=TIMEOUT)
        except SerialException as e:
            self.log.error("Could not connect to AA OptoElectronics AOTF. "
                           "Is the device plugged in? Is another program "
                           "using it?")
            raise
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        # Determine if MPDS has 1, 4, or 8 channels.
        self.num_channels = len(self.get_lines_status()) - 1

    def reset(self):
        """Reset the device to external mode with stored parameter settings."""
        self._send(Cmds.RESET.value, reply=False)
        # Wait a certain period before issuing subsequent commands;
        # otherwise, the device will respond with EOL instead of the
        # appropriate response.
        time.sleep(RESET_BOOT_TIME_S)

    def save_profile(self):
        """Save current frequency and power settings for all channels to the
        current profile.

        Note: the current profile is set externally with with a binary code set
        on pins 18 - 20 (LSb - MSb) and enabled with pin 4 asserted. Note that
        pin 4 is pulled up by default.

        """
        self._send(Cmds.DATA_STORAGE.value, reply_startswith_eol=False,
                   read_until="?")

    @channel_range_check
    def set_frequency(self, channel: int, frequency: float,
                      validate: bool = True):
        """Set the active channel frequency in [MHz].

        :param channel: channel to set the frequency for.
        :param frequency: frequency input in [MHz].
        :param validate: if True, read the value back from the hardware to
            confirm that it was set correctly. Useful since models have
            factory-set minimum and maximum frequencies.
        """
        # Must specify channel first.
        msg = Cmds.FREQUENCY_ADJUST.value.format(channel, frequency)
        self._send(msg)
        if validate:
            actual_freq = self.get_frequency(channel)
            desired_freq = round(frequency, 3)
            # Compare rounded numbers.
            if abs(actual_freq - desired_freq) > 0.0005:
                raise ValueError(f"Error: desired frequency is {frequency} "
                                 f"[MHz] but actual frequency is "
                                 f"{actual_freq} [MHz].")

    @channel_range_check
    def set_power_dbm(self, channel: int, dbm: float, validate: bool = True):
        """Set the active channel power in [dBm].

        :param channel: channel to set the frequency for.
        :param dbm: frequency input in [MHz].
        :param validate: if True, read the value back from the hardware to
            confirm that it was set correctly. Useful since models have
            factory-set minimum and maximum frequencies.
        """
        if dbm > MAX_POWER_DBM or dbm < 0:
            raise IndexError("Specified fine power [dBm] is out of range.")
        msg = Cmds.FINE_POWER_ADJUST.value.format(channel, dbm)
        self._send(msg)
        if validate:
            actual_power = self.get_power_dbm(channel)
            desired_power = round(dbm, 1)
            # Compare rounded numbers.
            if abs(actual_power - desired_power) > 0.05:
                raise ValueError(f"Error: desired power is {dbm}[dBm] "
                                 f"but actual power is "
                                 f"{actual_power} [dBm].")

    def _set_channel_output_state(self, channel: int, state: OutputState):
        """Turn on or off the specified channel output."""
        msg = Cmds.PLL_SWITCH.value.format(channel, state.value)
        self._send(msg)

    @channel_range_check
    def enable_channel(self, channel: int):
        self._set_channel_output_state(channel, OutputState.ON)

    @channel_range_check
    def disable_channel(self, channel: int):
        self._set_channel_output_state(channel, OutputState.OFF)

    @channel_range_check
    def set_channel_input_mode(self, channel: int, mode: InputMode):
        msg = Cmds.DRIVER_MODE.value.format(channel, mode.value)
        self._send(msg)

    def set_blanking_mode(self, mode: BlankingMode):
        """Set the blanking mode to internal or external.

        Note: if set to external mode, all laser output values are scaled
        (0% to 100%) by the voltage on the blanking input pin (0-5V or 0-10V).
        If set to internal mode, the blanking input pin is ignored and laser
        output values are scaled by 1.

        Note: if set to external mode and the blanking pin is left
        disconnected, all outputs will be disabled.

        :param mode: :obj:`~BlankingMode.INTERNAL` or
            :obj:`~BlankingMode.EXTERNAL`
        """
        msg = Cmds.DRIVER_MODE.value.format(0, mode.value)
        self._send(msg)

    def set_external_input_voltage_range(self, vrange: VoltageRange):
        msg = Cmds.VOLTAGE_RANGE.value.format(vrange.value)
        # Note: this command does not issue any characters in response.
        self._send(msg, reply=False)

    def set_global_input_mode(self, mode: Union[InputMode, GlobalInputMode]):
        """Set both driver mode for all channels and blanking mode to internal
        or external."""
        # InputMode values are reversed from GlobalInputMode values.
        # Convert to GlobalInputMode for consistency.
        mode = GlobalInputMode[mode.name]
        msg = Cmds.GLOBAL_DRIVER_MODE.value.format(mode.value)
        # Note: this command does not issue any characters in response.
        self._send(msg, reply=False)

    def get_lines_status(self):
        """Return the line status as a dictionary keyed by channel index."""
        settings = {}
        reply = self._send(Queries.LINES_STATUS.value,
                           multiline_reply=True, read_until="?")
        reply_lines = reply.split(EOL)
        # TODO: return these as enums
        # Parse channel settings.
        template = "l{channel} F={freq:.3f} P={power:.3f} {state} {mode}"
        # TODO: may or may not start with 'Temp = 0\n\rAlim = 0\n\rUSB = 0\'
        for line in reply_lines[:-1]:
            ch_settings = parse(template, line).named
            settings[int(ch_settings.pop('channel'))] = ch_settings
        # Parse blanking settings.
        template = "{blanking} {state} {mode}"
        blanking_settings = parse(template, reply_lines[-1]).named
        settings[blanking_settings.pop('blanking').lower()] = blanking_settings
        return settings

    @channel_range_check
    def get_frequency(self, channel: int):
        """Return the frequency in [MHz] of the current channel."""
        reply = self._send(Queries.CHANNEL_SPECIFIC_STATUS.value.format(channel))
        return parse(Replies.CHANNEL_SPECIFIC_STATUS, reply).fixed[1]

    @channel_range_check
    def get_power_dbm(self, channel: int):
        """return the fine power value of the current channel."""
        reply = self._send(Queries.CHANNEL_SPECIFIC_STATUS.value.format(channel))
        return parse(Replies.CHANNEL_SPECIFIC_STATUS, reply).fixed[2]

    @channel_range_check
    def get_channel_input_mode(self, channel):
        return InputMode[self.get_lines_status()['mode']]

    @channel_range_check
    def get_channel_output_state(self, channel: int):
        """Get state of the pll for the current channel."""
        reply = self._send(Queries.CHANNEL_SPECIFIC_STATUS.value.format(channel))
        return bool(parse(Replies.CHANNEL_SPECIFIC_STATUS, reply).fixed[3])

    def get_blanking_mode(self):
        """return the blanking mode (internal or external)."""
        # This needs to be read from line status.
        return BlankingMode[self.get_lines_status()['blanking']['mode']]

    def get_product_id(self):
        """Get the product id."""
        reply = self._send(Queries.PRODUCT_ID, read_until="?",
                           reply_startswith_eol=False)
        return parse(Replies.PRODUCT_ID, reply.rstrip()).fixed[0]

    def _send(self, msg: str, reply: bool = True,
              multiline_reply: bool = False,
              read_until: str = EOL,
              reply_startswith_eol: bool = True):
        """Send message to the AOTF. Return the reply if it exists.,

        :param msg: the message (in string format) to send.
        :param reply: True if the msg expects a reply.
        :param read_until: the string match until we stop reading a reply.
        :param reply_startswith_eol: True if the first string is an EOL.

        """
        self.log.debug(fr"Sending: {repr(msg)}")
        self.ser.write(f"{msg}".encode('ascii'))
        if not reply:
            return
        # Msgs that are prefixed with channel number return a one-line reply.
        if msg.startswith(CmdRoots.CHANNEL_PREFIX):
            line = self.ser.read_until(EOL.encode("ascii")).decode("utf8")
            self.log.debug(fr"Received: {repr(line)}")
            return line.rsplit(EOL, 1)[0]
        # Most other cmds that issue a reply start with '\n\r'.
        if reply_startswith_eol:  # Discard the first '\n\r'.
            self.ser.read_until(EOL.encode("ascii"))
        line = self.ser.read_until(read_until.encode("ascii")).decode("utf8")
        self.log.debug(fr"Received: {repr(line)}")
        # Return everything minus the last '\n\r?'.
        return line.rsplit(EOL, 1)[0]
