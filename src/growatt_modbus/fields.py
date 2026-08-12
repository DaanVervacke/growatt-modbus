"""Growatt-specific field codecs and the component base.

Most of the register map is expressible with the stock helpers from
``modbus_connection.model``. What is not, lives here:

- :class:`OptionField` — the integer-to-label maps the inverter uses for
  settings, invertible so the field can be written back by label;
- :class:`TimeOfDayField` — an hour/minute pair packed into one register;
- :class:`RtcField` — the six-register real-time clock;
- :func:`bms_power` / :func:`bms_current` — the APX battery's split-range
  signed encoding;
- :func:`inverter_module_code` — the packed module-version code.
"""

from __future__ import annotations

from datetime import datetime, time
from typing import TYPE_CHECKING, Any, ClassVar, Self

from modbus_connection.model import Component, NumberField, RegisterField
from modbus_connection.model.fields import PackedBitsField, WriteValidator

from .variants import Variant, matches

if TYPE_CHECKING:
    from collections.abc import Mapping

    from modbus_connection import ModbusUnit


# The inverter answers a read of at most 100 registers; the upstream integration
# splits its polls on the same boundary.
MAX_READ_SPAN = 100


class GrowattComponent(Component):
    """A Growatt sub-system, narrowed to the fields a given inverter serves.

    ``FIELD_VARIANTS`` tags every declared field with the ``allowedtypes`` mask
    it carries upstream. :meth:`for_variant` keeps only the fields that match the
    inverter, which also keeps the read plan off registers the model does not
    serve — a block read is atomic, so a single unserved register inside one
    would fail every field sharing it.
    """

    max_span = MAX_READ_SPAN

    FIELD_VARIANTS: ClassVar[dict[str, Variant]] = {}
    # Fields upstream excludes for particular serial-number prefixes.
    FIELD_BLACKLISTS: ClassVar[dict[str, tuple[str, ...]]] = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Which fields survived for_variant(). Everything else reads as None,
        # so a computed total needs this to tell "absent" from "not read yet".
        self.active_fields: frozenset[str] = frozenset(self.declared_fields)

    def serves(self, *names: str) -> bool:
        """Whether every named field is one this inverter serves."""
        return all(name in self.active_fields for name in names)

    @classmethod
    def field_names_for(cls, variant: Variant, serial_number: str | None = None) -> list[str]:
        """Return the declared fields this inverter serves."""
        names = []
        for name, mask in cls.FIELD_VARIANTS.items():
            if not matches(variant, mask):
                continue
            blacklist = cls.FIELD_BLACKLISTS.get(name)
            if blacklist and serial_number and serial_number.startswith(blacklist):
                continue
            names.append(name)
        return names

    @classmethod
    def for_variant(
        cls,
        unit: ModbusUnit,
        variant: Variant,
        serial_number: str | None = None,
    ) -> Self | None:
        """Build this component for ``variant``, or None if it serves no fields."""
        names = cls.field_names_for(variant, serial_number)
        if not names:
            return None
        component = cls(unit)
        component.restrict_fields(names)
        component.active_fields = frozenset(names)
        return component


def in_range(low: float, high: float, *sentinels: float) -> WriteValidator:
    """Build a validator rejecting a value outside the inverter's accepted range.

    ``sentinels`` are values outside the range that the register nonetheless
    accepts — the power limits take 255 to mean "no limit", which the upstream
    integration writes from a button rather than the slider.
    """
    allowed = frozenset(sentinels)

    def validate(value: Any) -> Any:
        if value not in allowed and not low <= value <= high:
            extra = f" (or {sorted(allowed)})" if allowed else ""
            raise ValueError(f"{value} is outside {low}..{high}{extra}")
        return value

    return validate


