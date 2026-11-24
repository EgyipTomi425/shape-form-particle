"""Independent second sample: the issue #1 numbers of s2 (same finder, tuned on s1; own MIP calibration) against s1, each difference
in units of the combined statistical error (z). Run after `CORE_MIP_SAMPLE=s2 python scripts/core_mip_answers.py`.
    python scripts/core_mip_s2_check.py      -> results/core_mip/s2_check.csv, s2_check.json"""
import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D1 = os.path.join(ROOT, "results", "core_mip")
D2 = os.path.join(D1, "s2")
rows = []


def add(group, name, v1, e1, v2, e2):
    e = float(np.hypot(e1, e2))
    rows.append({"group": group, "quantity": name, "s1": float(v1), "s2": float(v2), "s1_err": float(e1), "s2_err": float(e2),
                 "z": float((v1 - v2) / e) if e > 0 else np.nan})


def tables(name):
    return pd.read_csv(os.path.join(D1, name)), pd.read_csv(os.path.join(D2, name))


# Q1: shares of MIP segment, core, halo (bootstrap errors)
a, b = tables("q1_fractions.csv")
key = ["particle", "bin", "version", "component"]
m = a.merge(b, on=key, suffixes=("1", "2"))
for _, r in m[(m.version == "strict") & m.bin.isin([1, 4, 9, 19])].iterrows():
    add("Q1 shares", f"{r.particle} bin {r.bin} {r.component}", r.ratio_of_sums1, r.se1, r.ratio_of_sums2, r.se2)
# Q2 windows
a, b = tables("q2_table.csv")
m = a.merge(b, on=["particle", "p_window"], suffixes=("1", "2"))
for _, r in m.iterrows():
    add("Q2 f_core", f"{r.particle} {r.p_window} GeV/c", r.f_core1, r.f_core_se1, r.f_core2, r.f_core_se2)
    for c in ("truth_before_layer1", "truth_inelastic", "truth_stops"):
        if r[c + "1"] > 0.005 or r[c + "2"] > 0.005:
            add("Q2 truth", f"{r.particle} {r.p_window} {c}", r[c + "1"], np.sqrt(r[c + "1"] * (1 - r[c + "1"]) / r.events1),
                r[c + "2"], np.sqrt(r[c + "2"] * (1 - r[c + "2"]) / r.events2))
# Q2 AUC of f_core (Hanley-McNeil)
a, b = tables("q2_auc_fcore.csv")
m = a.merge(b, on=["pair", "bin"], suffixes=("1", "2"))
for _, r in m[m.bin.isin([1, 4, 9, 19])].iterrows():
    add("Q2 AUC", f"{r.pair.split(':')[0]} bin {r.bin}", r.auc1, r.se1, r.auc2, r.se2)
# Q3: P(L >= 8 / 10 cm)
a, b = tables("q3_p_long.csv")
m = a.merge(b, on=["particle", "bin"], suffixes=("1", "2"))
for _, r in m[m.bin.isin([1, 4, 9, 19])].iterrows():
    for x in (8, 10):
        add("Q3 P(L>=x)", f"{r.particle} bin {r.bin} L>={x}", r[f"P_L_ge_{x}1"], r[f"P_L_ge_{x}_se1"], r[f"P_L_ge_{x}2"], r[f"P_L_ge_{x}_se2"])
# Q3: agreement with the truth (binomial)
a, b = tables("q3_truth_agreement.csv")
m = a.merge(b, on=["particle", "p_range"], suffixes=("1", "2"))
for _, r in m.iterrows():
    for c in ("within_1", "early", "no_start"):
        add("Q3 truth agreement", f"{r.particle} {r.p_range} {c}", r[c + "1"], np.sqrt(r[c + "1"] * (1 - r[c + "1"]) / r.events1),
            r[c + "2"], np.sqrt(r[c + "2"] * (1 - r[c + "2"]) / r.events2))
# Q3: classification (test split)
a, b = tables("q3_classify.csv")
m = a.merge(b, on=["pair", "bin", "feature"], suffixes=("1", "2"))
for _, r in m[m.bin.isin([2, 4, 9, 19])].iterrows():
    add("Q3 AUC", f"{r.pair} bin {r.bin} {r.feature}", r.auc1, r.auc_se1, r.auc2, r.auc_se2)
    if r.pair.startswith("electron"):
        add("Q3 eff99", f"{r.pair} bin {r.bin} {r.feature}", r.eff991, r.eff99_se1, r.eff992, r.eff99_se2)
# interaction lengths
j1, j2 = (json.load(open(os.path.join(d, "answers.json"))) for d in (D1, D2))
for p in ("pion", "proton"):
    for rng in ("3-20", "3-5", "5-10", "10-20"):
        for v in ("truth", "strict", "narrow"):
            x1, x2 = j1["q3_lambda"][p][rng][v], j2["q3_lambda"][p][rng][v]
            add("Q3 lambda", f"{p} {rng} {v}", x1["lambda_cm"], x1["se"], x2["lambda_cm"], x2["se"])
x1, x2 = j1["q3_lambda"]["muon_false_start"]["strict"], j2["q3_lambda"]["muon_false_start"]["strict"]
add("Q3 lambda", "muon false starts (lambda_fake)", x1["lambda_fake_cm"], x1["se"], x2["lambda_fake_cm"], x2["se"])
df = pd.DataFrame(rows)
df.round(5).to_csv(os.path.join(D1, "s2_check.csv"), index=False)
# MIP calibration of the two samples (no error model: relative difference per tile)
c1 = json.load(open(os.path.join(ROOT, "results", "features", "mip_calibration.json")))
c2 = json.load(open(os.path.join(ROOT, "results", "features", "mip_calibration_s2.json")))
rel = np.array(c2["mpv"]) / np.array(c1["mpv"]) - 1
z = df.z.abs().dropna()
summ = {"comparisons": int(len(z)), "within_1_sigma": float((z <= 1).mean()), "within_2_sigma": float((z <= 2).mean()),
        "within_3_sigma": float((z <= 3).mean()), "max_abs_z": float(z.max()),
        "largest": df.loc[df.z.abs().nlargest(5).index, ["quantity", "s1", "s2", "z"]].round(4).to_dict("records"),
        "mpv_rel_diff_median": float(np.median(rel)), "mpv_rel_diff_max": float(np.abs(rel).max())}
json.dump(summ, open(os.path.join(D1, "s2_check.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
print(df.dropna(subset=["z"]).groupby("group").z.apply(lambda s: f"n={len(s)}, |z|<=2: {np.mean(np.abs(s) <= 2):.2f}, max |z| {np.abs(s).max():.2f}").to_string())
