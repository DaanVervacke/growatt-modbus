"""MIN / MOD / MID / WIT TL-XH hybrids and TL-X PV — the ``GEN4`` generation.

Addresses, types and scales are extracted from the ``plugin_growatt.py``
entity declarations of homeassistant-solax-modbus."""

from __future__ import annotations

from typing import ClassVar

from modbus_connection.model import bit, bits, gauge, int32, integer, string, uint32

from .enums import INVERTER_STATE, MODULE_STATUS, MODULE_WARNING, RUN_MODE, TIME_SLOT_MODE
from .fields import (
    GrowattComponent,
    bms_current,
    bms_power,
    in_range,
    option,
    packed_option,
    rtc,
    time_of_day,
)
from .variants import Variant


class Gen4Settings(GrowattComponent):
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

    rtc = rtc(45, writable=True)
    """RTC."""

    limit_grid_export = option(
        122, {0: "Disabled", 1: "Meter 1", 2: "Meter 2", 3: "CT Clamp"}, writable=True
    )
    """Limit Grid Export."""

    grid_export_limit = gauge(123, 0.1, signed=True, writable=in_range(-100, 100))
    """Grid Export Limit."""

    inverter_total_module_count = integer(185, signed=False)
    """Inverter Total Module Count."""

    bms_type = option(700, {0: "ARO ARK?", 1: "LG ver 3", 2: "APX HV", 4: "LG ver 4"})
    """BMS Type."""

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
        "rtc": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF,
        "limit_grid_export": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "grid_export_limit": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "inverter_total_module_count": Variant.GEN4 | Variant.HYBRID,
        "bms_type": Variant.GEN4,
    }


