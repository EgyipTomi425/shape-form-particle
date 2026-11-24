"""Q1 picture: where the MIP segment, the core and the halo lie in the shower. Mean energy density per event against the depth along
the axis (from the entry point) and the distance from the axis (cell centres), prompt deposits, fiducial events at 4.5-5.5 GeV/c of s1,
with the core radius R = 5 cm and the median shower start of the finder.
    python scripts/core_mip_region_map.py      -> results/core_mip/q1_region_map.npz (the figure: core_mip_figures.q1_region_map)"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import core_mip as cm  # noqa: E402
from core_mip_analysis import ANS, PARTICLES  # noqa: E402

P_WINDOW = (4.5, 5.5)
DEPTH = np.arange(0.0, 142.0, 2.05)          # cm along the axis (about one tile per bin)
RAD = np.arange(0.0, 42.0, 2.0)              # cm from the axis


def region_map(particle):
    hits, ev = cm.load(particle)
    f = pd.read_parquet(os.path.join(cm.FEAT, f"{particle}.parquet"),
                        columns=["event_number", "p", "entry_inside", "fiducial", "E_vis", "z_start_strict"])
    f = f[f.entry_inside & f.fiducial & (f.E_vis > 0) & (f.p >= P_WINDOW[0]) & (f.p < P_WINDOW[1])]
    h = hits[hits.event_number.isin(f.event_number.values)]
    e = ev.loc[h.event_number.values]
    th, ph = e.theta.values, e.phi.values
    n = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], 1)
    xyz = h[["x", "y", "z"]].values
    r = np.linalg.norm(xyz - (xyz * n).sum(1)[:, None] * n, axis=1) / 10.0
    k = np.clip(np.rint((h.z.values - cm.Z_L1) / cm.PITCH), 0, cm.N_LAYERS - 1)
    depth = (cm.Z_L1 + cm.PITCH * k - cm.Z_FRONT) / np.cos(th) / 10.0
    H, _, _ = np.histogram2d(depth, r, bins=[DEPTH, RAD], weights=h.energy.values * 1e3)      # MeV
    ring = np.pi * (RAD[1:] ** 2 - RAD[:-1] ** 2)                                             # cm^2
    dens = H / len(f) / (ring[None, :] * np.diff(DEPTH)[:, None])                            # MeV / cm^3 per event
    return dens, len(f), float(np.nanmedian(f.z_start_strict.values))


if __name__ == "__main__":
    out = {"depth_edges": DEPTH, "r_edges": RAD, "p_window": np.array(P_WINDOW)}
    for p in PARTICLES:
        d, nev, zs = region_map(p)
        out[f"{p}_density"], out[f"{p}_events"], out[f"{p}_z_start_median"] = d, nev, zs
        print(f"{p}: {nev} events, median shower start {zs:.1f} cm", flush=True)
    np.savez_compressed(os.path.join(ANS, "q1_region_map.npz"), **out)
