# ImpactATC M6 integration for LinuxCNC

An `M6` remap that changes tools automatically between ImpactATC modules, and by hand for any tool
that does not live in a module.

> **Status: for testing.** The sequence is the one used daily on the development machine, but this
> generic package has not yet been through a validation campaign on hardware. It has been run
> through the LinuxCNC 2.9 interpreter in simulation — all four cases, the configuration guards,
> and the sensor and cover options. Commission it with the test sequence below, hand on the E-stop.

> **Do this last.** Only start here once the standalone macros in [`../`](../) load and unload
> reliably on your machine. See [setup.md](../../../docs/setup.md#6-integrate).

---

## What it does

When your program calls `M6`, LinuxCNC runs `impactatc_m6.ngc` instead of its built-in tool change.
It looks at the **P (pocket)** column of the tool table for the tool in the spindle and the tool
requested:

| P | Meaning |
|---|---|
| 1–60 | Manual tool. Changed by hand at the manual change position |
| 61–66 | Lives in that ImpactATC module (61 = first module, 62 = second, …) |

and picks one of four cases:

| Case | What happens |
|---|---|
| manual → manual | Goes to the manual change position, LinuxCNC's normal tool-change prompt |
| manual → ATC | Manual stop to **empty** the spindle (skipped if it is already empty), then the ATC loads the new tool |
| ATC → manual | ATC unloads the current tool, then manual stop to insert the new one (skipped for `T0`) |
| ATC → ATC | ATC unloads into one module, then loads from the other |

Travel to and from the modules goes along a **safe lane** you define, so a tool hanging below the
spindle never passes over a module.

### Safety behaviour

The remap **aborts before anything moves** if:

- any required value in the config is still `9999`
- a tool's P number is 61–66 but that module has no coordinates (or P is above 66)
- an ATC → ATC change has both tools assigned to the **same module** — unloading one and loading
  "the other" would just reload the same tool, with the wrong tool length

With the optional sensor fitted it also aborts if the spindle is not empty after an unload, not
loaded after a load, or the sensor is blocked by a chip.

---

## Files

| File | Edit it? | Purpose |
|---|---|---|
| `impactatc_m6_config.ngc` | **Yes — the only one** | All your machine's values |
| `impactatc_m6_after_change.ngc` | Optional | Your hook, e.g. tool-length measurement |
| `impactatc_m6.ngc` | No | The remap — decides the case and runs it |
| `impactatc_m6_load.ngc` | No | Load sequence (production values) |
| `impactatc_m6_unload.ngc` | No | Unload sequence (production values) |
| `impactatc_m6_pocket_xy.ngc` | No | Pocket lookup — aborts on unknown pockets |
| `impactatc_m6_lane.ngc` | No | Safe-lane travel |
| `impactatc_m6_check.ngc` | No | Optional beam-sensor check |
| `impactatc_m6_cover.ngc` | No | Optional powered cover |
| `python/toplevel.py`, `python/remap.py` | No | Hook LinuxCNC's standard remap glue in |

The load and unload sequences use exactly the same speeds, feeds and depths as the standalone
macros. The Z reference and pocket positions now come from the one config file, so load and unload
can no longer disagree about them.

---

## Requirements

- LinuxCNC **2.8 or later**, with a **non-random** tool changer (`RANDOM_TOOLCHANGER = 0`, the default)
- A working manual tool change — normally `hal_manualtoolchange`, which most configs already load
- **M4 reverses the spindle**, and the standalone macros already commissioned
- If you already remap `M6` (for example with Probe Screen), you will need to merge the two — see
  [Existing M6 remaps](#existing-m6-remaps)

---

## Installing

1. **Copy the `.ngc` files** into a folder inside your config, e.g. `~/linuxcnc/configs/mymill/impactatc/`.
   Do **not** put the standalone macros from `../` in the same folder.
2. **Copy the `python/` folder** into your config folder, and copy LinuxCNC's own `stdglue.py` next
   to the two files in it. Find it with:
   ```sh
   find / -name stdglue.py 2>/dev/null
   ```
   It ships with LinuxCNC (under `remap_lib/python-stdglue/`). If your config already has a
   `python/` folder with `stdglue.py`, keep yours and skip this step.
3. **Edit your INI:**
   ```ini
   [RS274NGC]
   SUBROUTINE_PATH = impactatc
   REMAP = M6 modalgroup=6 prolog=change_prolog ngc=impactatc_m6 epilog=change_epilog

   [PYTHON]
   PATH_PREPEND = ./python
   TOPLEVEL = python/toplevel.py

   [EMCIO]
   RANDOM_TOOLCHANGER = 0
   ```
   If `SUBROUTINE_PATH` already lists folders, add `impactatc` to it with a colon:
   `SUBROUTINE_PATH = macros:impactatc`.
4. **Fill in `impactatc_m6_config.ngc`.** Copy `z_reference` and the pocket XY values you proved
   during standalone commissioning. Then add the safe lane and the manual change position.
5. **Set up the tool table.** Give each ATC tool the P number of the module it lives in:
   ```
   T1   P1   D6.000  Z-25.0  ; manual tool
   T61  P61  D6.000  Z-31.9  ; lives in module 1
   T62  P62  D5.000  Z-24.8  ; lives in module 2
   ```
   Tool numbers do not have to match P numbers. Several tools may share a module's P number if you
   swap them in and out by hand, but **the table must always say which tool is physically in each
   module** — the ATC cannot tell them apart.

---

## The config values

| Value | What it is |
|---|---|
| `_atc_z_reference` | Machine Z, spindle **without nut** touching the module top. One value for all modules |
| `_atc_pocket_61_x` … `_66_y` | Pocket centre per module, measured with the nut fitted. Unused = `9999` |
| `_atc_z_safe` | Safe Z for all travel. Normally `0` |
| `_atc_lane_axis`, `_atc_lane` | Modules in a row along X → `0` and a Y that clears them all. Along Y → `1` and an X |
| `_atc_manual_x/y/z` | Where the spindle waits for a manual tool change |
| `_atc_use_sensor` … | Optional beam sensor — same meaning as in the standalone check macros |
| `_atc_use_cover` … | Optional powered cover on a digital output (`M64`/`M65`) |

Measure positions as described in [calibration.md](../../../docs/calibration.md).

---

## Commissioning

Hand on the E-stop. Do not stand in line with the modules. Work through these in order. Before
each test, set LinuxCNC's tool state to match reality with `M61 Q<tool>` (`M61 Q0` = spindle empty).

| # | Starting state | Command | Expect | Watch for |
|---|---|---|---|---|
| 1 | Config still at 9999 | `T61 M6` | Immediate abort, **no motion** | Any movement at all = stop |
| 2 | Config filled; add a test tool `T99 P67` | `T99 M6` | Abort: pocket not configured, **no motion** | |
| 3 | Spindle empty, `M61 Q0` | `T61 M6` | Lane → module 1 → load → lane | Path along the lane is clear; tool is tight |
| 4 | T61 loaded | `T1 M6` (manual tool) | Unload into module 1 → manual position, prompt | Nut left in module 1, spindle empty |
| 5 | T1 in by hand | `T61 M6` | Message to **empty** the spindle, prompt, then load | Prompt says "insert T61" — empty the spindle anyway |
| 6 | T61 loaded, second module fitted | `T62 M6` | Unload 61, load 62 | Lane used between modules |
| 7 | Two tools set to the same P | change between them | Abort: same module | |
| 8 | Any ATC tool loaded | `T0 M6` | Unload, spindle left empty, no prompt | |

Repeat tests 3, 4 and 6 for several cycles and watch for drift. With the sensor enabled, also run
test 3 with a strip of card in the beam: it must abort with *beam blocked*.

---

## After an abort

An abort stops the program where it is. The cover, if powered, is left open so you can get at the
module. LinuxCNC's idea of which tool is loaded **may now be wrong**:

1. Clear the physical problem.
2. Tell LinuxCNC the truth: `M61 Q<tool in spindle>`, or `M61 Q0` if it is empty.
3. Only then run anything else.

See [troubleshooting.md](../../../docs/troubleshooting.md#recovering-after-a-failed-change).

---

## Your program

- After `M6`, the spindle is **stopped** and **no tool length offset is applied**. Your program must
  restart the spindle and issue `G43 H..` after `M6`. Most CAM post-processors do both already.
- Re-measuring tool length after each ATC load is recommended — put your tool-setter routine in
  `impactatc_m6_after_change.ngc`.

---

## Existing M6 remaps

LinuxCNC allows only one `M6` remap. If you already have one — Probe Screen's
`psng_manual_change`, for example — you have two choices:

- **Replace it** with this one and call your measurement from `impactatc_m6_after_change.ngc`.
- **Keep yours** and copy the case logic from `impactatc_m6.ngc` into it, calling the same
  `impactatc_m6_*` subroutines. This is how the development machine is set up.
