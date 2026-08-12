"""Writing settings back to the inverter."""

from __future__ import annotations

from datetime import datetime, time

import pytest

from growatt_modbus import Variant, build

SPF = Variant.SPF | Variant.HYBRID | Variant.X1
GEN3 = Variant.GEN3 | Variant.HYBRID | Variant.X1
GEN4 = Variant.GEN4 | Variant.HYBRID | Variant.X1


async def test_a_setting_is_written_by_its_label(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, SPF)
    await inverter.settings.write("state_power", "Grid First")
    assert await mock_modbus_unit.read_holding_registers(1, 1) == [2]


async def test_an_unknown_label_never_reaches_the_device(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, SPF)
    writes: list[object] = []
    mock_modbus_unit.on_write(writes.append)

    with pytest.raises(ValueError, match="not one of"):
        await inverter.settings.write("state_power", "Wind First")
    assert writes == []


async def test_a_numeric_setting_is_range_checked(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, GEN3)
    settings = inverter.storage_settings
    assert settings is not None

    await settings.write("battery_first_charge_rate", 80)
    assert await mock_modbus_unit.read_holding_registers(1090, 1) == [80]

    with pytest.raises(ValueError, match="outside"):
        await settings.write("battery_first_charge_rate", 120)
    # The rejected write left the register alone.
    assert await mock_modbus_unit.read_holding_registers(1090, 1) == [80]


async def test_a_scaled_setting_is_encoded_back_through_its_scale(  # type: ignore[no-untyped-def]
    mock_modbus_unit,
) -> None:
    inverter = build(mock_modbus_unit, GEN4)
    settings = inverter.hybrid_settings
    assert settings is not None
    # peak_import_limit is 0.1-scaled, so 12.5 goes out as 125.
    await settings.write("peak_import_limit", 12.5)
    assert await mock_modbus_unit.read_holding_registers(3307, 1) == [125]


async def test_a_time_of_day_setting_round_trips(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, GEN3)
    settings = inverter.storage_settings
    assert settings is not None

    await settings.write("grid_first_time_1_begin", time(1, 30))
    assert await mock_modbus_unit.read_holding_registers(1080, 1) == [(1 << 8) | 30]

    await settings.async_update()
    assert settings.grid_first_time_1_begin == time(1, 30)


async def test_writing_one_part_of_a_time_slot_keeps_the_rest(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # Holding 3038 packs start time, mode and the enable bit into one word.
    mock_modbus_unit.holding[3038] = (1 << 15) | (6 << 8) | 30  # enabled, 06:30
    inverter = build(mock_modbus_unit, GEN4)
    settings = inverter.hybrid_settings
    assert settings is not None

    await settings.write("time_1_mode", "Grid First")

    await settings.async_update()
    assert settings.time_1_mode == "Grid First"
    assert settings.time_1_begin == time(6, 30)  # untouched
    assert settings.time_1_enabled is True  # untouched


async def test_disabling_a_time_slot_keeps_its_times(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    mock_modbus_unit.holding[3038] = (1 << 15) | (1 << 13) | (6 << 8) | 30
    inverter = build(mock_modbus_unit, GEN4)
    settings = inverter.hybrid_settings
    assert settings is not None

    await settings.write("time_1_enabled", False)

    await settings.async_update()
    assert settings.time_1_enabled is False
    assert settings.time_1_begin == time(6, 30)
    assert settings.time_1_mode == "Battery First"


async def test_the_clock_is_written_over_all_six_registers(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, SPF)
    await inverter.settings.write("rtc", datetime(2024, 6, 15, 13, 5, 30))
    assert await mock_modbus_unit.read_holding_registers(45, 6) == [24, 6, 15, 13, 5, 30]


async def test_a_read_only_measurement_cannot_be_written(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    inverter = build(mock_modbus_unit, SPF)
    with pytest.raises(Exception, match="not writable|read-only"):
        await inverter.status.write("pv_voltage_1", 1)


async def test_a_field_this_variant_lacks_cannot_be_written(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # eps_switch is declared for a Gen4 with a backup output; without EPS it is
    # restricted away, so the write is refused rather than silently issued.
    inverter = build(mock_modbus_unit, GEN4)
    settings = inverter.hybrid_settings
    assert settings is not None
    assert "eps_switch" not in settings.active_fields
    with pytest.raises(Exception):  # noqa: B017 - any refusal is acceptable
        await settings.write("eps_switch", "Enabled")


async def test_the_same_field_is_writable_once_the_option_is_declared(  # type: ignore[no-untyped-def]
    mock_modbus_unit,
) -> None:
    inverter = build(mock_modbus_unit, GEN4 | Variant.EPS)
    settings = inverter.hybrid_settings
    assert settings is not None
    await settings.write("eps_switch", "Enabled")
    assert await mock_modbus_unit.read_holding_registers(3079, 1) == [1]