class Gen4HybridSettings(GrowattComponent):
    """Battery management, time slots and peak shaving."""

    serialnumber = string(3001, 5)
    """Serial Number."""

    ems_discharging_rate = integer(3036, signed=False, writable=in_range(0, 100))
    """Ems Discharging Rate."""

    ems_discharging_stop_soc = integer(3037, signed=False, writable=in_range(10, 100))
    """Ems Discharging Stop Soc."""

    time_1_begin = time_of_day(3038, mask=0x1FFF, writable=True)
    """Time slot 1 start."""

    time_1_mode = packed_option(3038, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 1 priority mode."""

    time_1_enabled = bit(3038, 15, writable=True)
    """Whether time slot 1 is active."""

    time_1_end = time_of_day(3039, writable=True)
    """Time slot 1 end."""

    time_2_begin = time_of_day(3040, mask=0x1FFF, writable=True)
    """Time slot 2 start."""

    time_2_mode = packed_option(3040, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 2 priority mode."""

    time_2_enabled = bit(3040, 15, writable=True)
    """Whether time slot 2 is active."""

    time_2_end = time_of_day(3041, writable=True)
    """Time slot 2 end."""

    time_3_begin = time_of_day(3042, mask=0x1FFF, writable=True)
    """Time slot 3 start."""

    time_3_mode = packed_option(3042, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 3 priority mode."""

    time_3_enabled = bit(3042, 15, writable=True)
    """Whether time slot 3 is active."""

    time_3_end = time_of_day(3043, writable=True)
    """Time slot 3 end."""

    time_4_begin = time_of_day(3044, mask=0x1FFF, writable=True)
    """Time slot 4 start."""

    time_4_mode = packed_option(3044, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 4 priority mode."""

    time_4_enabled = bit(3044, 15, writable=True)
    """Whether time slot 4 is active."""

    time_4_end = time_of_day(3045, writable=True)
    """Time slot 4 end."""

    ems_charging_rate = integer(3047, signed=False, writable=in_range(0, 100))
    """Ems Charging Rate."""

    ems_charging_stop_soc = integer(3048, signed=False, writable=in_range(11, 100))
    """Ems Charging Stop Soc."""

    charger_switch = option(3049, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Charger Switch."""

    time_5_begin = time_of_day(3050, mask=0x1FFF, writable=True)
    """Time slot 5 start."""

    time_5_mode = packed_option(3050, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 5 priority mode."""

    time_5_enabled = bit(3050, 15, writable=True)
    """Whether time slot 5 is active."""

    time_5_end = time_of_day(3051, writable=True)
    """Time slot 5 end."""

    time_6_begin = time_of_day(3052, mask=0x1FFF, writable=True)
    """Time slot 6 start."""

    time_6_mode = packed_option(3052, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 6 priority mode."""

    time_6_enabled = bit(3052, 15, writable=True)
    """Whether time slot 6 is active."""

    time_6_end = time_of_day(3053, writable=True)
    """Time slot 6 end."""

    time_7_begin = time_of_day(3054, mask=0x1FFF, writable=True)
    """Time slot 7 start."""

    time_7_mode = packed_option(3054, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 7 priority mode."""

    time_7_enabled = bit(3054, 15, writable=True)
    """Whether time slot 7 is active."""

    time_7_end = time_of_day(3055, writable=True)
    """Time slot 7 end."""

    time_8_begin = time_of_day(3056, mask=0x1FFF, writable=True)
    """Time slot 8 start."""

    time_8_mode = packed_option(3056, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 8 priority mode."""

    time_8_enabled = bit(3056, 15, writable=True)
    """Whether time slot 8 is active."""

    time_8_end = time_of_day(3057, writable=True)
    """Time slot 8 end."""

    time_9_begin = time_of_day(3058, mask=0x1FFF, writable=True)
    """Time slot 9 start."""

    time_9_mode = packed_option(3058, 13, 2, TIME_SLOT_MODE, writable=True)
    """Time slot 9 priority mode."""

    time_9_enabled = bit(3058, 15, writable=True)
    """Whether time slot 9 is active."""

    time_9_end = time_of_day(3059, writable=True)
    """Time slot 9 end."""

    ems_discharging_stop_soc_on_grid = integer(3067, signed=False, writable=in_range(10, 100))
    """Ems Discharging Stop Soc On Grid."""

    battery_type = option(3070, {0: "Lithium", 1: "Lead Acid", 2: "Other"})
    """Battery Type."""

    eps_switch = option(3079, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Eps Switch."""

    eps_set_voltage = option(3080, {0: "230", 1: "208", 2: "240"})
    """EPS Set Voltage."""

    eps_set_frequency = option(3081, {0: "50", 1: "60"})
    """EPS Set Frequency."""

    bms_1_serialnumber = string(3087, 8)
    """BMS 1 Serial Number."""

    bms_monitoring_version = string(3096, 2)
    """Bms Monitoring Version."""

    peak_shaving_enable = option(3306, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Peak Shaving Enable."""

    peak_import_limit = gauge(3307, 0.1, signed=False, writable=in_range(0, 100))
    """Peak Import Limit."""

    peak_export_limit = gauge(3308, 0.1, signed=False, writable=in_range(0, 100))
    """Peak Export Limit."""

    reserved_soc_peak_shaving_enable = option(3309, {0: "Disabled", 1: "Enabled"}, writable=True)
    """Reserved Soc Peak Shaving Enable."""

    reserved_soc_peak_shaving = integer(3310, signed=False, writable=in_range(0, 100))
    """Reserved Soc Peak Shaving."""

    max_charge_power_from_grid = gauge(3311, 0.1, signed=False, writable=in_range(0, 100))
    """Max Charge Power From Grid."""

    charge_stop_soc_from_grid = integer(3312, signed=False, writable=in_range(0, 100))
    """Charge Stop Soc From Grid."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "serialnumber": Variant.GEN4,
        "ems_discharging_rate": Variant.GEN4 | Variant.HYBRID,
        "ems_discharging_stop_soc": Variant.GEN4 | Variant.HYBRID,
        "time_1_begin": Variant.GEN4 | Variant.HYBRID,
        "time_1_mode": Variant.GEN4 | Variant.HYBRID,
        "time_1_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_1_end": Variant.GEN4 | Variant.HYBRID,
        "time_2_begin": Variant.GEN4 | Variant.HYBRID,
        "time_2_mode": Variant.GEN4 | Variant.HYBRID,
        "time_2_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_2_end": Variant.GEN4 | Variant.HYBRID,
        "time_3_begin": Variant.GEN4 | Variant.HYBRID,
        "time_3_mode": Variant.GEN4 | Variant.HYBRID,
        "time_3_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_3_end": Variant.GEN4 | Variant.HYBRID,
        "time_4_begin": Variant.GEN4 | Variant.HYBRID,
        "time_4_mode": Variant.GEN4 | Variant.HYBRID,
        "time_4_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_4_end": Variant.GEN4 | Variant.HYBRID,
        "ems_charging_rate": Variant.GEN4 | Variant.HYBRID,
        "ems_charging_stop_soc": Variant.GEN4 | Variant.AC | Variant.HYBRID,
        "charger_switch": Variant.GEN4 | Variant.AC | Variant.HYBRID,
        "time_5_begin": Variant.GEN4 | Variant.HYBRID,
        "time_5_mode": Variant.GEN4 | Variant.HYBRID,
        "time_5_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_5_end": Variant.GEN4 | Variant.HYBRID,
        "time_6_begin": Variant.GEN4 | Variant.HYBRID,
        "time_6_mode": Variant.GEN4 | Variant.HYBRID,
        "time_6_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_6_end": Variant.GEN4 | Variant.HYBRID,
        "time_7_begin": Variant.GEN4 | Variant.HYBRID,
        "time_7_mode": Variant.GEN4 | Variant.HYBRID,
        "time_7_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_7_end": Variant.GEN4 | Variant.HYBRID,
        "time_8_begin": Variant.GEN4 | Variant.HYBRID,
        "time_8_mode": Variant.GEN4 | Variant.HYBRID,
        "time_8_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_8_end": Variant.GEN4 | Variant.HYBRID,
        "time_9_begin": Variant.GEN4 | Variant.HYBRID,
        "time_9_mode": Variant.GEN4 | Variant.HYBRID,
        "time_9_enabled": Variant.GEN4 | Variant.HYBRID,
        "time_9_end": Variant.GEN4 | Variant.HYBRID,
        "ems_discharging_stop_soc_on_grid": Variant.GEN4 | Variant.HYBRID,
        "battery_type": Variant.GEN4 | Variant.AC | Variant.HYBRID,
        "eps_switch": Variant.GEN4 | Variant.AC | Variant.HYBRID | Variant.EPS,
        "eps_set_voltage": Variant.GEN4 | Variant.AC | Variant.HYBRID | Variant.EPS,
        "eps_set_frequency": Variant.GEN4 | Variant.AC | Variant.HYBRID | Variant.EPS,
        "bms_1_serialnumber": Variant.GEN4 | Variant.HYBRID,
        "bms_monitoring_version": Variant.GEN4 | Variant.HYBRID,
        "peak_shaving_enable": Variant.GEN4 | Variant.HYBRID,
        "peak_import_limit": Variant.GEN4 | Variant.HYBRID,
        "peak_export_limit": Variant.GEN4 | Variant.HYBRID,
        "reserved_soc_peak_shaving_enable": Variant.GEN4 | Variant.HYBRID,
        "reserved_soc_peak_shaving": Variant.GEN4 | Variant.HYBRID,
        "max_charge_power_from_grid": Variant.GEN4 | Variant.HYBRID,
        "charge_stop_soc_from_grid": Variant.GEN4 | Variant.HYBRID,
    }


class Gen4BatterySettings(GrowattComponent):
    """APX battery pack identity."""

    bms_1_monitoring_version = string(5011, 2)
    """BMS 1 Monitoring Version."""

    bms_2_serialnumber = string(5042, 8)
    """BMS 2 Serial Number."""

    bms_2_monitoring_version = string(5051, 2)
    """BMS 2 Monitoring Version."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "bms_1_monitoring_version": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_monitoring_version": Variant.GEN4 | Variant.HYBRID | Variant.APX,
    }


class Gen4BatteryModuleSettings(GrowattComponent):
    """APX battery per-module identity.

    Split from the pack registers above: the module banks are separate islands
    at a stride of 40, and a pack with fewer modules than the map declares
    refuses the ones it does not have.
    """

    bms_1_module_1_serialnumber = string(5400, 8)
    """BMS 1 Module 1 Serial Number."""

    bms_1_module_2_serialnumber = string(5440, 8)
    """BMS 1 Module 2 Serial Number."""

    bms_1_module_3_serialnumber = string(5480, 8)
    """BMS 1 Module 3 Serial Number."""

    bms_1_module_4_serialnumber = string(5520, 8)
    """BMS 1 Module 4 Serial Number."""

    bms_1_module_5_serialnumber = string(5560, 8)
    """BMS 1 Module 5 Serial Number."""

    bms_1_module_6_serialnumber = string(5600, 8)
    """BMS 1 Module 6 Serial Number."""

    bms_2_module_1_serialnumber = string(5640, 8)
    """BMS 2 Module 1 Serial Number."""

    bms_2_module_2_serialnumber = string(5680, 8)
    """BMS 2 Module 2 Serial Number."""

    bms_2_module_3_serialnumber = string(5720, 8)
    """BMS 2 Module 3 Serial Number."""

    bms_2_module_4_serialnumber = string(5760, 8)
    """BMS 2 Module 4 Serial Number."""

    bms_2_module_5_serialnumber = string(5800, 8)
    """BMS 2 Module 5 Serial Number."""

    bms_2_module_6_serialnumber = string(5840, 8)
    """BMS 2 Module 6 Serial Number."""

    bms_1_module_1_status = option(5880, MODULE_STATUS)
    """BMS 1 Module 1 Status."""

    bms_1_module_1_soh = integer(5882, signed=False)
    """BMS 1 Module 1 SoH."""

    bms_1_module_1_volt = gauge(5883, 0.1, signed=False, unit="V")
    """BMS 1 Module 1 Volt."""

    bms_1_module_1_combined_current = bms_current(5884)
    """BMS 1 Module 1 Combined Current."""

    bms_1_module_1_combined_power = bms_power(5885)
    """BMS 1 Module 1 Combined Power."""

    bms_1_module_1_toe = gauge(5887, 0.1, signed=False, unit="kWh")
    """BMS 1 Module 1 Total Output Energy."""

    bms_1_module_1_max_cell_temp = gauge(5890, 0.1, signed=False, unit="°C")
    """BMS 1 Module 1 Max Cell Temp."""

    bms_1_module_1_min_cell_temp = gauge(5891, 0.1, signed=False, unit="°C")
    """BMS 1 Module 1 Min Cell Temp."""

    bms_1_module_1_warning_text = option(5898, MODULE_WARNING)
    """BMS 1 Module 1 Warning Text."""

    bms_1_module_1_charge_cycles = integer(5908, signed=False)
    """BMS 1 Module 1 Charge Cycles."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "bms_1_module_1_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_serialnumber": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_max_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_min_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_1_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
    }


class Gen4VppSettings(GrowattComponent):
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


class Gen4Status(GrowattComponent):
    """Live measurements (input registers)."""

    register_space = "input"

    pv_power_total = uint32(1, scale=0.1, unit="W")
    """PV Power Total."""

    output_power = int32(35, scale=0.1, unit="W")
    """Output Power."""

    total_work_time_hours = uint32(57, scale=0.00013889, unit="h")
    """Total Work Time Hours."""

    inverter_fault_maincode = integer(105, signed=False)
    """Inverter Fault Maincode."""

    inverter_fault_subcode = integer(107, signed=False)
    """Inverter Fault Subcode."""

    inverter_warning_subcode = integer(111, signed=False)
    """Inverter Warning Subcode."""

    inverter_warning_maincode = integer(112, signed=False)
    """Inverter Warning Maincode."""

    priority = option(118, {0: "Load First", 1: "Battery First", 2: "Grid First"})
    """Priority."""

    pv_isolation_resistance = integer(200, signed=False, unit="kΩ")
    """PV Isolation Resistance."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "pv_power_total": Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "output_power": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "total_work_time_hours": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "inverter_fault_maincode": Variant.GEN4,
        "inverter_fault_subcode": Variant.GEN4,
        "inverter_warning_subcode": Variant.GEN4,
        "inverter_warning_maincode": Variant.GEN4,
        "priority": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
        "pv_isolation_resistance": Variant.GEN2 | Variant.GEN3 | Variant.GEN4,
    }


class Gen4HybridStatus(GrowattComponent):
    """Hybrid inverter, battery and backup measurements."""

    register_space = "input"

    run_mode = packed_option(3000, 0, 8, RUN_MODE)
    """Operating mode (low byte of the status word)."""

    inverter_state = packed_option(3000, 8, 8, INVERTER_STATE)
    """Inverter state (high byte of the status word)."""

    total_pv_power = uint32(3001, scale=0.1, unit="W")
    """Total PV Power."""

    pv_voltage_1 = gauge(3003, 0.1, signed=False, unit="V")
    """PV Voltage 1."""

    pv_current_1 = gauge(3004, 0.1, signed=False, unit="A")
    """PV Current 1."""

    pv_power_1 = uint32(3005, scale=0.1, unit="W")
    """PV Power 1."""

    pv_voltage_2 = gauge(3007, 0.1, signed=False, unit="V")
    """PV Voltage 2."""

    pv_current_2 = gauge(3008, 0.1, signed=False, unit="A")
    """PV Current 2."""

    pv_power_2 = uint32(3009, scale=0.1, unit="W")
    """PV Power 2."""

    pv_voltage_3 = gauge(3011, 0.1, signed=False, unit="V")
    """PV Voltage 3."""

    pv_current_3 = gauge(3012, 0.1, signed=False, unit="A")
    """PV Current 3."""

    pv_power_3 = uint32(3013, scale=0.1, unit="W")
    """PV Power 3."""

    pv_voltage_4 = gauge(3015, 0.1, signed=False, unit="V")
    """PV Voltage 4."""

    pv_current_4 = gauge(3016, 0.1, signed=False, unit="A")
    """PV Current 4."""

    pv_power_4 = uint32(3017, scale=0.1, unit="W")
    """PV Power 4."""

    grid_power = int32(3023, scale=0.1, unit="W")
    """Grid Power."""

    total_grid_power = int32(3023, scale=0.1, unit="W")
    """Total Grid Power."""

    grid_frequency = gauge(3025, 0.01, signed=False, unit="Hz")
    """Grid Frequency."""

    inverter_voltage = gauge(3026, 0.1, signed=False, unit="V")
    """Grid Voltage."""

    grid_voltage_l1 = gauge(3026, 0.1, signed=False, unit="V")
    """Grid Voltage L1."""

    grid_current = gauge(3027, 0.1, signed=True, unit="A")
    """Grid Current."""

    grid_current_l1 = gauge(3027, 0.1, signed=True, unit="A")
    """Grid Current L1."""

    grid_power_va = uint32(3028, scale=0.1, unit="VA")
    """Grid Power VA."""

    grid_power_l1 = uint32(3028, scale=0.1, unit="VA")
    """Grid Power L1."""

    grid_voltage_l2 = gauge(3030, 0.1, signed=False, unit="V")
    """Grid Voltage L2."""

    grid_current_l2 = gauge(3031, 0.1, signed=True, unit="A")
    """Grid Current L2."""

    grid_power_l2 = uint32(3032, scale=0.1, unit="VA")
    """Grid Power L2."""

    grid_voltage_l3 = gauge(3034, 0.1, signed=False, unit="V")
    """Grid Voltage L3."""

    grid_current_l3 = gauge(3035, 0.1, signed=True, unit="A")
    """Grid Current L3."""

    grid_power_l3 = uint32(3036, scale=0.1, unit="VA")
    """Grid Power L3."""

    total_forward_power = uint32(3041, scale=0.1, unit="W")
    """Total Import Power."""

    total_reverse_power = uint32(3043, scale=0.1, unit="W")
    """Total Export Power."""

    total_load_power = uint32(3045, scale=0.1, unit="W")
    """Total Load Power."""

    today_s_power_generation = uint32(3049, scale=0.1, unit="kWh")
    """Today's Power Generation."""

    total_power_generation = uint32(3051, scale=0.1, unit="kWh")
    """Total Power Generation."""

    total_solar_energy = uint32(3053, scale=0.1, unit="kWh")
    """Total Solar Energy."""

    today_s_pv1_solar_energy = uint32(3055, scale=0.1, unit="kWh")
    """Today's PV1 Solar Energy."""

    total_pv1_solar_energy = uint32(3057, scale=0.1, unit="kWh")
    """Total PV1 Solar Energy."""

    today_s_pv2_solar_energy = uint32(3059, scale=0.1, unit="kWh")
    """Today's PV2 Solar Energy."""

    total_pv2_solar_energy = uint32(3061, scale=0.1, unit="kWh")
    """Total PV2 Solar Energy."""

    today_s_pv3_solar_energy = uint32(3063, scale=0.1, unit="kWh")
    """Today's PV3 Solar Energy."""

    total_pv3_solar_energy = uint32(3065, scale=0.1, unit="kWh")
    """Total PV3 Solar Energy."""

    today_s_grid_import = uint32(3067, scale=0.1, unit="kWh")
    """Today's Grid Import."""

    total_grid_import = uint32(3069, scale=0.1, unit="kWh")
    """Total Grid Import."""

    today_s_grid_export = uint32(3071, scale=0.1, unit="kWh")
    """Today's Grid Export."""

    total_grid_export = uint32(3073, scale=0.1, unit="kWh")
    """Total Grid Export."""

    today_s_yield = uint32(3075, scale=0.1, unit="kWh")
    """Today's Load Energy."""

    total_yield = uint32(3077, scale=0.1, unit="kWh")
    """Total Load Energy."""

    today_s_pv4_solar_energy = uint32(3079, scale=0.1, unit="kWh")
    """Today's PV4 Solar Energy."""

    total_pv4_solar_energy = uint32(3081, scale=0.1, unit="kWh")
    """Total PV4 Solar Energy."""

    today_s_solar_energy = uint32(3083, scale=0.1, unit="kWh")
    """Today's Solar Energy."""

    inverter_temperature = gauge(3093, 0.1, signed=False, unit="°C")
    """Inverter Temperature."""

    ipm_inverter_temperature = gauge(3094, 0.1, signed=False, unit="°C")
    """IPM Inverter Temperature."""

    boost_temperature = gauge(3095, 0.1, signed=False, unit="°C")
    """Boost Temperature."""

    communication_board_temperature = gauge(3097, 0.1, signed=False, unit="°C")
    """Communication Board Temperature."""

    bmss_connceted = option(
        3118,
        {
            0: "No BMS Connected",
            1: "BMS 1 Connected",
            2: "BMS 2 Connected",
            3: "BMS 1 & 2 Connected",
        },
    )
    """BMS's Connected."""

    today_s_battery_output_energy = uint32(3125, scale=0.1, unit="kWh")
    """Today's Battery Output Energy."""

    total_battery_output_energy = uint32(3127, scale=0.1, unit="kWh")
    """Total Battery Output Energy."""

    today_s_battery_input_energy = uint32(3129, scale=0.1, unit="kWh")
    """Today's Battery Input Energy."""

    total_battery_input_energy = uint32(3131, scale=0.1, unit="kWh")
    """Total Battery Input Energy."""

    work_mode_priority = option(3144, {0: "Load First", 1: "Battery First", 2: "Grid First"})
    """Work Mode - Priority."""

    eps_frequency = gauge(3145, 0.01, signed=False, unit="Hz")
    """EPS Frequency."""

    eps_voltage = gauge(3146, 0.1, signed=False, unit="V")
    """EPS Voltage."""

    eps_voltage_l1 = gauge(3146, 0.1, signed=False, unit="V")
    """EPS Voltage L1."""

    eps_current = gauge(3147, 0.1, signed=False, unit="A")
    """EPS Current."""

    eps_current_l1 = gauge(3147, 0.1, signed=False, unit="A")
    """EPS Current L1."""

    eps_power = uint32(3148, scale=0.1, unit="VA")
    """EPS Power."""

    eps_power_l1 = uint32(3148, scale=0.1, unit="VA")
    """EPS Power L1."""

    eps_voltage_l2 = gauge(3150, 0.1, signed=False, unit="V")
    """EPS Voltage L2."""

    eps_current_l2 = gauge(3151, 0.1, signed=False, unit="A")
    """EPS Current L2."""

    eps_power_l2 = uint32(3152, scale=0.1, unit="VA")
    """EPS Power L2."""

    eps_voltage_l3 = gauge(3154, 0.1, signed=False, unit="V")
    """EPS Voltage L3."""

    eps_current_l3 = gauge(3155, 0.1, signed=False, unit="A")
    """EPS Current L3."""

    eps_power_l3 = uint32(3156, scale=0.1, unit="VA")
    """EPS Power L3."""

    eps_total_power = uint32(3158, scale=0.1, unit="VA")
    """EPS Total Power."""

    eps_loading = gauge(3160, 0.1, signed=False)
    """EPS Loading."""

    battery_voltage = integer(3169, signed=False, unit="V")
    """Battery Voltage."""

    battery_current = gauge(3170, 0.1, signed=True, unit="A")
    """Battery Current."""

    battery_soc = integer(3171, signed=False)
    """Battery SOC."""

    battery_discharge_power = uint32(3178, scale=0.1, unit="W")
    """Battery Discharge Power."""

    battery_charge_power = uint32(3180, scale=0.1, unit="W")
    """Battery Charge Power."""

    backup_status = option(3282, {0: "Backup Offgrid", 1: "Backup Ongrid", 2: "Backup Generator"})
    """Backup Status."""

    bms_1_charge_power = uint32(3331, scale=0.1, unit="W")
    """BMS 1 Charge Power."""

    bms_1_discharge_power = uint32(3334, scale=0.1, unit="W")
    """BMS 1 Discharge Power."""

    bms_2_charge_power = uint32(3336, scale=0.1, unit="W")
    """BMS 2 Charge Power."""

    bms_2_discharge_power = uint32(3338, scale=0.1, unit="W")
    """BMS 2 Discharge Power."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "run_mode": Variant.GEN4,
        "inverter_state": Variant.GEN4,
        "total_pv_power": Variant.GEN4,
        "pv_voltage_1": Variant.GEN4,
        "pv_current_1": Variant.GEN4,
        "pv_power_1": Variant.GEN4,
        "pv_voltage_2": Variant.GEN4,
        "pv_current_2": Variant.GEN4,
        "pv_power_2": Variant.GEN4,
        "pv_voltage_3": Variant.GEN4
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_current_3": Variant.GEN4
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_power_3": Variant.GEN4
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "pv_voltage_4": Variant.GEN4 | Variant.MPPT4,
        "pv_current_4": Variant.GEN4 | Variant.MPPT4,
        "pv_power_4": Variant.GEN4 | Variant.MPPT4,
        "grid_power": Variant.GEN4 | Variant.X1,
        "total_grid_power": Variant.GEN4 | Variant.X3,
        "grid_frequency": Variant.GEN4,
        "inverter_voltage": Variant.GEN4 | Variant.X1,
        "grid_voltage_l1": Variant.GEN4 | Variant.X3,
        "grid_current": Variant.GEN4 | Variant.X1,
        "grid_current_l1": Variant.GEN4 | Variant.X3,
        "grid_power_va": Variant.GEN4 | Variant.X1,
        "grid_power_l1": Variant.GEN4 | Variant.X3,
        "grid_voltage_l2": Variant.GEN4 | Variant.X3,
        "grid_current_l2": Variant.GEN4 | Variant.X3,
        "grid_power_l2": Variant.GEN4 | Variant.X3,
        "grid_voltage_l3": Variant.GEN4 | Variant.X3,
        "grid_current_l3": Variant.GEN4 | Variant.X3,
        "grid_power_l3": Variant.GEN4 | Variant.X3,
        "total_forward_power": Variant.GEN4,
        "total_reverse_power": Variant.GEN4,
        "total_load_power": Variant.GEN4,
        "today_s_power_generation": Variant.GEN4,
        "total_power_generation": Variant.GEN4,
        "total_solar_energy": Variant.GEN4,
        "today_s_pv1_solar_energy": Variant.GEN4,
        "total_pv1_solar_energy": Variant.GEN4,
        "today_s_pv2_solar_energy": Variant.GEN4,
        "total_pv2_solar_energy": Variant.GEN4,
        "today_s_pv3_solar_energy": Variant.GEN4
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "total_pv3_solar_energy": Variant.GEN4
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT6
        | Variant.MPPT8
        | Variant.MPPT10,
        "today_s_grid_import": Variant.GEN4,
        "total_grid_import": Variant.GEN4,
        "today_s_grid_export": Variant.GEN4,
        "total_grid_export": Variant.GEN4,
        "today_s_yield": Variant.GEN4,
        "total_yield": Variant.GEN4,
        "today_s_pv4_solar_energy": Variant.GEN4 | Variant.MPPT4,
        "total_pv4_solar_energy": Variant.GEN4 | Variant.MPPT4,
        "today_s_solar_energy": Variant.GEN4,
        "inverter_temperature": Variant.GEN4,
        "ipm_inverter_temperature": Variant.GEN4,
        "boost_temperature": Variant.GEN4,
        "communication_board_temperature": Variant.GEN4,
        "bmss_connceted": Variant.GEN4 | Variant.HYBRID,
        "today_s_battery_output_energy": Variant.GEN4 | Variant.HYBRID,
        "total_battery_output_energy": Variant.GEN4 | Variant.HYBRID,
        "today_s_battery_input_energy": Variant.GEN4 | Variant.HYBRID,
        "total_battery_input_energy": Variant.GEN4 | Variant.HYBRID,
        "work_mode_priority": Variant.GEN4,
        "eps_frequency": Variant.GEN4 | Variant.EPS,
        "eps_voltage": Variant.GEN4 | Variant.X1 | Variant.EPS,
        "eps_voltage_l1": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_current": Variant.GEN4 | Variant.X1 | Variant.EPS,
        "eps_current_l1": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_power": Variant.GEN4 | Variant.X1 | Variant.EPS,
        "eps_power_l1": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_voltage_l2": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_current_l2": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_power_l2": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_voltage_l3": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_current_l3": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_power_l3": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_total_power": Variant.GEN4 | Variant.X3 | Variant.EPS,
        "eps_loading": Variant.GEN4 | Variant.EPS,
        "battery_voltage": Variant.GEN4 | Variant.HYBRID,
        "battery_current": Variant.GEN4 | Variant.HYBRID,
        "battery_soc": Variant.GEN4 | Variant.HYBRID,
        "battery_discharge_power": Variant.GEN4 | Variant.HYBRID,
        "battery_charge_power": Variant.GEN4 | Variant.HYBRID,
        "backup_status": Variant.GEN4,
        "bms_1_charge_power": Variant.GEN4 | Variant.HYBRID,
        "bms_1_discharge_power": Variant.GEN4 | Variant.HYBRID,
        "bms_2_charge_power": Variant.GEN4 | Variant.HYBRID,
        "bms_2_discharge_power": Variant.GEN4 | Variant.HYBRID,
    }


class Gen4BatteryStatus(GrowattComponent):
    """APX battery pack measurements."""

    register_space = "input"

    bms_1_temp_a = gauge(4019, 0.1, signed=False, unit="°C")
    """BMS 1 Temp A."""

    bms_1_temp_b = gauge(4020, 0.1, signed=False, unit="°C")
    """BMS 1 Temp B."""

    bms_1_module_count = integer(4041, signed=False)
    """BMS 1 Module Count."""

    bms_1_status = option(
        4055,
        {
            0: "Dormancy",
            1: "Charging",
            2: "Discharging",
            3: "Free",
            4: "Standby",
            5: "Soft start",
            6: "Fault",
            7: "Updating",
        },
    )
    """BMS 1 Status."""

    bms_1_awake_modules = gauge(4078, 0.02, signed=True)
    """BMS 1 Awake Modules."""

    bms_2_temp_a = gauge(4127, 0.1, signed=False, unit="°C")
    """BMS 2 Temp A."""

    bms_2_temp_b = gauge(4128, 0.1, signed=False, unit="°C")
    """BMS 2 Temp B."""

    bms_2_module_count = integer(4149, signed=False)
    """BMS 2 Module Count."""

    bms_2_status = option(
        4163,
        {
            0: "Dormancy",
            1: "Charging",
            2: "Discharging",
            3: "Free",
            4: "Standby",
            5: "Soft start",
            6: "Fault",
            7: "Updating",
        },
    )
    """BMS 2 Status."""

    bms_2_awake_modules = gauge(4186, 0.02, signed=True)
    """BMS 2 Awake Modules."""

    bms_1_toe = gauge(5769, 0.1, signed=False, unit="kWh")
    """BMS 1 Total Output Energy."""

    bms_1_soc = integer(5777, signed=False)
    """BMS 1 SoC."""

    bms_1_soh = integer(5778, signed=False)
    """BMS 1 SoH."""

    bms_2_toe = gauge(5869, 0.1, signed=False, unit="kWh")
    """BMS 2 Total Output Energy."""

    bms_2_soc = integer(5877, signed=False)
    """BMS 2 SoC."""

    bms_2_soh = integer(5878, signed=False)
    """BMS 2 SoH."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "bms_1_temp_a": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_temp_b": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_count": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_awake_modules": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_temp_a": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_temp_b": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_count": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_awake_modules": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
    }


class Gen4BatteryModuleStatus(GrowattComponent):
    """APX battery per-module measurements."""

    register_space = "input"

    bms_1_module_1_soc = bits(5081, 0, 8, unit="%")
    """Bms 1 Module 1 Soc."""

    bms_1_module_2_status = option(5120, MODULE_STATUS)
    """BMS 1 Module 2 Status."""

    bms_1_module_2_soc = bits(5121, 0, 8, unit="%")
    """Bms 1 Module 2 Soc."""

    bms_1_module_2_soh = integer(5122, signed=False)
    """BMS 1 Module 2 SoH."""

    bms_1_module_2_volt = gauge(5123, 0.1, signed=False, unit="V")
    """BMS 1 Module 2 Volt."""

    bms_1_module_2_combined_current = bms_current(5124)
    """BMS 1 Module 2 Combined Current."""

    bms_1_module_2_combined_power = bms_power(5125)
    """BMS 1 Module 2 Combined Power."""

    bms_1_module_2_toe = gauge(5127, 0.1, signed=False, unit="kWh")
    """BMS 1 Module 2 Total Output Energy."""

    bms_1_module_2_max_cell_temp = gauge(5130, 0.1, signed=False, unit="°C")
    """BMS 1 Module 2 Max Cell Temp."""

    bms_1_module_2_min_cell_temp = gauge(5131, 0.1, signed=False, unit="°C")
    """BMS 1 Module 2 Min Cell Temp."""

    bms_1_module_2_warning_text = option(5138, MODULE_WARNING)
    """BMS 1 Module 2 Warning Text."""

    bms_1_module_2_charge_cycles = integer(5148, signed=False)
    """BMS 1 Module 2 Charge Cycles."""

    bms_1_module_3_status = option(5160, MODULE_STATUS)
    """BMS 1 Module 3 Status."""

    bms_1_module_3_soc = bits(5161, 0, 8, unit="%")
    """Bms 1 Module 3 Soc."""

    bms_1_module_3_soh = integer(5162, signed=False)
    """BMS 1 Module 3 SoH."""

    bms_1_module_3_volt = gauge(5163, 0.1, signed=False, unit="V")
    """BMS 1 Module 3 Volt."""

    bms_1_module_3_combined_current = bms_current(5164)
    """BMS 1 Module 3 Combined Current."""

    bms_1_module_3_combined_power = bms_power(5165)
    """BMS 1 Module 3 Combined Power."""

    bms_1_module_3_toe = gauge(5167, 0.1, signed=False, unit="kWh")
    """BMS 1 Module 3 Total Output Energy."""

    bms_1_module_3_max_cell_temp = gauge(5170, 0.1, signed=False, unit="°C")
    """BMS 1 Module 3 Max Cell Temp."""

    bms_1_module_3_min_cell_temp = gauge(5171, 0.1, signed=False, unit="°C")
    """BMS 1 Module 3 Min Cell Temp."""

    bms_1_module_3_warning_text = option(5178, MODULE_WARNING)
    """BMS 1 Module 3 Warning Text."""

    bms_1_module_3_charge_cycles = integer(5188, signed=False)
    """BMS 1 Module 3 Charge Cycles."""

    bms_1_module_4_status = option(5200, MODULE_STATUS)
    """BMS 1 Module 4 Status."""

    bms_1_module_4_soc = bits(5201, 0, 8, unit="%")
    """Bms 1 Module 4 Soc."""

    bms_1_module_4_soh = integer(5202, signed=False)
    """BMS 1 Module 4 SoH."""

    bms_1_module_4_volt = gauge(5203, 0.1, signed=False, unit="V")
    """BMS 1 Module 4 Volt."""

    bms_1_module_4_combined_current = bms_current(5204)
    """BMS 1 Module 4 Combined Current."""

    bms_1_module_4_combined_power = bms_power(5205)
    """BMS 1 Module 4 Combined Power."""

    bms_1_module_4_toe = gauge(5207, 0.1, signed=False, unit="kWh")
    """BMS 1 Module 4 Total Output Energy."""

    bms_1_module_4_max_cell_temp = gauge(5210, 0.1, signed=False, unit="°C")
    """BMS 1 Module 4 Max Cell Temp."""

    bms_1_module_4_min_cell_temp = gauge(5211, 0.1, signed=False, unit="°C")
    """BMS 1 Module 4 Min Cell Temp."""

    bms_1_module_4_warning_text = option(5218, MODULE_WARNING)
    """BMS 1 Module 4 Warning Text."""

    bms_1_module_4_charge_cycles = integer(5228, signed=False)
    """BMS 1 Module 4 Charge Cycles."""

    bms_1_module_5_status = option(5240, MODULE_STATUS)
    """BMS 1 Module 5 Status."""

    bms_1_module_5_soc = bits(5241, 0, 8, unit="%")
    """Bms 1 Module 5 Soc."""

    bms_1_module_5_soh = integer(5242, signed=False)
    """BMS 1 Module 5 SoH."""

    bms_1_module_5_volt = gauge(5243, 0.1, signed=False, unit="V")
    """BMS 1 Module 5 Volt."""

    bms_1_module_5_combined_current = bms_current(5244)
    """BMS 1 Module 5 Combined Current."""

    bms_1_module_5_combined_power = bms_power(5245)
    """BMS 1 Module 5 Combined Power."""

    bms_1_module_5_toe = gauge(5247, 0.1, signed=False, unit="kWh")
    """BMS 1 Module 5 Total Output Energy."""

    bms_1_module_5_max_cell_temp = gauge(5250, 0.1, signed=False, unit="°C")
    """BMS 1 Module 5 Max Cell Temp."""

    bms_1_module_5_min_cell_temp = gauge(5251, 0.1, signed=False, unit="°C")
    """BMS 1 Module 5 Min Cell Temp."""

    bms_1_module_5_warning_text = option(5258, MODULE_WARNING)
    """BMS 1 Module 5 Warning Text."""

    bms_1_module_5_charge_cycles = integer(5268, signed=False)
    """BMS 1 Module 5 Charge Cycles."""

    bms_1_module_6_status = option(5280, MODULE_STATUS)
    """BMS 1 Module 6 Status."""

    bms_1_module_6_soc = bits(5281, 0, 8, unit="%")
    """Bms 1 Module 6 Soc."""

    bms_1_module_6_soh = integer(5282, signed=False)
    """BMS 1 Module 6 SoH."""

    bms_1_module_6_volt = gauge(5283, 0.1, signed=False, unit="V")
    """BMS 1 Module 6 Volt."""

    bms_1_module_6_combined_current = bms_current(5284)
    """BMS 1 Module 6 Combined Current."""

    bms_1_module_6_combined_power = bms_power(5285)
    """BMS 1 Module 6 Combined Power."""

    bms_1_module_6_toe = gauge(5287, 0.1, signed=False, unit="kWh")
    """BMS 1 Module 6 Total Output Energy."""

    bms_1_module_6_max_cell_temp = gauge(5290, 0.1, signed=False, unit="°C")
    """BMS 1 Module 6 Max Cell Temp."""

    bms_1_module_6_min_cell_temp = gauge(5291, 0.1, signed=False, unit="°C")
    """BMS 1 Module 6 Min Cell Temp."""

    bms_1_module_6_warning_text = option(5298, MODULE_WARNING)
    """BMS 1 Module 6 Warning Text."""

    bms_1_module_6_charge_cycles = integer(5308, signed=False)
    """BMS 1 Module 6 Charge Cycles."""

    bms_2_module_1_status = option(5320, MODULE_STATUS)
    """BMS 2 Module 1 Status."""

    bms_2_module_1_soc = bits(5321, 0, 8, unit="%")
    """Bms 2 Module 1 Soc."""

    bms_2_module_1_soh = integer(5322, signed=False)
    """BMS 2 Module 1 SoH."""

    bms_2_module_1_volt = gauge(5323, 0.1, signed=False, unit="V")
    """BMS 2 Module 1 Volt."""

    bms_2_module_1_combined_current = bms_current(5324)
    """BMS 2 Module 1 Combined Current."""

    bms_2_module_1_combined_power = bms_power(5325)
    """BMS 2 Module 1 Combined Power."""

    bms_2_module_1_toe = gauge(5327, 0.1, signed=False, unit="kWh")
    """BMS 2 Module 1 Total Output Energy."""

    bms_2_module_1_max_cell_temp = gauge(5330, 0.1, signed=False, unit="°C")
    """BMS 2 Module 1 Max Cell Temp."""

    bms_2_module_1_min_cell_temp = gauge(5331, 0.1, signed=False, unit="°C")
    """BMS 2 Module 1 Min Cell Temp."""

    bms_2_module_1_warning_text = option(5338, MODULE_WARNING)
    """BMS 2 Module 1 Warning Text."""

    bms_2_module_1_charge_cycles = integer(5348, signed=False)
    """BMS 2 Module 1 Charge Cycles."""

    bms_2_module_2_status = option(5360, MODULE_STATUS)
    """BMS 2 Module 2 Status."""

    bms_2_module_2_soc = bits(5361, 0, 8, unit="%")
    """Bms 2 Module 2 Soc."""

    bms_2_module_2_soh = integer(5362, signed=False)
    """BMS 2 Module 2 SoH."""

    bms_2_module_2_volt = gauge(5363, 0.1, signed=False, unit="V")
    """BMS 2 Module 2 Volt."""

    bms_2_module_2_combined_current = bms_current(5364)
    """BMS 2 Module 2 Combined Current."""

    bms_2_module_2_combined_power = bms_power(5365)
    """BMS 2 Module 2 Combined Power."""

    bms_2_module_2_toe = gauge(5367, 0.1, signed=False, unit="kWh")
    """BMS 2 Module 2 Total Output Energy."""

    bms_2_module_2_warning_text = option(5378, MODULE_WARNING)
    """BMS 2 Module 2 Warning Text."""

    bms_2_module_2_charge_cycles = integer(5388, signed=False)
    """BMS 2 Module 2 Charge Cycles."""

    bms_2_module_3_status = option(5400, MODULE_STATUS)
    """BMS 2 Module 3 Status."""

    bms_2_module_3_soc = bits(5401, 0, 8, unit="%")
    """Bms 2 Module 3 Soc."""

    bms_2_module_3_soh = integer(5402, signed=False)
    """BMS 2 Module 3 SoH."""

    bms_2_module_3_volt = gauge(5403, 0.1, signed=False, unit="V")
    """BMS 2 Module 3 Volt."""

    bms_2_module_3_combined_current = bms_current(5404)
    """BMS 2 Module 3 Combined Current."""

    bms_2_module_3_combined_power = bms_power(5405)
    """BMS 2 Module 3 Combined Power."""

    bms_2_module_3_toe = gauge(5407, 0.1, signed=False, unit="kWh")
    """BMS 2 Module 3 Total Output Energy."""

    bms_2_module_3_warning_text = option(5418, MODULE_WARNING)
    """BMS 2 Module 3 Warning Text."""

    bms_2_module_3_charge_cycles = integer(5428, signed=False)
    """BMS 2 Module 3 Charge Cycles."""

    bms_2_module_4_status = option(5440, MODULE_STATUS)
    """BMS 2 Module 4 Status."""

    bms_2_module_4_soc = bits(5441, 0, 8, unit="%")
    """Bms 2 Module 4 Soc."""

    bms_2_module_4_soh = integer(5442, signed=False)
    """BMS 2 Module 4 SoH."""

    bms_2_module_4_volt = gauge(5443, 0.1, signed=False, unit="V")
    """BMS 2 Module 4 Volt."""

    bms_2_module_4_combined_current = bms_current(5444)
    """BMS 2 Module 4 Combined Current."""

    bms_2_module_4_combined_power = bms_power(5445)
    """BMS 2 Module 4 Combined Power."""

    bms_2_module_4_toe = gauge(5447, 0.1, signed=False, unit="kWh")
    """BMS 2 Module 4 Total Output Energy."""

    bms_2_module_4_warning_text = option(5458, MODULE_WARNING)
    """BMS 2 Module 4 Warning Text."""

    bms_2_module_4_charge_cycles = integer(5468, signed=False)
    """BMS 2 Module 4 Charge Cycles."""

    bms_2_module_5_status = option(5480, MODULE_STATUS)
    """BMS 2 Module 5 Status."""

    bms_2_module_5_soc = bits(5481, 0, 8, unit="%")
    """Bms 2 Module 5 Soc."""

    bms_2_module_5_soh = integer(5482, signed=False)
    """BMS 2 Module 5 SoH."""

    bms_2_module_5_volt = gauge(5483, 0.1, signed=False, unit="V")
    """BMS 2 Module 5 Volt."""

    bms_2_module_5_combined_current = bms_current(5484)
    """BMS 2 Module 5 Combined Current."""

    bms_2_module_5_combined_power = bms_power(5485)
    """BMS 2 Module 5 Combined Power."""

    bms_2_module_5_toe = gauge(5487, 0.1, signed=False, unit="kWh")
    """BMS 2 Module 5 Total Output Energy."""

    bms_2_module_5_warning_text = option(5498, MODULE_WARNING)
    """BMS 2 Module 5 Warning Text."""

    bms_2_module_5_charge_cycles = integer(5508, signed=False)
    """BMS 2 Module 5 Charge Cycles."""

    bms_2_module_6_status = option(5520, MODULE_STATUS)
    """BMS 2 Module 6 Status."""

    bms_2_module_6_soc = bits(5521, 0, 8, unit="%")
    """Bms 2 Module 6 Soc."""

    bms_2_module_6_soh = integer(5522, signed=False)
    """BMS 2 Module 6 SoH."""

    bms_2_module_6_volt = gauge(5523, 0.1, signed=False, unit="V")
    """BMS 2 Module 6 Volt."""

    bms_2_module_6_combined_current = bms_current(5524)
    """BMS 2 Module 6 Combined Current."""

    bms_2_module_6_combined_power = bms_power(5525)
    """BMS 2 Module 6 Combined Power."""

    bms_2_module_6_toe = gauge(5527, 0.1, signed=False, unit="kWh")
    """BMS 2 Module 6 Total Output Energy."""

    bms_2_module_6_warning_text = option(5538, MODULE_WARNING)
    """BMS 2 Module 6 Warning Text."""

    bms_2_module_6_charge_cycles = integer(5548, signed=False)
    """BMS 2 Module 6 Charge Cycles."""

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {
        "bms_1_module_1_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_max_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_min_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_2_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_max_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_min_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_3_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_max_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_min_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_4_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_max_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_min_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_5_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_max_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_min_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_1_module_6_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_max_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_min_cell_temp": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_1_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_2_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_3_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_4_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_5_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_status": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_soc": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_soh": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_volt": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_combined_current": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_combined_power": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_toe": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_warning_text": Variant.GEN4 | Variant.HYBRID | Variant.APX,
        "bms_2_module_6_charge_cycles": Variant.GEN4 | Variant.HYBRID | Variant.APX,
    }
