"""Device Codes for communicating with the AOTF."""

try:  # a 3.11 feature
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        pass

EOL = '\n\r'


class CmdRoots(StrEnum):
    CHANNEL_SELECT = "X"
    CHANNEL_PREFIX = "L"
    FREQUENCY_ADJUST = "F"
    #POWER_ADJUST = "P"
    FINE_POWER_ADJUST = "D"
    LINES_STATUS = "S"
    DRIVER_MODE = "I"
    PLL_SWITCH = "O"
    DATA_STORAGE = "E"
    VOLTAGE_RANGE = "V"
    RESET = "M"
    PRODUCT_ID = "q"


class Cmds(StrEnum):
    """Cmds implemented as unpopulated format strings."""
    CHANNEL_SELECT = CmdRoots.CHANNEL_SELECT.value + "{0}" + EOL
    FREQUENCY_ADJUST = CmdRoots.CHANNEL_PREFIX.value + "{0}" + CmdRoots.FREQUENCY_ADJUST.value + "{1:07.3f}" + EOL
    #POWER_ADJUST = CmdRoots.CHANNEL_PREFIX.value + "{0}" + CmdRoots.POWER_ADJUST.value + "{0:04d}" + EOL
    FINE_POWER_ADJUST = CmdRoots.CHANNEL_PREFIX.value + "{0}" + CmdRoots.FINE_POWER_ADJUST.value + "{1:05.02f}" + EOL
    DRIVER_MODE = CmdRoots.CHANNEL_PREFIX.value + "{0}" + CmdRoots.DRIVER_MODE.value + "{1}" + EOL
    PLL_SWITCH = CmdRoots.CHANNEL_PREFIX.value + "{0}" + CmdRoots.PLL_SWITCH.value + "{1}" + EOL
    GLOBAL_DRIVER_MODE = CmdRoots.DRIVER_MODE.value + EOL
    VOLTAGE_RANGE = CmdRoots.VOLTAGE_RANGE.value + "{0}" + EOL
    # Note: not all commands require EOL termination.
    DATA_STORAGE = CmdRoots.DATA_STORAGE.value
    RESET = CmdRoots.RESET.value
    PRODUCT_ID = CmdRoots.PRODUCT_ID.value


class Queries(StrEnum):
    CHANNEL_SELECT = CmdRoots.CHANNEL_SELECT.value + EOL
    CHANNEL_SPECIFIC_STATUS = CmdRoots.CHANNEL_PREFIX.value + "{0}" + EOL
    LINES_STATUS = CmdRoots.LINES_STATUS.value + EOL
    PRODUCT_ID = CmdRoots.PRODUCT_ID.value + EOL
    # FREQUENCY_ADJUST and POWER_ADJUST cannot be read this way because
    # reading them has the effect of clearing the value.


class Replies(StrEnum):
    CHANNEL_SELECT = "Line number> {0d}"
    PRODUCT_ID = "{0}"
    CHANNEL_SPECIFIC_STATUS = "l{0}F{1:.3f}P{2:.1f}S{:d}"  # channel index, freq, power (dBm), output state


class OutputState(StrEnum):
    OFF = "0"
    ON = "1"


class VoltageRange(StrEnum):
    ZERO_TO_FIVE_VOLTS = "0"
    ZERO_TO_TEN_VOLTS = "1"


class InputMode(StrEnum):
    # Note that codes correspond to sending commands with the channel prefix.
    # If the driver were implemented to send commands sequentially, these
    # codes would be reversed.
    INTERNAL = "1"
    EXTERNAL = "0"


class BlankingMode(StrEnum):
    INTERNAL = "1"
    EXTERNAL = "0"


class GlobalInputMode(StrEnum):
    INTERNAL = "0"
    EXTERNAL = "1"
