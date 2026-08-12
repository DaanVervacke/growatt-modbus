"""MOD / MID TL3-X PV inverters — the ``GEN2`` generation.

Addresses, types and scales are extracted from the ``plugin_growatt.py``
entity declarations of homeassistant-solax-modbus."""

from __future__ import annotations

from typing import ClassVar

from modbus_connection.model import gauge, int32, integer, string, uint32

from .fields import GrowattComponent, in_range, option, rtc
from .variants import Variant


class Gen2Settings(GrowattComponent):
    """Inverter settings and identity (holding registers)."""

    inverter_switch = option(
        0, {0: "Inverter Off", 1: "Inverter On", 2: "BDC Off", 3: "BDC On"}, writable=True
    )
    """Inverter Switch."""

    active_power_limit = integer(3, signed=False, writable=in_range(0, 100, 255))
    """Active Power Limit."""

    reactive_power_limit = integer(4, signed=True, writable=in_range(-100, 100, 255))
    """Reactive Power Limit."""

    firmware_version = string(9, 3)
    """Firmware Version."""

    firmware_control_version_ascii = string(12, 2)
    """Firmware Control Version Ascii."""

    firmware_control_version_number = integer(14, signed=False)
    """Firmware Control Version Number."""

    language = option(
        15,
        {
            0: "Italiano",
            1: "English",
            2: "Deutsch",
            3: "Espanol",
            4: "Francais",
            5: "Hanyu",
            6: "Polski",
            7: "Portugues",
            8: "Magyar",
        },
    )
    """Language."""

    select_baud_rate = option(22, {0: "9600bps", 1: "38400bps"}, writable=True)
    """Select Baud Rate."""

    serialnumber = string(23, 5)
    """Serial Number."""

    rtc = rtc(45, writable=True)
    """RTC."""

    limit_grid_export = option(
        122, {0: "Disabled", 1: "Meter 1", 2: "Meter 2", 3: "CT Clamp"}, writable=True
    )
    """Limit Grid Export."""

    grid_export_limit = gauge(123, 0.1, signed=True, writable=in_range(-100, 100))
    """Grid Export Limit."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "inverter_switch": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "active_power_limit": Variant.GEN
        | Variant.GEN2
        | Variant.GEN3
        | Variant.GEN4
        | Variant.SPF,
        "reactive_power_limit": Variant.GEN
        | Variant.GEN2
        | Variant.GEN3
        | Variant.GEN4
        | Variant.SPF,
        "firmware_version": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF,
        "firmware_control_version_ascii": Variant.GEN
        | Variant.GEN2
        | Variant.GEN3
        | Variant.GEN4
        | Variant.SPF,
        "firmware_control_version_number": Variant.GEN
        | Variant.GEN2
        | Variant.GEN3
        | Variant.GEN4
        | Variant.SPF,
        "language": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF,
        "select_baud_rate": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "serialnumber": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.SPF,
        "rtc": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF,
        "limit_grid_export": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "grid_export_limit": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
    }


class Gen2Status(GrowattComponent):
    """Live measurements (input registers)."""

    register_space = "input"

    pv_power_total = uint32(1, scale=0.1, unit="W")
    """PV Power Total."""

    pv_voltage_1 = gauge(3, 0.1, signed=False, unit="V")
    """PV Voltage 1."""

    pv_current_1 = gauge(4, 0.1, signed=False, unit="A")
    """PV Current 1."""

    pv_power_1 = uint32(5, scale=0.1, unit="W")
    """PV Power 1."""

    pv_voltage_2 = gauge(7, 0.1, signed=False, unit="V")
    """PV Voltage 2."""

    pv_current_2 = gauge(8, 0.1, signed=False, unit="A")
    """PV Current 2."""

    pv_power_2 = uint32(9, scale=0.1, unit="W")
    """PV Power 2."""

    pv_voltage_3 = gauge(11, 0.1, signed=False, unit="V")
    """PV Voltage 3."""

    pv_current_3 = gauge(12, 0.1, signed=False, unit="A")
    """PV Current 3."""

    pv_power_3 = uint32(13, scale=0.1, unit="W")
    """PV Power 3."""

    pv_voltage_4 = gauge(15, 0.1, signed=False, unit="V")
    """PV Voltage 4."""

    pv_current_4 = gauge(16, 0.1, signed=False, unit="A")
    """PV Current 4."""

    pv_power_4 = uint32(17, scale=0.1, unit="W")
    """PV Power 4."""

    pv_voltage_5 = gauge(19, 0.1, signed=False, unit="V")
    """PV Voltage 5."""

    pv_current_5 = gauge(20, 0.1, signed=False, unit="A")
    """PV Current 5."""

    pv_power_5 = uint32(21, scale=0.1, unit="W")
    """PV Power 5."""

    pv_voltage_6 = gauge(23, 0.1, signed=False, unit="V")
    """PV Voltage 6."""

    pv_current_6 = gauge(24, 0.1, signed=False, unit="A")
    """PV Current 6."""

    pv_power_6 = uint32(25, scale=0.1, unit="W")
    """PV Power 6."""

    pv_voltage_7 = gauge(27, 0.1, signed=False, unit="V")
    """PV Voltage 7."""

    pv_current_7 = gauge(28, 0.1, signed=False, unit="A")
    """PV Current 7."""

    pv_power_7 = uint32(29, scale=0.1, unit="W")
    """PV Power 7."""

    pv_voltage_8 = gauge(31, 0.1, signed=False, unit="V")
    """PV Voltage 8."""

    inverter_temperature_alt = gauge(32, 0.1, signed=False, unit="°C")
    """Inverter temperature at input register 32 (Gen2 only).

    Upstream declares this under the same key as the register 93
    reading, so the two collide there; both are kept here."""

    pv_current_8 = gauge(32, 0.1, signed=False, unit="A")
    """PV Current 8."""

    pv_power_8 = uint32(33, scale=0.1, unit="W")
    """PV Power 8."""

    output_power = int32(35, scale=0.1, unit="W")
    """Output Power."""

    grid_frequency = gauge(37, 0.01, signed=False, unit="Hz")
    """Grid Frequency."""

    inverter_voltage = gauge(38, 0.1, signed=False, unit="V")
    """Grid Voltage."""

    grid_voltage_l1 = gauge(38, 0.1, signed=False, unit="V")
    """Grid Voltage L1."""

    grid_current = gauge(39, 0.1, signed=True, unit="A")
    """Grid Current."""

    grid_current_l1 = gauge(39, 0.1, signed=True, unit="A")
    """Grid Current L1."""

    grid_power = int32(40, scale=0.1, unit="W")
    """Grid Power."""

    grid_power_l1 = int32(40, scale=0.1, unit="VA")
    """Grid Power L1."""

    grid_voltage_l2 = gauge(42, 0.1, signed=False, unit="V")
    """Grid Voltage L2."""

    grid_current_l2 = gauge(43, 0.1, signed=True, unit="A")
    """Grid Current L2."""

    grid_power_l2 = int32(44, scale=0.1, unit="VA")
    """Grid Power L2."""

    grid_voltage_l3 = gauge(46, 0.1, signed=False, unit="V")
    """Grid Voltage L3."""

    grid_current_l3 = gauge(47, 0.1, signed=True, unit="A")
    """Grid Current L3."""

    grid_power_l3 = int32(48, scale=0.1, unit="VA")
    """Grid Power L3."""

    today_s_power_generation = uint32(53, scale=0.1, unit="kWh")
    """Today's Power Generation."""

    total_power_generation = uint32(55, scale=0.1, unit="kWh")
    """Total Power Generation."""

    total_work_time_hours = uint32(57, scale=0.00013889, unit="h")
    """Total Work Time Hours."""

    today_s_pv1_solar_energy = uint32(59, scale=0.1, unit="kWh")
    """Today's PV1 Solar Energy."""

    total_pv1_solar_energy = uint32(61, scale=0.1, unit="kWh")
    """Total PV1 Solar Energy."""

    today_s_pv2_solar_energy = uint32(63, scale=0.1, unit="kWh")
    """Today's PV2 Solar Energy."""

    total_pv2_solar_energy = uint32(65, scale=0.1, unit="kWh")
    """Total PV2 Solar Energy."""

    today_s_pv3_solar_energy = uint32(67, scale=0.1, unit="kWh")
    """Today's PV3 Solar Energy."""

    total_pv3_solar_energy = uint32(69, scale=0.1, unit="kWh")
    """Total PV3 Solar Energy."""

    today_s_pv4_solar_energy = uint32(71, scale=0.1, unit="kWh")
    """Today's PV4 Solar Energy."""

    total_pv4_solar_energy = uint32(73, scale=0.1, unit="kWh")
    """Total PV4 Solar Energy."""

    today_s_pv5_solar_energy = uint32(75, scale=0.1, unit="kWh")
    """Today's PV5 Solar Energy."""

    total_pv5_solar_energy = uint32(77, scale=0.1, unit="kWh")
    """Total PV5 Solar Energy."""

    today_s_pv6_solar_energy = uint32(79, scale=0.1, unit="kWh")
    """Today's PV6 Solar Energy."""

    total_pv6_solar_energy = uint32(81, scale=0.1, unit="kWh")
    """Total PV6 Solar Energy."""

    today_s_pv7_solar_energy = uint32(83, scale=0.1, unit="kWh")
    """Today's PV7 Solar Energy."""

    total_pv7_solar_energy = uint32(85, scale=0.1, unit="kWh")
    """Total PV7 Solar Energy."""

    today_s_pv8_solar_energy = uint32(87, scale=0.1, unit="kWh")
    """Today's PV8 Solar Energy."""

    total_pv8_solar_energy = uint32(89, scale=0.1, unit="kWh")
    """Total PV8 Solar Energy."""

    total_solar_energy = uint32(91, scale=0.1, unit="kWh")
    """Total Solar Energy."""

    inverter_temperature = gauge(93, 0.1, signed=False, unit="°C")
    """Inverter Temperature."""

    ipm_inverter_temperature = gauge(94, 0.1, signed=False, unit="°C")
    """IPM Inverter Temperature."""

    boost_temperature = gauge(95, 0.1, signed=False, unit="°C")
    """Boost Temperature."""

    priority = option(118, {0: "Load First", 1: "Battery First", 2: "Grid First"})
    """Priority."""

    pv_isolation_resistance = integer(200, signed=False, unit="kΩ")
    """PV Isolation Resistance."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "pv_power_total": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "pv_voltage_1": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_current_1": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_power_1": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_voltage_2": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_current_2": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_power_2": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_voltage_3": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_current_3": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_power_3": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_voltage_4": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_current_4": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_power_4": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_voltage_5": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_current_5": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_power_5": Variant.GEN2 | Variant.GEN3 | Variant.MPPT6 | Variant.MPPT8 | Variant.MPPT10,
        "pv_voltage_6": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_current_6": Variant.GEN2
        | Variant.GEN3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_power_6": Variant.GEN2 | Variant.GEN3 | Variant.MPPT6 | Variant.MPPT8 | Variant.MPPT10,
        "pv_voltage_7": Variant.GEN2 | Variant.GEN3 | Variant.MPPT8 | Variant.MPPT10,
        "pv_current_7": Variant.GEN2 | Variant.GEN3 | Variant.MPPT8 | Variant.MPPT10,
        "pv_power_7": Variant.GEN2 | Variant.GEN3 | Variant.MPPT8 | Variant.MPPT10,
        "pv_voltage_8": Variant.GEN2 | Variant.GEN3 | Variant.MPPT8 | Variant.MPPT10,
        "inverter_temperature_alt": Variant.GEN2,
        "pv_current_8": Variant.GEN2 | Variant.GEN3 | Variant.MPPT8 | Variant.MPPT10,
        "pv_power_8": Variant.GEN2 | Variant.GEN3 | Variant.MPPT8 | Variant.MPPT10,
        "output_power": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "grid_frequency": Variant.GEN2 | Variant.GEN3,
        "inverter_voltage": Variant.GEN2 | Variant.GEN3 | Variant.X1,
        "grid_voltage_l1": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_current": Variant.GEN2 | Variant.GEN3 | Variant.X1,
        "grid_current_l1": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_power": Variant.GEN2 | Variant.GEN3 | Variant.X1,
        "grid_power_l1": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_voltage_l2": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_current_l2": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_power_l2": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_voltage_l3": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_current_l3": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "grid_power_l3": Variant.GEN2 | Variant.GEN3 | Variant.X3,
        "today_s_power_generation": Variant.GEN2 | Variant.GEN3,
        "total_power_generation": Variant.GEN2 | Variant.GEN3,
        "total_work_time_hours": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "today_s_pv1_solar_energy": Variant.GEN2 | Variant.GEN3,
        "total_pv1_solar_energy": Variant.GEN2 | Variant.GEN3,
        "today_s_pv2_solar_energy": Variant.GEN2 | Variant.GEN3,
        "total_pv2_solar_energy": Variant.GEN2 | Variant.GEN3,
        "today_s_pv3_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_pv3_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "today_s_pv4_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_pv4_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "today_s_pv5_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_pv5_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "today_s_pv6_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_pv6_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "today_s_pv7_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_pv7_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT8
        | Variant.MPPT10,
        "today_s_pv8_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_pv8_solar_energy": Variant.GEN2
        | Variant.GEN3
        | Variant.X3
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_solar_energy": Variant.GEN2 | Variant.GEN3,
        "inverter_temperature": Variant.GEN2 | Variant.GEN3,
        "ipm_inverter_temperature": Variant.GEN2 | Variant.GEN3,
        "boost_temperature": Variant.GEN2 | Variant.GEN3,
        "priority": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "pv_isolation_resistance": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
    }
