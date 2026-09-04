# Cross-check: GrowattESPHome vs growatt-modbus vs official protocol

Static comparison (no hardware access) of three sources for a **Growatt MIN
3000TL-XE** (PV-only, 1-phase, 2 MPPT — part of the documented "MIN
2500-6000TL-XE" family):

1. [pvprodk/GrowattESPHome](https://github.com/pvprodk/GrowattESPHome)'s
   `growatt.yaml` — an ESPHome config the author confirms works against real
   MIN/MOD TL3-X/XH/XE hardware.
2. This library (`growatt-modbus`), as forked from
   [balloobbot/growatt-modbus](https://github.com/balloobbot/growatt-modbus).
3. Growatt's own **"Growatt Inverter Modbus RTU Protocol" V1.24** (the
   manufacturer's register spec, cross-checked directly — not taken on either
   project's word).

## Model identification

The library's `variants.py` has no serial prefix for a plain "MIN 3000TL-XE".
The closest table entry is `BDK` → "MIN 4200 TL-XE" (`Variant.PV | Variant.GEN4
| Variant.X1`). Growatt's own datasheets group 2500/3000/4200/6000 TL-XE under
one family and one manual, so `BDK` (or a sibling prefix Growatt assigned to
the same family) is the most likely match — but this is **not confirmed**
without reading the actual serial number register (holding 3001 or input-space
equivalent) from the device. `detect()` may currently raise `LookupError` on
this exact unit if its true prefix isn't `BDK` or one of the other listed
prefixes.

The protocol doc (page 3) states the register-range rule this whole
comparison turns on:

> TL-X/TL-XH/TL-XH US (MIN Type): 03 register range: 0~124, 3000~3124,
> 3125~3249 (TL-XHUS); 04 register range: 3000~3124, ...
> Storage(SPH Type): 03 register range: 0~124, 1000~1124; ...

I.e. MIN/TL-X inverters have **two** valid register blocks (legacy `0-124`
and `3000-3124`), while `1000-1124` belongs to a **different product line**
(Storage/MIX/SPA/SPH), not MIN/TL-X at all.

## Register-by-register table

| ESPHome address (space) | ESPHome name | growatt-modbus field (class @ address) | Protocol doc (No. / name / scope) | Verdict |
|---|---|---|---|---|
| holding 0 | Remote On/Off | `inverter_switch` (`Gen4Settings` @ 0) | `00 OnOff`, values 0-3 | **Match** |
| holding 3 | Max Output Power | `active_power_limit` (`Gen4Settings` @ 3) | `03 Active P Rate`, 0-100 or 255 | **Match** |
| holding 1044 | Inverter Priority (Load/Battery/Grid First) | *none* | Not in MIN/TL-X holding range at all — `1000-1124` is the **Storage (MIX/SPA/SPH)** range | **Questionable in ESPHome**: address belongs to a different product line's holding block |
| holding 1092 | AC Charging (Enabled/Disabled) | *none* | Same as above — outside MIN/TL-X's documented holding ranges | **Questionable in ESPHome** |
| input 0 | status_code → 13-state text (Standby/Normal/Discharge/Fault/Flash/PV Charging/AC Charging/.../Bypass/PV Charge&Discharge) | *none* (only `Gen1Status.run_mode` @ 0, 4 states, different generation) | `0. Inverter Status`: **only 3 states** — 0:waiting, 1:normal, 3:fault | **Questionable in ESPHome**: states 2, 5-12 are a hybrid/storage status scheme, undocumented for this register |
| input 1 (32-bit) | Input Power | `pv_power_total` (`Gen4Status` @ 1) | `1-2. Ppv H/L`, Input power | **Match** |
| input 3 | PV1 voltage | *none in `Gen4Status`* (`Gen4HybridStatus.pv_voltage_1` exists but at 3003, not 3) | `3. Vpv1`, PV1 voltage | **Missing in growatt-modbus** |
| input 4 | PV1 current | *none* (`Gen4HybridStatus.pv_current_1` @ 3004) | `4. PV1Curr` | **Missing in growatt-modbus** |
| input 5 (32-bit) | PV1 Active power | *none* (`Gen4HybridStatus.pv_power_1` @ 3005) | `5-6. Ppv1 H/L` | **Missing in growatt-modbus** |
| input 7 | PV2 voltage | *none* (`Gen4HybridStatus.pv_voltage_2` @ 3007) | `7. Vpv2` | **Missing in growatt-modbus** |
| input 8 | PV2 current | *none* (`Gen4HybridStatus.pv_current_2` @ 3008) | `8. PV2Curr` | **Missing in growatt-modbus** |
| input 9 (32-bit) | PV2 Active power | *none* (`Gen4HybridStatus.pv_power_2` @ 3009) | `9-10. Ppv2 H/L` | **Missing in growatt-modbus** |
| input 35 (32-bit) | Grid Active Power | `output_power` (`Gen4Status` @ 35) | `35-36. Pac H/L`, Output power | **Match** |
| input 37 | Frequency | *none* (`Gen4HybridStatus.grid_frequency` @ 3025) | `37. Fac` | **Missing in growatt-modbus** |
| input 38/39/40-41 | Voltage/Current/Power Phase A | *none* (`Gen4HybridStatus` @ 3026-3028) | `38-41. Vac1/Iac1/Pac1 H/L` | **Missing in growatt-modbus** |
| input 42-48 | Voltage/Current/Power Phase B & C | *none* | `42-49. Vac2/Iac2/Pac2, Vac3/Iac3/Pac3` — 3-phase only, N/A for this 1-phase unit | N/A on this unit; **missing** for the X3 siblings it would matter for |
| input 53 (32-bit) | Today's Generation | *none* | `53-54. Eactoday H/L` | **Missing in growatt-modbus** |
| input 55 (32-bit) | Total Energy Production | *none* | `55-56. Eac total H/L` | **Missing in growatt-modbus** |
| input 93 | Inverter Module Temp | *none* (only `Gen2Status.inverter_temperature` @ 93, wrong generation) | `93. Temp1` | **Missing in growatt-modbus** |
| input 105 | Fault code (small hardcoded switch) | `inverter_fault_maincode` (`Gen4Status` @ 105) + `inverter_fault_subcode` @ 107 + `INVERTER_FAULT` lookup table | `105. Fault Maincode`, `107. Fault Subcode` | **Match, library is more complete** (main+sub code pair vs ESPHome's maincode-only switch) |
| *(library-only)* | — | `priority` (`Gen4Status` @ 118, tagged for every Gen4 variant) | `118. Priority`: 0/1/2, explicitly tagged **"Storage Power"** | **Library's own mismatch**: exposed on pure-PV Gen4 inverters too, backed by a register the manufacturer scopes to storage models |

## Summary

- **10 of the ~20 distinct measurements ESPHome reads successfully** (PV1/PV2
  voltage-current-power, grid frequency, grid voltage/current/power, today/total
  energy, inverter temperature) have **no field in `growatt-modbus`'s base
  `Gen4Status`** at their documented address. The library only models the
  equivalent data in `Gen4HybridStatus` at the `3000+` block — built for every
  Gen4 inverter regardless of PV/HYBRID category, per `variants.py`.
  **Confirmed live (see below): this data is genuinely available there too.**
  The gap is real but harmless in practice — a naming/documentation-clarity
  issue (plain-PV data served by a class named "Hybrid"), not a functional one.
- **2 of ESPHome's own entities** (holding 1044/1092, "Inverter Priority" /
  "AC Charging") read addresses the manufacturer's own doc scopes to the
  Storage/MIX/SPA/SPH product line, not MIN/TL-X. **Confirmed live: both read
  a clean, stable `0.0`** — not an error, not an unimplemented sentinel
  (`0xFFFF`) — consistent with being genuinely inactive on a battery-less
  unit, though this can't be proven with certainty short of seeing them ever
  change.
- **1 status register** (input 0) is decoded by ESPHome with a 13-state table
  the manufacturer's doc doesn't support (only 3 states documented) — likely
  copied from a hybrid/storage ESPHome template without adapting it for a
  PV-only unit. Live read showed `1` ("Normal") during production — consistent
  with either the 3-state doc or the 13-state table, so this alone doesn't
  distinguish them; would need to catch a fault/edge condition to test further.
- **1 library field** (`Gen4Status.priority` @ input 118) is built for every
  Gen4 variant but documented by Growatt as storage-only.
- What **does** line up across all three sources: `inverter_switch`,
  `active_power_limit`, `output_power`, and the fault-code registers.

## Live verification (2026-09-04, real MIN 3000TL-XE, mid-production)

Confirmed against the actual unit via temporary diagnostic sensors added to
`growatt.yaml`, read through Home Assistant:

| Measurement | Base address (ESPHome) | 3000-block address (`Gen4HybridStatus`) | Verdict |
|---|---|---|---|
| PV1 voltage | 188.1 V (addr 3) | 184.4 V (addr 3003) | **Live, tracks together** |
| PV1 current | 0.9 A (addr 4) | 0.9 A (addr 3004) | **Live, exact match** |
| PV1 power | 183.3 W (addr 5) | 182.1 W (addr 3005) | **Live, tracks together** |
| Frequency | 49.97 Hz (addr 37) | 49.98 Hz (addr 3025) | **Live, tracks together** |
| Voltage Phase A | 228.7 V (addr 38) | 228.6 V (addr 3026) | **Live, tracks together** |

Small deltas are normal sampling drift (readings taken via two separate
Modbus round-trips a few seconds apart on a moving PV/grid value) — this is
the same live feed, read twice through two different addresses. **The
`Gen4HybridStatus` 3000-block is fully live and correct on this PV-only unit**,
resolving open question 1 below in the library's favor.

Holding 1044 and 1092, read as raw unmapped 16-bit numbers (bypassing
ESPHome's `optionsmap`): both `0.0`, cleanly, no errors. Resolves open
question 2 as "reads real, stable data" — whether that data is *meaningful*
(a genuine "no AC charging / load-first" state) or merely an always-zero
unused register can't be fully distinguished without ever observing a change.

Serial number, fixed (the first attempt lacked `response_size`, an
undocumented required field for multi-register `modbus_controller`
text sensors — silently truncated to 1 register/2 bytes): **`DCF2A2509G`**.

`DCF` does **not** appear in `variants.py`'s `SERIAL_PREFIX_VARIANTS` table
(63 prefixes checked against the fork's source — ABJ, SKL, XVM, ..., BDK,
WVN, ..., BY3), nor in `FIRMWARE_PREFIX_VARIANTS`. `detect()` would exhaust
both tables and raise `LookupError("unrecognised Growatt inverter")` against
this exact, currently-producing, real-world unit.

## Open questions — need a live read to resolve

1. ~~Does register 3 (input) on this exact unit actually return PV1 voltage~~
   **Resolved: yes, and so does the 3000-block equivalent.** See above.
2. ~~What does holding 1044/1092 and input 0 actually return on this unit~~
   **Partially resolved:** clean `0.0` on both holding registers; input 0
   only observed at `1` (Normal) so far — still open whether it ever reports
   one of the 13 ESPHome-decoded states or stays within the documented 3.
3. ~~What is this unit's actual serial-number prefix~~ **Resolved, and it's
   the headline finding: `detect()` does not recognize this inverter.**
   `DCF` is missing from both lookup tables. This is the one finding here
   that's an unambiguous functional bug, not a nuance — a one-line fix
   (`"DCF": Variant.PV | Variant.GEN4 | Variant.X1` in
   `SERIAL_PREFIX_VARIANTS`) would resolve it, pending confirmation that
   `PV | GEN4 | X1` is the right variant for this specific unit (2 MPPT,
   1-phase, no battery — matches the pattern of neighboring `TL-X`/`TL-XE`
   entries like `BDK`, `XTD`, `QYL`).
