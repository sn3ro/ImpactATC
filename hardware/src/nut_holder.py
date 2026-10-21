"""Parametric ImpactATC nut holder. Usage: FreeCADCmd nut_holder.py <variant> <out.step> [compare.step]"""
import sys, math, Part, FreeCAD as App
V = App.Vector

# --- Module interface: shared by all variants (driven by the impact elements / spring / cover) ---
H          = 14.0    # overall height
R_BODY     = 20.0    # body circle
N_LOBES    = 6
LOBE_PCD_R = 20.0    # lobe centre radius
R_LOBE     = 5.0
LOBE_ANG0  = 30.0    # first lobe angle, deg
R_FILLET   = 12.5    # concave blend between lobe and body
BORE_D     = 17.0    # through bore under the pocket floor
FLOOR_Z    = 3.0     # pocket floor height
SPRING_ID, SPRING_OD, SPRING_DEPTH = 26.5, 31.5, 1.0   # spring seat groove in the underside

# --- Nut-specific ---
VARIANTS = {
    # ER20-A nut: 30 mm A/F hex, 0.25 mm/side clearance, pocket 9 mm + 2 mm x 45 deg lead-in
    "ER20": dict(hex_af=30.5, chamfer=2.0),
    # ER16-A nut (DIN 6499 hex, M22x1.5, 25 A/F, D28, L17.5, supplier data):
    # same 0.25 mm/side clearance, same floor and lead-in as ER20
    "ER16": dict(hex_af=25.5, chamfer=2.0),
}

def hex_wire(af, z):
    rc = af / math.sqrt(3)   # centre-to-corner; corners on +/-Y, flats normal to X
    pts = [V(rc*math.cos(math.radians(90+60*i)), rc*math.sin(math.radians(90+60*i)), z) for i in range(6)]
    return Part.makePolygon(pts + [pts[0]])

def build(v):
    p = VARIANTS[v]
    if p["hex_af"] is None:
        sys.exit(f"{v}: nut dimensions not set - refusing to guess")
    af, ch = p["hex_af"], p["chamfer"]
    # outer 6-lobe profile
    shape = Part.makeCylinder(R_BODY, H)
    for i in range(N_LOBES):
        a = math.radians(LOBE_ANG0 + 360/N_LOBES*i)
        lc = V(LOBE_PCD_R*math.cos(a), LOBE_PCD_R*math.sin(a), 0)
        shape = shape.fuse(Part.makeCylinder(R_LOBE, H, lc))
        for s in (-1, 1):
            # blend circle tangent to the lobe and the body circle
            d = R_BODY + R_FILLET; l = R_LOBE + R_FILLET; r = lc.Length
            phi = math.acos((d*d + r*r - l*l) / (2*d*r))
            b = a + s*phi
            fc = V(d*math.cos(b), d*math.sin(b), 0)
            t_body = V(R_BODY*math.cos(b), R_BODY*math.sin(b), 0)
            u = fc - lc; u.normalize(); t_lobe = lc + u*R_LOBE
            tri = Part.Face(Part.makePolygon([V(0,0,0), t_lobe, t_body, V(0,0,0)])).extrude(V(0,0,H))
            shape = shape.fuse(tri).cut(Part.makeCylinder(R_FILLET, H, fc))
    shape = shape.removeSplitter()
    # hex pocket with lead-in chamfer
    shape = shape.cut(Part.Face(hex_wire(af, FLOOR_Z)).extrude(V(0,0,H-ch-FLOOR_Z)))
    shape = shape.cut(Part.makeLoft([hex_wire(af, H-ch), hex_wire(af+2*ch, H)], True))
    # bore and spring seat
    shape = shape.cut(Part.makeCylinder(BORE_D/2, H))
    shape = shape.cut(Part.makeCylinder(SPRING_OD/2, SPRING_DEPTH).cut(Part.makeCylinder(SPRING_ID/2, SPRING_DEPTH)))
    return shape.removeSplitter()

v, out = sys.argv[-2], sys.argv[-1]
s = build(v)
s.exportStep(out)
print(f"{v}: valid={s.isValid()} solids={len(s.Solids)} faces={len(s.Faces)} vol={s.Volume:.1f}")
