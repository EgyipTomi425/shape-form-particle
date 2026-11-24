"""Figures of the issue #1 analysis (used by scripts/core_mip_answers.py and notebooks 09/10). PNG only."""
import os
import sys

import matplotlib
if "ipykernel" not in sys.modules:          # scripts: no display; notebooks keep their inline backend
    matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from core_mip_analysis import ANS, COLORS, PARTICLES  # noqa: E402

COMP = {"MIP": "#E69F00", "core": "#56B4E9", "halo": "#BBBBBB"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.3,
                     "lines.linewidth": 2, "legend.frameon": False})


def save(fig, name):
    os.makedirs(ANS, exist_ok=True)
    fig.savefig(os.path.join(ANS, name), dpi=130, bbox_inches="tight")
    return fig


def q1_fractions(q1, ver="strict"):
    fig, axs = plt.subplots(1, 4, figsize=(15, 3.6), sharey=True)
    for ax, p in zip(axs, PARTICLES):
        d = q1[(q1.particle == p) & (q1.version == ver)].pivot_table(index="bin", columns="component", values="ratio_of_sums")
        x = d.index.values + 0.5
        ax.stackplot(x, d["MIP"], d["core"], d["halo"], colors=[COMP[c] for c in ("MIP", "core", "halo")], labels=["MIP segment", "core", "halo"],
                     edgecolor="white", linewidth=1)
        ax.set_title(p); ax.set_xlabel("p [GeV/c]"); ax.set_xlim(0, 20); ax.set_ylim(0, 1)
    axs[0].set_ylabel("share of E_vis (ratio of sums)")
    axs[-1].legend(loc="lower right", fontsize=9)
    return save(fig, "q1_fractions.png")


def q1_rscan(cont, rs):
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.8))
    R = [2.5, 5.0, 7.5, 10.0]
    for p in PARTICLES:
        a.plot(R, [cont[p][f"R{int(r * 10)}"] for r in R], "o-", color=COLORS[p], label=p, ms=6)
    a.axvline(5, color="0.3", lw=1, ls=":")
    a.set_xlabel("R [cm]"); a.set_ylabel("energy within R (share of E_vis)"); a.legend(); a.set_title("containment around the axis")
    for pair, ls in (("electron_vs_pion", "-"), ("electron_vs_proton", "--")):
        d = rs[(rs.pair == pair) & (rs.R_mm != "centre50") & (rs.bin >= 2)].copy()
        d["sep"] = 1 - d.auc                       # electrons are more contained: separation = P(f_e > f_h)
        m = d.groupby("R_mm").sep.mean()
        b.plot([r / 10 for r in m.index.astype(int)], m.values, "o" + ls, color="0.2", label=pair.replace("_", " "), ms=6)
    b.axvline(5, color="0.3", lw=1, ls=":")
    b.set_xlabel("R [cm]"); b.set_ylabel("AUC (2-20 GeV/c average)"); b.set_title("e/h separation by the energy within R"); b.legend()
    return save(fig, "q1_rscan.png")


def q2_fcore(F, q2):
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    edges = np.arange(0, 20.5, 0.5)
    for p in PARTICLES:
        f = F[p]
        i = np.digitize(f.p.values, edges) - 1
        num = np.bincount(i, f.f_core_strict.values * f.E_vis.values, len(edges) - 1)
        den = np.bincount(i, f.E_vis.values, len(edges) - 1)
        tot = np.bincount(i, f.f_near_R50.values * f.E_vis.values, len(edges) - 1)
        x = 0.5 * (edges[1:] + edges[:-1])
        ax.plot(x, num / np.maximum(den, 1e-30), color=COLORS[p], label=f"{p}: f_core")
        ax.plot(x, tot / np.maximum(den, 1e-30), color=COLORS[p], ls=":", lw=1.5)
        g = q2[q2.particle == p]
        if g.formula_axial_term.max() > 0:
            ax.plot(g.p_mean, g.formula_axial_term, "D", mfc="white", mec=COLORS[p], ms=8, mew=2)
    ax.plot([], [], "k:", lw=1.5, label="f_core + f_MIP (whole axis region)")
    ax.plot([], [], "D", mfc="white", mec="k", ms=8, mew=2, label="formula axial term (infographic)")
    ax.set_xlabel("p [GeV/c]"); ax.set_ylabel("share of E_vis"); ax.set_xlim(0, 20); ax.set_ylim(0, 1)
    ax.legend(fontsize=8, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.17))
    return save(fig, "q2_fcore.png")


