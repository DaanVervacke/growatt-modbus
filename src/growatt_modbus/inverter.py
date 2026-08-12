"""The device objects a consumer works with.

Growatt's five protocol generations are five different register maps, so each
gets its own device class with its own typed sub-systems. :func:`detect` reads
the inverter's serial number and hands back the right one; a caller that already
knows what it has can construct the class directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from modbus_connection import ModbusExceptionError
from modbus_connection.model import ComponentGroup

from .enums import INVERTER_FAULT, INVERTER_WARNING
from .fields import GrowattComponent, total
from .gen1 import Gen1Settings, Gen1Status
from .gen2 import Gen2Settings, Gen2Status
from .gen3 import (
    Gen3Settings,
    Gen3Status,
    Gen3StorageSettings,
    Gen3StorageStatus,
    Gen3VppSettings,
)
from .gen4 import (
    Gen4BatterySettings,
    Gen4BatteryStatus,
    Gen4HybridSettings,
    Gen4HybridStatus,
    Gen4Settings,
    Gen4Status,
    Gen4VppSettings,
)
from .spf import SpfSettings, SpfStatus
from .variants import (
    FIRMWARE_PREFIX_VARIANTS,
    FIRMWARE_REGISTER,
    SERIAL_NUMBER_REGISTERS,
    SERIAL_PREFIX_VARIANTS,
    Variant,
    generation,
    variant_from_identifier,
)

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class GrowattInverter:
    """Base for the per-generation device objects.

    Subclasses build their sub-systems in ``_build`` and expose them as typed
    attributes; everything polled is refreshed in one pooled set of reads.
    """

    GENERATION: ClassVar[Variant]

    def __init__(
        self,
        unit: ModbusUnit,
        variant: Variant,
        serial_number: str | None = None,
    ) -> None:
        """Build the sub-systems this inverter serves.

        Raises ``ValueError`` if ``variant`` is not of this class's generation.
        """
        if generation(variant) is not self.GENERATION:
            raise ValueError(f"{type(self).__name__} needs {self.GENERATION!r}, got {variant!r}")
        self.unit = unit
        self.variant = variant
        self.serial_number = serial_number
        self.components: list[GrowattComponent] = []
        self._build()
        self._group = ComponentGroup(unit, list(self.components))

    def _component[C: GrowattComponent](self, cls: type[C]) -> C | None:
        """Build one sub-system for this inverter, registering it for polling."""
        component = cls.for_variant(self.unit, self.variant, self.serial_number)
        if component is not None:
            self.components.append(component)
        return component

    def _build(self) -> None:
        raise NotImplementedError

    async def async_update(self) -> None:
        """Refresh every sub-system in one pooled set of block reads."""
        await self._group.async_update()

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Refresh, and additionally return the raw register words read."""
        return await self._group.async_read_raw()

    @property
    def firmware_control_version(self) -> str | None:
        """The control firmware version, as the ASCII part joined to the numeric part."""
        settings = getattr(self, "settings", None)
        if settings is None:
            return None
        ascii_part = settings.firmware_control_version_ascii
        number = settings.firmware_control_version_number
        if ascii_part is None or number is None:
            return None
        return f"{ascii_part}-{number:04}"


class Gen1Inverter(GrowattInverter):
    """A legacy Growatt PV inverter (TL-S, TL3-S, NEO)."""

    GENERATION = Variant.GEN

    settings: Gen1Settings
    status: Gen1Status

    def _build(self) -> None:
        settings = self._component(Gen1Settings)
        status = self._component(Gen1Status)
        assert settings is not None and status is not None
        self.settings, self.status = settings, status


class Gen2Inverter(GrowattInverter):
    """A Growatt MOD / MID TL3-X PV inverter."""

    GENERATION = Variant.GEN2

    settings: Gen2Settings
    status: Gen2Status

    def _build(self) -> None:
        settings = self._component(Gen2Settings)
        status = self._component(Gen2Status)
        assert settings is not None and status is not None
        self.settings, self.status = settings, status

    @property
    def today_s_solar_energy(self) -> float | None:
        """Today's solar energy, summed over the PV inputs this model has (kWh)."""
        return _pv_total(self.status, "today_s_pv{}_solar_energy")


