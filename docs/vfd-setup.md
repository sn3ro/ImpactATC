# VFD and spindle setup

ImpactATC drives the collet nut with the spindle motor. That asks something of the spindle it was
never designed for: **high torque at very low speed**, from a standing start, repeatedly.

Out of the box, most VFDs cannot do it. This is the single most common reason a module loads fine
and then fails to unscrew.

> Parameter numbers below are for a **Huanyang HY-series** inverter (the HY02D223B, 2.2 kW / 220 V,
> is the one both the development machine and the first production installs use). Other makes use
> different numbering — the *concepts* transfer, the numbers do not. Check them against your manual.

---

## Why the spindle struggles

A 24,000 rpm spindle reaches full speed at 400 Hz. The tool change sequence runs at:

| Operation | Speed | Drive frequency | % of range |
|---|---:|---:|---:|
| Seating rock | 300 rpm | 5 Hz | 1.3% |
| Threading the nut on | 900 rpm | 15 Hz | 3.8% |
| Tightening | 1100 rpm | 18 Hz | 4.6% |
| Unscrewing | 1250 rpm | 21 Hz | 5.2% |

Everything happens in the **bottom 5%** of the drive's range. A basic V/F inverter delivers its
worst torque exactly there — output voltage scales with frequency, so at 18 Hz the motor sees a
fraction of the voltage it needs to produce torque.

The fix is not to spin faster. It is to configure the drive to deliver torque down there.

---

## The four parameters that matter

Change these in order. After each one, try an unload cycle.

### PD014 / PD015 — acceleration and deceleration time

| | |
|---|---|
| **PD014** | Accel time 1 — seconds from 0 to full speed |
| **PD015** | Decel time 1 — seconds from full speed to 0 |
| **Factory** | Often 10 s or more |
| **Set to** | **PD014 = 4**, **PD015 = 5** as a starting point |

A 10-second ramp means the spindle is still accelerating when the macro's 2-second dwell expires.
The impacts that should be happening at 1100 rpm happen at whatever speed it reached — which may be
nothing like enough.

Shortening the ramp also gives noticeably more torque breaking away from standstill, which is what
the unscrew sequence needs most.

> **Do not go too aggressive.** A very short ramp draws a large current spike and will trip the
> inverter's over-current protection. Come down in steps and stop when it works reliably.

### PD142 — rated motor current

Set this to the **rated current printed on your spindle**, in 0.1 A units. On a typical 2.2 kW
air-cooled spindle this is around 8 A.

The inverter uses this to limit its output and protect the motor. Set too low, the drive protects
itself *before* delivering the current the module needs, and the spindle stalls while the inverter
believes it is doing the right thing.

### PD120 — stall prevention at constant speed

| | |
|---|---|
| **Set to** | **0** (disabled) |

This one is counter-intuitive, and it is worth understanding rather than just copying.

When enabled, if current rises past the configured level at constant speed, the inverter **lowers
its output frequency** until current returns to normal.

That behaviour is correct for a fan or a pump. It is exactly wrong here. Unscrewing a tight nut
*is* a current spike — that is the whole operation. Stall prevention sees it, drops the frequency,
and the impacts lose the speed they need. The drive fights the very thing you are asking it to do.

Setting PD120 to 0 disables it. Factory setting is already 0 on many units; check rather than assume.

### PD145 — auto torque compensation

| | |
|---|---|
| **Factory** | 2.0% |
| **Set to** | **3**, then raise gradually |

This is the parameter that solves low-speed torque directly. It adds extra output voltage at low
frequency to compensate for the under-torque a V/F drive produces there.

**Raise it slowly, one step at a time, testing between each.** The manual is explicit about why:
too little and the motor stays under-torqued at low speed; too much produces a mechanical shock to
the machine and can trip the inverter outright.

On the first production install, 3 improved things immediately and 4 was better still.

---

## Recommended starting point

| Parameter | Value | Purpose |
|---|---|---|
| PD014 | 4 s | Accel time |
| PD015 | 5 s | Decel time |
| PD120 | 0 | Stall prevention off |
| PD142 | Your spindle's rated current | Correct current limit |
| PD145 | 3, raised gradually | Low-speed torque compensation |

Also confirm **PD143** (motor poles) and **PD144** (rated revolution) match your spindle's
nameplate — these affect whether the displayed speed means anything.

---

## Check commanded speed against actual speed

**Do this before you tune anything else.** It has caused real confusion.

The RPM in the macro is what the *controller* asks for. What the spindle actually turns at depends
on the controller's speed scaling, the VFD configuration, and whether they agree. They often do not.

Set the VFD display to show RPM, run the unload macro, and read the display while it spins. If the
macro says 1250 and the drive says something else, fix that mismatch first — otherwise you are
tuning against a number that does not mean what you think it does.

---

## Watch for a controller-side spindle delay

Separately from the VFD, many controllers insert their own dwell after a spindle command, to let it
reach speed before cutting.

That setting is helpful for milling and harmful here. The macros already contain their own dwells,
carefully sized. An extra 4-second delay on every spindle command stretches a tool change out
enormously and can leave the spindle turning at the wrong point in the sequence.

On the first RosettaCNC install, a 4-second controller spindle delay had to be removed before the
timings made any sense.

---

## If it still stalls

In order:

1. **Confirm PD145 is doing something.** Raise it a step and listen — the change at low speed is
   audible. If nothing changes, you may be editing a parameter the drive is ignoring because it is
   in the wrong control mode.
2. **Confirm PD142 is not throttling you.** A value well below the spindle's actual rating limits
   output current directly.
3. **Confirm PD120 is 0.** Stall prevention undoes everything else.
4. **Shorten PD014 further**, one step at a time, until the inverter complains.
5. **Only then raise the unscrew RPM.** More speed is the crude fix; the parameters above are the
   real one. See [parameters.md](parameters.md) — and never raise unscrew above the point where the
   mechanism engages cleanly.

---

## Related

- [parameters.md](parameters.md) — the macro-side speeds, feeds and dwells
- [troubleshooting.md](troubleshooting.md) — symptoms and causes across the whole system
