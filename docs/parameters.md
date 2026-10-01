# Parameters

Every value the macros use, what it does, and when changing it is justified.

The defaults are not arbitrary. They came out of a long series of logged tests, and several of them
sit close to a limit where the module stops working or starts damaging itself. Read the notes before
changing anything.

---

## Spindle speeds

| Parameter | Default | What it does |
|---|---|---|
| `rpm_engage` | **900** | Speed while threading the nut on, before tightening |
| `rpm_tighten` | **1100** | Final tightening speed. Sets clamping torque — about **35 Nm** |
| `rpm_unscrew` | **1250** | Speed for unscrewing |
| `rpm_settle` | **300** | Gentle rock either way to seat the nut holder on the nut before unscrewing |

### Why unscrew is faster than tighten

This asymmetry is deliberate and it surprises people.

A nut tightened at 1100 rpm can work itself **tighter** during cutting. Unscrewing at the same speed
that tightened it does not reliably break it loose. Running unscrew 150 rpm higher gives the headroom
to release those tools.

> **Never harmonise the two values.** If you raise the tightening speed, raise the unscrew speed to
> keep the margin.

### Changing `rpm_tighten`

This is the parameter people most want to change, because it sets clamping torque. Two cautions:

- **Higher is not automatically better.** Torque comes from impact energy, and the mechanism has a
  speed at which engagement stops being clean. Past that, cycles start failing — and on earlier
  hardware, running too fast destroyed the engagement teeth outright.
- **Change it in small steps and watch.** Raise by 50 rpm, run several cycles, and look at the
  parts. The failure mode is gradual and then sudden.

If you are not getting enough clamping force, check `z_reference` and the engagement depths before
reaching for the speed. A partly engaged nut holder will never tighten properly no matter how fast
it spins.

---

## Feeds

| Parameter | Default | What it does |
|---|---|---|
| `feed_slow_z` | **1000** (load) / **900** (unload) | Z feed while engaging the nut |
| `feed_fast_z` | **2400** | Z feed for positioning moves |

The engagement feed is a compromise. Too slow and the nut has time to bind as it threads; too fast
and the holder can skip over the nut instead of dropping onto it. The load and unload values differ
slightly because the two operations are not symmetric — loading threads a nut on, unloading has to
seat a holder onto a nut that is already tight.

---

## Dwells

| Parameter | Default | What it does |
|---|---|---|
| `dwell_tighten` | **2.0 s** | Time held at tightening speed |
| `dwell_unscrew` | **2.0 s** | Time held at unscrewing speed |
| `dwell_settle` | **0.3 s** | Each pause during the seating rock |
| `dwell_stop` | **1.0 s** | Time allowed for the spindle to come to rest |

The two long dwells have to cover **spindle spin-up plus the work itself**. If your spindle ramps
slowly, the dwell may expire while it is still accelerating, and the cycle will under-perform without
any obvious error. See below.

`dwell_stop` matters more than it looks: retracting while the spindle is still turning down can drag
the nut.

---

## Positions

| Parameter | Default | What it does |
|---|---|---|
| `z_reference` | **−62** | Machine Z where the bare spindle face touches the module top. **Machine-specific** |
| `z_engage_offset` | **16** | How far above the reference the descent begins |
| `z_nut_thread` | **−31** | Incremental plunge that threads the nut on (load) |
| `z_nut_contact` | **−24** | Incremental first step down onto the nut (unload) |
| `z_nut_seat` | **−5** | Incremental second step, fully seating the nut (unload) |
| `pocket_x` / `pocket_y` | — | Machine XY of the pocket. **Machine-specific** |

`z_reference`, `pocket_x` and `pocket_y` are yours to measure — see [calibration.md](calibration.md).
The rest describe the module's own geometry and should not need changing.

Note that unloading descends in **two steps** with a seating rock between them, while loading
descends in **one**. Unloading has to persuade a holder onto an already-tight nut; loading starts
with a nut sitting loose in the changer.

---

## Spindle ramp times

Not a macro parameter — a VFD setting — but it affects whether the macros work.

The long dwells assume the spindle reaches commanded speed within them. A VFD configured with a
10-second ramp will still be accelerating when a 2-second dwell expires.

Symptoms of a ramp that is too slow:
- Weak or inconsistent clamping
- The opening sequence failing to start, as if the spindle lacks torque

On the development machine, acceleration and deceleration were reduced to roughly **4 s up / 5 s
down** from a 10 s default. Consult your VFD manual for the equivalent parameters. Do not set them
so aggressively that the drive trips.

---

## Controller minimum speed

The sequence commands 300 rpm during the seating rock. Check that both your VFD and your controller
will actually deliver it:

- VFDs have a minimum output frequency, often set well above idle
- Controllers usually have a minimum spindle speed setting, below which they clamp or refuse

If 300 rpm is not achievable, the rock does nothing and the holder may not seat — which shows up as
unreliable unloading.

---

## Summary table

Quick reference for a working configuration.

```
rpm_engage      = 900
rpm_tighten     = 1100        ; ~35 Nm
rpm_unscrew     = 1250        ; deliberately > rpm_tighten
rpm_settle      = 300

feed_slow_z     = 1000 / 900  ; load / unload
feed_fast_z     = 2400

dwell_tighten   = 2.0
dwell_unscrew   = 2.0
dwell_settle    = 0.3
dwell_stop      = 1.0

z_reference     = machine-specific   ; measure it
pocket_x        = machine-specific   ; measure it
pocket_y        = machine-specific   ; measure it
z_engage_offset = 16
z_nut_thread    = -31
z_nut_contact   = -24
z_nut_seat      = -5
```
