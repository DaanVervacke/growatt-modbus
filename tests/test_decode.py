"""Decoding a seeded device, one generation at a time.

Values are the raw register words a real inverter would send; the assertions are
the engineering values the register map says they mean.
"""

from __future__ import annotations

from datetime import time

from growatt_modbus import Variant, build


async def test_spf_decodes_its_measurement_block(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[1] = 3251  # PV1 voltage, 0.1 V
    mock_modbus_unit.input[3] = [0x0000, 0x61A8]  # PV1 power u32, 0.1 W -> 2500.0
    mock_modbus_unit.input[18] = 87  # battery SOC, %
    mock_modbus_unit.input[25] = 412  # inverter temperature, 0.1 °C
    mock_modbus_unit.holding[0] = 1  # inverter switch
    mock_modbus_unit.holding[18] = 2  # output voltage type

    inverter = build(mock_modbus_unit, Variant.SPF | Variant.HYBRID | Variant.X1)
    await inverter.async_update()

    assert inverter.status.pv_voltage_1 == 325.1
    assert inverter.status.pv_power_1 == 2500.0
    assert inverter.status.battery_soc == 87
    assert inverter.status.inverter_temperature == 41.2
    assert inverter.settings.inverter_switch == "Inverter On"
    assert inverter.settings.output_voltage_type == "240"


async def test_spf_energy_counters_are_signed(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # total_solar_energy_pv2 is declared int32 upstream, so a negative
    # two's-complement word must not read as four billion kWh.
    mock_modbus_unit.input[54] = [0xFFFF, 0xFFFF]  # -1 raw, 0.1 scale
    inverter = build(mock_modbus_unit, Variant.SPF | Variant.HYBRID | Variant.X1)
    await inverter.async_update()
    assert inverter.status.total_solar_energy_pv2 == -0.1


async def test_gen4_decodes_status_and_its_packed_state_word(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # Input 3000 packs the inverter state in the high byte, run mode in the low.
    mock_modbus_unit.input[3000] = (5 << 8) | 1
    mock_modbus_unit.input[3005] = [0x0000, 0x2710]  # PV1 power -> 1000.0 W
    mock_modbus_unit.input[3093] = 355  # inverter temperature
    mock_modbus_unit.input[3171] = 64  # battery SOC

    inverter = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1)
    await inverter.async_update()

    assert inverter.hybrid_status is not None
    assert inverter.hybrid_status.run_mode == "Normal"
    assert inverter.hybrid_status.inverter_state == "PV Bat Online"
    assert inverter.hybrid_status.pv_power_1 == 1000.0
    assert inverter.hybrid_status.inverter_temperature == 35.5
    assert inverter.hybrid_status.battery_soc == 64


async def test_gen4_decodes_a_time_slot_out_of_one_register(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # Holding 3038: enabled (bit 15), Grid First (bit 14), start 06:30.
    mock_modbus_unit.holding[3038] = (1 << 15) | (1 << 14) | (6 << 8) | 30
    mock_modbus_unit.holding[3039] = (22 << 8) | 15  # slot end

    inverter = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1)
    await inverter.async_update()

    slots = inverter.hybrid_settings
    assert slots is not None
    assert slots.time_1_begin == time(6, 30)
    assert slots.time_1_end == time(22, 15)
    assert slots.time_1_mode == "Grid First"
    assert slots.time_1_enabled is True


async def test_gen3_decodes_storage_registers_and_schedule(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[1014] = 55  # battery SOC
    mock_modbus_unit.holding[1080] = (1 << 8) | 30  # grid-first slot 1 start 01:30
    mock_modbus_unit.holding[1081] = (5 << 8) | 45  # ... end 05:45
    mock_modbus_unit.holding[1090] = 80  # battery first charge rate, %

    inverter = build(mock_modbus_unit, Variant.GEN3 | Variant.HYBRID | Variant.X1)
    await inverter.async_update()

    assert inverter.storage_status is not None
    assert inverter.storage_status.battery_soc == 55
    settings = inverter.storage_settings
    assert settings is not None
    assert settings.grid_first_time_1_begin == time(1, 30)
    assert settings.grid_first_time_1_end == time(5, 45)
    assert settings.battery_first_charge_rate == 80


async def test_gen1_decodes_the_packed_module_version(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.holding[28] = [0x1234, 0x5678]
    inverter = build(mock_modbus_unit, Variant.GEN | Variant.PV | Variant.X1)
    await inverter.async_update()
    assert inverter.settings.inverter_module == "A1B2D3T4P5U6M7S8"


async def test_gen1_decodes_the_real_time_clock(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.holding[45] = [24, 6, 15, 13, 5, 30]
    inverter = build(mock_modbus_unit, Variant.GEN | Variant.PV | Variant.X1)
    await inverter.async_update()
    assert inverter.settings.rtc is not None
    assert inverter.settings.rtc.isoformat() == "2024-06-15T13:05:30"


async def test_gen2_keeps_both_temperature_declarations_apart(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # Upstream declares "inverter_temperature" twice for Gen2, at two registers.
    mock_modbus_unit.input[32] = 300
    mock_modbus_unit.input[93] = 400
    inverter = build(mock_modbus_unit, Variant.GEN2 | Variant.PV | Variant.X3)
    await inverter.async_update()
    assert inverter.status.inverter_temperature_alt == 30.0
    assert inverter.status.inverter_temperature == 40.0


async def test_gen3_keeps_the_battery_type_setting_and_report_apart(  # type: ignore[no-untyped-def]
    mock_modbus_unit,
) -> None:
    mock_modbus_unit.holding[1048] = 1  # the setting: Lead Acid
    mock_modbus_unit.input[119] = 1  # the report: Lithium (a different code map)
    inverter = build(mock_modbus_unit, Variant.GEN3 | Variant.HYBRID | Variant.X1)
    await inverter.async_update()
    assert inverter.storage_settings is not None
    assert inverter.storage_settings.battery_type == "Lead Acid"
    assert inverter.status.battery_type_reported == "Lithium"


async def test_apx_module_readings_decode_their_split_range(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[5120] = 2  # module status: charging
    mock_modbus_unit.input[5121] = (7 << 8) | 93  # SOC in the low byte
    mock_modbus_unit.input[5125] = 65536 - 900  # combined power, charging
    mock_modbus_unit.input[5124] = 1500  # combined current, discharging

    inverter = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1 | Variant.APX)
    await inverter.async_update()

    battery = inverter.battery_module_status
    assert battery is not None
    assert battery.bms_1_module_2_status == "Charging"
    assert battery.bms_1_module_2_soc == 93
    assert battery.bms_1_module_2_combined_power == -900
    assert battery.bms_1_module_2_combined_current == 150.0


async def test_an_unread_field_is_none(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, Variant.SPF | Variant.HYBRID | Variant.X1)
    assert inverter.status.pv_voltage_1 is None


async def test_a_field_this_variant_lacks_stays_none(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # PV4 exists only on a 4-MPPT Gen4; seeding its register changes nothing.
    mock_modbus_unit.input[3015] = 3000
    two_mppt = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1)
    await two_mppt.async_update()
    assert two_mppt.hybrid_status is not None
    assert two_mppt.hybrid_status.pv_voltage_4 is None

    four_mppt = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1 | Variant.MPPT4)
    await four_mppt.async_update()
    assert four_mppt.hybrid_status is not None
    assert four_mppt.hybrid_status.pv_voltage_4 == 300.0
