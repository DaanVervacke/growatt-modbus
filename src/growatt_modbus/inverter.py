"""The device objects a consumer works with.

Growatt's five protocol generations are five different register maps, so each
gets its own device class with its own typed sub-systems. :func:`detect` reads
the inverter's serial number and hands back the right one; a caller that already
knows what it has can construct the class directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from modbus_connection import (
    IllegalDataAddressError,
    IllegalFunctionError,
    ModbusConnectionError,
    ModbusError,
)

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
    Gen4BatteryModuleSettings,
    Gen4BatteryModuleStatus,
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
    BMS_TYPE_APX,
    BMS_TYPE_REGISTER,
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


@dataclass(frozen=True)
class UpdateReport:
    """What one poll refreshed, by the device's component attribute names.

    A failed component kept its previous values and did not notify; the error
    that failed it rides along. A dead link is never in here — the update
    raises ``ModbusConnectionError`` instead of reporting partial silence.
    """

    updated: set[str]
    failed: dict[str, ModbusError]

    @property
    def complete(self) -> bool:
        """Whether every polled component refreshed."""
        return not self.failed


class GrowattInverter:
    """Base for the per-generation device objects.

    Subclasses build their sub-systems in ``_build`` and expose them as typed
    attributes; ``POLLED`` names the ones a poll refreshes, in read order. Each
    is read independently, so one refused block cannot blank the device.
    """

    GENERATION: ClassVar[Variant]
    # Every component attribute a poll may refresh, in read order. A name whose
    # attribute is None on this inverter is dropped by async_setup().
    POLLED: ClassVar[tuple[str, ...]]

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
        self._build()
        self._polled: list[str] | None = None

    def _component[C: GrowattComponent](self, cls: type[C]) -> C | None:
        """Build one sub-system for this inverter, or None if it serves no fields."""
        return cls.for_variant(self.unit, self.variant, self.serial_number)

    def _build(self) -> None:
        raise NotImplementedError

    async def async_setup(self) -> None:
        """Settle which sub-systems this inverter polls.

        Run by the first :meth:`async_update` if the caller does not run it
        itself. A failure leaves the device unset up, so the next update retries.
        """
        self._polled = [name for name in self.POLLED if getattr(self, name) is not None]

    async def async_update(self) -> UpdateReport:
        """Refresh every sub-system this inverter serves, one at a time.

        Components are read independently, the way the integration reads its
        blocks: a sub-system whose read fails keeps its previous values while
        the rest still refresh. Listeners fire only after every component has
        been tried, and only on the ones that refreshed. A failure of the link
        itself raises ``ModbusConnectionError`` instead of reporting.
        """
        if self._polled is None:
            await self.async_setup()
        assert self._polled is not None  # async_setup() builds it
        updated: set[str] = set()
        failed: dict[str, ModbusError] = {}
        for name in self._polled:
            component: GrowattComponent = getattr(self, name)
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:
                raise
            except ModbusError as err:
                failed[name] = err
            else:
                updated.add(name)
        for name in updated:
            fresh: GrowattComponent = getattr(self, name)
            fresh.notify()
        return UpdateReport(updated, failed)

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Refresh, and additionally return the raw register words read.

        A diagnostic dump rather than a poll: it stops at the first refusal,
        because there the error is the interesting part. The identifier
        registers :func:`detect` reads are included — a poll never touches them,
        and they are the first thing an issue report is read for. The components
        refresh but do not notify, so a download is not seen as a poll.
        """
        if self._polled is None:
            await self.async_setup()
        assert self._polled is not None  # async_setup() builds it
        raw: dict[str, dict[int, int | bool]] = {"holding": await self._read_identity()}
        for name in self._polled:
            component: GrowattComponent = getattr(self, name)
            for space, values in (await component.async_read_raw(notify=False)).items():
                raw.setdefault(space, {}).update(values)
        return {space: dict(sorted(values.items())) for space, values in raw.items() if values}

    async def _read_identity(self) -> dict[int, int | bool]:
        """The identifier words :func:`detect` probes, skipping refused addresses.

        An inverter serves one of the candidate addresses and refuses the rest,
        so unlike in a component read a refusal here is ordinary.
        """
        words: dict[int, int | bool] = {}
        for address in (*SERIAL_NUMBER_REGISTERS, FIRMWARE_REGISTER):
            try:
                read = await self.unit.read_holding_registers(address, _IDENTIFIER_WORDS)
            except (IllegalDataAddressError, IllegalFunctionError):
                continue
            words.update(enumerate(read, address))
        return words

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
    POLLED = ("settings", "status")

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
    POLLED = ("settings", "status")

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
    POLLED = (
        "settings",
        "status",
        "storage_settings",
        "storage_status",
        "vpp_settings",
    )

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
    POLLED = (
        "settings",
        "status",
        "hybrid_settings",
        "hybrid_status",
        "battery_settings",
        "battery_module_settings",
        "battery_status",
        "battery_module_status",
        "vpp_settings",
    )

    settings: Gen4Settings
    status: Gen4Status

    def _build(self) -> None:
        settings = self._component(Gen4Settings)
        status = self._component(Gen4Status)
        assert settings is not None and status is not None
        self.settings, self.status = settings, status
        self.hybrid_settings = self._component(Gen4HybridSettings)
        self.hybrid_status = self._component(Gen4HybridStatus)
        self.vpp_settings = self._component(Gen4VppSettings)
        self._build_apx()

    def _build_apx(self) -> None:
        """Build the APX battery sub-systems, if the variant carries ``APX``."""
        self.battery_settings = self._component(Gen4BatterySettings)
        self.battery_module_settings = self._component(Gen4BatteryModuleSettings)
        self.battery_status = self._component(Gen4BatteryStatus)
        self.battery_module_status = self._component(Gen4BatteryModuleStatus)

    async def async_setup(self) -> None:
        """Probe for an APX battery, then settle what to poll.

        The APX register bank exists only behind an APX HV pack — a hybrid with
        an LG or ARK battery refuses all 29 of its blocks — so it is opted into
        with ``Variant.APX`` or detected here from the BMS type the inverter
        reports.
        """
        if Variant.HYBRID in self.variant and Variant.APX not in self.variant:
            if await _has_apx_battery(self.unit):
                self.variant |= Variant.APX
                self._build_apx()
        await super().async_setup()

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
    POLLED = ("settings", "status")

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
    read_apx: bool = False,
) -> GrowattInverter:
    """Identify the inverter on ``unit`` and build the matching device object.

    The serial number is probed at each of the addresses Growatt has used, then
    the firmware string, exactly as the upstream integration does. Set
    ``read_eps`` / ``read_dcb`` for an inverter with a backup output or a dry
    contact box, which adds the registers those bring. ``read_apx`` forces the
    APX battery registers on; left off, a Gen4 hybrid detects the pack itself
    at :meth:`GrowattInverter.async_setup`.

    Raises ``LookupError`` if no prefix identifies the inverter, and the
    underlying error if one of the probes failed transiently — a device that
    timed out is unidentified for now, not unrecognised for good.
    """
    identifier: str | None = None
    variant: Variant | None = None
    failures: list[ModbusError] = []

    for address in SERIAL_NUMBER_REGISTERS:
        candidate = await _probe_identifier(unit, address, failures)
        found = variant_from_identifier(candidate, SERIAL_PREFIX_VARIANTS)
        if found is not None:
            identifier, variant = candidate, found
            break

    if variant is None:
        firmware = await _probe_identifier(unit, FIRMWARE_REGISTER, failures)
        variant = variant_from_identifier(firmware, FIRMWARE_PREFIX_VARIANTS)
        if variant is None:
            # Some older models expose a model prefix only at the firmware register.
            variant = variant_from_identifier(firmware, SERIAL_PREFIX_VARIANTS)
        identifier = firmware
        if variant is None:
            if failures:
                raise failures[0]
            raise LookupError(f"unrecognised Growatt inverter (identifier {identifier or '?'})")

    if read_eps:
        variant |= Variant.EPS
    if read_dcb:
        variant |= Variant.DCB
    if read_apx:
        variant |= Variant.APX
    return build(unit, variant, identifier)


