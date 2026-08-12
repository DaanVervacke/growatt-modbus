"""The readings the inverter does not report directly, composed from registers."""

from __future__ import annotations

import pytest

from growatt_modbus import Gen4Inverter, Variant, build

SPF = Variant.SPF | Variant.HYBRID | Variant.X1
GEN2 = Variant.GEN2 | Variant.PV | Variant.X3
GEN3 = Variant.GEN3 | Variant.HYBRID | Variant.X1
GEN4 = Variant.GEN4 | Variant.HYBRID | Variant.X1


async def test_spf_totals_its_two_pv_inputs(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[3] = [0, 10000]  # PV1 power, 0.1 W -> 1000.0
    mock_modbus_unit.input[5] = [0, 5000]  # PV2 power -> 500.0
    inverter = build(mock_modbus_unit, SPF)
    await inverter.async_update()
    assert inverter.pv_power_total == 1500.0


async def test_a_single_mppt_spf_totals_only_the_input_it_has(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[3] = [0, 10000]
    mock_modbus_unit.input[5] = [0, 5000]  # PV2's register, which this model lacks
    inverter = build(mock_modbus_unit, SPF, "KAM0000001")
    await inverter.async_update()
    assert inverter.pv_power_total == 1000.0


async def test_a_missing_reading_makes_the_total_unknown(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # Never polled: a partial total would under-report, so there is no total.
    inverter = build(mock_modbus_unit, SPF)
    assert inverter.pv_power_total is None


async def test_gen2_totals_todays_solar_over_its_strings(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[59] = [0, 150]  # PV1 today, 0.1 kWh -> 15.0
    mock_modbus_unit.input[63] = [0, 75]  # PV2 today -> 7.5
    inverter = build(mock_modbus_unit, GEN2)
    await inverter.async_update()
    assert inverter.today_s_solar_energy == 22.5


async def test_battery_power_combines_charge_and_discharge(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[3178] = [0, 12000]  # discharging, 0.1 W -> 1200.0
    mock_modbus_unit.input[3180] = [0, 2000]  # charging -> 200.0
    inverter = build(mock_modbus_unit, GEN4)
    await inverter.async_update()
    assert inverter.battery_combined_power == 1000.0


async def test_battery_power_is_negative_while_charging(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[3178] = [0, 0]
    mock_modbus_unit.input[3180] = [0, 8000]  # charging at 800 W
    inverter = build(mock_modbus_unit, GEN4)
    await inverter.async_update()
    assert inverter.battery_combined_power == -800.0


async def test_gen3_combines_its_own_battery_registers(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.input[1009] = [0, 9000]  # discharge -> 900.0
    mock_modbus_unit.input[1011] = [0, 1000]  # charge -> 100.0
    inverter = build(mock_modbus_unit, GEN3)
    await inverter.async_update()
    assert inverter.battery_combined_power == 800.0


class TestBatteryVoltageScaling:
    """The scale depends on which battery pack is fitted."""

    async def test_a_standard_pack_is_hundredths(self, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
        mock_modbus_unit.input[3169] = 5120
        inverter = build(mock_modbus_unit, GEN4)
        await inverter.async_update()
        assert inverter.battery_voltage == 51.2

    async def test_an_apx_hv_pack_is_tenths(self, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
        mock_modbus_unit.input[3169] = 5120
        mock_modbus_unit.holding[3096] = [0x5A45, 0x4341]  # "ZECA"
        inverter = build(mock_modbus_unit, GEN4)
        await inverter.async_update()
        assert inverter.hybrid_settings is not None
        assert inverter.hybrid_settings.bms_monitoring_version == "ZECA"
        assert inverter.battery_voltage == 512.0


async def test_three_phase_grid_power_is_summed(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    for address, raw in ((3028, 1000), (3032, 2000), (3036, 3000)):
        mock_modbus_unit.input[address] = [0, raw]
    inverter = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X3)
    await inverter.async_update()
    assert inverter.total_grid_power_va == 600.0


async def test_a_single_phase_inverter_has_no_three_phase_total(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, GEN4)
    await inverter.async_update()
    assert inverter.total_grid_power_va is None


class TestFaultAndWarningText:
    async def test_a_healthy_inverter_reports_normal(self, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
        inverter = build(mock_modbus_unit, GEN4)
        await inverter.async_update()
        assert inverter.inverter_fault_text == "Normal"
        assert inverter.inverter_warning_text == "Normal"

    async def test_a_known_code_pair_is_named(self, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
        mock_modbus_unit.input[105] = 408  # fault main code
        mock_modbus_unit.input[112] = 401  # warning main code
        inverter = build(mock_modbus_unit, GEN4)
        await inverter.async_update()
        assert inverter.inverter_fault_text == "Over-temperature"
        assert inverter.inverter_warning_text == "Meter abnormal"

    async def test_an_unknown_code_pair_still_reports_the_codes(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        mock_modbus_unit.input[105] = 999
        mock_modbus_unit.input[107] = 7
        inverter = build(mock_modbus_unit, GEN4)
        await inverter.async_update()
        assert inverter.inverter_fault_text == "Unknown (main=999, sub=7)"

    async def test_it_is_unknown_before_the_first_poll(self, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
        assert build(mock_modbus_unit, GEN4).inverter_fault_text is None


async def test_the_control_firmware_version_joins_its_two_registers(  # type: ignore[no-untyped-def]
    mock_modbus_unit,
) -> None:
    mock_modbus_unit.holding[12] = [0x4148, 0x2D31]  # "AH-1"
    mock_modbus_unit.holding[14] = 23
    inverter = build(mock_modbus_unit, SPF)
    await inverter.async_update()
    assert inverter.firmware_control_version == "AH-1-0023"


async def test_a_device_object_refuses_the_wrong_generation(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(ValueError, match="needs"):
        Gen4Inverter(mock_modbus_unit, GEN3)


async def test_every_component_belongs_to_the_polled_group(inverter) -> None:  # type: ignore[no-untyped-def]
    # Nothing is built and then left unpolled.
    assert inverter.components
    assert all(c.active_fields for c in inverter.components)
