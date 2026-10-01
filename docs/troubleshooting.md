# Troubleshooting

Symptoms, their usual causes, and what to check first. Work down each list in order — the entries
are ordered by how often they turn out to be the problem.

> **Before changing any parameter,** re-check `z_reference`. A drifted reference produces symptoms
> that look like a dozen different problems, and adjusting speeds to compensate only hides it.

---

## The nut will not unscrew

**The spindle turns but the nut stays put.**

1. **M4 is not actually reversing.** Command `M4 S300` on its own and watch. Many router and VFD
   setups are wired clockwise-only, in which case unloading cannot work. This is the most common
   blocker on a new installation.
2. **The spindle stalls instead of turning.** If it tries and gives up, this is a VFD configuration
   problem, not a macro problem. Work through [vfd-setup.md](vfd-setup.md) — low-speed torque
   compensation, stall prevention and the current limit all have to be right before the module can
   do its job.
2. **The nut is tighter than it was tightened.** Nuts work themselves tighter during cutting. Confirm
   `rpm_unscrew` is at 1250 and has not been "tidied up" to match the tightening speed.
3. **The holder is not fully seated on the nut.** It is perching on the nut flats rather than
   dropping over them. Check the seating rock is happening — you should see the spindle twitch
   either way before it unscrews — and that 300 rpm is actually achievable on your setup.
4. **Not descending far enough.** Check `z_reference`, then the two incremental steps.
5. **Spindle ramp too slow.** The dwell expires before the spindle reaches speed. See
   [vfd-setup.md](vfd-setup.md).
6. **The Z reference was changed in only one macro.** Loading and unloading each carry their own
   copy. Changing one and not the other produces exactly this symptom.
7. **Commanded RPM is not actual RPM.** Set the VFD to display RPM and check what the spindle really
   turns at. Tuning against a number the drive is not honouring wastes a lot of time.

---

## It unloads on an idle machine but not after cutting

**Tool changes work fine when you test them, then fail once you have actually been cutting.**

The nut works itself **tighter during machining**. This is real and has been observed by more than
one user — a module that changes tools happily all afternoon on an idle machine can refuse to
release the first tool after a real job.

In order:

1. **Raise the unscrew RPM** so it sits meaningfully above the tightening RPM. This is the whole
   reason the two are asymmetric — see [parameters.md](parameters.md#why-unscrew-is-faster-than-tighten).
2. **Lengthen the unscrew dwell** from 2.0 s to 3.0 s, giving the impacts longer to break it loose.
3. **Clean the spindle thread and the inside of the spindle cone.** Dust packs into the thread over
   a job and makes it progressively harder to release. This appears to be worse when cutting **wood**
   than metal — fine dust behaves differently from chips.
4. **A trace of grease on the spindle thread.** Very little. Enough to keep debris from binding in it.

---

## The nut does not tighten enough

**The tool comes loose during cutting, or pulls out.**

1. **Partial engagement.** A holder that is not fully on the nut cannot transmit torque no matter
   how fast it spins. Check `z_reference` and the engagement depth before touching speeds.
2. **Spindle ramp too slow.** Same cause as above: the dwell expires mid-acceleration, so the
   impacts never happen at full speed.
3. **Worn nut holder.** It is a wear part. After a few hundred cycles the drive features round off
   and it slips. Fit a new one — see [hardware](../hardware/README.md).
4. **`rpm_tighten` reduced.** Confirm it is at 1100.
5. **Collet or nut in poor condition.** The module can only tighten what it is given. A worn collet
   or a galled nut thread will not clamp properly.

---

## The tool creeps up in the collet

Observed over many cycles: the tool gradually moves **towards Z+**, out of the collet.

This is expected behaviour rather than a fault, and it is counter-intuitive the first time you see
it. Re-measure tool length after each automatic change rather than trusting a stored offset — most
setups probe against a tool setter as part of the change sequence.

---

## Every step takes far too long

**The sequence works, but each move crawls and the whole change takes an age.**

Look for a **spindle delay in your controller** — a dwell it inserts after every spindle command so
the spindle can reach speed before cutting. Sensible for milling; harmful here, because the macros
already contain their own dwells sized for the job. On the first RosettaCNC install a 4-second
controller delay was being added to every spindle command.

Also check whether your controller's **return-to-position move after a tool change** is using the
last feed rate rather than a rapid. If the last motion was a slow probing move, the return crawls.

---

## The cycle locks up partway through

**The assembly jams, or the sequence stalls mid-cycle.**

1. **Tightening speed too high.** Past a certain speed the mechanism can lock itself during
   threading. If you have raised `rpm_tighten`, put it back to 1100.
2. **Engagement feed wrong.** Too fast and the holder skips over the nut instead of dropping onto
   it; too slow and the nut has time to bind while threading.
3. **Debris in the module.** Chips in the mechanism change how everything moves. Check the chip
   covers are fitted and doing their job.

---

## Damage to the engagement features

**Visible wear or deformation on the drive teeth.**

The nut holder is *designed* to be the part that wears. Damage there after a few hundred cycles is
normal — replace it.

Damage anywhere else, or damage to a holder after only a few cycles, means something is wrong:
almost always a tightening speed that has been raised past what the mechanism tolerates. On earlier
hardware, over-speeding destroyed the engagement features outright in a single cycle.

**Damage to the centre of the module** is a different fault with a different cause: the spindle is
descending too far. Re-measure `z_reference` — see [calibration.md](calibration.md). A reference set
too deep has broken a module in the field.

---

## The spindle will not start the opening sequence

**It stalls instead of breaking the nut loose.**

The spindle does not have enough torque at the moment it needs it. Speed up the VFD ramp so it
reaches the commanded speed faster — see [parameters.md](parameters.md#spindle-ramp-times). On the
development machine, going from a 10-second ramp to roughly 4 s up / 5 s down fixed exactly this.

---

## It worked and now it does not

Something changed. In rough order of likelihood:

1. **Homing.** A crash, a knocked home switch, or an edited home offset moves every machine
   coordinate, including `z_reference` and the pocket. Re-home and re-check.
2. **Worn nut holder.** Consumable, and the decline is gradual enough to be easy to miss.
3. **The module moved.** Check the mounting bolts.
4. **A parameter was edited.** Compare against the summary in
   [parameters.md](parameters.md#summary-table).
5. **Debris.** Chips where they should not be.

---

## Recovering after a failed change

If a tool change fails partway, the machine's idea of what is in the spindle can disagree with
reality. That disagreement is dangerous: the next move may be planned around a tool that is not
there, or not planned around one that is.

1. **Stop.** Do not resume the program.
2. **Look at the machine.** Establish what is physically in the spindle and what is in each pocket.
3. **Clear the problem by hand** — remove a stuck tool, clear chips, undo a half-threaded nut.
4. **Tell the controller the truth.** Set the current tool to match reality before running anything
   else. In LinuxCNC that is `M61 Q<n>`, with `M61 Q0` for an empty spindle.
5. **Re-measure tool length** before cutting again.

Only then resume. Restarting a program without correcting the tool state is how a failed change
turns into a crash.
