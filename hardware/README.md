# Hardware

User-serviceable parts only. This is **not** the full mechanical design of ImpactATC — see the note
in the top-level [README](../README.md).

## What's here

| File | Part |
|---|---|
| `step/ImpactATC-ER20-Nut-holder.step` | ER20 nut holder |

STEP is supplied rather than STL because slicers such as Bambu Studio and Orca open STEP directly,
and it stays useful if you want to modify the part.

---

## ER20 nut holder

The nut holder transfers torque from the module directly onto the ER20 collet nut.

It is a **wear part**. Expect to replace it after a few hundred tool-change cycles — it is meant to
be the component that wears, so print spares and keep one on the shelf.

### Print settings

| Setting | Value |
|---|---|
| Material | **PETG** |
| Profile | Bambu Studio **Strength** preset |
| Infill | **100%** |

The part is under repeated impact loading, so the 100% infill and the Strength profile both matter —
a standard or draft profile will not survive. Do not substitute PLA.

### Printing it

1. Open `step/ImpactATC-ER20-Nut-holder.step` directly in Bambu Studio (or your slicer of choice).
2. Select the **Strength** profile and a PETG filament.
3. Set infill to **100%**.
4. Slice and print.

### Replacing it

Replacement is covered by the disassembly sequence: remove the top dust cover, lift out the old nut
holder and the spring beneath it, fit the new holder, and reassemble in reverse.
