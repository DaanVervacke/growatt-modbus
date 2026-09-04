"""Which Growatt inverter a register belongs to.

The upstream integration tags every entity with an ``allowedtypes`` bitmask and
matches it against the detected inverter with a per-group rule. This module is a
faithful port of that scheme: :class:`Variant` carries the same bits, and
:func:`matches` the same predicate, so a field that exists only on some
generations is never read on the others.

The bits fall into seven independent groups. Within a group the bits of a mask are
OR-ed; between groups the results are AND-ed. A mask with no bits in a group
places no constraint from that group.
"""

from __future__ import annotations

from enum import IntFlag
from typing import Final


class Variant(IntFlag):
    """A Growatt inverter's capability bits, or the set a register applies to."""

    # Protocol generation. An inverter has exactly one.
    GEN = 0x0001
    """Legacy PV inverters (TL-S, TL3-S, NEO)."""
    GEN2 = 0x0002
    """MOD/MID TL3-X PV inverters."""
    GEN3 = 0x0004
    """SPH / SPA storage inverters."""
    GEN4 = 0x0008
    """MIN / MOD / MID / WIT TL-XH hybrids and TL-X PV."""
    SPF = 0x0010
    """SPF / SPE off-grid inverters."""

    # Phase count.
    X1 = 0x0100
    """Single phase."""
    X3 = 0x0200
    """Three phase."""

    # Inverter category.
    PV = 0x0400
    """PV-only (no battery)."""
    AC = 0x0800
    """AC-coupled storage (no PV input)."""
    HYBRID = 0x1000
    """PV plus battery."""
    MIC = 0x2000
    """Micro inverter."""

    # Optional hardware, enabled by the caller.
    EPS = 0x8000
    """Emergency power supply / backup output installed."""
    DCB = 0x10000
    """Dry contact box installed."""
    APX = 0x20000
    """APX HV battery attached (BMS type 2), which brings its own register bank."""

    # MPPT count above the two every model has.
    MPPT3 = 0x40000
    MPPT4 = 0x80000
    MPPT6 = 0x100000
    MPPT8 = 0x200000
    MPPT10 = 0x400000


ALL_GEN_GROUP: Final = Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.SPF
ALL_X_GROUP: Final = Variant.X1 | Variant.X3
ALL_TYPE_GROUP: Final = Variant.PV | Variant.AC | Variant.HYBRID | Variant.MIC
ALL_EPS_GROUP: Final = Variant.EPS
ALL_DCB_GROUP: Final = Variant.DCB
ALL_APX_GROUP: Final = Variant.APX
ALL_MPPT_GROUP: Final = (
    Variant.MPPT3 | Variant.MPPT4 | Variant.MPPT6 | Variant.MPPT8 | Variant.MPPT10
)

_GROUPS: Final = (
    ALL_GEN_GROUP,
    ALL_X_GROUP,
    ALL_TYPE_GROUP,
    ALL_EPS_GROUP,
    ALL_DCB_GROUP,
    ALL_APX_GROUP,
    ALL_MPPT_GROUP,
)

# Holding register carrying the attached battery's BMS type, and the code that
# means an APX HV pack. Probed at setup to decide whether Variant.APX applies.
BMS_TYPE_REGISTER: Final = 700
BMS_TYPE_APX: Final = 2


def matches(inverter: Variant, field_mask: Variant) -> bool:
    """Return whether a field tagged ``field_mask`` exists on ``inverter``."""
    return all(
        (inverter & field_mask & group) != 0 or (field_mask & group) == 0 for group in _GROUPS
    )


def generation(inverter: Variant) -> Variant:
    """Return the single generation bit of ``inverter``.

    Raises ``ValueError`` unless exactly one generation bit is set — every other
    part of the library keys off the generation, so an ambiguous one is a bug in
    the caller rather than something to guess at.
    """
    gen = inverter & ALL_GEN_GROUP
    if gen.bit_count() != 1:
        raise ValueError(f"expected exactly one generation bit, got {gen!r}")
    return gen


