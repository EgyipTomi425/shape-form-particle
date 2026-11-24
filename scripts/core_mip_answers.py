"""All numbers and figures of the issue #1 answers (core, MIP segment, halo) from results/features/<particle>.parquet.
    python scripts/core_mip_answers.py      -> results/core_mip/*.csv, answers.json, *.png
Order of the full chain: src/core_mip.py build (muon first) -> scripts/core_mip_tune.py -> src/core_mip.py features -> this script."""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import core_mip as cm  # noqa: E402
import core_mip_analysis as A  # noqa: E402
import core_mip_figures as G  # noqa: E402


def main():
    os.makedirs(A.ANS, exist_ok=True)
    F = A.load_all()
    full = {p: A.load(p, fiducial=False) for p in A.PARTICLES}
    csv = lambda d, n: d.round(5).to_csv(os.path.join(A.ANS, n), index=False)
    ans = {"selection": {p: {"events_fiducial": len(F[p]), "events_entry_inside": len(full[p]),
                             "fiducial_share": len(F[p]) / len(full[p])} for p in A.PARTICLES},
           "finder": json.load(open(os.path.join(cm.FEAT, "mip_finder.json"))),
           "calibration": {k: v for k, v in json.load(open(os.path.join(cm.FEAT, "mip_calibration.json" if A.SAMPLE == "s1" else f"mip_calibration_{A.SAMPLE}.json"))).items()
                           if k in ("core_quantiles_mip", "definition", "unit")}}
    cal = json.load(open(os.path.join(cm.FEAT, "mip_calibration.json" if A.SAMPLE == "s1" else f"mip_calibration_{A.SAMPLE}.json")))
    th = A.calibration_theta_check(); csv(th, "q3_calibration_theta.csv"); G.q3_calibration(cal, th)
    ans["calibration"].update({"mpv_layer1_MeV": cal["mpv"][0] * 1e3, "mpv_median_MeV": float(np.median(cal["mpv"])) * 1e3,
                               "hwhm_left_median_MeV": float(np.median(cal["w_left"])) * 1e3,
                               "hwhm_right_median_MeV": float(np.median(cal["w_right"])) * 1e3,
                               "zero_frac_median": float(np.median(cal["zero_frac"]))})
    # Q1
    q1 = A.q1_fractions(F); csv(q1, "q1_fractions.csv"); G.q1_fractions(q1)
    cont, rs = A.q1_rscan(F); csv(rs, "q1_rscan_auc.csv"); G.q1_rscan(cont, rs)
    ans["q1"] = {"containment": cont}
    sep = rs[(rs.bin >= 2) & (rs.R_mm != "centre50")].assign(sep=lambda d: 1 - d.auc).groupby(["pair", "R_mm"]).sep.mean()
    ans["q1"]["e_h_separation_2_20GeV"] = {f"{a}|R{b}": float(v) for (a, b), v in sep.items() if a.startswith("electron")}
    # Q2
    q2 = A.q2_table(F); csv(q2, "q2_table.csv"); G.q2_fcore(F, q2)
    aucs = {"pion vs proton: P(f_core of p > f_core of pi)": A.auc_by_bin(F, "pion", "proton", "f_core_strict", split="test"),
            "electron vs pion: P(f_core of pi < f_core of e)": A.auc_by_bin(F, "electron", "pion", "f_core_strict", sign=-1.0, split="test"),
            "electron vs proton: P(f_core of p < f_core of e)": A.auc_by_bin(F, "electron", "proton", "f_core_strict", sign=-1.0, split="test")}
    csv(pd.concat([d.assign(pair=k) for k, d in aucs.items()]), "q2_auc_fcore.csv"); G.q2_auc(aucs)
    # Q3
    pl = A.p_long(F); csv(pl, "q3_p_long.csv"); G.q3_lmip(F); G.q3_plong(pl)
    lam = A.q3_lambda(F); ans["q3_lambda"] = lam; G.q3_survival(F, lam, A.interaction_depth)
    agr = A.q3_truth_agreement(F); csv(agr, "q3_truth_agreement.csv"); G.q3_truth(agr)
    vis = pd.concat([A.start_visibility(p) for p in A.HADRONS]); csv(vis, "q3_start_visibility.csv")
    cl = A.q3_classify(F); csv(cl, "q3_classify.csv"); G.q3_eff99(cl)
    cls = A.claims(F)
    for k, d in cls.items():
        csv(d, f"{k}.csv")
    ans["claim3_pre_interaction_tiles"] = {p: A.claim3_pre_interaction(p) for p in A.HADRONS}
    ans["claim3_pre_interaction_tiles"]["muon_reference"] = A.muon_outside_r_per_tile()
    json.dump(ans, open(os.path.join(A.ANS, "answers.json"), "w"), indent=1, default=float)
    print("written:", sorted(os.listdir(A.ANS)))


if __name__ == "__main__":
    main()