def q2_auc(auc_tables):
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for (name, d), c in zip(auc_tables.items(), ("#0072B2", "#CC79A7", "#D55E00")):
        x = d.bin.values + 0.5
        ax.errorbar(x, d.auc, yerr=d.se, fmt="o-", color=c, ms=6, capsize=2, label=name)
    ax.axhline(0.5, color="0.3", lw=1)
    ax.set_xlabel("p [GeV/c]"); ax.set_ylabel("AUC"); ax.set_ylim(0.3, 1.0); ax.set_xlim(0, 20); ax.legend(fontsize=8)
    ax.set_title("f_core as a feature (test split; 0.5 = no separation)")
    return save(fig, "q2_auc_fcore.png")


def q3_lmip(F, ranges=((2, 3), (5, 6), (10, 11), (19, 20))):
    fig, axs = plt.subplots(1, len(ranges), figsize=(15, 3.4), sharey=True)
    bins = np.arange(0, 132, 4.1)
    for ax, (lo, hi) in zip(axs, ranges):
        for p in PARTICLES:
            f = F[p]
            v = f[(f.p >= lo) & (f.p < hi)].L_MIP_strict.values
            ax.hist(np.clip(v, 0, 130), bins=bins, histtype="step", density=True, color=COLORS[p], lw=1.8, label=p)
        ax.set_yscale("log"); ax.set_title(f"{lo}-{hi} GeV/c"); ax.set_xlabel("L_MIP [cm]")
        for x in (8, 10):
            ax.axvline(x, color="0.3", lw=1, ls=":")
    axs[0].set_ylabel("probability density [1/cm]"); axs[-1].legend(fontsize=8)
    return save(fig, "q3_lmip.png")


def q3_plong(pl):
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for ax, x in zip(axs, (8, 10)):
        for p in PARTICLES:
            d = pl[pl.particle == p]
            ax.errorbar(d.bin + 0.5, d[f"P_L_ge_{x}"], yerr=d[f"P_L_ge_{x}_se"], fmt="o-", ms=5, color=COLORS[p], label=p, capsize=2)
            if f"truth_P_L_ge_{x}" in d and d[f"truth_P_L_ge_{x}"].notna().any():
                ax.plot(d.bin + 0.5, d[f"truth_P_L_ge_{x}"], ls="--", lw=1.5, color=COLORS[p])
        ax.set_title(f"P(L_MIP >= {x} cm)  (dashed: true passage of the primary)"); ax.set_xlabel("p [GeV/c]"); ax.set_xlim(0, 20)
    axs[0].set_ylabel("share of events"); axs[0].legend(fontsize=8)
    return save(fig, "q3_plong.png")


def q3_survival(F, lam, interaction_depth):
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.9), sharey=True)
    x = np.arange(0, 100.5, 1.0)
    for ax, p in zip(axs, ("pion", "proton")):
        f = F[p][F[p].p >= 3.0]
        for ver, ls in (("truth", "-"), ("strict", "--"), ("narrow", ":")):
            d, obs = interaction_depth(f, ver)
            dd = np.where(obs, d, np.inf)
            S = np.array([np.mean(dd > v) for v in x])
            L = lam[p]["3-20"][ver]["lambda_cm"]
            ax.plot(x, S, ls=ls, color=COLORS[p] if ver == "truth" else "0.25", label=f"{ver}: lambda = {L:.1f} cm")
        ax.set_yscale("log"); ax.set_xlabel("interaction depth along the axis [cm]"); ax.set_title(f"{p}, p >= 3 GeV/c")
        ax.axvspan(8, 80, color="0.9", zorder=0)
        ax.legend(fontsize=8)
    axs[0].set_ylabel("share without (visible) interaction")
    return save(fig, "q3_survival.png")


def q3_truth(agr):
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    cols = {"exact": "#009E73", "within_1": "#56B4E9", "early": "#D55E00", "late": "#E69F00", "no_start": "#999999"}
    for ax, p in zip(axs, ("pion", "proton")):
        d = agr[agr.particle == p]
        x = np.arange(len(d))
        w = 0.16
        for i, (c, col) in enumerate(cols.items()):
            ax.bar(x + (i - 2) * w, d[c], w, color=col, label=c.replace("_", " "))
        ax.set_xticks(x, d.p_range + " GeV/c"); ax.set_title(f"{p}: start tile vs. true interaction"); ax.set_ylim(0, 1)
    axs[0].set_ylabel("share of interacting events"); axs[0].legend(fontsize=8, ncol=2)
    return save(fig, "q3_truth.png")


