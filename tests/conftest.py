"""Shared fixtures: the variants the suite exercises."""

from __future__ import annotations

import pytest

from growatt_modbus import Variant, build
from growatt_modbus.inverter import GrowattInverter

# One representative inverter per generation, plus the phase/MPPT variations
# that change which registers exist.
VARIANTS: dict[str, Variant] = {
    "gen1_x1_pv": Variant.GEN | Variant.PV | Variant.X1,
    "gen1_x3_pv": Variant.GEN | Variant.PV | Variant.X3,
    "gen2_x3_pv": Variant.GEN2 | Variant.PV | Variant.X3,
    "gen3_x1_hybrid": Variant.GEN3 | Variant.HYBRID | Variant.X1,
    "gen3_x3_hybrid": Variant.GEN3 | Variant.HYBRID | Variant.X3,
    "gen3_x3_hybrid_mppt8": (Variant.GEN3 | Variant.HYBRID | Variant.X3 | Variant.MPPT8),
    "gen3_x1_ac_eps": Variant.GEN3 | Variant.AC | Variant.X1 | Variant.EPS,
    "gen4_x1_hybrid": Variant.GEN4 | Variant.HYBRID | Variant.X1,
    "gen4_x3_hybrid": Variant.GEN4 | Variant.HYBRID | Variant.X3,
    "gen4_x1_hybrid_mppt4": (Variant.GEN4 | Variant.HYBRID | Variant.X1 | Variant.MPPT4),
    "gen4_x1_pv": Variant.GEN4 | Variant.PV | Variant.X1,
    "spf_x1_hybrid": Variant.SPF | Variant.HYBRID | Variant.X1,
}


@pytest.fixture(params=sorted(VARIANTS), ids=sorted(VARIANTS))
def variant(request: pytest.FixtureRequest) -> Variant:
    """Each supported variant in turn."""
    return VARIANTS[request.param]


@pytest.fixture
def inverter(mock_modbus_unit, variant: Variant) -> GrowattInverter:  # type: ignore[no-untyped-def]
    """The device object for the variant under test, on the mock unit."""
    return build(mock_modbus_unit, variant)
