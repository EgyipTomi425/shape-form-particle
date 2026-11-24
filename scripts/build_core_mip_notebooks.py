"""Builds and runs notebooks/09_axis_core.ipynb (Q1, Q2) and notebooks/10_mip_segment.ipynb (Q3) of particle issue #1 (the issue
proposed 08/09; 08 is taken by the proton shape notebook). Every number comes from src/core_mip_analysis.py; the same functions write
results/core_mip/ through scripts/core_mip_answers.py.
    python scripts/build_core_mip_notebooks.py [--no-run]"""
import os
import sys

import nbformat
from nbclient import NotebookClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NB = os.path.join(ROOT, "notebooks")
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell

SETUP = r'''import os, sys, json
_d = os.getcwd()                                              # find the repository root, so that the notebook runs from any folder
while not os.path.exists(os.path.join(_d, "ALL-README.md")) and os.path.dirname(_d) != _d:
    _d = os.path.dirname(_d)
os.chdir(_d)
sys.path.insert(0, os.path.abspath("src"))
import numpy as np, pandas as pd
from IPython.display import display
import core_mip as cm, core_mip_analysis as A, core_mip_figures as G
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40)
F = A.load_all()                                              # fiducial events with E_vis > 0
FINDER = json.load(open(os.path.join(cm.FEAT, "mip_finder.json")))
HAVE_CACHE = all(os.path.exists(os.path.join(cm.CACHE_DIR, f"{p}_s1.npz")) for p in A.PARTICLES)
NO_CACHE = ("needs the per-layer cache, which is not in git: python src/core_mip.py build <particle> (muon first; "
            "reads the simulation CSVs from $LFHCAL_DATA)")
print({p: len(f) for p, f in F.items()}, "events;  finder:", FINDER["versions"]["strict"], ";  per-layer cache:", HAVE_CACHE)'''

DEFS = """**Definitions** (issue #1). The **axis** is the straight line of the incoming direction (θ, φ) from the vertex (0, 0, 0); it enters
the calorimeter at the front face z = 3620.0 mm (ePIC `LFHCAL_zmin`). In front of the first tile there are 40.4 mm of steel (25.4 mm
mounting plate + 15 mm module front wall); every layer is 4 mm scintillator, 0.8 mm Kapton and 15.2 mm steel, so **a tile sits in front of
its absorber** and an interaction in the steel behind tile k is first seen in tile k + 1. Depths are measured from the entry point along the
axis. Every event is split into three regions: the **MIP segment** (energy within R = 5 cm of the axis in the tiles before the shower
start), the **core** (within 5 cm, from the shower start on) and the **halo** (farther than 5 cm): `E_vis = E_MIP + E_core + E_halo`.
A cell's energy is shared by the part of its 48.6 × 48.6 mm face inside R (8 × 8 points, "folding"); the cell-centre rule is kept for
comparison. Only prompt deposits (t < 100 ns) count, as in the report.

**Selection and statistics.** The entry point must be in the instrumented area and the axis must stay 10 cm inside it in all 60 layers
(the points 10 cm from the axis in ±x and ±y lie in the instrumented area; 59 % of the events). Ratios of sums carry bootstrap errors, AUCs Hanley–McNeil
errors; efficiencies at 99 % electron rejection use thresholds from the train + val electrons applied to the test split.

**Simulation truth** (validation only). The CSV gives each cell's earliest contributor with its complete list of direct daughters. The
primary's cells are its prompt passage along the axis (99.9 % within 33 mm and within 0.06 ns of straight-line flight), so the deepest
primary tile marks the end of its track; daughters with hadronic products (n, π, d, α, ...) mark an inelastic interaction, no primary cell
at all an interaction in the front steel. About 13 % of crossed tiles miss the primary's cell (gaps, δ electrons arriving first)."""

