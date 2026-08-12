"""SPH and SPA storage inverters — the ``GEN3`` generation.

Addresses, types and scales are extracted from the ``plugin_growatt.py``
entity declarations of homeassistant-solax-modbus."""

from __future__ import annotations

from typing import ClassVar

from modbus_connection.model import gauge, int32, integer, string, uint32

from .fields import (
    GrowattComponent,
    in_range,
    inverter_module_code,
    option,
    packed_option,
    rtc,
    time_of_day,
)
from .variants import Variant


class Gen3Settings(GrowattComponent):
    """Inverter settings and identity (holding registers)."""

    inverter_switch = option(
        0, {0: "Inverter Off", 1: "Inverter On", 2: "BDC Off", 3: "BDC On"}, writable=True
    )
    """Inverter Switch."""

    active_power_limit = integer(3, signed=False, writable=in_range(0, 100))
    """Active Power Limit."""

    reactive_power_limit = integer(4, signed=True, writable=in_range(-100, 100))
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

    pv_startup_voltage = gauge(17, 0.1, signed=False, unit="V", writable=in_range(0, 1000))
    """PV Start-up Voltage."""

    select_baud_rate = option(22, {0: "9600bps", 1: "38400bps"}, writable=True)
    """Select Baud Rate."""

    serialnumber = string(23, 5)
    """Serial Number."""

    inverter_module = inverter_module_code(28)
    """Inverter Module."""

    rtc = rtc(45)
    """RTC."""

    limit_grid_export = option(
        122, {0: "Disabled", 1: "Meter 1", 2: "Meter 2", 3: "CT Clamp"}, writable=True
    )
    """Limit Grid Export."""

    grid_export_limit = gauge(123, 0.1, signed=True, writable=in_range(-100, 100))
    """Grid Export Limit."""

    load_first_battery_minimum_soc = integer(608, signed=False, writable=in_range(10, 100))
    """Load First Battery Minimum SOC."""

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
        "pv_startup_voltage": Variant.GEN3 | Variant.HYBRID,
        "select_baud_rate": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "serialnumber": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.SPF,
        "inverter_module": Variant.GEN | Variant.GEN3,
        "rtc": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF,
        "limit_grid_export": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "grid_export_limit": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "load_first_battery_minimum_soc": Variant.GEN3,
    }


