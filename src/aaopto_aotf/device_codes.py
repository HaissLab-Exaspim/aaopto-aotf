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
    FREQUENCY_ADJUST = "F"
    POWER_ADJUST = "P"
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
    CHANNEL_SELECT = CmdRoots.CHANNEL_SELECT.value + "{0}{EOL}"
    FREQUENCY_ADJUST = CmdRoots.FREQUENCY_ADJUST.value + "{0:07.3F}{EOL}"
    POWER_ADJUST = CmdRoots.POWER_ADJUST.value + "{0:04d}{EOL}"
    FINE_POWER_ADJUST = CmdRoots.FINE_POWER_ADJUST.value + "{1:05.02F}{EOL}"
    DRIVER_MODE = CmdRoots.DRIVER_MODE.value + "{EOL}"
    PLL_SWITCH = CmdRoots.PLL_SWITCH.value + "O{0}{EOL}"
    DATA_STORAGE = CmdRoots.DRIVER_MODE.value + "{0}{EOL}"
    VOLTAGE_RANGE = CmdRoots.VOLTAGE_RANGE.value + "{0}{EOL}"
    RESET = CmdRoots.RESET.value
    PRODUCT_ID = CmdRoots.PRODUCT_ID.value


class Queries(StrEnum):
    CHANNEL_SELECT = CmdRoots.CHANNEL_SELECT.value + "{EOL}"
    FREQUENCY_ADJUST = CmdRoots.FREQUENCY_ADJUST.value + "{EOL}"
    POWER_ADJUST = CmdRoots.POWER_ADJUST.value + "{EOL}"
    FINE_POWER_ADJUST = CmdRoots.FINE_POWER_ADJUST + "{EOL}"
    LINES_STATUS = CmdRoots.LINES_STATUS.value
    PRODUCT_ID = CmdRoots.PRODUCT_ID.value + "{EOL}"

query_excludes = [CmdRoots.RESET]  # TODO: finish.
Queries = StrEnum('Queries', {c.name: f"{c.value}{EOL}" for c in CmdRoots
                              if c not in query_excludes})

class Replies(StrEnum):
    CHANNEL_SELECT = f"Line number> {0}{EOL}?"
    FREQUENCY_ADJUST = f"Frequency> {0}{EOL}?"
    PRODUCT_ID = f"> {0}{EOL}?"


class DriverMode(StrEnum):
    INTERNAL = "0"
    EXTERNAL = "1"

class PLLState(StrEnum):
    OFF = "0"
    ON= "1"

class VoltageRange(StrEnum):
    ZERO_TO_FIVE_VOLTS = "0"
    ZERO_TO_TEN_VOLTS = "1"
