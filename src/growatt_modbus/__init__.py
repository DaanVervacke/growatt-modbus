"""growatt-modbus — read and control a Growatt inverter over Modbus.

Hand a :class:`~modbus_connection.ModbusUnit` to :func:`detect`, which
identifies the inverter from its serial number and returns the device object for
its protocol generation::

    inverter = await detect(connection.for_unit(1))
    await inverter.async_update()
    inverter.status.pv_power_1

Growatt's five generations are five different register maps — the same address
means different things on an SPF and on a MIN TL-XH — so each has its own
device class and its own components. Within a generation the fields a model
actually serves are selected from its :class:`Variant` bits (phase count, PV /
AC / hybrid, MPPT count, backup output, APX battery), so a poll never reads a
register the inverter does not have.

Each component is polled on its own, so one refused block cannot blank the
device: :meth:`GrowattInverter.async_update` returns an :class:`UpdateReport`
naming what refreshed and what kept its previous values.

ASCII framing over TCP is not supported.
"""

from .enums import (
    INVERTER_FAULT,
    INVERTER_STATE,
    INVERTER_WARNING,
    MODULE_STATUS,
    MODULE_WARNING,
    RUN_MODE,
    TIME_SLOT_MODE,
)
from .fields import GrowattComponent
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
from .inverter import (
    Gen1Inverter,
    Gen2Inverter,
    Gen3Inverter,
    Gen4Inverter,
    GrowattInverter,
    SpfInverter,
    UpdateReport,
    build,
    detect,
)
from .spf import SpfSettings, SpfStatus
from .variants import (
    FIRMWARE_PREFIX_VARIANTS,
    SERIAL_PREFIX_VARIANTS,
    Variant,
    generation,
    matches,
)

__all__ = [
    "FIRMWARE_PREFIX_VARIANTS",
    "INVERTER_FAULT",
    "INVERTER_STATE",
    "INVERTER_WARNING",
    "MODULE_STATUS",
    "MODULE_WARNING",
    "RUN_MODE",
    "SERIAL_PREFIX_VARIANTS",
    "TIME_SLOT_MODE",
    "Gen1Inverter",
    "Gen1Settings",
    "Gen1Status",
    "Gen2Inverter",
    "Gen2Settings",
    "Gen2Status",
    "Gen3Inverter",
    "Gen3Settings",
    "Gen3Status",
    "Gen3StorageSettings",
    "Gen3StorageStatus",
    "Gen3VppSettings",
    "Gen4BatteryModuleSettings",
    "Gen4BatteryModuleStatus",
    "Gen4BatterySettings",
    "Gen4BatteryStatus",
    "Gen4HybridSettings",
    "Gen4HybridStatus",
    "Gen4Inverter",
    "Gen4Settings",
    "Gen4Status",
    "Gen4VppSettings",
    "GrowattComponent",
    "GrowattInverter",
    "SpfInverter",
    "SpfSettings",
    "SpfStatus",
    "UpdateReport",
    "Variant",
    "build",
    "detect",
    "generation",
    "matches",
]
