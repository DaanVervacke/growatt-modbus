"""SPF and SPE off-grid inverters — the ``SPF`` generation.

Addresses, types and scales are extracted from the ``plugin_growatt.py``
entity declarations of homeassistant-solax-modbus."""

from __future__ import annotations

from typing import ClassVar

from modbus_connection.model import gauge, int32, integer, string, uint32

from .fields import GrowattComponent, in_range, option, rtc
from .variants import SPF_SINGLE_MPPT_SERIAL_PREFIXES, Variant


class SpfSettings(GrowattComponent):
    """Inverter settings and identity (holding registers)."""

    inverter_switch = option(0, {0: "Inverter Off", 1: "Inverter On"}, writable=True)
    """Inverter Switch."""

    state_power = option(1, {0: "Battery First", 1: "Solar First", 2: "Grid First"}, writable=True)
    """State Power."""

    state_charge = option(
        2, {0: "Solar First", 1: "Solar and Grid", 2: "Solar Only"}, writable=True
    )
    """State Charge."""

    active_power_limit = integer(3, signed=False, writable=in_range(0, 100))
    """Active Power Limit."""

    reactive_power_limit = integer(4, signed=True, writable=in_range(-100, 100))
    """Reactive Power Limit."""

    pv_input_mode = option(7, {0: "Independent", 1: "Parallel"}, writable=True)
    """PV Input Mode."""

    ac_input_mode = option(8, {0: "APL", 1: "UPS", 2: "Gen"}, writable=True)
    """AC Input Mode."""

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

    output_voltage_type = option(
        18, {0: "208", 1: "230", 2: "240", 3: "220", 4: "100", 5: "110", 6: "120"}, writable=True
    )
    """Output Voltage Type."""

    output_frequency_type = option(19, {0: "50", 1: "60"}, writable=True)
    """Output Frequency Type."""

    overload_restart = option(20, {0: "Yes", 1: "No", 2: "Switch to UTI"}, writable=True)
    """Overload Restart."""

    overtemperature_restart = option(21, {0: "Yes", 1: "No"}, writable=True)
    """Overtemperature Restart."""

    buzzer = option(22, {0: "Disable", 1: "Enable"}, writable=True)
    """Buzzer."""

    serialnumber = string(23, 5)
    """Serial Number."""

    max_charge_current = integer(34, signed=False, unit="A")
    """Max Charge Current."""

    max_ac_charge_current = integer(38, signed=False, unit="A")
    """Max AC Charge Current."""

    battery_type = option(
        39, {0: "AGM", 1: "Flooded", 2: "User Defined", 3: "Lithium", 4: "User Defined 2"}
    )
    """Battery Type."""

    rtc = rtc(45)
    """RTC."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "inverter_switch": Variant.GEN | Variant.SPF,
        "state_power": Variant.SPF,
        "state_charge": Variant.SPF,
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
        "pv_input_mode": Variant.SPF,
        "ac_input_mode": Variant.SPF,
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
        "output_voltage_type": Variant.SPF,
        "output_frequency_type": Variant.SPF,
        "overload_restart": Variant.SPF,
        "overtemperature_restart": Variant.SPF,
        "buzzer": Variant.SPF,
        "serialnumber": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.SPF,
        "max_charge_current": Variant.SPF,
        "max_ac_charge_current": Variant.SPF,
        "battery_type": Variant.SPF,
        "rtc": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF,
    }


class SpfStatus(GrowattComponent):
    """Live measurements (input registers)."""

    register_space = "input"

    run_mode = option(
        0,
        {
            0: "Standby",
            1: "PV & Grid Discharge",
            2: "Discharge",
            3: "Fault",
            4: "Flash",
            5: "PV Charge",
            6: "AC Charge",
            7: "Combine Charge",
            8: "Combine Charge & Bypass",
            9: "PV Charge & Bypass",
            10: "AC Charge & Bypass",
            11: "Bypass",
            12: "PV Charge & Discharge",
        },
    )
    """Machine Status."""

    pv_voltage_1 = gauge(1, 0.1, signed=False, unit="V")
    """PV Voltage 1."""

    pv_voltage_2 = gauge(2, 0.1, signed=False, unit="V")
    """PV Voltage 2."""

    pv_power_1 = uint32(3, scale=0.1, unit="W")
    """PV Power 1."""

    pv_power_2 = uint32(5, scale=0.1, unit="W")
    """PV Power 2."""

    pv_current_1 = gauge(7, 0.1, signed=False, unit="A")
    """PV Current 1."""

    pv_current_2 = gauge(8, 0.1, signed=False, unit="A")
    """PV Current 2."""

    output_active_power = uint32(9, scale=0.1, unit="W")
    """Output Active Power."""

    output_apparent_power = uint32(11, scale=0.1, unit="VA")
    """Output Apparent Power."""

    ac_charge_power = uint32(13, scale=0.1, unit="W")
    """AC Charge Power."""

    ac_charge_apparent_power = uint32(15, scale=0.1, unit="VA")
    """AC Charge Apparent Power."""

    battery_voltage = gauge(17, 0.01, signed=False, unit="V")
    """Battery Voltage."""

    battery_soc = integer(18, signed=False)
    """Battery SOC."""

    grid_voltage = gauge(20, 0.1, signed=False, unit="V")
    """Grid Voltage."""

    grid_frequency = gauge(21, 0.01, signed=False, unit="Hz")
    """Grid Frequency."""

    output_voltage = gauge(22, 0.1, signed=False, unit="V")
    """Output Voltage."""

    output_frequency = gauge(23, 0.01, signed=False, unit="Hz")
    """Output Frequency."""

    output_voltage_dc = gauge(24, 0.1, signed=False, unit="V")
    """Output Voltage DC."""

    inverter_temperature = gauge(25, 0.1, signed=False, unit="°C")
    """Inverter Temperature."""

    dcdc_temperature = gauge(26, 0.1, signed=False, unit="°C")
    """DC-DC Temperature."""

    inverter_load = gauge(27, 0.1, signed=False)
    """Inverter Load."""

    total_work_time = uint32(30, scale=0.5, unit="s")
    """Total Work Time."""

    output_current = gauge(34, 0.1, signed=False, unit="A")
    """Output Current."""

    inverter_current = gauge(35, 0.1, signed=False, unit="A")
    """Inverter Current."""

    ac_input_power = uint32(36, scale=0.1, unit="W")
    """AC Input Power."""

    ac_input_apparent_power = uint32(38, scale=0.1, unit="VA")
    """AC Input Apparent Power."""

    fault_code = integer(42, signed=False)
    """Fault Code."""

    warning_code = integer(43, signed=False)
    """Warning Code."""

    constant_power_ok = option(47, {0: "Not OK", 1: "OK"})
    """Constant Power OK."""

    today_s_solar_energy_pv1 = int32(48, scale=0.1, unit="kWh")
    """Today's Solar Energy PV1."""

    total_solar_energy_pv1 = int32(50, scale=0.1, unit="kWh")
    """Total Solar Energy PV1."""

    today_s_solar_energy_pv2 = int32(52, scale=0.1, unit="kWh")
    """Today's Solar Energy PV2."""

    total_solar_energy_pv2 = int32(54, scale=0.1, unit="kWh")
    """Total Solar Energy PV2."""

    today_s_ac_charge = int32(56, scale=0.1, unit="kWh")
    """Today's AC Charge."""

    total_ac_charge = int32(58, scale=0.1, unit="kWh")
    """Total AC Charge."""

    today_s_battery_discharge = int32(60, scale=0.1, unit="kWh")
    """Today's Battery Discharge."""

    total_battery_discharge = int32(62, scale=0.1, unit="kWh")
    """Total Battery Discharge."""

    today_s_ac_discharge = int32(64, scale=0.1, unit="kWh")
    """Today's AC Discharge."""

    total_ac_discharge = int32(66, scale=0.1, unit="kWh")
    """Total AC Discharge."""

    ac_battery_charge = gauge(68, 0.1, signed=False, unit="A")
    """AC Battery Charge."""

    ac_discharge_power = uint32(69, scale=0.1, unit="W")
    """AC Discharge Power."""

    ac_discharge_apparent_power = uint32(71, scale=0.1, unit="VA")
    """AC Discharge Apparent Power."""

    battery_discharge_power = uint32(73, scale=0.1, unit="W")
    """Battery Discharge Power."""

    battery_discharge_apparent_power = uint32(75, scale=0.1, unit="VA")
    """Battery Discharge Apparent Power."""

    battery_power_charge = int32(77, scale=0.1, unit="W")
    """Battery Power Charge."""

    battery_over_charge = option(80, {0: "Not Over Charge", 1: "Over Charge"})
    """Battery Over Charge."""

    mppt_fan_speed = gauge(81, 0.1, signed=False)
    """MPPT Fan Speed."""

    inverter_fan_speed = gauge(82, 0.1, signed=False)
    """Inverter Fan Speed."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "run_mode": Variant.SPF,
        "pv_voltage_1": Variant.SPF,
        "pv_voltage_2": Variant.SPF,
        "pv_power_1": Variant.SPF,
        "pv_power_2": Variant.SPF,
        "pv_current_1": Variant.SPF,
        "pv_current_2": Variant.SPF,
        "output_active_power": Variant.SPF,
        "output_apparent_power": Variant.SPF,
        "ac_charge_power": Variant.SPF,
        "ac_charge_apparent_power": Variant.SPF,
        "battery_voltage": Variant.SPF,
        "battery_soc": Variant.SPF,
        "grid_voltage": Variant.SPF,
        "grid_frequency": Variant.SPF,
        "output_voltage": Variant.SPF,
        "output_frequency": Variant.SPF,
        "output_voltage_dc": Variant.SPF,
        "inverter_temperature": Variant.SPF,
        "dcdc_temperature": Variant.SPF,
        "inverter_load": Variant.SPF,
        "total_work_time": Variant.SPF,
        "output_current": Variant.SPF,
        "inverter_current": Variant.SPF,
        "ac_input_power": Variant.SPF,
        "ac_input_apparent_power": Variant.SPF,
        "fault_code": Variant.SPF,
        "warning_code": Variant.SPF,
        "constant_power_ok": Variant.SPF,
        "today_s_solar_energy_pv1": Variant.SPF,
        "total_solar_energy_pv1": Variant.SPF,
        "today_s_solar_energy_pv2": Variant.SPF,
        "total_solar_energy_pv2": Variant.SPF,
        "today_s_ac_charge": Variant.SPF,
        "total_ac_charge": Variant.SPF,
        "today_s_battery_discharge": Variant.SPF,
        "total_battery_discharge": Variant.SPF,
        "today_s_ac_discharge": Variant.SPF,
        "total_ac_discharge": Variant.SPF,
        "ac_battery_charge": Variant.SPF,
        "ac_discharge_power": Variant.SPF,
        "ac_discharge_apparent_power": Variant.SPF,
        "battery_discharge_power": Variant.SPF,
        "battery_discharge_apparent_power": Variant.SPF,
        "battery_power_charge": Variant.SPF,
        "battery_over_charge": Variant.SPF,
        "mppt_fan_speed": Variant.SPF,
        "inverter_fan_speed": Variant.SPF,
    }

    FIELD_BLACKLISTS: ClassVar[dict[str, tuple[str, ...]]] = {
        "pv_voltage_2": SPF_SINGLE_MPPT_SERIAL_PREFIXES,
        "pv_power_2": SPF_SINGLE_MPPT_SERIAL_PREFIXES,
        "pv_current_2": SPF_SINGLE_MPPT_SERIAL_PREFIXES,
        "today_s_solar_energy_pv2": SPF_SINGLE_MPPT_SERIAL_PREFIXES,
        "total_solar_energy_pv2": SPF_SINGLE_MPPT_SERIAL_PREFIXES,
    }
