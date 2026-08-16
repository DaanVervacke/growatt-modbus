"""One failing block must not take the rest of the poll with it.

The upstream integration reads its blocks independently and tolerates a failure
(``auto_block_ignore_readerror=True``): the failing block's sensors keep their
last values while everything else refreshes. The library mirrors that at
component granularity.

The exception is an inverter that has answered nothing at all: there a timeout
raises rather than being contained, so one silent poll costs one timeout.
"""

from __future__ import annotations

import pytest
from modbus_connection import (
    IllegalDataAddressError,
    IllegalFunctionError,
    ModbusConnectionError,
    ModbusTimeoutError,
    ServerDeviceBusyError,
)
from modbus_connection.mock import MockModbusUnit

from growatt_modbus import Gen4Inverter, Variant, build

GEN4 = Variant.GEN4 | Variant.HYBRID | Variant.X3
GEN4_APX = GEN4 | Variant.APX


@pytest.fixture
def hybrid(mock_modbus_unit: MockModbusUnit) -> Gen4Inverter:
    """A Gen4 hybrid with an APX pack, the widest poll the library has."""
    inverter = build(mock_modbus_unit, GEN4_APX)
    assert isinstance(inverter, Gen4Inverter)
    return inverter


async def test_a_failed_component_leaves_the_rest_fresh(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    mock_modbus_unit.input[3171] = 42  # battery SOC
    await hybrid.async_update()

    mock_modbus_unit.input[3171] = 55  # the device moves on
    mock_modbus_unit.input[1] = [0, 20000]  # so does PV power
    # 3169 sits in hybrid_status' 3169..3181 block, and in no other component's.
    mock_modbus_unit.fail_read(
        3169, ModbusTimeoutError("slow battery block"), register_type="input"
    )
    report = await hybrid.async_update()

    assert not report.complete
    assert set(report.failed) == {"hybrid_status"}
    assert isinstance(report.failed["hybrid_status"], ModbusTimeoutError)
    assert "status" in report.updated
    assert hybrid.hybrid_status is not None
    assert hybrid.hybrid_status.battery_soc == 42  # previous value kept
    assert hybrid.status.pv_power_total == 2000.0  # refreshed


async def test_listeners_fire_at_the_end_and_only_for_fresh_components(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    await hybrid.async_update()
    seen: list[int] = []
    hybrid.status.add_update_listener(lambda: seen.append(len(mock_modbus_unit.read_events)))
    assert hybrid.hybrid_status is not None
    hybrid.hybrid_status.add_update_listener(lambda: seen.append(-1))

    mock_modbus_unit.fail_read(
        3169, ModbusTimeoutError("slow battery block"), register_type="input"
    )
    mock_modbus_unit.read_events.clear()
    await hybrid.async_update()

    # One notification, after every status component was tried; none for the
    # failure. The settings poll that follows is its own and does not hold it
    # up, so the listener sees the reads up to settings' first block.
    settings_start = next(
        i
        for i, event in enumerate(mock_modbus_unit.read_events)
        if event.register_type == "holding" and event.address == 0
    )
    assert seen == [settings_start]


async def test_a_dead_link_raises_instead_of_reporting(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    await hybrid.async_update()
    mock_modbus_unit.fail_requests(ModbusConnectionError("link down"))
    with pytest.raises(ModbusConnectionError):
        await hybrid.async_update()


async def test_a_silent_inverter_raises_after_one_timeout_not_nine(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    """An inverter asleep behind a bridge that keeps the socket open.

    Nothing answered, so the remaining components would only pay a timeout each.
    """
    await hybrid.async_update()
    assert hybrid.POLLED[0] == "status"
    mock_modbus_unit.fail_requests(ModbusTimeoutError("asleep"))
    mock_modbus_unit.read_events.clear()

    with pytest.raises(ModbusTimeoutError):
        await hybrid.async_update()
    assert len(mock_modbus_unit.read_events) == 1


async def test_a_refused_first_component_still_contains_a_later_timeout(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    """A refusal is an answer: the inverter is there, so the poll goes on."""
    await hybrid.async_update()
    # status leads the poll, so refusing its first block is the refusal the
    # timeout after it has to be contained by.
    mock_modbus_unit.fail_read(1, IllegalDataAddressError(), register_type="input")
    mock_modbus_unit.fail_read(
        3169, ModbusTimeoutError("slow battery block"), register_type="input"
    )
    report = await hybrid.async_update()

    assert {"status", "hybrid_status"} <= set(report.failed)
    assert "battery_status" in report.updated


async def test_a_settings_poll_of_a_silent_inverter_raises_at_once(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    """A settings poll on its own is its own "nothing answered" run."""
    await hybrid.async_update()
    mock_modbus_unit.fail_requests(ModbusTimeoutError("asleep"))
    mock_modbus_unit.read_events.clear()

    with pytest.raises(ModbusTimeoutError):
        await hybrid.async_update_settings()
    assert len(mock_modbus_unit.read_events) == 1


async def test_every_component_refreshes_on_a_healthy_device(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    report = await hybrid.async_update()
    assert report.complete
    assert report.failed == {}
    assert {"settings", "status", "hybrid_status", "battery_status"} <= report.updated


async def test_a_refused_battery_bank_does_not_touch_the_inverter_readings(
    hybrid: Gen4Inverter, mock_modbus_unit: MockModbusUnit
) -> None:
    """The APX module banks are the blocks most likely to be refused."""
    mock_modbus_unit.input[1] = [0, 20000]
    for address in (5081, 5120, 5228, 5330, 5440, 5548):
        mock_modbus_unit.fail_read(address, IllegalDataAddressError(), register_type="input")
    report = await hybrid.async_update()

    assert set(report.failed) == {"battery_module_status"}
    assert "battery_status" in report.updated  # the pack gate survives its modules
    assert hybrid.status.pv_power_total == 2000.0


class TestApxGating:
    """A hybrid without an APX pack must never poll the APX register bank."""

    async def test_a_non_apx_hybrid_polls_none_of_the_apx_blocks(
        self, mock_modbus_unit: MockModbusUnit
    ) -> None:
        mock_modbus_unit.holding[700] = 1  # BMS type: LG ver 3
        inverter = build(mock_modbus_unit, GEN4)
        report = await inverter.async_update()

        assert Variant.APX not in inverter.variant
        assert not {name for name in report.updated if name.startswith("battery")}
        mock_modbus_unit.read_events.clear()
        await inverter.async_update()
        # The APX bank spans 4019..5908 in both register spaces.
        assert not [e for e in mock_modbus_unit.read_events if 4019 <= e.address <= 5908]

    async def test_an_apx_pack_is_detected_from_the_bms_type(
        self, mock_modbus_unit: MockModbusUnit
    ) -> None:
        mock_modbus_unit.holding[700] = 2  # BMS type: APX HV
        inverter = build(mock_modbus_unit, GEN4)
        report = await inverter.async_update()

        assert Variant.APX in inverter.variant
        assert {"battery_settings", "battery_status"} <= report.updated

    async def test_an_inverter_that_refuses_the_bms_register_has_no_apx(
        self, mock_modbus_unit: MockModbusUnit
    ) -> None:
        mock_modbus_unit.fail_read(700, IllegalFunctionError())
        inverter = build(mock_modbus_unit, GEN4)
        report = await inverter.async_update()

        assert Variant.APX not in inverter.variant
        assert "settings" in report.failed  # bms_type is in its block
        assert "status" in report.updated

    async def test_the_probe_is_skipped_when_apx_was_opted_into(
        self, mock_modbus_unit: MockModbusUnit
    ) -> None:
        mock_modbus_unit.fail_read(700, IllegalDataAddressError())
        inverter = build(mock_modbus_unit, GEN4_APX)
        report = await inverter.async_update()
        assert "battery_status" in report.updated

    async def test_a_pv_only_gen4_is_never_probed(self, mock_modbus_unit: MockModbusUnit) -> None:
        inverter = build(mock_modbus_unit, Variant.GEN4 | Variant.PV | Variant.X1)
        await inverter.async_setup()
        assert Variant.APX not in inverter.variant


class TestSetupIsRetryable:
    """A transient fault at setup must not brick the device."""

    async def test_a_timed_out_probe_raises_and_leaves_the_device_unset_up(
        self, mock_modbus_unit: MockModbusUnit
    ) -> None:
        mock_modbus_unit.holding[700] = 2
        mock_modbus_unit.fail_read(700, ModbusTimeoutError("no answer"))
        inverter = build(mock_modbus_unit, GEN4)

        with pytest.raises(ModbusTimeoutError):
            await inverter.async_update()
        assert Variant.APX not in inverter.variant

        mock_modbus_unit.fail_read(700, None)  # the inverter wakes up
        report = await inverter.async_update()
        assert Variant.APX in inverter.variant
        assert "battery_status" in report.updated

    async def test_a_busy_answer_is_not_latched_as_absence(
        self, mock_modbus_unit: MockModbusUnit
    ) -> None:
        # ServerDeviceBusyError is a ModbusExceptionError but not a refusal:
        # reading it as "no APX pack" would lose the bank until a restart.
        mock_modbus_unit.holding[700] = 2
        mock_modbus_unit.fail_read(700, ServerDeviceBusyError())
        inverter = build(mock_modbus_unit, GEN4)

        with pytest.raises(ServerDeviceBusyError):
            await inverter.async_update()

        mock_modbus_unit.fail_read(700, None)
        await inverter.async_update()
        assert Variant.APX in inverter.variant