class Gen3Inverter(GrowattInverter):
    """A Growatt SPH or SPA storage inverter."""

    GENERATION = Variant.GEN3

    settings: Gen3Settings
    status: Gen3Status

    def _build(self) -> None:
        settings = self._component(Gen3Settings)
        status = self._component(Gen3Status)
        assert settings is not None and status is not None
        self.settings, self.status = settings, status
        self.storage_settings = self._component(Gen3StorageSettings)
        self.storage_status = self._component(Gen3StorageStatus)
        self.vpp_settings = self._component(Gen3VppSettings)

    @property
    def today_s_solar_energy(self) -> float | None:
        """Today's solar energy, summed over the PV inputs this model has (kWh)."""
        return _pv_total(self.status, "today_s_pv{}_solar_energy")

    @property
    def battery_combined_power(self) -> float | None:
        """Battery power: positive discharging, negative charging (W)."""
        if self.storage_status is None:
            return None
        return _battery_combined_power(self.storage_status)


class Gen4Inverter(GrowattInverter):
    """A Growatt MIN / MOD / MID / WIT TL-XH hybrid or TL-X PV inverter."""

    GENERATION = Variant.GEN4

    settings: Gen4Settings
    status: Gen4Status

    def _build(self) -> None:
        settings = self._component(Gen4Settings)
        status = self._component(Gen4Status)
        assert settings is not None and status is not None
        self.settings, self.status = settings, status
        self.hybrid_settings = self._component(Gen4HybridSettings)
        self.hybrid_status = self._component(Gen4HybridStatus)
        self.battery_settings = self._component(Gen4BatterySettings)
        self.battery_status = self._component(Gen4BatteryStatus)
        self.vpp_settings = self._component(Gen4VppSettings)

    @property
    def battery_combined_power(self) -> float | None:
        """Battery power: positive discharging, negative charging (W)."""
        if self.hybrid_status is None:
            return None
        return _battery_combined_power(self.hybrid_status)

    @property
    def battery_voltage(self) -> float | None:
        """Battery voltage (V).

        The raw register is 0.01-scaled, except on an APX HV pack (BMS
        monitoring version ``ZECA``) where it is 0.1-scaled.
        """
        if self.hybrid_status is None:
            return None
        raw = self.hybrid_status.battery_voltage
        if raw is None:
            return None
        version = self.hybrid_settings.bms_monitoring_version if self.hybrid_settings else None
        return round(raw / (10 if version == "ZECA" else 100), 2)

    @property
    def total_grid_power_va(self) -> float | None:
        """Apparent grid power summed over the three phases (VA)."""
        status = self.hybrid_status
        if status is None or not status.serves("grid_power_l1", "grid_power_l2", "grid_power_l3"):
            return None
        return total(status.grid_power_l1, status.grid_power_l2, status.grid_power_l3)

    @property
    def inverter_warning_text(self) -> str | None:
        """The active warning, from its main and sub code."""
        return _coded_text(self, INVERTER_WARNING, "warning")

    @property
    def inverter_fault_text(self) -> str | None:
        """The active fault, from its main and sub code."""
        return _coded_text(self, INVERTER_FAULT, "fault")


class SpfInverter(GrowattInverter):
    """A Growatt SPF or SPE off-grid inverter."""

    GENERATION = Variant.SPF

    settings: SpfSettings
    status: SpfStatus

    def _build(self) -> None:
        settings = self._component(SpfSettings)
        status = self._component(SpfStatus)
        assert settings is not None and status is not None
        self.settings, self.status = settings, status

    @property
    def pv_power_total(self) -> float | None:
        """Total PV power over both inputs (W)."""
        return _pv_total(self.status, "pv_power_{}", count=2)

    @property
    def today_s_solar_energy(self) -> float | None:
        """Today's solar energy over both PV inputs (kWh)."""
        return _pv_total(self.status, "today_s_solar_energy_pv{}", count=2)

    @property
    def total_solar_energy(self) -> float | None:
        """Lifetime solar energy over both PV inputs (kWh)."""
        return _pv_total(self.status, "total_solar_energy_pv{}", count=2)


