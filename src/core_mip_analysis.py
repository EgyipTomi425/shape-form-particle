"""Issue #1 analysis: every number of notebooks 09/10, the answer pages and results/core_mip/answers.json comes from these functions.

Selection ("fiducial"): the entry point is in the instrumented area, the axis stays 10 cm inside the area in all 60 layers (no lateral
leakage at the outer edge or at the beam hole; 59 % of the events, median theta 0.36 rad) and E_vis > 0.
Statistics: bootstrap (Poisson weights, 200 replicas) for ratios of sums and efficiencies, binomial errors for shares, Hanley-McNeil
errors for AUCs; the interaction length by a truncated, censored exponential maximum likelihood. Thresholds at 99 % electron rejection
come from the train+val electrons and are applied to the test split; the combined classifier is trained on the train split.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core_mip as cm  # noqa: E402
from paths import RESULTS  # noqa: E402

PARTICLES = ("electron", "muon", "pion", "proton")
HADRONS = ("pion", "proton")
PAIRS = (("electron", "pion"), ("electron", "proton"), ("pion", "proton"))
SAMPLE = os.environ.get("CORE_MIP_SAMPLE", "s1")           # s2: the independent second sample (same finder, no re-tuning)
ANS = os.path.join(RESULTS, "core_mip") if SAMPLE == "s1" else os.path.join(RESULTS, "core_mip", SAMPLE)


def feat_path(particle):
    return os.path.join(cm.FEAT, f"{particle}.parquet" if SAMPLE == "s1" else f"{particle}_{SAMPLE}.parquet")
COLORS = {"electron": "#0072B2", "muon": "#009E73", "pion": "#D55E00", "proton": "#CC79A7"}   # Okabe-Ito, colour-blind safe
LAMBDA_PDG = {"proton": 21.2, "pion": 26.0}       # cm: the layer stack with the PDG interaction lengths (200 GeV/c), README ch. 1
WINDOWS = {1: (0.9, 1.1), 5: (4.75, 5.25), 20: (19.5, 20.0)}
P_RANGES = ((1.0, 2.0), (2.0, 3.0), (3.0, 5.0), (5.0, 10.0), (10.0, 20.01))
FIT = (8.0, 80.0)                                 # cm along the axis: window of the interaction-length fit
SEED, N_BOOT = 12345, 200


# ----------------------------------------------------------------------------------------------------------------- data and statistics
def load(particle, fiducial=True):
    f = pd.read_parquet(feat_path(particle))
    sel = f.entry_inside & (f.E_vis > 0)
    if fiducial:
        sel &= f.fiducial
    return f[sel].reset_index(drop=True)


def load_all(fiducial=True):
    return {p: load(p, fiducial) for p in PARTICLES}


def boot_ratio(num, den):
    """Ratio of sums and its bootstrap standard error."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    W = np.random.default_rng(SEED).poisson(1.0, (N_BOOT, len(num))).astype(float)
    b = (W @ num) / np.maximum(W @ den, 1e-30)
    return float(num.sum() / den.sum()), float(b.std(ddof=1))


def share(mask):
    m = np.asarray(mask, bool)
    p = float(m.mean()) if len(m) else np.nan
    return p, float(np.sqrt(p * (1 - p) / max(len(m), 1)))


def auc(neg, pos):
    """P(score_pos > score_neg) and its Hanley-McNeil standard error."""
    neg, pos = np.asarray(neg, float), np.asarray(pos, float)
    neg, pos = neg[np.isfinite(neg)], pos[np.isfinite(pos)]
    a = roc_auc_score(np.r_[np.zeros(len(neg)), np.ones(len(pos))], np.r_[neg, pos])
    q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
    n1, n2 = len(pos), len(neg)
    return float(a), float(np.sqrt((a * (1 - a) + (n1 - 1) * (q1 - a * a) + (n2 - 1) * (q2 - a * a)) / (n1 * n2)))


