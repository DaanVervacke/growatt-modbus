"""Legacy Growatt PV inverters (TL-S, TL3-S, NEO) — the ``GEN`` generation.

Addresses, types and scales are extracted from the ``plugin_growatt.py``
entity declarations of homeassistant-solax-modbus."""

from __future__ import annotations

from typing import ClassVar

from modbus_connection.model import gauge, int32, integer, string, uint32

from .fields import GrowattComponent, in_range, inverter_module_code, option, rtc
from .variants import Variant


class Gen1Settings(GrowattComponent):
    """Inverter settings and identity (holding registers)."""

    inverter_switch = option(0, {0: "Inverter Off", 1: "Inverter On"}, writable=True)
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

    serialnumber = string(23, 5)
    """Serial Number."""

    inverter_module = inverter_module_code(28)
    """Inverter Module."""

    rtc = rtc(45, writable=True)
    """RTC."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "inverter_switch": Variant.GEN | Variant.SPF,
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
        "serialnumber": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.SPF,
        "inverter_module": Variant.GEN | Variant.GEN3,
        "rtc": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF,
    }


class Gen1Status(GrowattComponent):
    """Live measurements (input registers)."""

    register_space = "input"

    run_mode = option(0, {0: "Waiting", 1: "Normal Mode", 2: "?", 3: "Permanent Fault Mode"})
    """Machine Status."""

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

    output_power = uint32(11, scale=0.1, unit="W")
    """Output Power."""

    grid_frequency = gauge(13, 0.01, signed=False, unit="Hz")
    """Grid Frequency."""

    inverter_voltage = gauge(14, 0.1, signed=False, unit="V")
    """Grid Voltage."""

    grid_voltage_l1 = gauge(14, 0.1, signed=False, unit="V")
    """Grid Voltage L1."""

    grid_current = gauge(15, 0.1, signed=True, unit="A")
    """Grid Current."""

    grid_current_l1 = gauge(15, 0.1, signed=True, unit="A")
    """Grid Current L1."""

    grid_power = int32(16, scale=0.1, unit="W")
    """Grid Power."""

    grid_power_l1 = int32(16, scale=0.1, unit="VA")
    """Grid Power L1."""

    grid_voltage_l2 = gauge(18, 0.1, signed=False, unit="V")
    """Grid Voltage L2."""

    grid_current_l2 = gauge(19, 0.1, signed=True, unit="A")
    """Grid Current L2."""

    grid_power_l2 = int32(20, scale=0.1, unit="VA")
    """Grid Power L2."""

    grid_voltage_l3 = gauge(22, 0.1, signed=False, unit="V")
    """Grid Voltage L3."""

    grid_current_l3 = gauge(23, 0.1, signed=True, unit="A")
    """Grid Current L3."""

    grid_power_l3 = int32(24, scale=0.1, unit="VA")
    """Grid Power L3."""

    today_s_power_generation = uint32(26, scale=0.1, unit="kWh")
    """Today's Power Generation."""

    total_power_generation = uint32(28, scale=0.1, unit="kWh")
    """Total Power Generation."""

    total_work_time = uint32(30, scale=0.5, unit="s")
    """Total Work Time."""

    today_s_pv1_solar_energy = uint32(48, scale=0.1, unit="kWh")
    """Today's PV1 Solar Energy."""

    total_pv1_solar_energy = uint32(50, scale=0.1, unit="kWh")
    """Total PV1 Solar Energy."""

    today_s_pv2_solar_energy = uint32(52, scale=0.1, unit="kWh")
    """Today's PV2 Solar Energy."""

    total_pv2_solar_energy = uint32(54, scale=0.1, unit="kWh")
    """Total PV2 Solar Energy."""

    total_solar_energy = uint32(56, scale=0.1, unit="kWh")
    """Total Solar Energy."""

    reactive_power = uint32(58, unit="var")
    """Reactive Power."""

    pv_voltage_3 = gauge(120, 0.1, signed=False, unit="V")
    """PV Voltage 3."""

    pv_current_3 = gauge(121, 0.1, signed=False, unit="A")
    """PV Current 3."""

    pv_power_3 = uint32(122, scale=0.1, unit="W")
    """PV Power 3."""

    today_s_pv3_solar_energy = uint32(124, scale=0.1, unit="kWh")
    """Today's PV3 Solar Energy."""

    total_pv3_solar_energy = uint32(126, scale=0.1, unit="kWh")
    """Total PV3 Solar Energy."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "run_mode": Variant.GEN,
        "pv_power_total": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "pv_voltage_1": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_current_1": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_power_1": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_voltage_2": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_current_2": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "pv_power_2": Variant.GEN | Variant.GEN2 | Variant.GEN3,
        "output_power": Variant.GEN,
        "grid_frequency": Variant.GEN,
        "inverter_voltage": Variant.GEN | Variant.X1,
        "grid_voltage_l1": Variant.GEN | Variant.X3,
        "grid_current": Variant.GEN | Variant.X1,
        "grid_current_l1": Variant.GEN | Variant.X3,
        "grid_power": Variant.GEN | Variant.X1,
        "grid_power_l1": Variant.GEN | Variant.X3,
        "grid_voltage_l2": Variant.GEN | Variant.X3,
        "grid_current_l2": Variant.GEN | Variant.X3,
        "grid_power_l2": Variant.GEN | Variant.X3,
        "grid_voltage_l3": Variant.GEN | Variant.X3,
        "grid_current_l3": Variant.GEN | Variant.X3,
        "grid_power_l3": Variant.GEN | Variant.X3,
        "today_s_power_generation": Variant.GEN,
        "total_power_generation": Variant.GEN,
        "total_work_time": Variant.GEN,
        "today_s_pv1_solar_energy": Variant.GEN,
        "total_pv1_solar_energy": Variant.GEN,
        "today_s_pv2_solar_energy": Variant.GEN,
        "total_pv2_solar_energy": Variant.GEN,
        "total_solar_energy": Variant.GEN,
        "reactive_power": Variant.GEN,
        "pv_voltage_3": Variant.GEN | Variant.MPPT3,
        "pv_current_3": Variant.GEN | Variant.MPPT3,
        "pv_power_3": Variant.GEN | Variant.MPPT3,
        "today_s_pv3_solar_energy": Variant.GEN | Variant.MPPT3,
        "total_pv3_solar_energy": Variant.GEN | Variant.MPPT3,
    }
