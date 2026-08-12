"""Label maps shared by more than one register.

Settings whose labels appear at a single address are declared inline on the
component; these are the ones the inverter reuses across registers, or that the
upstream plugin expressed as a decoding function rather than a table.
"""

from __future__ import annotations

from typing import Final

MODULE_STATUS: Final[dict[int, str]] = {
    1: "Standby",
    2: "Charging",
    3: "Discharging",
    7: "Sleeping",
}
"""State of one APX battery module."""

MODULE_WARNING: Final[dict[int, str]] = {
    0: "Normal",
    404: "Abnormal EEPROM",
    410: "External oscillation abnormal/Oscillation abnormal/USB communication abnormal",
    411: "Parallel communication failed",
    417: "BM and PM software versions mismatched",
    431: "BOOT abnormal",
    500: (
        "Abnormal CAN communication during parallel operation/BM went offline/"
        "Abnormal with PM communication"
    ),
    701: "Module not discharging alarm",
    702: "Forced charge is required",
    703: "Module is fully charged",
    704: "PM to INV overvoltage",
    705: "PM to INV overvoltage",
    707: "Discharge Overload Alarm",
    708: "Discharge Overload Anomaly",
}
"""Warning reported by one APX battery module."""

RUN_MODE: Final[dict[int, str]] = {
    0: "Standby",
    1: "Normal",
    2: "Off-Grid (Backup)",
    3: "Fault",
    4: "Flash",
}
"""Gen4 operating mode — the low byte of input register 3000."""

INVERTER_STATE: Final[dict[int, str]] = {
    0: "Waiting",
    3: "Fault",
    4: "Flash",
    5: "PV Bat Online",
    6: "Bat Online",
    8: "Bat Offline Mode",
}
"""Gen4 inverter state — the high byte of input register 3000."""

TIME_SLOT_MODE: Final[dict[int, str]] = {
    0: "Load First",
    1: "Battery First",
    2: "Grid First",
    3: "Grid First",
}
"""Gen4 time-slot priority, from bits 13-14 of the slot's start register.

Bit 14 wins over bit 13, so code 3 reads back as "Grid First" — matching how the
inverter's own encoding is interpreted upstream.
"""

INVERTER_WARNING: Final[dict[tuple[int, int], str]] = {
    (0, 0): "Normal",
    (200, 0): "PV string fault",
    (201, 0): "PV string/PID quick-connect terminals abnormal",
    (202, 0): "DC SPD function abnormal",
    (203, 0): "PV1 or PV2 short circuited",
    (204, 0): "Dry contact function abnormal",
    (205, 0): "PV boost driver abnormal",
    (206, 0): "AC SPD function abnormal",
    (207, 0): "USB flash drive overcurrent protection",
    (208, 0): "DC fuse blown",
    (209, 0): "DC input voltage exceeds the upper threshold",
    (210, 0): "PV wiring abnormal",
    (217, 0): "BMS abnormal",
    (218, 1): "BMS Bus disconnected",
    (219, 0): "PID function abnormal",
    (220, 0): "PV string disconnected",
    (221, 0): "PV string current unbalanced",
    (300, 0): "No utility grid connected or utility grid power failure",
    (301, 0): "Grid voltage is beyond the permissible range",
    (302, 0): "Grid frequency is beyond the permissible range",
    (303, 0): "Off-grid mode, overload",
    (400, 0): "Fan failure",
    (401, 0): "Meter abnormal",
    (406, 0): "Boost circuit malfunction",
    (407, 0): "Over-temperature",
    (408, 0): "NTC temperature sensor is broken",
    (409, 0): "Reactive power scheduling communication failure",
    (411, 0): "Sync signal abnormal",
    (600, 0): "DC component excessively high in output current",
    (601, 0): "DC component excessively high in output voltage",
    (602, 0): "Off-grid output voltage too low",
    (603, 0): "Off-grid output voltage too high",
    (604, 0): "Off-grid output overcurrent",
    (605, 0): "Off-grid bus voltage too low",
    (606, 0): "Off-grid output overloaded",
    (607, 0): "Communication with the backup box is abnormal",
    (608, 0): "Backup box is abnormal",
    (609, 0): "Balanced circuit abnormal",
}
"""Gen4 warning text, keyed by (main code, sub code)."""

INVERTER_FAULT: Final[dict[tuple[int, int], str]] = {
    (0, 0): "Normal",
    (200, 0): "DC arc fault has been detected",
    (201, 0): "High leakage current detected",
    (202, 0): "PV input voltage exceeds the upper threshold",
    (203, 0): "PV panels have low insulation resistance",
    (204, 0): "PV string reversely connected",
    (300, 0): "Grid voltage is beyond the permissible range",
    (301, 0): "AC terminals reversed",
    (302, 0): "No utility grid connected or utility grid power failure",
    (304, 0): "Grid frequency is beyond the permissible range",
    (305, 0): "Overload",
    (309, 0): "ROCOF Fault",
    (311, 0): "Export limitation fail-safe",
    (401, 0): "High DC component in output voltage",
    (402, 0): "High DC component in output current",
    (403, 0): "Output current unbalanced",
    (404, 0): "Bus voltage sampling abnormal",
    (405, 0): "Relay fault",
    (407, 0): "Auto-test failed",
    (408, 0): "Over-temperature",
    (409, 0): "Bus voltage abnormal",
    (411, 0): "Internal communication failure",
    (412, 0): "Temperature sensor disconnected",
    (416, 0): "DC/AC overcurrent protection",
    (420, 0): "GFCI module abnormal",
    (424, 0): "INV current waveform abnormal",
    (425, 0): "AFCI self-test failure",
    (426, 0): "PV current sampling abnormal",
    (427, 0): "AC current sampling abnormal",
    (428, 0): "BOOST short-circuited",
    (429, 0): "BUS soft start failed",
    (600, 0): "Off-grid output short-circuited",
    (601, 0): "Off-grid Bus Voltage Low",
    (602, 0): "Abnormal voltage at the off-grid terminal",
    (603, 0): "Soft start failed",
    (604, 0): "Off-grid output voltage abnormal",
    (605, 0): "Balanced circuit self-test failed",
    (606, 0): "High DC component in output voltage (off-grid)",
    (607, 0): "Off-grid output overload",
    (608, 0): "Off-grid parallel signal abnormal",
    (609, 0): "Backup box is not detected",
    (610, 0): "Off-grid split-phase voltage abnormal",
    (700, 0): "Abnormal communication between the backup box and the inverter",
    (701, 0): "Backup box grid-side relay failure",
    (703, 0): "Backup box on-grid overload",
    (705, 0): "Overheat inside the backup box",
}
"""Gen4 fault text, keyed by (main code, sub code)."""
