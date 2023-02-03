"""Python driver for an AA OptoElectronics AOTF device."""

import logging
from parse import parse
from serial import Serial, SerialException
from aaopto_aotf.device_codes import *

def channel_specified(func):
    """Check that the channel has already been specified."""
    @wraps(func)  # Required for sphinx doc generation.
    def inner(self, *args, **kwds):
        if self._active_channel is None:
            raise NameError("Active channel must first be specified.")
        return func(self, *args, **kwds)
    return inner


MAX_CHANNELS = 8
MAX_POWER_DBM = 22.0
MAX_POWER_INT = 1023

BAUDRATE = 19200
EOL = '\r'


class AOTF:


    def __init__(self, com_port: str):
        self.ser = None
        self.log = logging.getLogger(__name__)
        try:
            self.ser = Serial(com_port, AOTF.BAUDRATE)
        except SerialException as e:
            self.log.error("Could not connect to AA OptoElectronics AOTF. "
                           "Is the device plugged in? Is another program "
                           "using it?")
            raise
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        self._active_channel = None

    def reset(self):
        """Reset the device to external mode with stored parameter settings."""
        self._send(Cmds.RESET.value)

    def save_settings(self):
        """Save all specified channel settings since the prior reset."""
        self._send(Cmds.DATA_STORAGE.value)

    def select_channel(self, channel: int):
        """Select the active channel."""
        if channel > MAX_CHANNELS or channel < 1:
            raise IndexError("Specified channel is out of range.")
        msg = Cmds.CHANNEL_SELECT.value.format(channel)
        self._send(msg)
        self._active_channel = channel

    @channel_specified
    def set_frequency(self, frequency: int):
        """Set the active channel frequency in [MHz]."""
        msg = Cmds.FREQUENCY_ADJUST.value.format(frequency)
        self._send(msg)

    @channel_specified
    def set_power_percent(self, power: float):
        """Set the active channel power in percent."""
        power_int = round(power*MAX_POWER_INT)
        if power_int > MAX_POWER_INT or power_int < 0:
            raise IndexError("Specified coarse power value is out of range.")
        msg = Cmds.POWER_ADJUST.value.format(power_int)
        self._send(msg)

    @channel_specified
    def set_power_dbm(self, dbm: float):
        """Set the active channel power in [dBm]."""
        if channel > MAX_POWER_DBM or channel < 0:
            raise IndexError("Specified fine power [dBm] is out of range.")
        msg = Cmds.FINE_POWER_ADJUST.value.format(power)
        self._send(msg)

    def set_driver_mode(self, mode: DriverMode):
        msg = Cmds.DriverMode.value.format(mode.value)
        self._send(msg)

    def set_external_input_voltage_range(self, vrange: VoltageRange):
        msg = Cmds.VoltageRange.value.format(vrange.value)
        self._send(msg)

    @channel_specified
    def set_pll(self, state: PLLState):
        msg = Cmds.PLL_SWITCH.value.format(state.value)
        self._send(msg)

    def get_lines_status(self):
        """Return the line status as a dictionary keyed by channel index."""
        settings = {}
        reply = self._send(Queries.LINES_STATUS.value,
                           reply_lines=MAX_CHANNELS)
        template = "L{channel} F={freq.3f} P={power.3f} {state}"
        for line in reply.split(EOL):
            ch_settings = parse(template, line).named
            settings[int(ch_settings.pop())] = ch_settings
        return settings

    def get_channel(self):
        """Return the most recently specified channel."""
        return int(self._send(Queries.CHANNEL_SELECT.value).rstrip(EOL))

    @channel_specified
    def get_frequency(self):
        """Return the frequency in [MHz] of the current channel."""
        return float(self._send(Queries.FREQUENCY_ADJUST.value).rstrip(EOL))

    @channel_specified
    def get_power_percent(self):
        return int(self._send(Queries.POWER_ADJUST.value).rstrip(EOL)) * \
            100./MAX_POWER_INT

    @channel_specified
    def get_power_dbm(self):
        """return the fine power value of the current channel."""
        return float(self._send(Queries.FINE_POWER_ADJUST.value).rstrip(EOL))

    @channel_specified
    def get_driver_mode(self):
        """return the driver mode of the current channel."""
        return DriverMode(self._send(Queries.DRIVER_MODE.value).rstrip(EOL))

    @channel_specified
    def get_pll(self):
        """Get state of the pll for the current channel."""
        return PLLState(self._send(Queries.PLL_SWITCH.value).rstrip(EOL))

    def _send(self, msg: str, reply_lines: int = 1, wait: bool = True):
        """Send message to the AOTF. Optionally wait for a reply."""
        self.log.debug(f"Sending: {msg}")
        self.ser.write(f"{msg}{EOL}".encode('ascii'))
        # TODO: handle wait=False case.
        reply = ""
        for i in range(reply_lines):
            line = self.ser.read_until(EOL.encode("ascii").decode("utf8")
            self.log.debug("Received: {reply}")
            reply += line
        return reply