_INVERTERS: dict[Variant, type[GrowattInverter]] = {
    Variant.GEN: Gen1Inverter,
    Variant.GEN2: Gen2Inverter,
    Variant.GEN3: Gen3Inverter,
    Variant.GEN4: Gen4Inverter,
    Variant.SPF: SpfInverter,
}


def build(
    unit: ModbusUnit,
    variant: Variant,
    serial_number: str | None = None,
) -> GrowattInverter:
    """Build the device object for a known variant."""
    return _INVERTERS[generation(variant)](unit, variant, serial_number)


async def detect(
    unit: ModbusUnit,
    *,
    read_eps: bool = False,
    read_dcb: bool = False,
) -> GrowattInverter:
    """Identify the inverter on ``unit`` and build the matching device object.

    The serial number is probed at each of the addresses Growatt has used, then
    the firmware string, exactly as the upstream integration does. Set
    ``read_eps`` / ``read_dcb`` for an inverter with a backup output or a dry
    contact box, which adds the registers those bring.

    Raises ``LookupError`` if no prefix identifies the inverter.
    """
    identifier: str | None = None
    variant: Variant | None = None

    for address in SERIAL_NUMBER_REGISTERS:
        candidate = await _read_identifier(unit, address)
        found = variant_from_identifier(candidate, SERIAL_PREFIX_VARIANTS)
        if found is not None:
            identifier, variant = candidate, found
            break

    if variant is None:
        firmware = await _read_identifier(unit, FIRMWARE_REGISTER)
        variant = variant_from_identifier(firmware, FIRMWARE_PREFIX_VARIANTS)
        if variant is None:
            # Some older models expose a model prefix only at the firmware register.
            variant = variant_from_identifier(firmware, SERIAL_PREFIX_VARIANTS)
        identifier = firmware
        if variant is None:
            raise LookupError(f"unrecognised Growatt inverter (identifier {identifier or '?'})")

    if read_eps:
        variant |= Variant.EPS
    if read_dcb:
        variant |= Variant.DCB
    return build(unit, variant, identifier)


# Every identifier the inverter reports is read as ten ASCII characters, at
# whichever address answers — the same probe upstream uses.
_IDENTIFIER_WORDS = 5


async def _read_identifier(unit: ModbusUnit, address: int) -> str | None:
    """Read an identifier string, or None if the inverter has none there."""
    try:
        registers = await unit.read_holding_registers(address, _IDENTIFIER_WORDS)
    except ModbusExceptionError:
        return None
    raw = b"".join(word.to_bytes(2, "big") for word in registers)
    return raw.decode("ascii", errors="ignore").rstrip("\x00").strip() or None


def _pv_total(status: GrowattComponent, pattern: str, count: int = 4) -> float | None:
    """Sum a per-PV-input reading over the inputs this inverter actually has."""
    names = [pattern.format(n) for n in range(1, count + 1)]
    served = [name for name in names if status.serves(name)]
    if not served:
        return None
    return total(*(getattr(status, name) for name in served))


def _battery_combined_power(status: Gen3StorageStatus | Gen4HybridStatus) -> float | None:
    """Discharge power less charge power."""
    if not status.serves("battery_discharge_power", "battery_charge_power"):
        return None
    discharge = status.battery_discharge_power
    charge = status.battery_charge_power
    if discharge is None or charge is None:
        return None
    return round(discharge - charge, 3)


def _coded_text(
    inverter: Gen4Inverter,
    table: dict[tuple[int, int], str],
    kind: str,
) -> str | None:
    """Look a (main, sub) code pair up in a fault or warning table."""
    status = inverter.status
    main = getattr(status, f"inverter_{kind}_maincode", None)
    sub = getattr(status, f"inverter_{kind}_subcode", None)
    if main is None or sub is None:
        return None
    return table.get((main, sub), f"Unknown (main={main}, sub={sub})")
