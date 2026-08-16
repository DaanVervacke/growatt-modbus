# growatt-modbus

A standalone Python library that reads and controls **Growatt** solar inverters
over Modbus, exposed as a normal, object-oriented Python API.

The register maps are based on
[homeassistant-solax-modbus](https://github.com/wills106/homeassistant-solax-modbus)
(Apache-2.0), whose Growatt plugin they are extracted from. This library keeps
that project's licence and is a derived work of it.

## Design

- It **consumes the connection abstraction**, not a backend: you build a
  [`modbus_connection.ModbusUnit`](https://github.com/home-assistant-libs/modbus-connection)
  and hand it over. You choose and own the transport.
- **Five generations, five register maps.** Growatt's protocol generations are
  not layers on one map — the same input register means one thing on an SPF and
  something else on a MIN TL-XH. Each generation therefore has its own device
  class and its own components, so an attribute always means what its name says.
- **A model only reads the registers it has.** Every field carries the
  `allowedtypes` mask it has upstream; the inverter's `Variant` bits (phase
  count, PV / AC / hybrid, MPPT count, backup output, dry contact box) select
  the subset at construction, via `restrict_fields`. This is not cosmetic: a
  Modbus block read is atomic, so one register the inverter does not serve would
  fail every field sharing its block.
- **Settings are writable**, by the same names they are read under — a label for
  a mode, a `datetime.time` for a schedule slot, a number for a limit. Ranges
  are validated before anything reaches the inverter, and a setting packed into
  part of a register is written read-modify-write, so its neighbours survive.

## Supported inverters

| Generation | Models | Class | Fields |
| --- | --- | --- | --- |
| `GEN` | Legacy PV: TL-S, TL3-S, NEO | `Gen1Inverter` | 46 |
| `GEN2` | MOD / MID TL3-X PV | `Gen2Inverter` | 77 |
| `GEN3` | SPH, SPA storage | `Gen3Inverter` | 192 |
| `GEN4` | MIN / MOD / MID / WIT TL-XH hybrid, TL-X PV | `Gen4Inverter` | 322 |
| `SPF` | SPF, SPE off-grid | `SpfInverter` | 69 |

`detect()` identifies the generation and the model's options from the serial
number, using the same prefix tables as upstream — 63 serial prefixes and 20
firmware prefixes, covering MIN, MOD, MID, MAX, MIC, SPH, SPA, SPE, SPF, WIT and
NEO families.

Within a generation, the `Variant` bits decide which fields exist:

| Bits | Selects |
| --- | --- |
| `X1` / `X3` | single- or three-phase grid registers |
| `PV` / `AC` / `HYBRID` / `MIC` | inverter category |
| `MPPT3` … `MPPT10` | PV strings beyond the two every model has |
| `EPS` | the backup-output registers |
| `DCB` | the dry-contact-box registers |
| `APX` | the APX HV battery's own register bank |

`EPS` and `DCB` are opted into (`detect(read_eps=True)`). `APX` is detected: a
Gen4 hybrid reads the BMS type the inverter reports and only then polls the 29
blocks the APX bank spans, because a hybrid with an LG or ARK pack refuses every
one of them. `detect(read_apx=True)` forces it on for a device that misreports.

## Use

```python
import asyncio
from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection
from growatt_modbus import Gen4Inverter, detect


async def main() -> None:
    conn = ModbusConnection(ModbusTcpParams(host="192.168.1.50", framer="rtu"))
    try:
        inverter = await detect(conn.for_unit(1), read_eps=True)
        assert isinstance(inverter, Gen4Inverter)  # a MIN TL-XH, say
        await inverter.async_update()

        print("Serial:", inverter.serial_number)
        print("Variant:", repr(inverter.variant))
        print("PV1 power:", inverter.hybrid_status.pv_power_1, "W")
        print("Battery SOC:", inverter.hybrid_status.battery_soc, "%")
        print("Battery power:", inverter.battery_combined_power, "W")
        print("Fault:", inverter.inverter_fault_text)

        # Settings are written by the same names they are read under.
        await inverter.hybrid_settings.write("ems_charging_rate", 80)
        await inverter.hybrid_settings.write("time_1_mode", "Battery First")
    finally:
        await conn.close()


asyncio.run(main())
```

If you already know the model, skip detection:

```python
from growatt_modbus import Variant, build

inverter = build(unit, Variant.SPF | Variant.HYBRID | Variant.X1, "KAM0000001")
```

`detect()` returns whichever device class matches the inverter it found, so
narrow it (with `isinstance`, or `match`) before reaching for a generation's own
sub-systems.

Passing the serial number matters for the handful of models whose registers a
prefix rules out — a KAM-series SPF has one PV input, so its PV2 registers are
never read.

### Polling one sub-system

Each sub-system is an independently updatable component with its own listeners:

```python
await inverter.hybrid_status.async_update()  # just the live measurements
unsub = inverter.hybrid_status.add_update_listener(refresh_my_entity)
```

`inverter.async_update()` refreshes each of them in turn — 2 requests for an
SPF, 20 for an SPH, 25 for a MIN TL-XH and 54 with an APX battery, none wider
than the 100 registers the inverter answers.

### Partial updates

A poll reads each sub-system independently, the way the integration reads its
blocks: one slow or refused block does not take the rest of the poll with it.
`async_update()` returns an `UpdateReport` — a failed component keeps its
previous values, does not notify its listeners, and is listed by attribute name
with its error, while every other component refreshes and notifies once the
whole poll is done. A dead link (`ModbusConnectionError`) raises, and so does a
timeout on the very first component: nothing answered at all, so the inverter is
asleep or unreachable and walking the rest would only pay a timeout each. Once
any component has answered — refreshed *or* refused — a later timeout is
contained like any other failure:

```python
report = await inverter.async_update()
for name, error in report.failed.items():
    print(f"{name} kept its previous values: {error}")
```

## Connection

Growatt inverters speak **Modbus RTU on RS-485**, reached either directly over
serial or through a transparent RTU-over-TCP gateway (hence `framer="rtu"` on a
TCP connection above). The library never opens a connection itself — it takes
the `ModbusUnit` you give it.

**ASCII framing over TCP is not supported.** Do not construct the connection you
hand this library with `framer="ascii"`; the register semantics here assume RTU
or socket framing, and ASCII-over-TCP is out of scope.

## Checking a real inverter

`script/query.py` identifies the inverter, reads it once and prints everything
it has, which is the quickest way to see whether one is wired and addressed
correctly:

```bash
uv run script/query.py /dev/ttyUSB0 --transport serial --unit 1
uv run script/query.py 192.168.1.50 --transport tcp --unit 1 --framer rtu
```

It prints the detected variant and the read count as well, so what this inverter
turned out to be — and how few requests its poll takes — is visible against real
hardware rather than only in the tests. Add `--eps`, `--dcb` or `--apx` to bring
in the register groups those options carry.

## Scope

Every entity in the upstream Growatt plugin that carries register knowledge is
modelled — 616 sensor and 145 writable declarations, translated mechanically and
then checked back against the source field by field on address, register space,
word count, scale, signedness, option map and writability.

Two things upstream does are deliberately not carried over, because they are
Home Assistant concerns rather than device knowledge: entity presentation
(icons, device classes, entity categories, translation keys), and the
UI-local state behind the Gen4 time-slot editor. The slot registers themselves
are modelled directly — start time, end time, priority mode and the enable bit
are four fields over the two registers the inverter actually has, so the
upstream "update" and "clear" buttons are not needed. The upstream buttons that
do write a register (clock sync, and the "not limited" power-limit command) are
modelled as writable fields instead.

Where upstream declares one key twice within a single generation, at two
different registers, both are kept here under distinct names — the collision is
real, and dropping either would lose a register:

- `inverter_temperature` (input 93) and `inverter_temperature_alt` (input 32) on
  Gen2;
- `battery_type` (holding 1048, the setting) and `battery_type_reported`
  (input 119, the reported value, with a different code map) on Gen3.

## Develop / test

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check . && uv run mypy
```

Tests run against the in-memory mock backend that ships with `modbus-connection`
(its `mock_modbus_unit` pytest fixture) — no hardware, no Modbus server, and no
Home Assistant.
