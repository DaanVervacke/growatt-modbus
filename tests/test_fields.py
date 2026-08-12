"""The Growatt-specific codecs, decoded and encoded directly."""

from __future__ import annotations

from datetime import datetime, time

import pytest

from growatt_modbus.fields import (
    bms_current,
    bms_power,
    in_range,
    inverter_module_code,
    option,
    packed_option,
    rtc,
    time_of_day,
)

MODES = {0: "Off", 1: "On", 2: "Auto"}


class TestOptionField:
    def test_decodes_a_code_to_its_label(self) -> None:
        assert option(0, MODES).decode([2]) == "Auto"

    def test_an_unmapped_code_decodes_to_none(self) -> None:
        assert option(0, MODES).decode([7]) is None

    def test_encodes_a_label_back_to_its_code(self) -> None:
        assert option(0, MODES, writable=True).encode("Auto") == [2]

    def test_encodes_a_raw_code_unchanged(self) -> None:
        assert option(0, MODES, writable=True).encode(1) == [1]

    def test_rejects_a_label_the_device_has_no_code_for(self) -> None:
        with pytest.raises(ValueError, match="not one of"):
            option(0, MODES, writable=True).encode("Turbo")


class TestPackedOptionField:
    # Bits 13-14 of a Gen4 time-slot register hold the priority mode.
    def test_decodes_only_its_own_bits(self) -> None:
        field = packed_option(0, 13, 2, MODES)
        assert field.decode([0b010_0_1000_0011_0000]) == "Auto"

    def test_merging_leaves_the_neighbouring_bits_alone(self) -> None:
        field = packed_option(0, 13, 2, MODES, writable=True)
        word = 0b1000_0000_0000_1111  # enable bit set, a time in the low bits
        merged = field.merge(word, "On")
        assert merged == 0b1010_0000_0000_1111

    def test_merging_accepts_a_label_or_a_code(self) -> None:
        field = packed_option(0, 13, 2, MODES, writable=True)
        assert field.merge(0, "Auto") == field.merge(0, 2)

    def test_rejects_an_unknown_label(self) -> None:
        with pytest.raises(ValueError, match="not one of"):
            packed_option(0, 13, 2, MODES, writable=True).merge(0, "Turbo")


class TestTimeOfDayField:
    def test_decodes_hour_from_the_high_byte_and_minute_from_the_low(self) -> None:
        assert time_of_day(0).decode([(21 << 8) | 45]) == time(21, 45)

    def test_masks_off_the_flags_a_gen4_slot_packs_alongside_the_time(self) -> None:
        # Bit 15 (enabled) and bit 14 (mode) set, on top of 06:30.
        raw = 0b1100_0000_0000_0000 | (6 << 8) | 30
        assert time_of_day(0, mask=0x1FFF).decode([raw]) == time(6, 30)
        # Without the mask the flags corrupt the hour, which is not a valid time.
        assert time_of_day(0).decode([raw]) is None

    @pytest.mark.parametrize("raw", [(24 << 8), (12 << 8) | 60, 0xFFFF])
    def test_an_impossible_time_decodes_to_none(self, raw: int) -> None:
        assert time_of_day(0).decode([raw]) is None

    def test_encodes_back_to_the_same_word(self) -> None:
        assert time_of_day(0, writable=True).encode(time(21, 45)) == [(21 << 8) | 45]

    def test_rejects_a_value_that_is_not_a_time(self) -> None:
        with pytest.raises(ValueError, match="datetime.time"):
            time_of_day(0, writable=True).encode("21:45")


class TestRtcField:
    def test_decodes_six_registers_into_a_datetime(self) -> None:
        assert rtc(45).decode([24, 6, 15, 13, 5, 30]) == datetime(2024, 6, 15, 13, 5, 30)

    def test_an_unset_clock_decodes_to_none(self) -> None:
        assert rtc(45).decode([0, 0, 0, 0, 0, 0]) is None

    def test_round_trips(self) -> None:
        field = rtc(45, writable=True)
        moment = datetime(2031, 12, 1, 23, 59, 59)
        assert field.decode(field.encode(moment)) == moment


class TestSplitRangeField:
    # The APX modules report a positive band, then wrap for negative values.
    def test_decodes_the_positive_band_as_is(self) -> None:
        assert bms_power(0).decode([1800]) == 1800

    def test_decodes_the_high_band_as_negative(self) -> None:
        assert bms_power(0).decode([65536 - 500]) == -500

    def test_the_gap_between_the_bands_is_not_a_reading(self) -> None:
        assert bms_power(0).decode([30000]) is None

    def test_current_is_scaled_after_the_sign_is_resolved(self) -> None:
        assert bms_current(0).decode([1234]) == 123.4
        assert bms_current(0).decode([65536 - 1234]) == -123.4


def test_inverter_module_code_labels_each_hex_digit() -> None:
    # 0x12345678 over two registers, against the fixed A B D T P U M S sequence.
    assert inverter_module_code(28).decode([0x1234, 0x5678]) == "A1B2D3T4P5U6M7S8"


class TestInRange:
    def test_passes_a_value_inside_the_range(self) -> None:
        assert in_range(10, 100)(55) == 55

    @pytest.mark.parametrize("value", [9, 101])
    def test_rejects_a_value_outside_it(self, value: int) -> None:
        with pytest.raises(ValueError, match="outside"):
            in_range(10, 100)(value)