def q3_eff99(cl):
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.9), sharey=True)
    st = {"f_core": ("#0072B2", "o"), "L_MIP": ("#D55E00", "s"), "seg1": ("#009E73", "^"), "combined": ("0.15", "D")}
    for ax, pair in zip(axs, ("electron_vs_pion", "electron_vs_proton")):
        for feat, (c, m) in st.items():
            d = cl[(cl.pair == pair) & (cl.feature == feat)]
            ax.errorbar(d.bin + 0.5, d.eff99, yerr=d.eff99_se, fmt=m + "-", color=c, ms=5, capsize=2, label=feat)
        ax.set_title(pair.replace("_", " ") + ": hadron efficiency at 99 % e rejection"); ax.set_xlabel("p [GeV/c]"); ax.set_xlim(0, 20)
        ax.set_ylim(0, 1.02)
    axs[0].set_ylabel("hadron efficiency (test split)"); axs[0].legend(fontsize=8)
    return save(fig, "q3_eff99.png")


def q3_calibration(cal, th):
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 3.6))
    k = np.array(cal["layer"])
    mpv, wl, wr = (np.array(cal[x]) * 1e3 for x in ("mpv", "w_left", "w_right"))
    a.fill_between(k, mpv - wl, mpv + wr, color="#56B4E9", alpha=0.35, lw=0, label="half width at half maximum")
    a.plot(k, mpv, "o-", color="#0072B2", ms=4, label="most probable value (1 MIP)")
    a.plot(k[:1], mpv[:1], "o", mfc="white", mec="#D55E00", ms=9, mew=2, label="first tile (calibrated separately)")
    a.set_xlabel("tile (layer)"); a.set_ylabel("core energy x cos(theta) [MeV]"); a.set_ylim(0, None); a.legend(fontsize=8)
    a.set_title("MIP calibration with muons (p >= 2 GeV/c)")
    x = 0.5 * (th.theta_lo + th.theta_hi)
    b.plot(x, th.mpv_raw_MeV, "s--", color="0.4", ms=6, label="raw")
    b.plot(x, th.mpv_cos_MeV, "o-", color="#0072B2", ms=6, label="x cos(theta)")
    b.set_xlabel("theta [rad]"); b.set_ylabel("most probable value [MeV]"); b.legend(fontsize=8); b.set_title("path-length correction")
    return save(fig, "q3_calibration.png")


def q1_region_map(path=os.path.join(ANS, "q1_region_map.npz")):
    """Mean energy density against depth along the axis and distance from it, with the regions of issue #1."""
    from matplotlib.colors import LogNorm
    z = np.load(path)
    D, R = z["depth_edges"], z["r_edges"]
    vmax = max(z[f"{p}_density"].max() for p in PARTICLES)
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad(cmap(0.0))                                    # empty bins = no energy
    fig, axs = plt.subplots(1, 4, figsize=(17, 3.7), sharey=True)
    for ax, p in zip(axs, PARTICLES):
        d = np.where(z[f"{p}_density"] > 0, z[f"{p}_density"], np.nan)
        im = ax.pcolormesh(D, R, d.T, norm=LogNorm(vmin=vmax * 1e-5, vmax=vmax), cmap=cmap, shading="flat")
        ax.axhline(5.0, color="white", lw=1.8, ls="--")
        zs = float(z[f"{p}_z_start_median"])
        kw = dict(color="white", ha="center", va="center", fontsize=10, fontweight="bold")
        if p in ("pion", "proton"):
            ax.plot([zs, zs], [0, 5], color="#E69F00", lw=4)
            ax.annotate("MIP segment", xy=(zs / 2, 2.5), xytext=(30, 12), color="white", fontsize=9, ha="left",
                        arrowprops=dict(arrowstyle="->", color="white", lw=1.2))
            ax.text(70, 2.5, "core", **kw)
        elif p == "electron":
            ax.text(30, 2.5, "core", color="0.1", ha="center", va="center", fontsize=10, fontweight="bold")
        else:
            ax.text(70, 2.5, "MIP segment", **kw)
        ax.text(95, 20, "halo", **kw)
        ax.set_title(p, fontsize=12)
        ax.set_xlabel("depth along the axis [cm]"); ax.set_xlim(0, 140); ax.set_ylim(0, 30); ax.grid(False)
    axs[0].set_ylabel("distance from the axis [cm]")
    fig.colorbar(im, ax=axs, label="energy density per event [MeV/cm³]", pad=0.01)
    fig.suptitle(f"Where the energy goes, {z['p_window'][0]:g}–{z['p_window'][1]:g} GeV/c: dashed line R = 5 cm, orange mark = median "
                 "shower start (pion, proton)", y=1.02, fontsize=11)
    return save(fig, "q1_region_map.png")
