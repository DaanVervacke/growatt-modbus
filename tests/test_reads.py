"""What a poll actually asks the inverter for.

These check the read plan is *correct* — every field covered, nothing read that
the variant does not have, and no request wider than the inverter answers —
before pinning the resulting request counts.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model.fields import CoilField, DiscreteInputField

from growatt_modbus import UpdateReport, Variant, build
from growatt_modbus.fields import MAX_READ_SPAN
from growatt_modbus.inverter import GrowattInverter


def _covered(unit: MockModbusUnit) -> dict[str, set[int]]:
    """Every address the poll asked for, per register space."""
    covered: dict[str, set[int]] = {}
    for event in unit.read_events:
        covered.setdefault(event.register_type, set()).update(
            range(event.address, event.address + event.count)
        )
    return covered


def _wanted(inverter: GrowattInverter, report: UpdateReport) -> dict[str, set[int]]:
    """Every address the polled components' active fields sit on, per space."""
    wanted: dict[str, set[int]] = {}
    for polled in report.updated:
        component = getattr(inverter, polled)
        space = component.register_space
        for name in component.active_fields:
            field = component.declared_fields[name]
            assert not isinstance(field, CoilField | DiscreteInputField)  # none here
            wanted.setdefault(space, set()).update(
                range(field.address, field.address + field.count)
            )
    return wanted


async def _poll(inverter: GrowattInverter, unit: MockModbusUnit) -> UpdateReport:
    """Run a second poll, so setup's one-off APX probe is not in the events."""
    await inverter.async_update()
    unit.read_events.clear()
    return await inverter.async_update()


