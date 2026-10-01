# Tool numbering

Once some tools live in the changer and some are still changed by hand, the controller needs to know
which is which. This is the convention used on the development machine.

---

## The convention

| Tool numbers | Meaning |
|---|---|
| **1 – 60** | Manual tools. The machine stops and asks you to change them |
| **61 and up** | ATC tools. The machine fetches them from a pocket automatically |

The tool change logic then reduces to a single test: *is the tool number above 60?*

## Why a number range rather than a flag

Controllers vary in how much they will let you annotate a tool. Many will not let you attach an
arbitrary "this one is automatic" flag to a tool table entry, and those that do often express it
through pocket assignment, which brings its own constraints.

A number range needs no support from the controller at all. It works on any of them, it survives
tool table edits, and it is obvious at a glance which kind of tool you are looking at. The cost is
that you have to remember the rule — hence writing it down here.

Pick a boundary that suits your shop. 60 is arbitrary; what matters is that it is well above the
number of manual tools you will ever have, and that you never cross it by accident.

---

## What this buys you

With the ranges in place, a tool change falls into one of four situations:

| | Current tool | New tool | What must happen |
|---|---|---|---|
| **1** | Manual | Manual | Normal manual change. The changer is not involved |
| **2** | Manual | ATC | Manual unload by hand, then automatic load from a pocket |
| **3** | ATC | Manual | Automatic unload to a pocket, then manual load by hand |
| **4** | ATC | ATC | Automatic unload to one pocket, automatic load from another |

Situation 4 is the one that pays for the changer. Situations 2 and 3 are the awkward middle ground
and are easy to forget when writing the logic — they are also where most integration bugs live.

---

## Pockets

Each ATC tool needs to know which pocket it lives in. How you express that depends on the
controller; in LinuxCNC it is the pocket column of the tool table.

> **One tool per pocket.** A pocket physically holds one tool. If the tool table claims two tools
> share a pocket, the controller will happily fetch whatever is actually there and then apply the
> *other* tool's length offset. That error goes straight into the work, and it can be several
> millimetres.
>
> If you swap tools in and out of a pocket as a matter of practice, keep the tool table honest at
> the same time — or accept that the length offset is only correct for whichever tool is currently
> fitted.

---

## Practical notes

- **Leave gaps.** Numbering pockets 61, 62, 63 and tools to match is tidy until you add a fourth.
- **Name your tools** in the tool table comment, including which are ATC tools. On the development
  machine the ATC entries are prefixed `ATC -` so they are obvious in a list.
- **Re-measure tool length after every automatic change.** The module clamps consistently, but a
  tool can sit slightly differently in the collet. Most setups probe against a tool setter as part
  of the change.