def eff_at_rejection(s_e_cal, s_e_test, s_h_test, rej=0.99):
    """Hadron efficiency at the electron rejection rej: threshold from the calibration electrons, applied to the test split;
    bootstrap error over both samples; also the electron rejection reached on the test electrons."""
    rng = np.random.default_rng(SEED)
    t = np.quantile(s_e_cal, rej)
    eff = float(np.mean(s_h_test > t))
    b = [np.mean(rng.choice(s_h_test, len(s_h_test)) > np.quantile(rng.choice(s_e_cal, len(s_e_cal)), rej)) for _ in range(N_BOOT)]
    return {"eff": eff, "se": float(np.std(b, ddof=1)), "threshold": float(t), "e_rejection_test": float(np.mean(s_e_test <= t)),
            "n_h": int(len(s_h_test)), "n_e_cal": int(len(s_e_cal))}


def in_range(f, lo, hi):
    return f[(f.p >= lo) & (f.p < hi)]


# --------------------------------------------------------------------------------------------------------------------------------- Q1
def q1_fractions(F, by="bin"):
    """MIP / core / halo shares per particle and momentum bin: ratio of sums (+- bootstrap SE) and event mean."""
    rows = []
    for p, f in F.items():
        for b, g in f.groupby(by):
            E = g.E_vis.values
            for ver in ("strict", "narrow"):
                for comp, col in (("MIP", f"f_MIP_{ver}"), ("core", f"f_core_{ver}"), ("halo", "f_halo")):
                    v, se = boot_ratio(g[col].values * E, E)
                    rows.append({"particle": p, by: int(b), "version": ver, "component": comp, "ratio_of_sums": v, "se": se,
                                 "event_mean": float(g[col].mean()), "n": len(g)})
    return pd.DataFrame(rows)


def q1_rscan(F):
    """Containment within R (ratio of sums, folding and the cell-centre rule) and the AUC of f_near_R per pair and bin."""
    cont = {}
    for p, f in F.items():
        E = f.E_vis.values
        cont[p] = {f"R{R}": boot_ratio(f[f"f_near_R{R}"].values * E, E)[0] for R in (25, 50, 75, 100)}
        cont[p]["centre_R50"] = boot_ratio(f.f_near_centre_R50.values * E, E)[0]
        # relative to 10 cm: the share of the energy within 10 cm that lies within R (for the MIP track of the muon)
        cont[p]["rel_to_R100"] = {f"R{R}": cont[p][f"R{R}"] / cont[p]["R100"] for R in (25, 50, 75)}
    rows = []
    for a, b in PAIRS:
        for k in range(20):
            fa, fb = F[a][F[a].bin == k], F[b][F[b].bin == k]
            for R in (25, 50, 75, 100):
                v, se = auc(fa[f"f_near_R{R}"], fb[f"f_near_R{R}"])
                rows.append({"pair": f"{a}_vs_{b}", "bin": k, "R_mm": R, "auc": v, "se": se})
            v, se = auc(fa.f_near_centre_R50, fb.f_near_centre_R50)
            rows.append({"pair": f"{a}_vs_{b}", "bin": k, "R_mm": "centre50", "auc": v, "se": se})
    return cont, pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------------------------------------------- Q2
def formula_axial_share():
    """The axial term's share of the in-detector energy in the fitted formula (the 'infographic' numbers) at 1, 5, 20 GeV/c."""
    out = {}
    for p in PARTICLES:
        s = json.load(open(os.path.join(RESULTS, "particles", p, "formula_values.json")))["slab"]
        key = "a detektorban: nyom"
        out[p] = {w: (float(s[key][s["p [GeV]"].index(float(w))]) if key in s else 0.0) for w in WINDOWS}
    return out