NB09 = [
    md("# 09 – Axis, core and halo (particle issue #1, Q1 and Q2)\n\n" + DEFS),
    code(SETUP),
    md("## Q1 – How is the visible energy split between MIP segment, core and halo?\n\nShares of `E_vis` (ratio of sums over the "
       "events of each 1 GeV/c bin, and the event mean; the MIP segment is found as described in notebook 10)."),
    code('Q1 = A.q1_fractions(F)\nG.q1_fractions(Q1)\n'
         't = Q1[Q1.version == "strict"].pivot_table(index=["particle", "bin"], columns="component", values=["ratio_of_sums", "event_mean"])\n'
         'display(t.loc[(slice(None), [0, 1, 2, 4, 9, 14, 19]), :].round(3))'),
    md("### Where the energy goes\n\nMean energy density per event against the depth along the axis and the distance from it, "
       "4.5–5.5 GeV/c (cell centres; computed from the CSVs by `scripts/core_mip_region_map.py`). Dashed: R = 5 cm; orange: the "
       "median shower start of pions and protons. Inside 5 cm before the mark lies the MIP segment, after it the core, outside the halo."),
    code('_ = G.q1_region_map() if os.path.exists("results/core_mip/q1_region_map.npz") else print("run scripts/core_mip_region_map.py first")'),
    md("### Why R = 5 cm\n\nThe energy within R of the axis (folding), and the separation of electrons from hadrons by that energy "
       "(AUC averaged over 2–20 GeV/c). One cell is 48.6 mm wide: below about 5 cm the folding assumption (uniform energy in a cell) "
       "dominates, so R = 2.5 cm is a statement about the granularity rather than about the shower."),
    code('CONT, RS = A.q1_rscan(F)\nG.q1_rscan(CONT, RS)\n'
         'display(pd.DataFrame({p: {k: v for k, v in c.items() if k != "rel_to_R100"} for p, c in CONT.items()}).T.round(3))\n'
         'print("muon: share of the energy within 10 cm that lies within R:", {k: round(v, 3) for k, v in CONT["muon"]["rel_to_R100"].items()})\n'
         'sep = RS[(RS.bin >= 2) & (RS.R_mm != "centre50")].assign(sep=lambda d: 1 - d.auc).pivot_table(index="pair", columns="R_mm", values="sep")\n'
         'display(sep.loc[["electron_vs_pion", "electron_vs_proton"]].round(4))'),
    md("## Q2 – Is the core fraction of protons ~60 % at 1 GeV/c and ~43 % for pions?\n\nThe infographic numbers are the share of the "
       "*axial term* of the fitted shape formula (a model component for the primary's passage), not a measurement. The table compares "
       "them with the measured `f_core`, with the whole axis region `f_core + f_MIP`, and with the simulation truth: the primary's own "
       "share of `E_vis`, the part of `f_core` that the primary itself deposited after the MIP segment (its passage, e.g. the Bragg "
       "region of a stopping proton), and how the primary track ended."),
    code('Q2 = A.q2_table(F)\n'
         'cols = ["particle", "p_window", "events", "f_core", "f_core_se", "f_core_event_mean", "f_core_half_window", "f_MIP", "f_core_plus_MIP",\n'
         '        "formula_axial_term", "truth_primary_share", "truth_core_from_primary_passage", "f_core_interacting", "f_core_not_interacting",\n'
         '        "truth_before_layer1", "truth_inelastic", "truth_stops", "truth_reaches_tile2"]\n'
         'display(Q2[cols].round(3))\n_ = G.q2_fcore(F, Q2)'),
    md("### `f_core` as a feature\n\nAUC per momentum bin on the test split (0.5 = no separation). For π vs. p the orientation is fixed "
       "(probability that a proton has the larger `f_core`), so a change of sign is visible. The ratio core / rest of the shower is a "
       "monotonic function of `f_core` and has the same AUC."),
    code('AUC = {"pion vs proton": A.auc_by_bin(F, "pion", "proton", "f_core_strict", split="test"),\n'
         '       "electron vs pion": A.auc_by_bin(F, "electron", "pion", "f_core_strict", sign=-1.0, split="test"),\n'
         '       "electron vs proton": A.auc_by_bin(F, "electron", "proton", "f_core_strict", sign=-1.0, split="test")}\n'
         'G.q2_auc(AUC)\ndisplay(pd.DataFrame({k: d.set_index("bin").auc for k, d in AUC.items()}).loc[[0, 1, 2, 4, 9, 14, 19]].round(3))'),
]

