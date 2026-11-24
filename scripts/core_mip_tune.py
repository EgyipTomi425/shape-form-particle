"""Choose the MIP-segment finder parameters against the simulation truth, on the train split only (issue #1).

Truth: the primary's track ends with an inelastic interaction between its last tile k_last and the next tile; the finder's start layer
agrees if it is k_last or k_last + 1 ("exact"; backsplash can light up tile k_last) and within one more layer on either side ("+-1").
No primary cell at all means an interaction before tile 1 (true start 0). Events: fiducial (axis 10 cm inside the area in all 60
layers), train split. The start threshold may grow with the momentum (core_sum + core_sum_per_gev * p MIP; the momentum of a charged
particle is known from the tracker; CMS-HGCAL also uses energy-dependent thresholds). Rule for the strict version: (1) keep the settings
within 0.01 of the best "+-1" agreement averaged over pions and protons at 3-5, 5-10 and 10-20 GeV/c (where a visible shower start is
well defined); (2) among them take the best mean hadron efficiency at 99 % electron rejection with L_MIP alone (pion, proton; 1-3 and
3-20 GeV/c); only settings whose muon false-start rate (p >= 2 GeV/c) stays at or below 3 % per interaction length lambda_I = 21.2 cm
take part (the CALICE Si-W ECAL level, 2.2-3.2 % of muons per interaction length, arXiv:1411.7215). The narrow version is Gabor's definition
as given: no core limit, energy outside R below the muon 99 % quantile, at most 2 fired cells, two consecutive non-MIP tiles.
    python scripts/core_mip_tune.py     -> results/core_mip/finder_scan.csv, results/features/mip_finder.json
"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import core_mip as cm  # noqa: E402
from paths import RESULTS  # noqa: E402

LAMBDA_I = 21.2        # cm, nuclear interaction length of the layer stack (PDG values, README chapter 1)
MAX_FAKE_PER_LAMBDA = 0.03   # muon false starts per interaction length: the CALICE Si-W ECAL level (2.2-3.2 %, arXiv:1411.7215)
GRID = {"core_up": [2.0, 2.5, 3.0], "halo_up": [1.1, 3.0, np.inf], "cells_up": [2, 4, 255], "n_consec": [2, 3],
        "core_sum": [2.0, 4.0, 6.0, 10.0], "core_sum_per_gev": [0.0, 0.25, 0.5, 1.0]}


def subset(C, m):
    return {k: v[m] for k, v in C.items() if isinstance(v, np.ndarray) and v.shape[:1] == m.shape}


def prepare():
    out = {}
    for p in ("electron", "muon", "pion", "proton"):
        C = cm.load_cache(p)
        m = (C["split"] == 0) & C["inside_margin"].all(1)
        out[p] = subset(C, m)
    return out


def agreement(C, k, end, pmin, pmax):
    """Shares of interacting primaries (truth) by the finder's start layer relative to the true interaction gap."""
    sel = (C["p"] >= pmin) & (C["p"] < pmax)
    has, kl = C["truth_has_prim"], C["truth_k_last"].astype(np.int64)
    inter = sel & (~has | C["truth_inelastic"])
    lo = np.where(has, kl, -1)                      # start layer k_last (backsplash) or k_last + 1; front interaction: 0
    found = end == 0
    exact = found & (k >= np.maximum(lo, 0)) & (k <= lo + 1)
    pm1 = found & (k >= lo - 1) & (k <= lo + 2)
    early, late = found & (k < lo - 1), found & (k > lo + 2)
    stops = sel & has & ~C["truth_inelastic"] & ~C["truth_mu_daughter"] & (kl < cm.N_LAYERS - 1)
    n = max(inter.sum(), 1)
    return {"n": int(inter.sum()), "exact": exact[inter].sum() / n, "pm1": pm1[inter].sum() / n, "early": early[inter].sum() / n,
            "late": late[inter].sum() / n, "missed": (~found)[inter].sum() / n,
            "stop_false_start": float(found[stops].mean()) if stops.any() else np.nan}


def eff99(Le, Lh):
    thr = np.quantile(Le, 0.99)
    return float(np.mean(Lh > thr))


def evaluate(D, prm):
    res = dict(prm)
    seg = {}
    for p, C in D.items():
        k, last, end, _, _ = cm.find_segment(C, **prm)
        s = cm.depth_cm(C["theta"])
        L = np.where(last >= 0, s[np.arange(len(k)), np.maximum(last, 0)], 0.0)
        seg[p] = (k, end, L)
    for p in ("pion", "proton"):
        for tag, (a, b) in {"": (1.0, 20.1), "_1_2": (1.0, 2.0), "_3_20": (3.0, 20.1), "_3_5": (3.0, 5.0), "_5_10": (5.0, 10.0),
                            "_10_20": (10.0, 20.1)}.items():
            for key, v in agreement(D[p], seg[p][0], seg[p][1], a, b).items():
                res[f"{p}{tag}_{key}"] = v
    mu = D["muon"]
    sel = mu["p"] >= 2.0
    k, end, _ = seg["muon"]
    fake = end[sel] == 0
    # false-start rate per cm of axis: starts / exposed path (to the start or to the last tile)
    s = cm.depth_cm(mu["theta"][sel])
    expo = np.where(fake, s[np.arange(sel.sum()), np.minimum(k[sel], cm.N_LAYERS - 1)], s[:, -1]) - s[:, 0]
    rate = fake.sum() / max(expo.sum(), 1e-9)
    res["muon_false_start"] = float(fake.mean())
    res["muon_false_per_lambda"] = float(1 - np.exp(-rate * LAMBDA_I))
    for tag, (a, b) in {"_1_3": (1.0, 3.0), "_3_20": (3.0, 20.1)}.items():
        e = D["electron"]
        me = (e["p"] >= a) & (e["p"] < b)
        for p in ("pion", "proton"):
            h = D[p]
            mh = (h["p"] >= a) & (h["p"] < b)
            res[f"eff99_{p}{tag}"] = eff99(seg["electron"][2][me], seg[p][2][mh])
    return res


