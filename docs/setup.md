# Setup and integration

How to get ImpactATC working on your machine, from unpacking to an automatic tool change.

Work through the stages in order. Each one is verifiable on its own, and stopping between them
costs nothing. The single most common cause of trouble is skipping ahead to a full cycle.

| Stage | You end up with | Time |
|---|---|---|
| [1. Check your machine suits it](#1-check-your-machine-suits-it) | Confidence it will work at all | 15 min |
| [2. Mount the module](#2-mount-the-module) | Module bolted down, spindle able to reach it | 30 min |
| [3. Calibrate](#3-calibrate) | Your Z reference and pocket coordinates | 30 min |
| [3b. Set up the VFD](vfd-setup.md) | A spindle that can actually turn the nut | 30 min |
| [4. Install the macros](#4-install-the-macros) | Macros on the machine with your values in them | 15 min |
| [5. Commission](#5-commission) | Load and unload working, run by hand | 1 hr |
| [6. Integrate](#6-integrate) | `M6` doing it automatically | 1–2 hr |

---

## 1. Check your machine suits it

ImpactATC drives the collet nut with the spindle itself. That puts a few hard requirements on the
machine, and it is much cheaper to find a blocker now than after mounting.

| Requirement | Why | Typical blocker |
|---|---|---|
| **ER20 collet nut** | The module is built around it | ER11/ER16/ER25 spindles need a different module |
| **Spindle reverse (M4)** | Unloading unscrews counter-clockwise | Many router/VFD setups are wired CW-only. **Check this first** |
| **Stable running at 300–1250 rpm** | The sequence uses 300, 900, 1100 and 1250 rpm | VFD minimum frequency set too high; controller minimum RPM setting |
| **Reasonably brisk spindle accel/decel** | The sequence relies on reaching speed within the dwell | VFD ramp times of 10 s+ will not keep up — see [vfd-setup.md](vfd-setup.md) |
| **Low-speed torque** | Everything happens below 5% of a 24 000 rpm spindle's range | Most VFDs need configuring for this. **[vfd-setup.md](vfd-setup.md) is not optional reading** |
| **Z travel below the module top** | Engagement happens roughly 46 mm below the reference | Short-Z machines, or soft limits set tight |
| **Somewhere to put it** | The module needs a clear XY position plus an approach path | Small tables, or fixtures in the way |

> **Test M4 before you do anything else.** Command `M4 S300` at the machine and confirm the spindle
> turns *backwards*. If it does not, unloading cannot work and everything below is wasted effort.

---

## 2. Mount the module

Bolt the module to the table where the spindle can reach it and where it will not foul your normal
work. Points that matter:

- **Rigid mounting.** The module generates high peak torque in short impacts. Anything springy
  will absorb the impacts instead of transmitting them to the nut.
- **Clear approach.** The spindle arrives from above and descends. Check the whole descent is clear,
  including with your *longest* tool fitted.
- **Away from the work.** Chips and coolant will find it. A position outside the normal working
  envelope is worth the lost table space.
- **Think about the retract path now.** After a change, the spindle lifts and travels away. On a
  machine with several pockets, plan a safe Y or X lane the spindle can use to get between them
  without crossing anything.

---

## 3. Calibrate

You need three numbers, all in **machine coordinates**: the Z reference, and the X and Y of the
pocket. Full method in [calibration.md](calibration.md).

The short version:

- **Z reference** — take the collet nut *off*, jog the spindle down until it just touches the top
  face of the module, and read machine Z. The nut is removed on purpose: the bare spindle face is a
  hard, repeatable surface anyone can find without knowing anything about our machine.
- **Pocket X and Y** — jog until the spindle is centred over the module, and read machine X and Y.

Write them down. You will put the same values into more than one file.

---

## 4. Install the macros

Pick your controller:

| Controller | Location | Notes |
|---|---|---|
| **LinuxCNC** | [`macros/linuxcnc/`](../macros/linuxcnc/) | Reference implementation. Files go in the folder named by `SUBROUTINE_PATH` in your INI |

Put your three calibration numbers into the **SET ME** block at the top of each macro. They must be
**identical in both** the load and unload macros — a mismatch is the classic cause of a module that
loads fine and then misses on unload.

---

## 5. Commission

**Hand on the E-stop for all of this.** Do not stand in line with the module.

1. **Dry-run the spindle.** Nothing in the module. Confirm `M3 S900`, `M3 S1100`, `M4 S300` and
   `M4 S1250` all behave, and that M4 genuinely reverses.
2. **Walk the moves by hand.** Jog to the pocket, then jog down through the engage height and the
   incremental steps. Confirm the nut holder lines up with the nut and nothing collides.
3. **Unload first.** Start with a nut and tool fitted in the spindle and run the unload macro.
   Unloading is the gentler operation and failure is more obvious — the nut simply does not come off.
4. **Then load.** With the nut sitting in the changer, run the load macro.
5. **Repeat.** Alternate the two and watch for drift. If something is marginal, it shows up over
   cycles rather than on the first one.

If any step misbehaves, stop and read [troubleshooting.md](troubleshooting.md) rather than adjusting
parameters hopefully. Most failures have one specific cause.

---

## 6. Integrate

Only once both macros work reliably on their own.

The macros ship as **standalone programs** on purpose. That is the commissioning form: you can run
one, watch it, and stop. Integration is the second step, when you already trust the sequence.

To integrate, you wrap the sequences in your controller's tool-change mechanism so that `M6` calls
them. That means deciding:

- **Which tools live in the changer** and which are still changed by hand — see
  [tool-numbering.md](tool-numbering.md) for the convention that keeps the two apart
- **What happens between pockets** — the safe travel path
- **How tool length is handled** — most people re-measure with a tool setter after each change
- **What happens when it goes wrong** — see [troubleshooting.md](troubleshooting.md#recovering-after-a-failed-change)

For LinuxCNC, a ready-to-configure `M6` remap covering all four situations (manual→manual,
manual→ATC, ATC→manual, ATC→ATC) is in [`macros/linuxcnc/m6-integration/`](../macros/linuxcnc/m6-integration/).
It is marked **for testing** until validated on hardware.