# Every identifier the inverter reports is read as ten ASCII characters, at
# whichever address answers — the same probe upstream uses.
_IDENTIFIER_WORDS = 5


async def _probe_identifier(
    unit: ModbusUnit, address: int, failures: list[ModbusError]
) -> str | None:
    """Read an identifier, collecting a transient failure rather than raising it.

    One slow address must not stop the remaining ones being tried; ``detect``
    re-raises what was collected if nothing identified the inverter.
    """
    try:
        return await _read_identifier(unit, address)
    except ModbusConnectionError:
        raise
    except ModbusError as err:
        failures.append(err)
        return None


async def _read_identifier(unit: ModbusUnit, address: int) -> str | None:
    """Read an identifier string, or None if the inverter has none there.

    Only a refusal means the address is unserved; every other error propagates.
    """
    try:
        registers = await unit.read_holding_registers(address, _IDENTIFIER_WORDS)
    except (IllegalDataAddressError, IllegalFunctionError):
        return None
    raw = b"".join(word.to_bytes(2, "big") for word in registers)
    return raw.decode("ascii", errors="ignore").rstrip("\x00").strip() or None


async def _has_apx_battery(unit: ModbusUnit) -> bool:
    """Whether an APX HV pack is attached, from the BMS type the inverter reports.

    Only a refused register means "no APX bank"; anything transient propagates,
    so a timeout is retried on the next update rather than latched as absence.
    """
    try:
        words = await unit.read_holding_registers(BMS_TYPE_REGISTER, 1)
    except (IllegalDataAddressError, IllegalFunctionError):
        return False
    return words[0] == BMS_TYPE_APX


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