# Serial-number prefixes of the supported model families, each mapped to the
# variant it identifies. Ported verbatim from the upstream plugin.
SERIAL_PREFIX_VARIANTS: Final[dict[str, Variant]] = {
    # MIN hybrid
    "ABJ": Variant.HYBRID | Variant.GEN4 | Variant.X1,  # MIN 2500 TL-XH, 2 MPPT
    "SKL": Variant.HYBRID | Variant.GEN4 | Variant.X1,  # MIN 3600 TL-XH, 2 MPPT
    "XVM": Variant.HYBRID | Variant.GEN4 | Variant.X1,  # MIN 5000 TL-XH, 2 MPPT
    "SMN": Variant.HYBRID | Variant.GEN4 | Variant.X1 | Variant.MPPT4,  # MIN TL-XH-US
    "JGQ": Variant.HYBRID | Variant.GEN4 | Variant.X1 | Variant.MPPT3,  # MIN 7600 TL-XH-US
    "HJU": Variant.HYBRID | Variant.GEN4 | Variant.X1,  # MIN 4200TL-XH2, 2 MPPT
    "VFJ": Variant.HYBRID | Variant.GEN4 | Variant.X1 | Variant.MPPT4,  # MIN 10000 TL-XH-US
    # MOD hybrid
    "XHL": Variant.HYBRID | Variant.GEN4 | Variant.X1,  # MOD 4000 TL3-XH, 2 MPPT
    "DPS": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 5000 TL3-HU, 2 MPPT
    "DMS": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # MOD 8000 TL3-HU
    "DKS": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # MOD 10000 TL3-HU
    "DO1": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # MOD 12000 TL3-HU
    "TTS": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # KTL3-HU 12kW
    "TSS": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # KTL3-HU 12kW
    "PYL": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 5000 TL3-XH, 2 MPPT
    "JCM": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 6000 TL3-XH, 2 MPPT
    "MEK": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 7000 TL3-XH, 2 MPPT
    "MFK": Variant.HYBRID | Variant.GEN4 | Variant.X1,  # MOD 8000 TL3-XH, 2 MPPT
    "DFK": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 100000 TL3-XH, 2 MPPT
    "EGR": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # MOD 150000 TL3-HU
    # MID hybrid
    "KLN": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MID 15000 TL3-XH, 2 MPPT
    "KMN": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MID 17000 TL3-XH, 2 MPPT
    "KNN": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # MID 25000 TL3-XH
    "RKM": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # MID 30000 TL3-XH
    "DLP": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT3,  # MID 30000 TL3-XH
    # MOD BP hybrid
    "FMP": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 5000 TL3-XH (BP)
    "FPP": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 7000 TL3-XH (BP)
    "FQP": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 8000 TL3-XH (BP)
    "CZM": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # MOD 10000 TL3-XH (BP)
    # SPH, SPE and SPA storage
    "YRP": Variant.HYBRID | Variant.GEN3 | Variant.X1,  # SPH 5000 TL-HUB, 2 MPPT
    "NFR": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPE 8000 ES, 2 MPPT
    "WPD": Variant.AC | Variant.GEN3 | Variant.X1,  # SPA 3000TL BL, no PV MPPT
    # SPF
    "YRE": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF 5000 ES, 1 MPPT
    "TTJ": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF 5000 ES, 1 MPPT
    "BNJ": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF 3000 TL LVM 24P, 1 MPPT
    "KAM": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF 5000 ES, 1 MPPT
    "NUK": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF 12000T DVM-US MPV, 2 MPPT
    # WIT
    "0PE": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # WIT 8000-HU, 2 MPPT
    "0PC": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # WIT 12000-HU, 2 MPPT
    "0PH": Variant.HYBRID | Variant.GEN4 | Variant.X3 | Variant.MPPT10,  # WIT 100000-HU
    "0HU": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # WIT 15K-HU, 2 MPPT
    # MIC and MIN PV
    "FPH": Variant.PV | Variant.GEN4 | Variant.X1,  # MIC 2000 TL-X, 1 MPPT
    "FWJ": Variant.PV | Variant.GEN4 | Variant.X1,  # MIC 3300 TL-X, 1 MPPT
    "QYL": Variant.PV | Variant.GEN4 | Variant.X1,  # MIN 2500 TL-X, 2 MPPT
    "XTD": Variant.PV | Variant.GEN4 | Variant.X1,  # MIN 5000 TL-X, 2 MPPT
    "BDK": Variant.PV | Variant.GEN4 | Variant.X1,  # MIN 4200 TL-XE, 2 MPPT
    "DCF": Variant.PV | Variant.GEN4 | Variant.X1,  # MIN 3000 TL-XE, 2 MPPT
    "WVN": Variant.PV | Variant.GEN4 | Variant.X1 | Variant.MPPT3,  # MIN 8000 TL-X2
    # MOD, MID and MAX PV
    "RDH": Variant.PV | Variant.GEN2 | Variant.X3,  # MOD 4000 TL3-X, 2 MPPT
    "QEH": Variant.PV | Variant.GEN2 | Variant.X3,  # MOD 8000 TL3-X, 2 MPPT
    "RPH": Variant.PV | Variant.GEN2 | Variant.X3,  # MOD 15000 TL3-X, 2 MPPT
    "GXF": Variant.PV | Variant.GEN4 | Variant.X3,  # MID 12000 TL3-XL, 2 MPPT
    "NAH": Variant.PV | Variant.GEN4 | Variant.X3 | Variant.MPPT6,  # MAX 60000 TL3 LV
    # SPH PV
    "DIE": Variant.PV | Variant.GEN3 | Variant.X1,  # SPH 1000-S, 1 MPPT
    "PYH": Variant.PV | Variant.GEN3 | Variant.X1,  # SPH 1500 TL-X, 1 MPPT
    "NLC": Variant.PV | Variant.GEN3 | Variant.X1,  # SPH 3000 BP, 1 MPPT
    "NRC": Variant.PV | Variant.GEN3 | Variant.X1,  # SPH 5000, 1 MPPT
    # NEO and older PV models
    "BZP": Variant.PV | Variant.GEN | Variant.X1,  # Neo 800M-X, 2 MPPT
    "QNB": Variant.PV | Variant.GEN | Variant.X1,  # 1000-S, 1 MPPT
    "QMB": Variant.PV | Variant.GEN | Variant.X1,  # 1500-S, 1 MPPT
    "JLE": Variant.PV | Variant.GEN | Variant.X1,  # 5000 TL3-S
    "MVC": Variant.PV | Variant.GEN | Variant.X3,  # 12000 TL3-S
    "4FZ": Variant.PV | Variant.GEN | Variant.X1,  # 5000 MTL-S, 2 MPPT
    "BY3": Variant.PV | Variant.GEN | Variant.X1,  # 5000
}

