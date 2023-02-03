"""Python driver for an AA OptoElectronics AOTF device."""

import logging
import parse
from serial import Serial, SerialException
from aaopto_aotf.device_codes import *

def channel_specified(func):
    """Check that the channel has already been specified."""
    @wraps(func)  # Required for sphinx doc generation.
    def inner(self, *args, **kwds):
        if self._selected_channel is None:
            raise NameError("Active channel must first be specified.")
        return func(self, *args, **kwds)
    return inner


MAX_CHANNELS = 8
MAX_POWER_DBM = 22.0
MAX_COARSE_POWER = 63

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

        self._selected_channel = None

    def select_channel(self, channel: int):
        """Select the active channel."""
        if channel > MAX_CHANNELS or channel < 1:
            raise IndexError("Specified channel is out of range.")
        msg = Cmds.CHANNEL_SELECT.value.format(channel)
        self._send(msg)
        self._selected_channel = channel

    @channel_specified
    def set_frequency(self, frequency: int):
        """Set the active channel frequency in [MHz]."""
        msg = Cmds.FREQUENCY_ADJUST.value.format(frequency)
        self._send(msg)

    @channel_specified
    def set_coarse_power(self, power: int):
        # Clamp to a range of 0 <= power <= 63
        if channel > MAX_COARSE_POWER or channel < 0:
            raise IndexError("Specified coarse power value is out of range.")
        msg = Cmds.POWER_ADJUST.value.format(round(power))
        self._send(msg)

    @channel_specified
    def set_fine_power(self, dbm: float):
        """Set the active channel power in [dBm]."""
        if channel > MAX_POWER_DBM or channel < 0:
            raise IndexError("Specified fine power [dBm] is out of range.")
        msg = Cmds.POWER_ADJUST.value.format(power)
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

    @channel_specified
    def set_driver_mode(self, mode: DriverMode):
        msg = Cmds.DriverMode.value.format(DriverMode.value)
        self._send(msg)

    @channel_specified
    def set_pll(self, state: PLLState):
        msg = Cmds.PLL_SWITCH.value.format(state.value)
        self._send(msg)


    def _send(self, msg: str, reply_lines: int = 1, wait: bool = True):
        """Send message to the AOTF. Optionally wait for a reply."""
        self.log.debug(f"Sending: {msg}")
        self.ser.write(f"{msg}{EOL}".encode('ascii'))
        reply = ""
        for i in range(reply_lines):
            line = self.ser.read_until(EOL.encode("ascii").decode("utf8")
            self.log.debug("Received: {reply}")
            reply += line
        return reply

