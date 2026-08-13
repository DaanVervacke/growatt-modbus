"""Identifying an inverter from the registers it answers."""

from __future__ import annotations

import pytest
from modbus_connection import (
    IllegalDataAddressError,
    ModbusConnectionError,
    ModbusTimeoutError,
    ServerDeviceBusyError,
)

from growatt_modbus import Gen3Inverter, Gen4Inverter, SpfInverter, Variant, detect


def _seed_string(unit, address: int, text: str) -> None:  # type: ignore[no-untyped-def]
    """Write a null-padded ASCII string the way the inverter reports one."""
    padded = text.encode("ascii")
    padded += b"\x00" * (-len(padded) % 2)
    unit.holding[address] = [
        int.from_bytes(padded[i : i + 2], "big") for i in range(0, len(padded), 2)
    ]


async def test_detects_a_gen4_hybrid_from_its_serial(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    _seed_string(mock_modbus_unit, 3001, "ABJ1234567")
    inverter = await detect(mock_modbus_unit)
    assert isinstance(inverter, Gen4Inverter)
    assert inverter.variant == Variant.HYBRID | Variant.GEN4 | Variant.X1
    assert inverter.serial_number == "ABJ1234567"


async def test_falls_back_to_the_older_serial_locations(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # Nothing at 3001 or 209; an SPH reports its serial at holding 23.
    _seed_string(mock_modbus_unit, 23, "YRP0000001")
    inverter = await detect(mock_modbus_unit)
    assert isinstance(inverter, Gen3Inverter)
    assert inverter.variant == Variant.HYBRID | Variant.GEN3 | Variant.X1


async def test_falls_back_to_the_firmware_string(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # No recognised serial anywhere, but the firmware prefix identifies an SPH.
    _seed_string(mock_modbus_unit, 23, "ZZZ9999999")
    _seed_string(mock_modbus_unit, 9, "RAA1234")
    inverter = await detect(mock_modbus_unit)
    assert isinstance(inverter, Gen3Inverter)
    assert inverter.serial_number == "RAA1234"


async def test_a_serial_style_prefix_at_the_firmware_register_still_counts(  # type: ignore[no-untyped-def]
    mock_modbus_unit,
) -> None:
    # Some older models expose a model prefix only at register 9.
    _seed_string(mock_modbus_unit, 9, "YRE0000123")
    inverter = await detect(mock_modbus_unit)
    assert isinstance(inverter, SpfInverter)


async def test_a_refused_serial_register_is_not_fatal(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # An SPF does not serve holding 3001 at all.
    mock_modbus_unit.fail_read(3001, IllegalDataAddressError())
    _seed_string(mock_modbus_unit, 23, "TTJ0000001")
    inverter = await detect(mock_modbus_unit)
    assert isinstance(inverter, SpfInverter)


async def test_an_unrecognised_inverter_is_reported(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    _seed_string(mock_modbus_unit, 23, "ZZZ9999999")
    with pytest.raises(LookupError, match="unrecognised"):
        await detect(mock_modbus_unit)


class TestATransientProbeIsNotAVerdict:
    """A slow or busy inverter is unidentified for now, never unrecognised."""

    async def test_a_timed_out_address_does_not_stop_the_remaining_ones(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        # 3001 is probed first; the serial actually lives at 23.
        mock_modbus_unit.fail_read(3001, ModbusTimeoutError("slow"))
        _seed_string(mock_modbus_unit, 23, "YRP0000001")
        inverter = await detect(mock_modbus_unit)
        assert isinstance(inverter, Gen3Inverter)

    async def test_a_device_that_never_answered_raises_the_read_error(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        # LookupError here would be a permanent verdict on a device that is
        # merely slow, and callers treat it as "stop trying".
        for address in (3001, 209, 23, 9):
            mock_modbus_unit.fail_read(address, ModbusTimeoutError("slow"))
        with pytest.raises(ModbusTimeoutError):
            await detect(mock_modbus_unit)

    async def test_a_busy_answer_is_not_read_as_an_empty_address(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        for address in (3001, 209, 23, 9):
            mock_modbus_unit.fail_read(address, ServerDeviceBusyError())
        with pytest.raises(ServerDeviceBusyError):
            await detect(mock_modbus_unit)

    async def test_a_dead_link_raises_at_the_first_address(self, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
        mock_modbus_unit.fail_requests(ModbusConnectionError("link down"))
        with pytest.raises(ModbusConnectionError):
            await detect(mock_modbus_unit)
        assert len(mock_modbus_unit.read_events) == 1


async def test_optional_hardware_is_opted_into(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    _seed_string(mock_modbus_unit, 3001, "ABJ1234567")

    plain = await detect(mock_modbus_unit)
    assert Variant.EPS not in plain.variant

    with_extras = await detect(mock_modbus_unit, read_eps=True, read_dcb=True, read_apx=True)
    assert Variant.EPS in with_extras.variant
    assert Variant.DCB in with_extras.variant
    assert Variant.APX in with_extras.variant
    assert with_extras.hybrid_settings is not None
    assert "eps_switch" in with_extras.hybrid_settings.active_fields


async def test_the_serial_prefix_narrows_the_fields(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # A KAM-series SPF has one PV input, so PV2's registers are dropped.
    _seed_string(mock_modbus_unit, 23, "KAM0000001")
    inverter = await detect(mock_modbus_unit)
    assert isinstance(inverter, SpfInverter)
    assert "pv_voltage_1" in inverter.status.active_fields
    assert "pv_voltage_2" not in inverter.status.active_fields