async def test_a_poll_reads_every_field_it_declares(inverter, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    report = await _poll(inverter, mock_modbus_unit)
    covered, wanted = _covered(mock_modbus_unit), _wanted(inverter, report)
    for space, addresses in wanted.items():
        missing = addresses - covered.get(space, set())
        assert not missing, f"{space}: {sorted(missing)[:10]} never read"


async def test_no_request_is_wider_than_the_inverter_answers(  # type: ignore[no-untyped-def]
    inverter, mock_modbus_unit
) -> None:
    await _poll(inverter, mock_modbus_unit)
    assert mock_modbus_unit.read_events
    assert all(e.count <= MAX_READ_SPAN for e in mock_modbus_unit.read_events)


async def test_requests_do_not_overlap(inverter, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    # Components plan their reads separately now, so nothing forces them apart;
    # they still land on disjoint blocks, and a poll that started re-reading a
    # register would be paying for it every cycle.
    await _poll(inverter, mock_modbus_unit)
    seen: dict[str, set[int]] = {}
    for event in mock_modbus_unit.read_events:
        block = set(range(event.address, event.address + event.count))
        already = seen.setdefault(event.register_type, set())
        assert not block & already, f"{event.register_type} {event.address} read twice"
        already |= block


async def test_only_holding_and_input_registers_are_read(  # type: ignore[no-untyped-def]
    inverter, mock_modbus_unit
) -> None:
    # This device has no coils or discrete inputs; booleans are packed in registers.
    await _poll(inverter, mock_modbus_unit)
    spaces = {e.register_type for e in mock_modbus_unit.read_events}
    assert spaces <= {"holding", "input"}


async def test_a_second_poll_issues_the_same_requests(inverter, mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    await _poll(inverter, mock_modbus_unit)
    first = list(mock_modbus_unit.read_events)
    mock_modbus_unit.read_events.clear()
    await inverter.async_update()
    assert list(mock_modbus_unit.read_events) == first


class TestVariantNarrowsThePoll:
    """The variant bits must keep reads off registers the model does not serve."""

    async def test_a_two_mppt_gen4_never_reads_the_third_string(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        # PV3 lives at input 3011-3013 and exists only from three MPPTs up.
        two = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1)
        await _poll(two, mock_modbus_unit)
        assert not _covered(mock_modbus_unit).get("input", set()) & {3011, 3012, 3013}

        mock_modbus_unit.read_events.clear()
        three = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1 | Variant.MPPT3)
        await _poll(three, mock_modbus_unit)
        assert {3011, 3012, 3013} <= _covered(mock_modbus_unit)["input"]

    async def test_a_single_phase_gen3_never_reads_the_other_two_phases(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        # The L2/L3 grid registers at input 42-48 are three-phase only.
        single = build(mock_modbus_unit, Variant.GEN3 | Variant.HYBRID | Variant.X1)
        await single.async_update()
        assert not _covered(mock_modbus_unit).get("input", set()) & {42, 43, 44, 46, 47}

        mock_modbus_unit.read_events.clear()
        three = build(mock_modbus_unit, Variant.GEN3 | Variant.HYBRID | Variant.X3)
        await three.async_update()
        assert {42, 43, 44, 46, 47, 48} <= _covered(mock_modbus_unit)["input"]

    async def test_an_inverter_without_a_backup_output_never_reads_eps(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        # The Gen4 EPS switch sits at holding 3079.
        plain = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1)
        await _poll(plain, mock_modbus_unit)
        assert 3079 not in _covered(mock_modbus_unit).get("holding", set())

        mock_modbus_unit.read_events.clear()
        with_eps = build(mock_modbus_unit, Variant.GEN4 | Variant.HYBRID | Variant.X1 | Variant.EPS)
        await _poll(with_eps, mock_modbus_unit)
        assert 3079 in _covered(mock_modbus_unit)["holding"]

    async def test_a_single_mppt_spf_never_reads_its_second_string(  # type: ignore[no-untyped-def]
        self, mock_modbus_unit
    ) -> None:
        # Blacklisted by serial prefix: a KAM-series SPF has one PV input, so
        # PV2's voltage (2), power (5-6) and current (8) must not be read.
        variant = Variant.SPF | Variant.HYBRID | Variant.X1
        single = build(mock_modbus_unit, variant, "KAM1234567")
        await single.async_update()
        covered = _covered(mock_modbus_unit)["input"]
        assert not covered & {2, 5, 6, 8, 52, 53, 54, 55}

        mock_modbus_unit.read_events.clear()
        dual = build(mock_modbus_unit, variant, "NUK1234567")
        await dual.async_update()
        assert {2, 5, 6, 8, 54, 55} <= _covered(mock_modbus_unit)["input"]


# Measured request counts for a steady-state poll, as a regression pin on the
# read plan. A change here means the map or the planner moved; check it is
# intended before updating.
#
# Polling per component rather than through one pooled group cost nothing: every
# count below is what the pooled group issued. The Gen4 hybrids dropped 29 —
# the APX battery blocks, which are now gated on Variant.APX instead of being
# read on every hybrid. gen4_x3_hybrid_apx is the old gen4_x3_hybrid figure, so
# splitting the two APX components into four did not add a request either: the
# pack/module boundary already fell between blocks.
EXPECTED_REQUESTS = {
    "gen1_x1_pv": 4,
    "gen1_x3_pv": 3,
    "gen2_x3_pv": 9,
    "gen3_x1_ac_eps": 22,
    "gen3_x1_hybrid": 20,
    "gen3_x3_hybrid": 17,
    "gen3_x3_hybrid_mppt8": 15,
    "gen4_x1_hybrid": 25,
    "gen4_x1_hybrid_mppt4": 22,
    "gen4_x1_pv": 19,
    "gen4_x3_hybrid": 24,
    "gen4_x3_hybrid_apx": 53,
    "spf_x1_hybrid": 2,
}


@pytest.mark.parametrize("name", sorted(EXPECTED_REQUESTS))
async def test_request_count_is_pinned(mock_modbus_unit, name: str) -> None:  # type: ignore[no-untyped-def]
    from .conftest import VARIANTS

    inverter = build(mock_modbus_unit, VARIANTS[name])
    await _poll(inverter, mock_modbus_unit)
    assert len(mock_modbus_unit.read_events) == EXPECTED_REQUESTS[name]


async def test_the_apx_blocks_are_the_whole_difference(mock_modbus_unit) -> None:  # type: ignore[no-untyped-def]
    """The 29 blocks a non-APX hybrid no longer polls are exactly the APX ones."""
    from .conftest import VARIANTS

    with_apx = build(mock_modbus_unit, VARIANTS["gen4_x3_hybrid_apx"])
    report = await _poll(with_apx, mock_modbus_unit)
    apx = {
        "battery_settings",
        "battery_module_settings",
        "battery_status",
        "battery_module_status",
    }
    assert apx <= report.updated

    blocks = 0
    for name in apx:
        mock_modbus_unit.read_events.clear()
        await getattr(with_apx, name).async_update(notify=False)
        blocks += len(mock_modbus_unit.read_events)
    assert blocks == 29
    assert EXPECTED_REQUESTS["gen4_x3_hybrid_apx"] - EXPECTED_REQUESTS["gen4_x3_hybrid"] == 29