# Firmware/build prefixes, used when no supported serial-number prefix is found.
FIRMWARE_PREFIX_VARIANTS: Final[dict[str, Variant]] = {
    "dha": Variant.PV | Variant.GEN | Variant.X3,  # PV TL3-SL 10-22kW
    "DL1": Variant.PV | Variant.GEN2 | Variant.X3,  # PV TL3-X 15kW (MOD)
    "DM1": Variant.PV | Variant.GEN2 | Variant.X3 | Variant.MPPT4,  # PV TL3-X 35kW (MID)
    "AH1": Variant.PV | Variant.GEN3 | Variant.X1,  # Hybrid SPH 4kW - 10kW
    "AJ1": Variant.PV | Variant.GEN4 | Variant.X1,  # PV TL-X 2.5kW - 6kW (MIN)
    "GH1": Variant.PV | Variant.GEN4 | Variant.X1,  # PV TL-X 2.5kW - 6kW (MIN)
    "AK1": Variant.PV | Variant.GEN4 | Variant.X1,  # MIN 3600TL-X2, 2 MPPT
    "AM1": Variant.PV | Variant.GEN4 | Variant.X1 | Variant.MPPT3,  # PV TL-X2 7kW - 120kW
    "RAA": Variant.HYBRID | Variant.GEN3 | Variant.X1,  # Hybrid SPH 3kW - 6kW
    "RA1": Variant.HYBRID | Variant.GEN3 | Variant.X1,  # Hybrid SPH 3kW - 6kW
    "SPH": Variant.HYBRID | Variant.GEN3 | Variant.X3,  # Hybrid SPH 4kW - 10kW
    "YA1": Variant.HYBRID | Variant.GEN3 | Variant.X3,  # Hybrid SPH 4kW - 10kW 3P TL UP
    "RH1": Variant.AC | Variant.GEN3 | Variant.X1,  # SPA 3000TL BL, no PV MPPT
    # The PV MIN TL-XE reports this firmware prefix too, despite having no
    # battery; it is caught by its serial prefix above. An unlisted TL-XE
    # serial falls through to here and is mislabelled HYBRID.
    "AL1": Variant.HYBRID | Variant.GEN4 | Variant.X1,  # Hybrid TL-XH 2.5kW - 6kW (MIN)
    "DN1": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # Hybrid TL3-XH (BP) (MOD/MID)
    "V": Variant.HYBRID | Variant.GEN4 | Variant.X3,  # Hybrid TL3-XH 3kW - 10kW (MOD)
    "067": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF5000ES branch
    "113": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF5000ES branch
    "500": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF5000ES branch
    "040": Variant.HYBRID | Variant.SPF | Variant.X1,  # SPF5000ES branch
}

# Holding registers the serial number may live at, in the order upstream probes
# them. Each holds a null-padded ASCII string.
SERIAL_NUMBER_REGISTERS: Final = (3001, 209, 23)

# The firmware string, probed when no serial prefix is recognised.
FIRMWARE_REGISTER: Final = 9

# SPF models that expose only one PV input even though the generic SPF block
# declares PV2 registers.
SPF_SINGLE_MPPT_SERIAL_PREFIXES: Final = ("YRE", "TTJ", "BNJ", "KAM", "067", "113", "500")


def variant_from_identifier(identifier: str | None, table: dict[str, Variant]) -> Variant | None:
    """Look ``identifier`` up by prefix in ``table``."""
    if not identifier:
        return None
    for prefix, variant in table.items():
        if identifier.startswith(prefix):
            return variant
    return None