def q2_table(F):
    ax = formula_axial_share()
    rows = []
    for p, f in F.items():
        for w, (lo, hi) in WINDOWS.items():
            g = in_range(f, lo, hi)
            E = g.E_vis.values
            r = {"particle": p, "p_window": f"{lo}-{hi}", "p_mean": float(g.p.mean()), "events": len(g)}
            for name, col in (("f_core", "f_core_strict"), ("f_core_narrow", "f_core_narrow"), ("f_MIP", "f_MIP_strict"),
                              ("f_core_plus_MIP", "f_near_R50"), ("f_halo", "f_halo"), ("truth_primary_share", "f_primary"),
                              ("truth_primary_within_5cm", "f_primary_near_R50"),
                              ("truth_core_from_primary_passage", "f_core_primary_strict")):
                r[name], r[name + "_se"] = boot_ratio(g[col].values * E, E)
            r["f_core_event_mean"] = float(g.f_core_strict.mean())
            r["f_core_event_mean_se"] = float(g.f_core_strict.std(ddof=1) / np.sqrt(len(g)))
            # half-width window: sensitivity to the window
            c, h = 0.5 * (lo + hi), 0.25 * (hi - lo)
            gg = in_range(f, c - h, c + h)
            r["f_core_half_window"] = boot_ratio(gg.f_core_strict.values * gg.E_vis.values, gg.E_vis.values)[0]
            for cls in ("before_layer1", "inelastic", "stops", "decay", "exits", "leaves"):
                r[f"truth_{cls}"] = float((g.true_end == cls).mean())
            r["truth_reaches_tile1"] = float((g.k_last_true >= 0).mean())
            r["truth_reaches_tile2"] = float((g.k_last_true >= 1).mean())
            inter = g.true_end.isin(["before_layer1", "inelastic"])
            for tag, m in (("interacting", inter), ("not_interacting", ~inter)):
                gm = g[m.values]
                r[f"f_core_{tag}"] = (boot_ratio(gm.f_core_strict.values * gm.E_vis.values, gm.E_vis.values)[0] if len(gm) > 20 else np.nan)
                r[f"share_{tag}"] = float(m.mean())
            r["formula_axial_term"] = ax[p][w]
            rows.append(r)
    return pd.DataFrame(rows)


def auc_by_bin(F, a, b, col, sign=1.0, split=None):
    rows = []
    for k in range(20):
        fa, fb = F[a][F[a].bin == k], F[b][F[b].bin == k]
        if split:
            fa, fb = fa[fa.split == split], fb[fb.split == split]
        v, se = auc(sign * fa[col].values, sign * fb[col].values)
        rows.append({"bin": k, "auc": v, "se": se})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------------------------------------------- Q3
def p_long(F, ver="strict"):
    rows = []
    for p, f in F.items():
        for k, g in f.groupby("bin"):
            r = {"particle": p, "bin": int(k), "n": len(g)}
            for x in (8, 10):
                r[f"P_L_ge_{x}"], r[f"P_L_ge_{x}_se"] = share(g[f"L_MIP_{ver}"] >= x)
                if p in HADRONS:
                    r[f"truth_P_L_ge_{x}"] = share(g.L_true >= x)[0]
            r["P_L_gt_0"] = share(g[f"L_MIP_{ver}"] > 0)[0]
            rows.append(r)
    return pd.DataFrame(rows)


def interaction_depth(f, ver):
    """Interaction-depth estimate x and 'observed' flag for the finder (x = z_start - half a pitch: the steel in front of the start
    tile) and for the truth (x = L_true + half a pitch: the steel behind the primary's last tile); censored events carry the depth up
    to which the particle was seen without an interaction."""
    half = 0.5 * cm.PITCH / 10.0 / np.cos(f.theta.values)
    if ver == "truth":
        inter = f.true_end.isin(["inelastic", "before_layer1"]).values
        x = np.where(f.true_end.values == "before_layer1", 0.0, f.L_true.values + half)
        return np.where(inter, x, f.L_true.values), inter
    obs = (f[f"end_{ver}"] == "shower").values
    return np.where(obs, f[f"z_start_{ver}"].values - half, f[f"L_MIP_{ver}"].values), obs


def lambda_mle(x, obs, lo=FIT[0], hi=FIT[1]):
    """Exponential interaction length from depths x (observed interactions or censoring depths), truncated to [lo, hi]."""
    keep = x > lo
    xx, oo = np.minimum(x[keep], hi), obs[keep] & (x[keep] <= hi)
    n = int(oo.sum())
    lam = float((xx - lo).sum() / max(n, 1))
    return {"lambda_cm": lam, "se": lam / np.sqrt(max(n, 1)), "interactions": n, "events": int(keep.sum())}