class Gen3StorageSettings(GrowattComponent):
    """Battery charge/discharge schedule and limits."""

    battery_first_time_4_begin = time_of_day(1017, writable=True)
    """Battery First Time 4 Begin."""

    battery_first_time_4_end = time_of_day(1018, writable=True)
    """Battery First Time 4 End."""

    battery_first_time_4 = option(1019, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Battery First Time 4."""

    battery_first_time_5_begin = time_of_day(1020, writable=True)
    """Battery First Time 5 Begin."""

    battery_first_time_5_end = time_of_day(1021, writable=True)
    """Battery First Time 5 End."""

    battery_first_time_5 = option(1022, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Battery First Time 5."""

    battery_first_time_6_begin = time_of_day(1023, writable=True)
    """Battery First Time 6 Begin."""

    battery_first_time_6_end = time_of_day(1024, writable=True)
    """Battery First Time 6 End."""

    battery_first_time_6 = option(1025, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Battery First Time 6."""

    grid_first_time_4_begin = time_of_day(1026, writable=True)
    """Grid First Time 4 Begin."""

    grid_first_time_4_end = time_of_day(1027, writable=True)
    """Grid First Time 4 End."""

    grid_first_time_4 = option(1028, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Grid First Time 4."""

    grid_first_time_5_begin = time_of_day(1029, writable=True)
    """Grid First Time 5 Begin."""

    grid_first_time_5_end = time_of_day(1030, writable=True)
    """Grid First Time 5 End."""

    grid_first_time_5 = option(1031, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Grid First Time 5."""

    grid_first_time_6_begin = time_of_day(1032, writable=True)
    """Grid First Time 6 Begin."""

    grid_first_time_6_end = time_of_day(1033, writable=True)
    """Grid First Time 6 End."""

    grid_first_time_6 = option(1034, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Grid First Time 6."""

    battery_type = option(1048, {0: "Lithium", 1: "Lead Acid", 2: "Other"})
    """Battery Type."""

    eps_set_voltage = option(1061, {0: "230", 1: "208", 2: "240"})
    """EPS Set Voltage."""

    eps_set_frequency = option(1062, {0: "50", 1: "60"})
    """EPS Set Frequency."""

    grid_first_discharge_rate = integer(1070, signed=False, writable=in_range(0, 100))
    """Grid First Discharge Rate."""

    grid_first_battery_minimum_soc = integer(1071, signed=False, writable=in_range(0, 100))
    """Grid First Battery Minimum SOC."""

    grid_first_time_1_begin = time_of_day(1080, writable=True)
    """Grid First Time 1 Begin."""

    grid_first_time_1_end = time_of_day(1081, writable=True)
    """Grid First Time 1 End."""

    grid_first_time_1 = option(1082, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Grid First Time 1."""

    grid_first_time_2_begin = time_of_day(1083, writable=True)
    """Grid First Time 2 Begin."""

    grid_first_time_2_end = time_of_day(1084, writable=True)
    """Grid First Time 2 End."""

    grid_first_time_2 = option(1085, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Grid First Time 2."""

    grid_first_time_3_begin = time_of_day(1086, writable=True)
    """Grid First Time 3 Begin."""

    grid_first_time_3_end = time_of_day(1087, writable=True)
    """Grid First Time 3 End."""

    grid_first_time_3 = option(1088, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Grid First Time 3."""

    battery_first_charge_rate = integer(1090, signed=False, writable=in_range(0, 100))
    """Battery First Charge Rate."""

    battery_first_maximum_soc = integer(1091, signed=False, writable=in_range(0, 100))
    """Battery First Maximum SOC."""

    battery_first_charge_from_grid = option(1092, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Battery First Charge From Grid."""

    battery_first_time_1_begin = time_of_day(1100, writable=True)
    """Battery First Time 1 Begin."""

    battery_first_time_1_end = time_of_day(1101, writable=True)
    """Battery First Time 1 End."""

    battery_first_time_1 = option(1102, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Battery First Time 1."""

    battery_first_time_2_begin = time_of_day(1103, writable=True)
    """Battery First Time 2 Begin."""

    battery_first_time_2_end = time_of_day(1104, writable=True)
    """Battery First Time 2 End."""

    battery_first_time_2 = option(1105, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Battery First Time 2."""

    battery_first_time_3_begin = time_of_day(1106, writable=True)
    """Battery First Time 3 Begin."""

    battery_first_time_3_end = time_of_day(1107, writable=True)
    """Battery First Time 3 End."""

    battery_first_time_3 = option(1108, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Battery First Time 3."""

    load_first_time_1_begin = time_of_day(1110, writable=True)
    """Load First Time 1 Begin."""

    load_first_time_1_end = time_of_day(1111, writable=True)
    """Load First Time 1 End."""

    load_first_time_1 = option(1112, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Load First Time 1."""

    load_first_time_2_begin = time_of_day(1113, writable=True)
    """Load First Time 2 Begin."""

    load_first_time_2_end = time_of_day(1114, writable=True)
    """Load First Time 2 End."""

    load_first_time_2 = option(1115, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Load First Time 2."""

    load_first_time_3_begin = time_of_day(1116, writable=True)
    """Load First Time 3 Begin."""

    load_first_time_3_end = time_of_day(1117, writable=True)
    """Load First Time 3 End."""

    load_first_time_3 = option(1118, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Load First Time 3."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "battery_first_time_4_begin": Variant.GEN3,
        "battery_first_time_4_end": Variant.GEN3,
        "battery_first_time_4": Variant.GEN3,
        "battery_first_time_5_begin": Variant.GEN3,
        "battery_first_time_5_end": Variant.GEN3,
        "battery_first_time_5": Variant.GEN3,
        "battery_first_time_6_begin": Variant.GEN3,
        "battery_first_time_6_end": Variant.GEN3,
        "battery_first_time_6": Variant.GEN3,
        "grid_first_time_4_begin": Variant.GEN3,
        "grid_first_time_4_end": Variant.GEN3,
        "grid_first_time_4": Variant.GEN3,
        "grid_first_time_5_begin": Variant.GEN3,
        "grid_first_time_5_end": Variant.GEN3,
        "grid_first_time_5": Variant.GEN3,
        "grid_first_time_6_begin": Variant.GEN3,
        "grid_first_time_6_end": Variant.GEN3,
        "grid_first_time_6": Variant.GEN3,
        "battery_type": Variant.GEN3,
        "eps_set_voltage": Variant.GEN3 | Variant.EPS,
        "eps_set_frequency": Variant.GEN3 | Variant.EPS,
        "grid_first_discharge_rate": Variant.GEN3,
        "grid_first_battery_minimum_soc": Variant.GEN3,
        "grid_first_time_1_begin": Variant.GEN3,
        "grid_first_time_1_end": Variant.GEN3,
        "grid_first_time_1": Variant.GEN3,
        "grid_first_time_2_begin": Variant.GEN3,
        "grid_first_time_2_end": Variant.GEN3,
        "grid_first_time_2": Variant.GEN3,
        "grid_first_time_3_begin": Variant.GEN3,
        "grid_first_time_3_end": Variant.GEN3,
        "grid_first_time_3": Variant.GEN3,
        "battery_first_charge_rate": Variant.GEN3,
        "battery_first_maximum_soc": Variant.GEN3,
        "battery_first_charge_from_grid": Variant.GEN3,
        "battery_first_time_1_begin": Variant.GEN3,
        "battery_first_time_1_end": Variant.GEN3,
        "battery_first_time_1": Variant.GEN3,
        "battery_first_time_2_begin": Variant.GEN3,
        "battery_first_time_2_end": Variant.GEN3,
        "battery_first_time_2": Variant.GEN3,
        "battery_first_time_3_begin": Variant.GEN3,
        "battery_first_time_3_end": Variant.GEN3,
        "battery_first_time_3": Variant.GEN3,
        "load_first_time_1_begin": Variant.GEN3,
        "load_first_time_1_end": Variant.GEN3,
        "load_first_time_1": Variant.GEN3,
        "load_first_time_2_begin": Variant.GEN3,
        "load_first_time_2_end": Variant.GEN3,
        "load_first_time_2": Variant.GEN3,
        "load_first_time_3_begin": Variant.GEN3,
        "load_first_time_3_end": Variant.GEN3,
        "load_first_time_3": Variant.GEN3,
    }


class Gen3VppSettings(GrowattComponent):
    """Virtual power plant remote-control settings."""

    vpp_status = option(30100, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Vpp Status."""

    vpp_remote_control = option(30407, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Vpp Remote Control."""

    vpp_time = integer(30408, signed=False, writable=in_range(0, 1440))
    """Vpp Time."""

    vpp_power = integer(30409, signed=True, writable=in_range(-100, 100))
    """Vpp Power."""

    vpp_allow_ac_charging = packed_option(30410, 0, 8, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Vpp Allow Ac Charging."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "vpp_status": Variant.GEN3 | Variant.GEN4,
        "vpp_remote_control": Variant.GEN3 | Variant.GEN4,
        "vpp_time": Variant.GEN3 | Variant.GEN4,
        "vpp_power": Variant.GEN3 | Variant.GEN4,
        "vpp_allow_ac_charging": Variant.GEN3 | Variant.GEN4 | Variant.HYBRID,
    }


class Gen3Status(GrowattComponent):
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

    battery_voltage = gauge(97, 0.1, signed=False, unit="V")
    """Battery Voltage."""

    priority = option(118, {0: "Load First", 1: "Battery First", 2: "Grid First"})
    """Priority."""

    battery_type_reported = option(119, {0: "Lead-Acid", 1: "Lithium"})
    """Battery type the inverter reports at input register 119 (Gen3).

    Distinct from the ``battery_type`` setting at holding 1048, which
    upstream declares under the same key with a different code map."""

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
        "battery_voltage": Variant.GEN3,
        "priority": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "battery_type_reported": Variant.GEN3,
        "pv_isolation_resistance": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
    }


class Gen3StorageStatus(GrowattComponent):
    """Battery and load measurements."""

    register_space = "input"

    run_mode = option(
        1000,
        {
            0: "Waiting",
            1: "Self Test",
            2: "2, ?",
            3: "Permanent Fault Mode",
            4: "Update Mode",
            5: "PV Bat Online",
            6: "Bat Online",
            7: "7, ?",
            8: "Normal Mode",
            9: "Bypass",
        },
    )
    """Machine Status."""

    battery_discharge_power = uint32(1009, scale=0.1, unit="W")
    """Battery Discharge Power."""

    battery_charge_power = uint32(1011, scale=0.1, unit="W")
    """Battery Charge Power."""

    battery_soc = integer(1014, signed=False)
    """Battery SOC."""

    ac_power_to_user = int32(1015, scale=0.1, unit="W")
    """AC Power to User."""

    ac_power_to_user_l1 = integer(1017, signed=True, unit="W")
    """AC Power to User L1."""

    ac_power_to_user_l2 = integer(1018, signed=True, unit="W")
    """AC Power to User L2."""

    ac_power_to_user_l3 = integer(1019, signed=True, unit="W")
    """AC Power to User L3."""

    ac_power_to_user_total = int32(1021, scale=0.1, unit="W")
    """AC Power to User Total."""

    ac_power_to_grid = int32(1023, scale=0.1, unit="W")
    """AC Power to Grid."""

    ac_power_to_grid_l1 = integer(1025, signed=True, unit="W")
    """AC Power to Grid L1."""

    ac_power_to_grid_l2 = integer(1026, signed=True, unit="W")
    """AC Power to Grid L2."""

    ac_power_to_grid_l3 = integer(1027, signed=True, unit="W")
    """AC Power to Grid L3."""

    ac_power_to_grid_total = int32(1029, scale=0.1, unit="W")
    """AC Power to Grid Total."""

    house_load = int32(1031, scale=0.1, unit="W")
    """House Load."""

    house_load_l1 = integer(1034, signed=True, unit="W")
    """House Load L1."""

    house_load_l2 = integer(1035, signed=True, unit="W")
    """House Load L2."""

    house_load_l3 = integer(1036, signed=True, unit="W")
    """House Load L3."""

    total_house_load = uint32(1037, scale=0.1, unit="W")
    """Total House Load."""

    battery_temperature = gauge(1040, 0.1, signed=False, unit="°C")
    """Battery Temperature."""

    today_s_grid_import = uint32(1044, scale=0.1, unit="kWh")
    """Today's Grid Import."""

    total_grid_import = uint32(1046, scale=0.1, unit="kWh")
    """Total Grid Import."""

    today_s_grid_export = uint32(1048, scale=0.1, unit="kWh")
    """Today's Grid Export."""

    total_grid_export = uint32(1050, scale=0.1, unit="kWh")
    """Total Grid Export."""

    today_s_battery_output_energy = uint32(1052, scale=0.1, unit="kWh")
    """Today's Battery Output Energy."""

    total_battery_output_energy = uint32(1054, scale=0.1, unit="kWh")
    """Total Battery Output Energy."""

    today_s_battery_input_energy = uint32(1056, scale=0.1, unit="kWh")
    """Today's Battery Input Energy."""

    total_battery_input_energy = uint32(1058, scale=0.1, unit="kWh")
    """Total Battery Input Energy."""

    today_s_load = uint32(1060, scale=0.1, unit="kWh")
    """Today's Load."""

    total_load = uint32(1062, scale=0.1, unit="kWh")
    """Total Load."""

    eps_frequency = gauge(1067, 0.01, signed=False, unit="Hz")
    """EPS Frequency."""

    eps_voltage = gauge(1068, 0.1, signed=False, unit="V")
    """EPS Voltage."""

    eps_voltage_l1 = gauge(1068, 0.1, signed=False, unit="V")
    """EPS Voltage L1."""

    eps_current = gauge(1069, 0.1, signed=False, unit="A")
    """EPS Current."""

    eps_current_l1 = gauge(1069, 0.1, signed=False, unit="A")
    """EPS Current L1."""

    eps_power = uint32(1070, scale=0.1, unit="VA")
    """EPS Power."""

    eps_power_l1 = uint32(1070, scale=0.1, unit="VA")
    """EPS Power L1."""

    eps_voltage_l2 = gauge(1072, 0.1, signed=False, unit="V")
    """EPS Voltage L2."""

    eps_current_l2 = gauge(1073, 0.1, signed=False, unit="A")
    """EPS Current L2."""

    eps_power_l2 = uint32(1074, scale=0.1, unit="VA")
    """EPS Power L2."""

    eps_voltage_l3 = gauge(1076, 0.1, signed=False, unit="V")
    """EPS Voltage L3."""

    eps_current_l3 = gauge(1077, 0.1, signed=False, unit="A")
    """EPS Current L3."""

    eps_power_l3 = uint32(1078, scale=0.1, unit="VA")
    """EPS Power L3."""

    eps_loading = gauge(1080, 0.1, signed=False)
    """EPS Loading."""

    battery_highest_temperature = gauge(1114, 0.1, signed=False, unit="°C")
    """Battery highest Temperature."""

    battery_lowest_temperature = gauge(1115, 0.1, signed=False, unit="°C")
    """Battery lowest Temperature."""

    system_electric_energy_today = uint32(1137, scale=0.1, unit="kWh")
    """System Electric Energy Today."""

    system_electric_energy_total = uint32(1139, scale=0.1, unit="kWh")
    """System Electric Energy Total."""

    self_electric_energy_today = uint32(1141, scale=0.1, unit="kWh")
    """Self Electric Energy Today."""

    self_electric_energy_total = uint32(1143, scale=0.1, unit="kWh")
    """Self Electric Energy Total."""

    system_power = uint32(1145, scale=0.1, unit="W")
    """System Power."""

    self_power = uint32(1147, scale=0.1, unit="W")
    """Self Power."""

    battery_soh = integer(31218, signed=False)
    """Battery SOH."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "run_mode": Variant.GEN3,
        "battery_discharge_power": Variant.GEN3,
        "battery_charge_power": Variant.GEN3,
        "battery_soc": Variant.GEN3,
        "ac_power_to_user": Variant.GEN3 | Variant.X3,
        "ac_power_to_user_l1": Variant.GEN3 | Variant.X3,
        "ac_power_to_user_l2": Variant.GEN3 | Variant.X3,
        "ac_power_to_user_l3": Variant.GEN3 | Variant.X3,
        "ac_power_to_user_total": Variant.GEN3,
        "ac_power_to_grid": Variant.GEN3,
        "ac_power_to_grid_l1": Variant.GEN3 | Variant.X3,
        "ac_power_to_grid_l2": Variant.GEN3 | Variant.X3,
        "ac_power_to_grid_l3": Variant.GEN3 | Variant.X3,
        "ac_power_to_grid_total": Variant.GEN3,
        "house_load": Variant.GEN3 | Variant.X1,
        "house_load_l1": Variant.GEN3 | Variant.X3,
        "house_load_l2": Variant.GEN3 | Variant.X3,
        "house_load_l3": Variant.GEN3 | Variant.X3,
        "total_house_load": Variant.GEN3,
        "battery_temperature": Variant.GEN3,
        "today_s_grid_import": Variant.GEN3,
        "total_grid_import": Variant.GEN3,
        "today_s_grid_export": Variant.GEN3,
        "total_grid_export": Variant.GEN3,
        "today_s_battery_output_energy": Variant.GEN3,
        "total_battery_output_energy": Variant.GEN3,
        "today_s_battery_input_energy": Variant.GEN3,
        "total_battery_input_energy": Variant.GEN3,
        "today_s_load": Variant.GEN3,
        "total_load": Variant.GEN3,
        "eps_frequency": Variant.GEN3 | Variant.EPS,
        "eps_voltage": Variant.GEN3 | Variant.X1 | Variant.EPS,
        "eps_voltage_l1": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_current": Variant.GEN3 | Variant.X1 | Variant.EPS,
        "eps_current_l1": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_power": Variant.GEN3 | Variant.X1 | Variant.EPS,
        "eps_power_l1": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_voltage_l2": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_current_l2": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_power_l2": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_voltage_l3": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_current_l3": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_power_l3": Variant.GEN3 | Variant.X3 | Variant.EPS,
        "eps_loading": Variant.GEN3 | Variant.EPS,
        "battery_highest_temperature": Variant.GEN3,
        "battery_lowest_temperature": Variant.GEN3,
        "system_electric_energy_today": Variant.GEN3,
        "system_electric_energy_total": Variant.GEN3,
        "self_electric_energy_today": Variant.GEN3,
        "self_electric_energy_total": Variant.GEN3,
        "system_power": Variant.GEN3,
        "self_power": Variant.GEN3,
        "battery_soh": Variant.GEN3,
    }
