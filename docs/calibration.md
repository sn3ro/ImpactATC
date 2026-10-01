# Calibration

You need three numbers before the macros will do anything useful, all in **machine coordinates**
(the coordinate system `G53` works in, not your work offset):

| Value | What it is |
|---|---|
| `z_reference` | Machine Z where the bare spindle face just touches the top of the module |
| `pocket_x` | Machine X of the pocket centre |
| `pocket_y` | Machine Y of the pocket centre |

Everything else the macros do is derived from these.

---

## Why the reference point is defined this way

`z_reference` is measured with the **collet nut removed**, with the spindle's bare face touching
the top face of the module.

That looks awkward the first time. It is deliberate: the bare spindle face and the module's top
face are both hard, flat and repeatable. Anyone can find that point on any machine without knowing
anything about the machine it was designed on, and without depending on a particular nut, collet or
tool. Every other height the macros use is an offset from it.

If instead the reference were "nut fitted, touching something", it would shift with nut wear, collet
choice and how far the tool sticks out — and it would not transfer between machines at all.

---

## Finding `z_reference`

1. **Home the machine.** All of this is in machine coordinates, so homing must be reliable first.
2. **Remove the collet nut** from the spindle completely. No nut, no collet, no tool.
3. **Jog the spindle over the module** and roughly centre it.
4. **Jog down in decreasing steps** — 1 mm, then 0.1 mm, then 0.01 mm — until the spindle face just
   touches the top face of the module. A strip of paper is the usual trick: jog down until the paper
   just binds.
5. **Read machine Z** and write it down. On the development machine this is about **−62**; yours
   will differ.

> **Do not guess this.** Too high and the nut holder never engages the nut. Too low and the spindle
> drives down into the module — on the first production install, a reference set too deep **broke
> the centre component of a module**. It takes five minutes to measure and it is the number
> everything else hangs off.

If a module starts making a noise it did not make before, or a cycle ends with the spindle further
down than you expected, stop and re-check this value before running another cycle.

---

## Finding `pocket_x` and `pocket_y`

Note the difference from the Z reference: this one is measured **with the collet nut fitted**.

1. **Fit the nut** to the spindle.
2. **Jog the spindle over the module** at a safe height.
3. **Lower the spindle so the nut sits about halfway into the nut holder.** Not all the way down —
   halfway is enough to judge the fit.
4. **Centre it.** Push the module gently sideways in each direction; there should be a little play
   all the way around, and it should be even. That even play is your centre, and it is a far more
   reliable judgement than eyeballing the bore from above.
5. **Bolt the module down** so it cannot move, then **read machine X and Y**.

Do this for every module. Keep the values in a table and label them clearly — transposing two
pockets is an easy mistake with an expensive result.

### Spacing multiple modules

The module body is **95 mm**. Spacing them on **100 mm centres** works well and leaves room to get
a hand in.

Do not assume the spacing is exact and derive the other pockets arithmetically. Calibrate **each
module individually** — small differences in mounting add up, and a pocket that is 2 mm out is a
pocket that will eventually miss.

---

## Checking your numbers before you trust them

Do this with the **spindle stopped** and your hand on the E-stop. You are checking geometry, not
function.

1. Jog to `pocket_x` / `pocket_y` at a safe Z.
2. Jog down to `z_reference + 16` — the height the macros descend to before engaging. The spindle
   should be clearly above the nut with room to spare.
3. Continue down slowly, by hand, through the engagement depth. Watch the nut holder meet the nut.
   It should drop onto the nut flats, not perch on top of them.
4. Retract.

If the holder sits on top of the flats rather than dropping over them, that is normal — it is what
the seating rock at the start of the unload sequence is for.

---

## Putting the values in

Both the load and the unload macro have a **SET ME** block at the top. Put the same three numbers in
**both files**.

```gcode
#<z_reference>     = -62        ; SET ME
#<pocket_x>        = 0          ; SET ME
#<pocket_y>        = 0          ; SET ME
```

The LinuxCNC macros ship with all three set to `9999` and refuse to run until you replace them.
Other dialects ship with the placeholders above and cannot check — be careful there.

A mismatch between the two files is the classic cause of a module that loads correctly and then
misses on unload. If you change one, change the other in the same sitting.

> This is not a hypothetical. On the first production install, the reference was updated in the
> loading macro but not the unloading one. Loading worked; unloading drove to the old height and
> failed. If unloading misbehaves immediately after you have changed something, check this first.

---

## When to re-calibrate

- After moving or re-mounting the module
- After anything that changes your homing — a crash, a new home switch, a changed home offset
- After changing the spindle or its mounting
- If loads start to feel inconsistent, re-check `z_reference` before changing any other parameter