def choose(df):
    ok = df[df.muon_false_per_lambda <= MAX_FAKE_PER_LAMBDA]
    best = ok.had_pm1_3_20.max()
    return ok[ok.had_pm1_3_20 >= best - 0.01].sort_values("eff99_mean", ascending=False).iloc[0]


def muon_halo_q99(D):
    mu = D["muon"]
    sel = (mu["p"] >= 2.0)[:, None] & mu["inside"]
    return float(np.quantile(((mu["all"] - mu["core"]) / mu["mip"])[sel], 0.99))


if __name__ == "__main__":
    D = prepare()
    rows = []
    keys = list(GRID)
    for vals in itertools.product(*GRID.values()):
        prm = dict(zip(keys, vals))
        rows.append(evaluate(D, prm))
    halo99 = muon_halo_q99(D)
    narrow = evaluate(D, {"core_up": np.inf, "halo_up": round(halo99, 3), "cells_up": 2, "n_consec": 2, "core_sum": 0.0,
                          "core_sum_per_gev": 0.0})
    df = pd.DataFrame(rows)
    df["had_pm1"] = 0.5 * (df.pion_pm1 + df.proton_pm1)
    df["had_pm1_3_20"] = df[[f"{p}_{r}_pm1" for p in ("pion", "proton") for r in ("3_5", "5_10", "10_20")]].mean(1)
    df["eff99_mean"] = df[["eff99_pion_1_3", "eff99_pion_3_20", "eff99_proton_1_3", "eff99_proton_3_20"]].mean(1)
    os.makedirs(os.path.join(RESULTS, "core_mip"), exist_ok=True)
    df.round(5).to_csv(os.path.join(RESULTS, "core_mip", "finder_scan.csv"), index=False)
    strict = choose(df)
    gabor = evaluate(D, {"core_up": 2.5, "halo_up": round(halo99, 3), "cells_up": 2, "n_consec": 2, "core_sum": 0.0, "core_sum_per_gev": 0.0})
    narrow, gabor = pd.Series(narrow), pd.Series(gabor)
    for ser in (narrow, gabor):
        ser["had_pm1_3_20"] = np.mean([ser[f"{p}_{q}_pm1"] for p in ("pion", "proton") for q in ("3_5", "5_10", "10_20")])
    pick = lambda r: {k: (float(r[k]) if k != "n_consec" and k != "cells_up" else int(r[k])) for k in keys}
    out = {"versions": {"strict": pick(strict), "narrow": pick(narrow)},
           "rule": "train split, fiducial; strict: among settings with <= 3 % muon false starts per lambda_I, those within 0.01 of the "
                   "best +-1 truth agreement averaged over pion, proton and 3-5, 5-10, 10-20 GeV/c, "
                   "then the best mean L_MIP efficiency at 99 % electron rejection; narrow: Gabor's definition (no core limit, outside-R "
                   f"energy below the muon 99 % quantile {halo99:.3f} MIP, at most 2 fired cells, two consecutive non-MIP tiles)",
           "train_metrics": {"strict": strict.to_dict(), "narrow": narrow.to_dict(), "gabor_rule": gabor.to_dict()},
           "gabor_rule": "core <= 2.5 MIP, outside-R energy below the muon 99 % quantile, <= 2 fired cells, two consecutive non-MIP tiles, "
                         "no energy condition (the issue's rule with the band edge of the earlier band scan)"}
    json.dump(out, open(os.path.join(cm.FEAT, "mip_finder.json"), "w"), indent=1, default=float)
    cols = ["core_up", "halo_up", "cells_up", "n_consec", "core_sum", "core_sum_per_gev", "had_pm1_3_20", "pion_pm1", "proton_pm1", "pion_early", "pion_late",
            "pion_missed", "muon_false_start", "muon_false_per_lambda", "eff99_pion_1_3", "eff99_pion_3_20", "eff99_proton_1_3"]
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(df.sort_values("had_pm1_3_20", ascending=False)[cols].head(12).round(3).to_string(index=False))
        print("\nchosen strict:\n", strict[cols].round(3).to_string())
        print("\nnarrow (Gabor's definition):\n", narrow[cols + ["proton_1_2_pm1"]].round(3).to_string())
