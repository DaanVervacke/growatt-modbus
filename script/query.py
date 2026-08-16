#!/usr/bin/env python3

"""Query a Growatt inverter and print every value.

Identifies the inverter on the wire, reads it once, and dumps it to the
terminal — the quickest way to check real hardware with no application around it.

::

    uv run script/query.py /dev/ttyUSB0 --transport serial --unit 1
    uv run script/query.py 192.168.1.50 --transport tcp --unit 1 --framer rtu
"""

from __future__ import annotations

import argparse
import asyncio

from modbus_connection import ModbusError
from modbus_connection.cli_helper import (
    CountingUnit,
    add_connection_args,
    connect_from_args,
    field_rows,
)

from growatt_modbus import GrowattComponent, detect

# The inverter is RS-485 RTU; over TCP it is reached through a gateway, which
# presents it either transparently (rtu) or as native Modbus TCP (socket).
CONNECTIONS = (("tcp", "rtu"), ("tcp", "socket"), ("serial", "rtu"))


def print_served(title: str, component: GrowattComponent) -> None:
    """Print a component, less the fields this inverter does not serve.

    ``for_variant`` narrows the read plan but leaves the class descriptors, so
    an unfiltered dump is half "—" and an unserved field then looks exactly like
    one whose read came back empty.
    """
    dead = set(component.declared_fields) - component.active_fields
    rows = [(name, value) for name, value in field_rows(component) if name not in dead]
    width = max((len(name) for name, _ in rows), default=0)
    print(f"\n{title}")
    print("-" * len(title))
    for name, value in rows:
        print(f"  {name.ljust(width)}  {value}")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_connection_args(parser, connections=CONNECTIONS)
    parser.add_argument("--unit", type=int, default=1, help="Modbus unit id")
    parser.add_argument("--eps", action="store_true", help="read the backup-output registers")
    parser.add_argument("--dcb", action="store_true", help="read the dry-contact-box registers")
    parser.add_argument("--apx", action="store_true", help="force the APX battery registers on")
    args = parser.parse_args()

    try:
        connection = await connect_from_args(args)
    except ModbusError as err:
        print(f"Could not connect: {err}")
        return 1

    counting = CountingUnit(connection.for_unit(args.unit))
    try:
        inverter = await detect(counting, read_eps=args.eps, read_dcb=args.dcb, read_apx=args.apx)
        report = await inverter.async_update()
    except LookupError as err:
        print(f"Could not identify the inverter: {err}")
        return 1
    except ModbusError as err:
        print(f"Could not read the inverter: {err}")
        return 1
    finally:
        await connection.close()

    print("Inverter")
    print("--------")
    print(f"  serial number  {inverter.serial_number or '—'}")
    print(f"  variant        {inverter.variant!r}")
    print(f"  firmware       {inverter.firmware_control_version or '—'}")

    # Which sub-systems exist depends on the variant detect() settled and on the
    # APX probe async_setup() runs, so walk POLLED rather than a fixed list —
    # a name this inverter has no use for is None.
    for name in inverter.POLLED:
        component = getattr(inverter, name)
        if component is not None:
            print_served(name, component)

    if report.failed:
        print("\nFailed to read")
        print("--------------")
        for name, error in sorted(report.failed.items()):
            print(f"  {name}: {error}")

    print(f"\n{counting.reads} Modbus reads")
    return 0


raise SystemExit(asyncio.run(main()))
