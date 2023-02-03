"""Device Codes for communicating with the AOTF."""

try:  # a 3.11 feature
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass


class CmdRoots(StrEnum):
    CHANNEL_SELECT = "X"
    FREQUENCY_ADJUST = "F"
    POWER_ADJUST = "P"
    FINE_POWER_ADJUST = "D"
    LINES_STATUS = "S"
    DRIVER_MODE = "I"
    PLL_SWITCH = "O"
    DATA_STORAGE = "E"


class Cmds(StrEnum):
    """Cmds implemented as unpopulated format strings."""
    CHANNEL_SELECT = CmdRoots.CHANNEL_SELECT.value + "{0}"
    FREQUENCY_ADJUST = CmdRoots.FREQUENCY_ADJUST.value + "{0:07.3F}"
    POWER_ADJUST = CmdRoots.POWER_ADJUST.value + "{0:04d}"
    FINE_POWER_ADJUST = CmdRoots.FINE_POWER_ADJUST.value + "{1:05.02F}"
    DRIVER_MODE = CmdRoots.DRIVER_MODE.value
    PLL_SWITCH = CmdRoots.PLL_SWITCH.value + "O{0}"
    DATA_STORAGE = CmdRoots.DriverMode.value


Queries = StrEnum('Queries', {c.name: f"{c.value}?" for c in CmdRoots})


class DriverMode(StrEnum):
    INTERNAL = "0"
    EXTERNAL = "1"

class PLLState(StrEnum):
    OFF = "0"
    ON= "1"