def q3_lambda(F):
    out = {}
    mu = F["muon"][F["muon"].p >= 2.0]
    fake = {}
    for ver in ("strict", "narrow"):
        x, obs = interaction_depth(mu, ver)
        r = lambda_mle(x, obs)
        fake[ver] = r
    out["muon_false_start"] = {v: {"lambda_fake_cm": r["lambda_cm"], "se": r["se"], "starts": r["interactions"],
                                   "share_with_start": float((mu[f"end_{v}"] == "shower").mean())} for v, r in fake.items()}
    for p in HADRONS:
        f = F[p]
        out[p] = {}
        for lo, hi in ((3.0, 20.01),) + P_RANGES[2:]:
            g = in_range(f, lo, hi)
            r = {}
            for ver in ("truth", "strict", "narrow"):
                x, obs = interaction_depth(g, ver)
                r[ver] = lambda_mle(x, obs)
                if ver != "truth":
                    lf, sf = fake[ver]["lambda_cm"], fake[ver]["se"]
                    le, se = r[ver]["lambda_cm"], r[ver]["se"]
                    inv = 1 / le - 1 / lf
                    r[ver]["lambda_corrected_cm"] = float(1 / inv)
                    r[ver]["lambda_corrected_se"] = float(np.hypot(se / le ** 2, sf / lf ** 2) / inv ** 2)
            out[p][f"{lo:g}-{min(hi, 20):g}"] = r
        out[p]["pdg_stack_cm"] = LAMBDA_PDG[p]
    return out


def q3_truth_agreement(F, ver="strict"):
    """The finder's start tile against the true interaction (between the primary's last tile k_last and the next tile)."""
    rows = []
    for p in HADRONS:
        for lo, hi in P_RANGES:
            g = in_range(F[p], lo, hi)
            g = g[g.true_end.isin(["inelastic", "before_layer1"])]
            k, kl = g[f"k_start_{ver}"].values, np.where(g.true_end == "before_layer1", -1, g.k_last_true).astype(int)
            found = k >= 0
            n = max(len(g), 1)
            rows.append({"particle": p, "p_range": f"{lo:g}-{min(hi, 20):g}", "events": len(g),
                         "exact": float((found & (k >= np.maximum(kl, 0)) & (k <= kl + 1)).sum() / n),
                         "within_1": float((found & (k >= kl - 1) & (k <= kl + 2)).sum() / n),
                         "early": float((found & (k < kl - 1)).sum() / n), "late": float((found & (k > kl + 2)).sum() / n),
                         "no_start": float((~found).sum() / n)})
    return pd.DataFrame(rows)


def scores(f, feat, pair):
    """Feature oriented so that the second particle of the pair scores high."""
    a, b = pair
    sign = {"f_core": -1.0 if a == "electron" else -1.0, "L_MIP": 1.0, "seg1": -1.0}.get(feat, 1.0)
    if feat == "seg1":
        return sign * (f.seg1_core_mip.values + f.seg1_halo_mip.values)
    col = {"f_core": "f_core_strict", "L_MIP": "L_MIP_strict"}[feat]
    return sign * f[col].values


def q3_classify(F):
    """Per pair and momentum bin: AUC (test split) and the efficiency at 99 % rejection of the first particle, for f_core, L_MIP,
    the readout-segment variable seg1 and the combination (logistic regression on f_core and L_MIP, trained on train)."""
    rows = []
    for a, b in PAIRS:
        for k in range(20):
            fa, fb = F[a][F[a].bin == k], F[b][F[b].bin == k]
            cal_a = fa[fa.split.isin(["train", "val"])]
            ta, tb = fa[fa.split == "test"], fb[fb.split == "test"]
            tr = pd.concat([fa[fa.split == "train"].assign(y=0), fb[fb.split == "train"].assign(y=1)])
            X = lambda d: np.c_[d.f_core_strict.values, np.log1p(d.L_MIP_strict.values)]
            lr = LogisticRegression(max_iter=1000).fit(X(tr), tr.y.values)
            feats = {"f_core": lambda d: scores(d, "f_core", (a, b)), "L_MIP": lambda d: scores(d, "L_MIP", (a, b)),
                     "seg1": lambda d: scores(d, "seg1", (a, b)), "combined": lambda d: lr.decision_function(X(d))}
            for name, fn in feats.items():
                v, se = auc(fn(ta), fn(tb))
                r = {"pair": f"{a}_vs_{b}", "bin": k, "feature": name, "auc": v, "auc_se": se}
                if a == "electron":
                    e = eff_at_rejection(fn(cal_a), fn(ta), fn(tb))
                    r.update({"eff99": e["eff"], "eff99_se": e["se"], "e_rejection_test": e["e_rejection_test"]})
                    if name == "L_MIP":       # the same electron threshold applied to the true passage length (a perfect finder)
                        r["eff99_truth_bound"] = float(np.mean(tb.L_true.values > e["threshold"]))
                rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------------ Gabor's four MIP-segment claims