class OptionField(NumberField[str]):
    """A register whose value is one of a fixed set of labels.

    ``NumberField``'s ``convert`` mapping already decodes the label; this adds
    the inverse so a setting can be written back as the label the device reports.
    """

    def __init__(
        self,
        address: int,
        options: Mapping[int, str],
        *,
        signed: bool = False,
        writable: bool | WriteValidator = False,
        count: int = 1,
    ) -> None:
        super().__init__(
            address, convert=dict(options), signed=signed, writable=writable, count=count
        )
        self.options: dict[int, str] = dict(options)
        self._codes = {label: code for code, label in self.options.items()}

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode a label (or its raw code) back into a register word."""
        if isinstance(value, str):
            try:
                value = self._codes[value]
            except KeyError:
                raise ValueError(f"{value!r} is not one of {sorted(self._codes)}") from None
        return super().encode(value, scale_exponent)


def option(
    address: int,
    options: Mapping[int, str],
    *,
    writable: bool = False,
) -> OptionField:
    """Create a labelled-setting field."""
    return OptionField(address, options, writable=writable)


class PackedOptionField(PackedBitsField):
    """A labelled setting held in part of a register.

    Writing merges into the register, so the bits it shares with other settings
    survive — the Gen4 time slots pack a mode, an enable bit and a time into one
    word.
    """

    def __init__(
        self,
        address: int,
        start: int,
        width: int,
        options: Mapping[int, str],
        *,
        writable: bool | WriteValidator = False,
    ) -> None:
        super().__init__(address, start, width, writable=writable)
        self.options: dict[int, str] = dict(options)
        self._codes = {label: code for code, label in self.options.items()}

    def decode(self, words: list[int], scale_exponent: int | None = None) -> Any:
        return self.options.get(super().decode(words))

    def merge(self, word: int, value: Any) -> int:
        if isinstance(value, str):
            try:
                value = self._codes[value]
            except KeyError:
                raise ValueError(f"{value!r} is not one of {sorted(self._codes)}") from None
        return super().merge(word, value)


def packed_option(
    address: int,
    start: int,
    width: int,
    options: Mapping[int, str],
    *,
    writable: bool = False,
) -> PackedOptionField:
    """Create a labelled setting inside part of a register."""
    return PackedOptionField(address, start, width, options, writable=writable)


class TimeOfDayField(RegisterField[time]):
    """An hour/minute pair packed into one register: hour in bits 8-15, minute in 0-7.

    ``mask`` narrows the field to part of the register, for the Gen4 time slots
    that pack mode and enable bits into the top three bits alongside the time.
    """

    def __init__(
        self,
        address: int,
        *,
        mask: int = 0xFFFF,
        writable: bool | WriteValidator = False,
    ) -> None:
        super().__init__(address, writable=writable)
        self.mask = mask

    def decode(self, words: list[int], scale_exponent: int | None = None) -> time | None:
        raw = words[0] & self.mask
        hour, minute = raw >> 8, raw & 0xFF
        if hour > 23 or minute > 59:
            return None
        return time(hour, minute)

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        if not isinstance(value, time):
            raise ValueError(f"expected a datetime.time, got {value!r}")
        return [(value.hour << 8) | value.minute]


def time_of_day(address: int, *, mask: int = 0xFFFF, writable: bool = False) -> TimeOfDayField:
    """Create a packed hour/minute field."""
    return TimeOfDayField(address, mask=mask, writable=writable)


class RtcField(RegisterField[datetime]):
    """The real-time clock: six registers holding year, month, day, hour, minute, second.

    The year register carries only the last two digits.
    """

    def __init__(self, address: int, *, writable: bool | WriteValidator = False) -> None:
        super().__init__(address, count=6, writable=writable)

    def decode(self, words: list[int], scale_exponent: int | None = None) -> datetime | None:
        year, month, day, hour, minute, second = words
        try:
            return datetime(2000 + year % 100, month, day, hour, minute, second)
        except ValueError:
            return None  # the clock is unset or the read was torn

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        if not isinstance(value, datetime):
            raise ValueError(f"expected a datetime, got {value!r}")
        return [
            value.year % 100,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
        ]


def rtc(address: int, *, writable: bool = False) -> RtcField:
    """Create a real-time-clock field."""
    return RtcField(address, writable=writable)


class SplitRangeField(NumberField[float]):
    """The APX battery's signed values: a low positive band, a high band wrapping to negative.

    The module reports e.g. discharge power as 0..2500 and charge power as
    63035..65535 (i.e. -2500..-1), leaving the middle of the range meaningless.
    A value in neither band decodes to ``None`` rather than a fabricated number.
    """

    def __init__(
        self,
        address: int,
        *,
        scale: float = 1.0,
        positive_max: int,
        negative_min: int,
        unit: str | None = None,
    ) -> None:
        super().__init__(address, signed=False, scale=scale, unit=unit)
        self.positive_max = positive_max
        self.negative_min = negative_min

    def decode(self, words: list[int], scale_exponent: int | None = None) -> float | None:
        raw = words[0]
        if raw <= self.positive_max:
            return self._scale(raw, scale_exponent)  # type: ignore[no-any-return]
        if raw >= self.negative_min:
            return self._scale(raw - 65536, scale_exponent)  # type: ignore[no-any-return]
        return None


def bms_power(address: int) -> SplitRangeField:
    """APX module power in W: 0..2500 charging out, 63035..65535 as -2500..-1."""
    return SplitRangeField(address, positive_max=2500, negative_min=63035, unit="W")


def bms_current(address: int) -> SplitRangeField:
    """APX module current in A, 0.1-scaled, over the same split range."""
    return SplitRangeField(address, scale=0.1, positive_max=2500, negative_min=63035, unit="A")


class InverterModuleField(RegisterField[str]):
    """The packed module-version code held in two registers.

    Each of the eight hex digits is one module revision, reported against the
    fixed label sequence ``A B D T P U M S``.
    """

    LABELS = "ABDTPUMS"

    def __init__(self, address: int) -> None:
        super().__init__(address, count=2)

    def decode(self, words: list[int], scale_exponent: int | None = None) -> str:
        raw = (words[0] << 16) | words[1]
        digits = f"{raw:08x}"
        return "".join(
            f"{label}{digit}" for label, digit in zip(self.LABELS, digits, strict=True)
        ).upper()


def inverter_module_code(address: int) -> InverterModuleField:
    """Create a packed module-version field."""
    return InverterModuleField(address)


def total(*values: float | None) -> float | None:
    """Sum readings, or None if any of them is missing.

    A partial sum would silently under-report — a solar production total that
    dips to a fraction of its real value is worse than no value at all.
    """
    if any(value is None for value in values):
        return None
    return round(sum(v for v in values if v is not None), 3)
