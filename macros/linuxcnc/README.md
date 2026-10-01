# ImpactATC macros for LinuxCNC

The **reference implementation**. The load and unload sequences here are the ones run daily on the
development machine (LinuxCNC on a Remora-converted EC300); every other dialect is ported from them.

---

## Files

| File | Purpose | Needed? |
|---|---|---|
| `impactatc_tool_loading.ngc` | Load a tool — screws the collet nut on | **Yes** |
| `impactatc_tool_unloading.ngc` | Unload a tool — unscrews the collet nut | **Yes** |
| `impactatc_check_loaded.ngc` | Confirms a tool is in the spindle after a load | Optional — needs a beam sensor |
| `impactatc_check_unloaded.ngc` | Confirms the spindle is empty after an unload | Optional — needs a beam sensor |

For automatic changes on `M6`, see [`m6-integration/`](m6-integration/) once these are commissioned.

All four ship as **standalone programs**: open one in AXIS / gmoccapy / QtDragon and run it like any
other program. That is the commissioning step — see [setup.md, stage 5](../../docs/setup.md#5-commission).

---

## Installing

Copy the files into a folder listed in `SUBROUTINE_PATH` in your INI's `[RS274NGC]` section — for
example:

```ini
[RS274NGC]
SUBROUTINE_PATH = macros
```

**Keep the filenames lowercase.** LinuxCNC lower-cases `o<name>` when it looks a subroutine file
up, so a file with capitals in its name cannot be called once you integrate. Don't rename them.

---

## Setting it up

Each macro has a **SET ME** block at the top. The values ship as `9999`, and the macro **aborts
with a message** until you replace them — it will not drive anywhere with placeholder coordinates.

| Parameter | In | What it is |
|---|---|---|
| `#<z_reference>` | load, unload | Machine Z where the spindle, **with no collet nut fitted**, just touches the top face of the module. About −62 on the development machine — yours will differ |
| `#<pocket_x>` / `#<pocket_y>` | load, unload | Machine XY of the pocket centre, measured with the nut fitted |
| `#<sensor_x>`, `#<beam_x>`, `#<sensor_y>`, `#<z_check>` | both checks | Sensor approach position, in-beam X, and the Z where your shortest tool still breaks the beam |
| `#<beam_broken_val>` | both checks | What `#5399` reads with the beam broken. `1` on the development machine; confirm yours in Halshow |

Measure them as described in [calibration.md](../../docs/calibration.md). The load and unload values
**must be identical** — a mismatch is the classic cause of a module that loads and then misses on
unload. The same goes for the two check macros.

Everything else — speeds, feeds, dwells, engagement depths — is the production configuration.
See [parameters.md](../../docs/parameters.md) before changing any of it, and note that the unscrew
speed (1250) is **deliberately** higher than the tightening speed (1100).

---

## Commissioning

Hand on the E-stop throughout. Follow [setup.md](../../docs/setup.md#5-commission); in short:

1. Dry-run the spindle: `M3 S900`, `M3 S1100`, `M4 S300`, `M4 S1250`. **M4 must reverse.**
2. Fill in the SET ME blocks. Run each macro once with values still at `9999` and confirm it aborts —
   that proves the guard works on your install.
3. Walk the Z moves by hand at the pocket, spindle stopped.
4. Run **unload** first, with a nut and tool in the spindle. Then **load**.
5. Alternate them for several cycles and watch for drift.

### Optional: tool presence sensor

The check macros read a through-beam sensor (developed with an Autonics BUP-50 fork sensor) on
`motion.digital-in-00`, using `M66 P0 L0`. Your HAL needs one line; the input pin name depends on
your hardware:

```hal
net tool-present motion.digital-in-00 <= <your-input-pin>
```

`motion.digital-in-00` exists by default (motmod creates four). Then:

1. Open Halshow, watch `motion.digital-in-00`, and break the beam by hand. If broken reads `0`, set
   `#<beam_broken_val> = 0` in both check macros.
2. With a tool loaded, run `impactatc_check_loaded.ngc` — it should complete silently.
3. With the spindle empty, run `impactatc_check_unloaded.ngc` — it should complete silently.
4. Hold a chip or a strip of card in the fork and run either one — it must abort with
   *beam blocked before check*.

A dead sensor stuck at "clear" cannot be caught by the unload check (clear is the expected answer);
the load check catches it on the next load.

---

## Integrating with M6

Only once the standalone macros work reliably.

**Converting a macro to a subroutine:** uncomment the `o<...> sub` and `o<...> endsub` lines and
delete the final `M2`. It can then be called as `o<impactatc_tool_unloading> call` from your
`M6` remap (`REMAP=M6 ... ngc=...` in the INI).

How the development machine does it, and the lessons from doing it:

- **Tool numbering** — manual tools in pockets 1–60, ATC pockets 61 and up. The remap compares the
  current and requested pockets to pick one of four cases: manual→manual, manual→ATC, ATC→manual,
  ATC→ATC. See [tool-numbering.md](../../docs/tool-numbering.md).
- **Pocket coordinates live in the remap**, which moves over the pocket and then calls load or
  unload. With several modules, remove the XY move and the pocket SET ME lines from the load/unload
  subroutines so there is only one copy of each coordinate. Keep `z_reference` in both.
- **Abort on an unknown pocket.** If the requested pocket has no coordinates, the remap must
  `(ABORT, ...)` — never fall back to a default position and run the cycle there. Adding a module
  and forgetting its coordinates should stop the machine, not plunge the spindle somewhere else.
- **Travel along a safe lane.** Retract to safe Z and move along a Y (or X) that clears every
  module before going over the pocket.
- **Call the checks straight after each load / unload**, while still near the changer.
- **Update the tool number after an ATC→ATC change** with `M61 Q<tool>`; the builtin `M6` does it
  in the cases that end in a manual change.
- **After any abort**, LinuxCNC's idea of the loaded tool may be wrong. Fix the physical problem,
  then set the true state with `M61 Q<n>` (`M61 Q0` for an empty spindle) before running anything.

A complete, ready-to-configure remap built on these lessons is in [`m6-integration/`](m6-integration/).