NB10 = [
    md("# 10 – The MIP segment (particle issue #1, Q3)\n\n" + DEFS),
    code(SETUP),
    md("## MIP calibration with muons\n\nPer tile: the most probable value (MPV, 1 MIP) and the half widths at half maximum of the core "
       "energy times cos θ (path-length correction), muons with p ≥ 2 GeV/c; the first tile is calibrated on its own like every other tile. "
       "Right: the MPV in bins of θ, raw and corrected."),
    code('CAL = json.load(open(os.path.join(cm.FEAT, "mip_calibration.json")))\n'
         'print(f"MPV tile 1: {CAL[\'mpv\'][0]*1e3:.4f} MeV, median of the tiles: {np.median(CAL[\'mpv\'])*1e3:.4f} MeV")\n'
         'print("core energy of muon tiles in MIP units, quantiles:", {k: round(v, 2) for k, v in CAL["core_quantiles_mip"].items()})\n'
         'if HAVE_CACHE:\n    TH = A.calibration_theta_check()\n    G.q3_calibration(CAL, TH)\n    display(TH.round(4))\n'
         'else:\n    print("theta check of the calibration:", NO_CACHE)'),
    md("## The MIP-segment finder\n\nA tile is **MIP-like** if its core energy is at most `core_up` MIP, its energy outside R at most "
       "`halo_up` MIP and at most `cells_up` cells fire (> 0.3 MIP). The shower starts at the first `n_consec` consecutive non-MIP "
       "tiles whose summed core energy exceeds `core_sum + core_sum_per_gev · p` MIP (p is known from the tracker); empty tiles do not "
       "interrupt the segment. `L_MIP` is the depth of the last tile with a deposit on the axis before the start. The parameters were "
       "chosen on the train split against the simulation truth (`scripts/core_mip_tune.py`): among the settings with at most 3 % muon "
       "false starts per interaction length, those within 0.01 of the best ±1-tile agreement with the true "
       "interaction (π and p, 3–5, 5–10, 10–20 GeV/c), then the best L_MIP efficiency at 99 % electron rejection. Gábor's original rule "
       "(core within the MIP band, outside-R energy below a threshold, ≤ 2 cells, two consecutive non-MIP tiles) and the narrow-deposit "
       "version are evaluated with the same metrics."),
    code('TM = FINDER["train_metrics"]\n'
         'k = ["core_up", "halo_up", "cells_up", "n_consec", "core_sum", "core_sum_per_gev"]\n'
         'show = ["had_pm1_3_20", "pion_early", "pion_late", "pion_missed", "muon_false_per_lambda", "eff99_pion_1_3", "eff99_pion_3_20", "eff99_proton_1_3", "eff99_proton_3_20"]\n'
         'rows = {"chosen": TM["strict"], "issue rule (2.5 MIP band, no energy condition)": TM["gabor_rule"], "narrow deposit": TM["narrow"]}\n'
         'display(pd.DataFrame({n: {a: r[a] for a in k + show} for n, r in rows.items()}).T.round(3))'),
    md("## L_MIP distributions and P(L_MIP ≥ 8 / 10 cm)\n\nDashed: the same probability for the true passage of the primary "
       "(depth of its last tile before the interaction)."),
    code('G.q3_lmip(F)\nPL = A.p_long(F)\nG.q3_plong(PL)\n'
         'CL = A.claims(F)\ndisplay(CL["claim1_may_or_may_not_be_there"].round(3))'),
    md("## Effective interaction length\n\nTruncated, censored exponential likelihood on 8–80 cm (p ≥ 3 GeV/c; the interaction is placed "
       "in the steel in front of the start tile; events without a start are censored). `truth` uses the primary's last tile; the finder "
       "values use the finder's start tile; `corrected` removes the muon false-start rate. The PDG values of "
       "the layer stack are for 200 GeV/c."),
    code('LAM = A.q3_lambda(F)\nG.q3_survival(F, LAM, A.interaction_depth)\n'
         'rows = []\nfor p in A.HADRONS:\n'
         '    for rng, r in LAM[p].items():\n'
         '        if isinstance(r, dict):\n'
         '            rows.append({"particle": p, "p_range": rng, **{f"{v} [cm]": f"{x[\'lambda_cm\']:.1f} ± {x[\'se\']:.1f}" for v, x in r.items()},\n'
         '                         "strict corrected [cm]": f"{r[\'strict\'][\'lambda_corrected_cm\']:.1f}", "PDG stack [cm]": LAM[p]["pdg_stack_cm"]})\n'
         'display(pd.DataFrame(rows))\nprint("muon false starts:", LAM["muon_false_start"])'),
    md("## The start tile against the true interaction\n\n`exact`: start in the tile right after the interaction or in the tile in "
       "front of it; `within_1`: one more tile on either side; `early` / `late`: farther away; `no_start`: no shower start "
       "found. The second table shows the core energy in the two tiles after the true interaction, compared with the start "
       "threshold."),
    code('AGR = A.q3_truth_agreement(F)\nG.q3_truth(AGR)\ndisplay(AGR.round(3))\n'
         'display(pd.concat([A.start_visibility(p) for p in A.HADRONS]).round(3)) if HAVE_CACHE else print("visibility of the start:", NO_CACHE)'),
    md("## Hadron identification\n\nTest split: AUC and hadron efficiency at 99 % electron rejection for `f_core`, `L_MIP`, the "
       "readout-segment variable `seg1` (energy of tiles 1–5, which the ePIC LFHCal reads out as one channel) and the combination "
       "(logistic regression on `f_core` and `L_MIP`, trained on the train split). `eff99_truth_bound` applies the electron threshold "
       "of L_MIP to the true passage length of the hadrons."),
    code('CLS = A.q3_classify(F)\nG.q3_eff99(CLS)\n'
         'for pair in ("electron_vs_pion", "electron_vs_proton"):\n'
         '    display(CLS[CLS.pair == pair].pivot_table(index="bin", columns="feature", values="eff99").loc[[1, 2, 4, 9, 14, 19]].round(3).rename_axis(pair))\n'
         'display(CLS[CLS.pair == "pion_vs_proton"].pivot_table(index="bin", columns="feature", values="auc").loc[[0, 1, 2, 4, 9, 19]].round(3).rename_axis("pion vs proton AUC"))'),
    md("## Gábor's four properties of the MIP segment\n\n1. *it may or may not be there* – shares above, and the truth share of "
       "primaries that reach tile 1;\n2. *if it is there, it always starts at the entry point* – MIP-like runs of ≥ 4 tiles that begin "
       "after the shower start, and who carries them (truth);\n3. *very small energy deposit, along the axis only* – energy in the tiles "
       "the primary crossed before its interaction (truth);\n4. *8–10 cm or longer is a very powerful hadron indicator* – probabilities "
       "for electrons and hadrons and the likelihood ratio."),
    code('display(CL["claim2_starts_at_entry"].round(3))\n'
         'display(pd.DataFrame({p: A.claim3_pre_interaction(p) for p in A.HADRONS}).round(3)) if HAVE_CACHE else print("claim 3:", NO_CACHE)\n'
         'display(CL["claim4_indicator"].round(3))'),
]


def build(name, cells, run=True):
    nb = nbformat.v4.new_notebook()
    nb.cells = cells
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    path = os.path.join(NB, name)
    if run:
        NotebookClient(nb, timeout=3600, kernel_name="python3", resources={"metadata": {"path": NB}}).execute()
    nbformat.write(nb, path)
    print("written", path)


if __name__ == "__main__":
    run = "--no-run" not in sys.argv
    build("09_axis_core.ipynb", NB09, run)
    build("10_mip_segment.ipynb", NB10, run)
