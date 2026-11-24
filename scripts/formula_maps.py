"""Density of the final formula per particle at 1, 5 and 20 GeV/c (3D metric, the uncut body of revolution), with the iso-density
contour that holds 95 % of the energy. No data needed: works from the checkpoints and the grid constants.
    python formula_maps.py            output: results/formula_maps.png"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # repository root
sys.path.insert(0, os.path.join(ROOT, "src"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

import protonlab
import shapelab

P_SHOW = (1.0, 5.0, 20.0)
NAME = {"electron": "Electron", "muon": "Muon", "pion": "Pion", "proton": "Proton"}
DECADES = 6
INK, MUTED = "#1f2933", "#52606d"

fig, axes = plt.subplots(4, 3, figsize=(13, 11.5), sharex=True, sharey=True, constrained_layout=True)
for row, particle in enumerate(NAME):
    C = protonlab.load_common_for(particle)                 # only the 00_common definitions (grid, Formula); no data is loaded
    D = os.path.join(ROOT, "results", "particles", particle)
    model, *_ = shapelab.build_final(C, particle, D, 0.0, 1.0, metric="slab")   # lnp0 / lnp_s come from the checkpoint
    with torch.no_grad():
        logP = model(torch.log(torch.tensor(P_SHOW, device=C["DEVICE"])))
    P = logP.exp().cpu().numpy()                                                 # cell probabilities (B, N_Z, N_R)
    lrho = (logP - C["LOG_VOL"]).cpu().numpy() / np.log(10)                     # log10 density [1/mm³]
    ze, re = C["Z_EDGES"].cpu().numpy(), C["R_EDGES"].cpu().numpy()
    redges = np.concatenate([-re[::-1], re[1:]])
    vmax = lrho.max()
    for col, p in enumerate(P_SHOW):
        ax = axes[row, col]
        img = np.concatenate([lrho[col][:, ::-1], lrho[col]], 1).T               # r mirrored: (2 N_R, N_Z)
        mesh = ax.pcolormesh(ze, redges, img, cmap="Blues", vmin=vmax - DECADES, vmax=vmax, shading="flat", rasterized=True)
        o = np.argsort(-lrho[col], axis=None)                                     # 95 % iso-density level: densest cells up to 0.95
        level = lrho[col].ravel()[o][np.searchsorted(np.cumsum(P[col].ravel()[o]), 0.95)]
        zc, rc = 0.5 * (ze[1:] + ze[:-1]), 0.5 * (redges[1:] + redges[:-1])
        ax.contour(zc, rc, img, levels=[level], colors=INK, linewidths=1.0, linestyles="solid")
        ax.axvline(0, color=MUTED, lw=0.6, ls=":")
        if row == 0:
            ax.set_title(f"p = {p:g} GeV/c", fontsize=11, color=INK)
        if col == 0:
            ax.set_ylabel(f"{NAME[particle]}\nr [mm]", fontsize=11, color=INK)
        if row == 3:
            ax.set_xlabel("z' [mm]", color=INK)
        ax.tick_params(colors=MUTED, labelsize=9)
        for s in ax.spines.values():
            s.set_color("#cbd2d9")
    cb = fig.colorbar(mesh, ax=axes[row, :], shrink=0.9, pad=0.01)
    cb.set_label("log₁₀ ρ [1/mm³]", color=INK, fontsize=9)
    cb.ax.tick_params(colors=MUTED, labelsize=8)
axes[0, 0].set_xlim(-200, 1450)
axes[0, 0].set_ylim(-700, 700)
fig.suptitle("Density of the final formula (3D metric, uncut body of revolution); line: iso-density contour holding 95 % of the energy",
             fontsize=12, color=INK)
out = os.path.join(ROOT, "results", "formula_maps.png")
fig.savefig(out, dpi=110)
print("saved", out)
