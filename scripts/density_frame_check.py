"""Where the x' shift of the hadron showers in the density notebook comes from (issue #2; the notebook's summary reports about -12 mm).

Mean transverse position x' (in the plane of incidence, positive = away from the beam line) of the deposits, energy-weighted per
event and then averaged over events, in two frames:
- the density notebook's shower frame: origin at the energy-weighted centre of the event's first hit layer, axes rotated by the
  incoming angles (as in notebooks/11_density.ipynb);
- the issue #1 axis: the line from the vertex along (theta, phi), origin at its entry point on the front face (z = Z_FRONT);
for events inside the issue #1 fiducial region (the axis at least 10 cm inside the instrumented area in all layers) and outside it,
with the mean E_vis / p as a measure of leakage. s1, 4-20 GeV/c, prompt deposits (t < 100 ns).
    python scripts/density_frame_check.py      -> results/density/frame_offset.csv"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import core_mip as cm  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "density", "frame_offset.csv")
P_RANGE = (4.0, 20.0)


def x_prime(dx, dy, dz, th, ph):
    return dx * np.cos(th) * np.cos(ph) + dy * np.cos(th) * np.sin(ph) - dz * np.sin(th)


def offsets(particle):
    hits, ev = cm.load(particle)
    feat = pd.read_parquet(os.path.join(cm.FEAT, f"{particle}.parquet"), columns=["event_number", "fiducial", "E_vis"]).set_index("event_number")
    h = hits[hits.energy > 0]
    e = ev.loc[h.event_number.values]
    m = (e.p.values >= P_RANGE[0]) & (e.p.values < P_RANGE[1])
    h, e = h[m], e[m]
    th, ph, w, evn = e.theta.values, e.phi.values, h.energy.values, h.event_number.values
    x, y, z = h.x.values, h.y.values, h.z.values
    t = np.tan(th)
    xa = x_prime(x - cm.Z_FRONT * t * np.cos(ph), y - cm.Z_FRONT * t * np.sin(ph), z - cm.Z_FRONT, th, ph)
    z0 = h.groupby("event_number").z.transform("min").values
    w0 = np.where(z == z0, w, 0.0)
    c = pd.DataFrame({"ev": evn, "wx": w0 * x, "wy": w0 * y, "w": w0}).groupby("ev").sum()
    xs = x_prime(x - (c.wx / c.w).reindex(evn).values, y - (c.wy / c.w).reindex(evn).values, z - z0, th, ph)
    d = pd.DataFrame({"ev": evn, "a": xa * w, "s": xs * w, "E": w}).groupby("ev").sum()
    per = pd.DataFrame({"axis": d.a / d.E, "first_layer": d.s / d.E}).join(ev[["p"]]).join(feat)
    rows = []
    for name, sel in (("fiducial", per.fiducial), ("not fiducial", ~per.fiducial), ("all", per.fiducial | ~per.fiducial)):
        q = per[sel]
        se = lambda v: float(v.std() / np.sqrt(len(v)))
        rows.append({"particle": particle, "events": name, "n": int(len(q)),
                     "x_axis_mm": float(q.axis.mean()), "x_axis_se": se(q.axis),
                     "x_first_layer_mm": float(q.first_layer.mean()), "x_first_layer_se": se(q.first_layer),
                     "E_vis_per_p": float((q.E_vis / q.p).mean())})
    return rows


if __name__ == "__main__":
    t = pd.DataFrame([r for p in ("electron", "muon", "pion", "proton") for r in offsets(p)])
    t.to_csv(OUT, index=False, float_format="%.4g")
    print(t.to_string(index=False, float_format=lambda v: f"{v:.3g}"))