def claims(F, ver="strict"):
    out = {"claim1_may_or_may_not_be_there": [], "claim2_starts_at_entry": [], "claim4_indicator": []}
    for p in PARTICLES:
        for lo, hi in P_RANGES:
            g = in_range(F[p], lo, hi)
            L = g[f"L_MIP_{ver}"]
            r = {"particle": p, "p_range": f"{lo:g}-{min(hi, 20):g}", "events": len(g), "P_L_gt_0": share(L > 0)[0],
                 "P_L_ge_8": share(L >= 8)[0], "P_L_ge_10": share(L >= 10)[0]}
            if p in HADRONS:
                r["truth_reaches_tile1"] = float((g.k_last_true >= 0).mean())
            out["claim1_may_or_may_not_be_there"].append(r)
            if p in HADRONS:
                late = g[f"late_run_layers_{ver}"] >= 4
                prim = g[f"late_run_primary_{ver}"] > 0.5
                out["claim2_starts_at_entry"].append({
                    "particle": p, "p_range": r["p_range"], "events": len(g), "late_run_ge_4_tiles": float(late.mean()),
                    "late_run_by_primary": float((late & prim).mean()), "late_run_by_secondary": float((late & ~prim).mean())})
    for lo, hi in P_RANGES:
        e = in_range(F["electron"], lo, hi)[f"L_MIP_{ver}"]
        for p in HADRONS:
            h = in_range(F[p], lo, hi)[f"L_MIP_{ver}"]
            for x in (8, 10):
                pe, ph = float((e >= x).mean()), float((h >= x).mean())
                out["claim4_indicator"].append({"hadron": p, "p_range": f"{lo:g}-{min(hi, 20):g}", "L_min_cm": x, "P_electron": pe,
                                                "P_hadron": ph, "likelihood_ratio": ph / max(pe, 1e-4), "purity_equal_mix": ph / (ph + pe)})
    return {k: pd.DataFrame(v) for k, v in out.items()}


def claim3_pre_interaction(particle, ver="strict", pmin=3.0):
    """Energy in the tiles the primary crossed before its interaction (truth: tiles 0 .. k_last - 1, events with k_last >= 2), in MIP
    units per tile: the primary's own core deposit, secondaries near the axis, energy outside R (all secondaries: backsplash, delta
    rays); and why such tiles fail the MIP-like test."""
    C = cm.load_cache(particle, SAMPLE)
    f = pd.read_parquet(feat_path(particle))
    sel = (f.entry_inside & f.fiducial & (f.p >= pmin) & (f.true_end == "inelastic") & (f.k_last_true >= 2)).values
    mip = C["mip"][sel]
    u, h, pu = C["core"][sel] / mip, (C["all"][sel] - C["core"][sel]) / mip, C["prim_core"][sel] / mip
    kl = f.k_last_true.values[sel]
    pre = (np.arange(cm.N_LAYERS)[None, :] < kl[:, None]) & C["inside"][sel]
    fin = json.load(open(os.path.join(cm.FEAT, "mip_finder.json")))["versions"][ver]
    nc = C["ncell"][sel]
    fail_core, fail_halo, fail_cells = u > fin["core_up"], h > fin["halo_up"], nc > fin["cells_up"]
    n = pre.sum()
    return {"tiles": int(n), "events": int(sel.sum()), "core_mip_per_tile": float(u[pre].mean()),
            "primary_core_mip_per_tile": float(pu[pre].mean()), "secondary_core_mip_per_tile": float((u - pu)[pre].mean()),
            "outside_R_mip_per_tile": float(h[pre].mean()), "share_tiles_with_outside_R_gt_1mip": float((h[pre] > 1).mean()),
            "share_tiles_non_mip": float((fail_core | fail_halo | fail_cells)[pre].mean()),
            "share_tiles_fail_core": float(fail_core[pre].mean()), "share_tiles_fail_halo": float(fail_halo[pre].mean()),
            "share_tiles_fail_cells": float(fail_cells[pre].mean())}


