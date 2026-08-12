"""The allowedtypes matching rule, and identifying an inverter from its serial."""

from __future__ import annotations

import pytest

from growatt_modbus import Variant, generation, matches
from growatt_modbus.variants import (
    FIRMWARE_PREFIX_VARIANTS,
    SERIAL_PREFIX_VARIANTS,
    variant_from_identifier,
)

GEN4_X1_HYBRID = Variant.GEN4 | Variant.HYBRID | Variant.X1


def test_a_mask_with_no_bits_in_a_group_ignores_that_group() -> None:
    # A field tagged only GEN4 exists on every Gen4, whatever its phase count.
    assert matches(GEN4_X1_HYBRID, Variant.GEN4)
    assert matches(Variant.GEN4 | Variant.X3 | Variant.PV, Variant.GEN4)


def test_bits_within_a_group_are_or_ed() -> None:
    shared = Variant.GEN2 | Variant.GEN3
    assert matches(Variant.GEN2 | Variant.PV | Variant.X3, shared)
    assert matches(Variant.GEN3 | Variant.HYBRID | Variant.X1, shared)
    assert not matches(GEN4_X1_HYBRID, shared)


def test_groups_are_and_ed() -> None:
    three_phase_gen3 = Variant.GEN3 | Variant.X3
    assert matches(Variant.GEN3 | Variant.HYBRID | Variant.X3, three_phase_gen3)
    # Right generation, wrong phase count.
    assert not matches(Variant.GEN3 | Variant.HYBRID | Variant.X1, three_phase_gen3)
    # Right phase count, wrong generation.
    assert not matches(Variant.GEN4 | Variant.HYBRID | Variant.X3, three_phase_gen3)


def test_optional_hardware_is_off_unless_asked_for() -> None:
    eps_field = Variant.GEN4 | Variant.EPS
    assert not matches(GEN4_X1_HYBRID, eps_field)
    assert matches(GEN4_X1_HYBRID | Variant.EPS, eps_field)


def test_mppt_gating_needs_at_least_the_declared_count() -> None:
    # Declared for 3 MPPTs and up; a 2-MPPT inverter does not have it.
    needs_three = Variant.GEN4 | Variant.MPPT3 | Variant.MPPT4 | Variant.MPPT6
    assert not matches(GEN4_X1_HYBRID, needs_three)
    assert matches(GEN4_X1_HYBRID | Variant.MPPT3, needs_three)
    assert matches(GEN4_X1_HYBRID | Variant.MPPT6, needs_three)


def test_generation_returns_the_single_generation_bit() -> None:
    assert generation(GEN4_X1_HYBRID) is Variant.GEN4


@pytest.mark.parametrize(
    "bad",
    [Variant.X1 | Variant.HYBRID, Variant.GEN3 | Variant.GEN4 | Variant.X1],
    ids=["none", "two"],
)
def test_generation_rejects_an_ambiguous_variant(bad: Variant) -> None:
    with pytest.raises(ValueError, match="exactly one generation"):
        generation(bad)


def test_serial_prefixes_identify_a_model() -> None:
    assert variant_from_identifier("ABJ1234567", SERIAL_PREFIX_VARIANTS) == (
        Variant.HYBRID | Variant.GEN4 | Variant.X1
    )
    assert variant_from_identifier("NAH0000001", SERIAL_PREFIX_VARIANTS) == (
        Variant.PV | Variant.GEN4 | Variant.X3 | Variant.MPPT6
    )
    assert variant_from_identifier("YRE9999999", SERIAL_PREFIX_VARIANTS) == (
        Variant.HYBRID | Variant.SPF | Variant.X1
    )


def test_an_unknown_prefix_identifies_nothing() -> None:
    assert variant_from_identifier("ZZZ0000000", SERIAL_PREFIX_VARIANTS) is None
    assert variant_from_identifier(None, SERIAL_PREFIX_VARIANTS) is None
    assert variant_from_identifier("", SERIAL_PREFIX_VARIANTS) is None


def test_firmware_prefixes_are_a_separate_table() -> None:
    assert variant_from_identifier("RAA1234", FIRMWARE_PREFIX_VARIANTS) == (
        Variant.HYBRID | Variant.GEN3 | Variant.X1
    )
    assert variant_from_identifier("RAA1234", SERIAL_PREFIX_VARIANTS) is None


def test_every_table_entry_names_exactly_one_generation() -> None:
    for table in (SERIAL_PREFIX_VARIANTS, FIRMWARE_PREFIX_VARIANTS):
        for prefix, variant in table.items():
            assert generation(variant), prefix