def start_visibility(particle, pmin_list=P_RANGES):
    """Truth: is a hadronic interaction visible as a shower start? Core energy (MIP) in the two tiles after the primary's last tile,
    against the finder's start threshold core_sum + core_sum_per_gev * p (events with an inelastic interaction inside the stack)."""
    C = cm.load_cache(particle, SAMPLE)
    f = pd.read_parquet(feat_path(particle))
    fin = json.load(open(os.path.join(cm.FEAT, "mip_finder.json")))["versions"]["strict"]
    sel = (f.entry_inside & f.fiducial & (f.true_end == "inelastic") & (f.k_last_true <= cm.N_LAYERS - 3)).values
    u = C["core"][sel] / C["mip"][sel]
    kl = f.k_last_true.values[sel].astype(int)
    rows = np.arange(len(kl))
    e2 = u[rows, kl + 1] + u[rows, kl + 2]
    thr = fin["core_sum"] + fin.get("core_sum_per_gev", 0.0) * f.p.values[sel]
    out = []
    for lo, hi in pmin_list:
        m = (f.p.values[sel] >= lo) & (f.p.values[sel] < hi)
        out.append({"particle": particle, "p_range": f"{lo:g}-{min(hi, 20):g}", "events": int(m.sum()),
                    "median_core_mip_two_tiles": float(np.median(e2[m])), "share_below_threshold": float(np.mean(e2[m] <= thr[m]))})
    return pd.DataFrame(out)


def calibration_theta_check(n_bins=6):
    """Muons, p >= 2 GeV/c, tiles 2-60 crossed by the axis: most probable value of the core energy per tile, raw and times cos(theta),
    in bins of theta (the path-length correction is right if the corrected MPV is flat)."""
    C = cm.load_cache("muon", SAMPLE)
    sel = (C["p"] >= 2.0)[:, None] & C["inside"] & (C["core"] > 0)
    sel[:, 0] = False
    th = np.broadcast_to(C["theta"][:, None], C["core"].shape)[sel]
    raw = C["core"][sel] * 1e3
    cor = raw * np.cos(th)
    edges = np.quantile(th, np.linspace(0, 1, n_bins + 1))

    def mpv(x):
        """Mode of the distribution: a parabola fitted to the log of a fine histogram within +-12 % of the smoothed maximum."""
        h, e = np.histogram(x, bins=800, range=(0, np.quantile(x, 0.99)))
        c = 0.5 * (e[1:] + e[:-1])
        x0 = c[np.argmax(np.convolve(h, np.ones(9) / 9, mode="same"))]
        w = (c > 0.88 * x0) & (c < 1.12 * x0) & (h > 0)
        a2, a1, _ = np.polyfit(c[w] - x0, np.log(h[w]), 2)
        return float(x0 - a1 / (2 * a2))
    rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (th >= a) & (th < b)
        rows.append({"theta_lo": float(a), "theta_hi": float(b), "mpv_raw_MeV": mpv(raw[m]), "mpv_cos_MeV": mpv(cor[m]), "tiles": int(m.sum())})
    return pd.DataFrame(rows)


def muon_outside_r_per_tile(pmin=3.0):
    """Reference for claim 3: energy outside R per crossed tile for muons (no hadronic interaction, so no backsplash), in MIP."""
    C = cm.load_cache("muon", SAMPLE)
    f = pd.read_parquet(feat_path("muon"))
    sel = (f.entry_inside & f.fiducial & (f.p >= pmin)).values
    h = (C["all"][sel] - C["core"][sel]) / C["mip"][sel]
    ins = C["inside"][sel]
    return {"outside_R_mip_per_tile": float(h[ins].mean()), "share_tiles_with_outside_R_gt_1mip": float((h[ins] > 1).mean())}
