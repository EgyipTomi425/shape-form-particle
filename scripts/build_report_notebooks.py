"""Copies of all notebooks of the team report (shape-form, 00-07) in report_notebooks/, each extended with a section 8 that puts the
methods of shape-form-particle next to the report's own:
  01_gflash_<p>, 04_cylinder_muon   baseline formula        -> the new formula next to the baseline (both metrics, profiles, formula)
  02_envelope_<p>, 03_drop_<p>      98 % envelope bodies     -> our bodies (refitted drop, super-egg, calibrated iso-density, r95)
  05_mlp_<p>, 06_cnn_<p>            network + distillation   -> the new formula next to the network and the distilled formula
  07_summary                        summary of all models    -> the summary with the new formula (export_new_formula.pt from 05)
The report's cells are unchanged; only the data path is absolute. The report's complete saved results (results/ of shape-form) are
copied to report_notebooks/results/ (protonlab.REPORT_RESULTS), so nothing is retrained. The saved test NLLs of the report's exports
are written into each notebook (REPORT_SAVED) before it runs, so section 8 compares against values that this run does not overwrite.
    python build_report_notebooks.py
    then run 01-04, then 05, 06, then 07 (cd ../report_notebooks; jupyter nbconvert --to notebook --execute --inplace <notebook>)"""
import json
import os
import shutil
import uuid

import numpy as np
import torch

SRC = os.environ.get("SOFIYA_SHAPE_FORM", "/home/user/sofiya/shape-form")                 # the report's notebooks and saved results (read-only)
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # repository root
OUT = os.path.join(ROOT, "report_notebooks")
DATA_ROOT = os.environ.get("LFHCAL_DATA", "/home/user/data/simulations")
KIND = {"01": "baseline", "04": "baseline", "02": "bodies", "03": "bodies", "05": "network", "06": "network", "07": "summary"}


def md(text):
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {}, "source": text.strip("\n").splitlines(True)}


def code(text):
    return {"cell_type": "code", "id": uuid.uuid4().hex[:8], "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(True)}


NOTE = """
> **Copy of the report notebook `{name}`** (shape-form). Its cells are unchanged; only the data path is absolute, and the report's
> saved models are loaded from `results/`. **Section 8** adds {what}.
"""
WHAT = {"baseline": "the shower-shape formula of shape-form-particle next to the baseline",
        "bodies": "the envelope bodies of shape-form-particle",
        "network": "the shower-shape formula of shape-form-particle next to the network and its distilled formula",
        "summary": "the shower-shape formula of shape-form-particle to the summary"}

S8_INTRO = """
## 8. The shape-form-particle formula, fitted directly to the data

shape-form-particle builds the average shower shape from physically separate terms – shower + axial term of the primary particle
(range, attenuation, multiple-scattering widening, Bragg rise) + entry spike + end-of-range blob + far halo, see `../ALL-README.md` –
and fits every parameter (a polynomial in ln T) **directly to the simulated hits** by maximum likelihood, with the detector folding of
this notebook. __CONTEXT__ Nothing is fitted here: the saved final models (`../results/particles/<particle>/`) are loaded and evaluated
on this notebook's test set.

Two metrics:
- **Report metric** (this notebook's `test_nll`). The formula is multiplied by the parameter-free template Ā(z', r), the detector
  acceptance averaged over the incidence angles (the tilted entrance face cuts the body of revolution). The fair reference is the
  report's baseline refitted with the same template ("old formula × Ā").
- **3D metric** of shape-form-particle: the likelihood normalised per event to its own detector slab (between the tilted entrance face
  and the back face). Only models trained in this metric are compared in it: the old formula, the new formula and the MLP, each refitted
  or fine-tuned in 3D.

"saved" next to a recomputed value is the report's own export (before this run) or the number of shape-form-particle (`test_v3.json`).
"""
CONTEXT = {"baseline": "The baseline of this notebook is the starting point: the new formula extends it with the terms above.",
           "network": "Sections 5–7 distil the network: a few formula families are fitted to the network's maps; here the network is "
                      "only the benchmark."}

S8_SETUP = r'''
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "src")))  # particle_shape.py, shapelab.py, protonlab.py
import protonlab
import shapelab

particle = PARTICLES[0]
data = DATA[particle]
OUR = os.path.abspath(os.path.join("..", "results", "particles", particle))   # saved final models of shape-form-particle
PIPE = json.load(open(f"{OUR}/test_v3.json"))                   # its saved test-set numbers (both metrics)
REPORT_SAVED = __REPORT_SAVED__                                 # the report's saved test NLLs (its exports, before this run)
c0, s0 = shapelab.lnp_center_scale(data)
base_name, base_long, _ = shapelab.REPORT_BASE[particle]       # the report's baseline: GFlash, or the cylinder for the muon
_arch = pd.read_csv(f"{OUT_DIR}/{particle}/mlp_architecture.csv").drop_duplicates("config", keep="last")
_row = _arch[_arch.chosen == "◀"].iloc[-1]
H_MLP, L_MLP = int(_row.hidden), int(_row.n_layers)            # architecture of the report's chosen MLP


def ours(kind, metric, C):
    """A saved model of shape-form-particle: 'new' (the final formula), 'base' (the report's baseline refitted), 'mlp' (the report's
    MLP fine-tuned); metric 'std' = report metric (× Ā), 'slab' = 3D metric."""
    if kind == "new":
        return shapelab.build_final(C, particle, OUR, c0, s0, metric=metric)[0]
    n = PIPE["degrees"][f"base_{metric}"]
    st = torch.load(f"{OUR}/{kind}_{metric}" + (f"_n{n}" if kind == "base" else "") + ".pt", map_location=DEVICE,
                    weights_only=False)["state"]
    if kind == "mlp":
        m = FieldModel(H_MLP, L_MLP)
    else:
        m = Formula(base_long, "core_tail", degree=n, lnp0=c0, lnp_s=s0)
        m = shapelab.WithAcceptance(m, torch.ones(N_Z, N_R)) if metric == "std" else m
        st = {("base." + k[7:] if k.startswith("base.f.") else k[2:] if k.startswith("f.") else k): v for k, v in st.items()}
    m.load_state_dict(st)
    return m.to(DEVICE).eval()


def table(nll, params, saved, ref):
    """Test NLL recomputed here, the saved value, and the paired difference to `ref` (± standard error)."""
    rows = []
    for k, v in nll.items():
        d = np.asarray(nll[ref], dtype=np.float64) - np.asarray(v, dtype=np.float64)
        rows.append({"model": k, "parameters": params[k], "test NLL (here)": float(np.mean(v)), "saved": saved.get(k, np.nan),
                     f"{ref} − model": float(d.mean()), "± SE": float(d.std(ddof=1) / np.sqrt(len(d)))})
    return pd.DataFrame(rows).set_index("model")


def gap_line(m_, key_new, key_old, key_net, saved_gap):
    gap = (m_[key_old] - m_[key_new]) / (m_[key_old] - m_[key_net])
    print(f"gap closed: {100 * gap:.0f} % (saved: {100 * saved_gap:.0f} %);  the new formula reaches "
          f"{100 * np.exp(m_[key_net] - m_[key_new]):.1f} % of the fine-tuned network's likelihood per deposit")
'''

S8_STD_MD = """
### 8.1 Accuracy in the report metric

All models on the same test events. Gap closed = (old formula × Ā − new formula) / (old formula × Ā − fine-tuned MLP).
"""

S8_STD_BASELINE = r'''
new_std, base_std, mlp_std = (ours(k, "std", globals()) for k in ("new", "base", "mlp"))
nll = {f"report baseline ({base_name}, section 4)": test_nll(model, data["test"]), "old formula × Ā (refit)": test_nll(base_std, data["test"]),
       "new formula × Ā": test_nll(new_std, data["test"]), "MLP fine-tuned": test_nll(mlp_std, data["test"])}
params = dict(zip(nll, [model.n_params(), base_std.n_params(), new_std.n_params(), sum(p.numel() for p in mlp_std.parameters())]))
saved = dict(zip(nll, [REPORT_SAVED[base_name], PIPE["nll"]["std:base_acc"], PIPE["nll"]["std:new"], PIPE["nll"]["std:mlp_ft"]]))
display(table(nll, params, saved, "new formula × Ā").round(4))
m_ = {k: float(np.mean(v)) for k, v in nll.items()}
gap_line(m_, "new formula × Ā", "old formula × Ā (refit)", "MLP fine-tuned", PIPE["gap_closed"]["std:new"])
'''

S8_STD_NETWORK = r'''
new_std, base_std, mlp_std = (ours(k, "std", globals()) for k in ("new", "base", "mlp"))
NET, FORM = NETS[particle], FORMULAS[particle]                 # the report's __NET__ and its distilled formula (sections 4–5)
ex_base = torch.load(f"{OUT_DIR}/{particle}/export_{base_name}.pt", weights_only=False)
nll = {f"report baseline ({base_name})": ex_base["test_nll"], "report __NET__": nll_net, "report __NET__-distilled formula": nll_f}
saved = {f"report baseline ({base_name})": REPORT_SAVED[base_name], "report __NET__": REPORT_SAVED["__net__"],
         "report __NET__-distilled formula": REPORT_SAVED["__net___formula"]}
params = {f"report baseline ({base_name})": ex_base["n_params"], "report __NET__": sum(p.numel() for p in NET.parameters()),
          "report __NET__-distilled formula": FORM.n_params()}
if "__net__" == "cnn":                                          # the CNN notebook also shows the report's MLP (05)
    nll["report MLP"], saved["report MLP"], params["report MLP"] = test_nll(MLP, data["test"]), REPORT_SAVED["mlp"], sum(p.numel() for p in MLP.parameters())
nll.update({"old formula × Ā (refit)": test_nll(base_std, data["test"]), "new formula × Ā": test_nll(new_std, data["test"]),
            "MLP fine-tuned": test_nll(mlp_std, data["test"])})
saved.update({"old formula × Ā (refit)": PIPE["nll"]["std:base_acc"], "new formula × Ā": PIPE["nll"]["std:new"], "MLP fine-tuned": PIPE["nll"]["std:mlp_ft"]})
params.update({"old formula × Ā (refit)": base_std.n_params(), "new formula × Ā": new_std.n_params(),
               "MLP fine-tuned": sum(p.numel() for p in mlp_std.parameters())})
display(table(nll, params, saved, "new formula × Ā").round(4))
m_ = {k: float(np.mean(v)) for k, v in nll.items()}
gap_line(m_, "new formula × Ā", "old formula × Ā (refit)", "MLP fine-tuned", PIPE["gap_closed"]["std:new"])
'''

S8_SLAB_MD = """
### 8.2 Accuracy in the 3D metric (shape-form-particle's own metric)

The same test events with the likelihood normalised to each event's detector slab. A fresh copy of the unchanged common code is used,
with only `event_nll` replaced by its slab-normalised version (`shapelab.SLAB_NLL_SRC`).
"""

S8_SLAB = r'''
C3 = protonlab.load_common_for(particle, OUT_DIR=OUT_DIR)       # the 00_common definitions in a separate namespace ...
exec(shapelab.SLAB_GEOM_SRC, C3)
exec(shapelab.SLAB_NLL_SRC, C3)                                  # ... with the likelihood normalised to each event's detector slab
names = {"old formula (3D refit)": "base", "new formula": "new", "MLP fine-tuned (3D)": "mlp"}
models3 = {k: ours(v, "slab", C3) for k, v in names.items()}
nll3 = {k: C3["test_nll"](m, data["test"]) for k, m in models3.items()}
params3 = {k: (m.n_params() if hasattr(m, "n_params") else sum(p.numel() for p in m.parameters())) for k, m in models3.items()}
saved3 = dict(zip(nll3, [PIPE["nll"]["slab:base"], PIPE["nll"]["slab:new"], PIPE["nll"]["slab:mlp_ft"]]))
display(table(nll3, params3, saved3, "new formula").round(4))
m3 = {k: float(np.mean(v)) for k, v in nll3.items()}
gap3 = (m3["old formula (3D refit)"] - m3["new formula"]) / (m3["old formula (3D refit)"] - m3["MLP fine-tuned (3D)"])
print(f"gap closed (3D): {100 * gap3:.0f} % (saved: {100 * PIPE['gap_closed']['slab:new']:.0f} %)")
if particle == "pion":
    print("note: the pion's 3D MLP is degenerate (almost all of its mass lies outside the detector slabs), so the 3D gap is not reliable")
'''

S8_FORMULA_MD = """
### 8.3 The fitted formula

The formula of this particle with the fitted values (3D metric), as written in `../ALL-README.md` (all coefficients:
`../results/particles/<particle>/formula_coefficients_slab.csv`; the full card: `formula.md` in the same folder).
"""

S8_FORMULA = r'''
name = {"electron": "Electron", "muon": "Muon", "pion": "Pion", "proton": "Proton"}[particle]
txt = open(os.path.join("..", "ALL-README.md"), encoding="utf-8").read()
i = txt.index(f"**{name}** (m =")
display(Markdown(txt[i:min(k for k in (txt.find("\n**", i + 5), txt.find("<!-- KEPLETEK:END", i)) if k > 0)]))
'''

S8_PROFILES_MD = """
### 8.4 Profiles and the true shape

The profile plots of this notebook, now with the new formula (report metric, × Ā), and the true (de-convolved) shape of the formula.
"""

S8_PROFILES = r'''
COLORS["new formula"] = "tab:blue"
samples["new formula"] = sample_folded(new_std, data["test"])
profile_plot(hits, samples, "z", f"{particle}: depth profile with the new formula")
profile_plot(hits, samples, "r", f"{particle}: lateral profile with the new formula")
shape_map(new_std.base, title=f"{particle}: new formula – true (de-convolved) shape, the body of revolution without Ā")
'''

S8_SHAPES_MD = """
### 8.5 The r95 region in the unified comparison of section 7

The 95 % region of the new formula's average map (the same definition and coverage test as for the network), added to the
comparison table and the 2D map of section 7.
"""

S8_SHAPES = r'''
rows = []
for b in range(20):
    te = (data["test"].ev["bin"] == b).nonzero().squeeze(1)
    if len(te) == 0:
        continue
    pm = float(data["test"].ev["p"][te].mean())
    r95 = r95_of(new_std, pm)
    rows.append({"bin": b, "p_mean": pm, "formula": "new formula r95", **stats(grid_fn(r95)),
                 "V_L": float(np.sum(np.pi * r95 ** 2) * DZ) / 1e6, "cov_test": profile_coverage(deposits(data["test"].subset(te)), grid_fn(r95))})
CMP = pd.concat([CMP, pd.DataFrame(rows)], ignore_index=True)
MODELS["new formula r95"] = new_std
ORDER = ORDER + ["new formula r95"]
STYLE["new formula r95"] = dict(c="cyan", lw=1.6)
colors["new formula r95"] = "tab:cyan"
display(CMP.groupby("formula")[["V_L", "cov_test", "z_env", "r_max"]].mean().reindex([o for o in ORDER if o in set(CMP.formula)]).round(3))
sh_ = {s["shape"]: s for s in json.load(open(f"{OUR}/shapes.json"))["shapes"]}
print(f"saved (shape-form-particle, r95 new formula): V = {sh_['r95 new formula']['V']:.1f} L, coverage {sh_['r95 new formula']['cov']:.2f}")
compare_map(data["train"], title=f"section 7 shapes and the new formula's r95 on the data density ({particle})")
'''

S8_EXPORT_MD = """
### 8.6 Export for the summary notebook

The new formula (report metric) is exported like every model of the report, so that `07_summary` can include it. `export` counts every
coefficient slot of the formula; the number of free parameters is stored instead.
"""

S8_EXPORT = r'''
export(particle, "new_formula", new_std, data, f"shape-form-particle formula ({particle}): see ../ALL-README.md")
_p = f"{OUT_DIR}/{particle}/export_new_formula.pt"
_e = torch.load(_p, weights_only=False)
_e["n_params"] = int(new_std.n_params())
torch.save(_e, _p)
'''

S8_BODIES_MD = """
## 8. The envelope bodies of shape-form-particle

The same criterion (≥ 95 % of the energy inside for 98 % of the showers, per 1-GeV bin, minimal volume), with two additions of
shape-form-particle: the drop refitted with the same fitter, the **super-egg** `r(z') = A·(1 − |τ|^n)^(1/m)` (separate front and back
half-lengths), the iso-density body of the new formula calibrated to the same criterion, and the formula's r95 region. Volumes in the
data domain (−200 < z' < 1450 mm, r < 700 mm) and inside the detector slab; mean over the 20 bins. Source:
`../results/particles/<particle>/shapes.json`, `shapes_perbin.csv` (computed by `../scripts/particle_shapes.py`).
"""

S8_BODIES = r'''
import json
particle = PARTICLES[0]
OUR = os.path.abspath(os.path.join("..", "results", "particles", particle))
SH = pd.DataFrame(json.load(open(f"{OUR}/shapes.json"))["shapes"]).set_index("shape")
names_ = [s for s in ["98% envelope (report)", "98% drop (report)", "98% drop (refit)", "98% superegg (refit)", "98% capsule (refit)",
                      "98% cylinder (refit)", "98% iso-density (new formula)", "r95 new formula"] if s in SH.index]
tab_ = SH.loc[names_, ["V_in", "V_slab", "cov", "cov_min"]]
tab_.columns = ["V in data domain [L]", "V in detector slab [L]", "test coverage", "min coverage (bin)"]
display(tab_.round(3))
PB = pd.read_csv(f"{OUR}/shapes_perbin.csv")
fig, ax = plt.subplots(1, 2, figsize=(13, 3.6))
for s in names_:
    g = PB[PB["shape"] == s].sort_values("bin")
    ax[0].plot(g.p_test, g.V_in, "o-", ms=3, label=s)
    ax[1].plot(g.p_test, g["cov"], "o-", ms=3, label=s)
ax[0].set(xlabel="p [GeV/c]", ylabel="volume in the data domain [L]", yscale="log")
ax[1].set(xlabel="p [GeV/c]", ylabel="test coverage"); ax[1].axhline(0.98, color="k", lw=0.8, ls="--")
ax[0].legend(fontsize=7)
fig.suptitle(f"Envelope bodies of shape-form-particle next to the report's ({particle})", fontsize=11)
plt.tight_layout(); plt.show()
'''

S8_SUMMARY_MD = """
## 8. The shape-form-particle formula in the summary

`05_mlp_<particle>` (section 8.6) exports the new formula (report metric) like every model of the report; here it joins the accuracy
table, the gain plot and the profiles. The fair reference of the formula is the baseline refitted with the acceptance template (see
`05_mlp_<particle>`, section 8.1); here the report's own baseline is the reference, as in section 1.
"""

S8_SUMMARY = r'''
EXP = {p: load_exports(p) for p in PARTICLES}                  # now with export_new_formula.pt
COLORS["new_formula"] = "tab:blue"
rows = []
for p in PARTICLES:
    base = EXP[p][BASE[p]]
    for key in [BASE[p], "mlp", "mlp_formula", "cnn", "cnn_formula", "new_formula"]:
        o = EXP[p].get(key)
        if o is None:
            continue
        t = torch.as_tensor(o["test_nll"]).double()
        d = t - torch.as_tensor(base["test_nll"]).double()
        rows.append({"particle": HU[p], "model": key, "params": o["n_params"], "test NLL": t.mean().item(),
                     "Δ vs baseline": d.mean().item(), "Δ SE (paired)": (d.std() / len(d) ** .5).item()})
ACC8 = pd.DataFrame(rows)
display(ACC8.style.format({"test NLL": "{:.4f}", "Δ vs baseline": "{:+.4f}", "Δ SE (paired)": "{:.4f}"}).hide(axis="index"))
fig, ax = plt.subplots(figsize=(10, 3.6))
names = ["mlp", "mlp_formula", "cnn", "cnn_formula", "new_formula"]
w = 0.16
for k, m in enumerate(names):
    sub = ACC8[ACC8.model == m].set_index("particle").reindex([HU[p] for p in PARTICLES])
    ax.bar(np.arange(len(PARTICLES)) + (k - 2) * w, sub["Δ vs baseline"], w, yerr=sub["Δ SE (paired)"], color=COLORS[m], label=m, capsize=2)
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(np.arange(len(PARTICLES)), [f"{HU[p]}\n(baseline: {BASE[p]})" for p in PARTICLES])
ax.set_ylabel("Δ test NLL vs baseline [nat]"); ax.legend(fontsize=8, ncol=5)
ax.set_title("Networks, distilled formulas and the new formula relative to the report's baseline")
plt.tight_layout(); plt.show()
ze, re_ = Z_EDGES.cpu().numpy(), R_EDGES.cpu().numpy()
zc, rc = 0.5 * (ze[1:] + ze[:-1]), 0.5 * (re_[1:] + re_[:-1])
fig, axes = plt.subplots(2, 4, figsize=(16, 6.5))
for j, p in enumerate(PARTICLES):
    for key in [BASE[p], "mlp", "cnn", "new_formula"]:
        o = EXP[p].get(key)
        if o is None:
            continue
        m = TableModel(o)
        for pv, ls in ((2.0, "--"), (15.0, "-")):
            P = m(torch.log(torch.tensor([pv], device=DEVICE))).exp()[0].cpu().numpy()
            axes[0, j].plot(zc, P.sum(1) / np.diff(ze), ls, color=COLORS[key], lw=1.2, label=key if pv == 15 else None)
            axes[1, j].plot(rc, P.sum(0) / np.diff(re_), ls, color=COLORS[key], lw=1.2)
    axes[0, j].set_title(f"{HU[p]}  (— 15 GeV, -- 2 GeV)", fontsize=9); axes[0, j].set_xlabel("z' [mm]")
    axes[1, j].set_yscale("log"); axes[1, j].set_xlabel("r [mm]"); axes[1, j].set_xlim(0, 700)
    axes[0, j].legend(fontsize=7)
axes[0, 0].set_ylabel("dE/dz' (norm.)"); axes[1, 0].set_ylabel("dE/dr (norm.)")
plt.tight_layout(); plt.show()
'''

S8_END = """
**What to look for:** the recomputed test NLLs agree with the saved numbers; the new formula lies between the old formula and the
network and closes most of the gap; in the profiles it follows the data where a single shower term cannot (primary particle, entrance,
lateral tail).
"""


def report_saved(particle):
    out = {}
    for k in ("gflash", "cylinder", "mlp", "mlp_formula", "cnn", "cnn_formula"):
        f = os.path.join(SRC, "results", particle, f"export_{k}.pt")
        if os.path.exists(f):
            out[k] = round(float(np.mean(np.asarray(torch.load(f, weights_only=False)["test_nll"], dtype=np.float64))), 6)
    return out


def section8(kind, name, particle):
    if kind == "summary":
        return [md(S8_SUMMARY_MD), code(S8_SUMMARY)]
    if kind == "bodies":
        return [md(S8_BODIES_MD), code(S8_BODIES)]
    setup = code(S8_SETUP.replace("__REPORT_SAVED__", repr(report_saved(particle))))
    cells = [md(S8_INTRO.replace("__CONTEXT__", CONTEXT[kind])), setup, md(S8_STD_MD)]
    if kind == "baseline":
        cells += [code(S8_STD_BASELINE)]
    else:
        net = "cnn" if name.startswith("06") else "mlp"
        cells += [code(S8_STD_NETWORK.replace("__NET__", net.upper()).replace("__net__", net))]
    cells += [md(S8_SLAB_MD), code(S8_SLAB), md(S8_FORMULA_MD), code(S8_FORMULA), md(S8_PROFILES_MD), code(S8_PROFILES)]
    if kind == "network":
        cells += [md(S8_SHAPES_MD), code(S8_SHAPES)]
        if name.startswith("05"):
            cells += [md(S8_EXPORT_MD), code(S8_EXPORT)]
    if name.startswith("04"):                                    # the muon baseline also shows our muon bodies
        cells += [md(S8_BODIES_MD.replace("## 8.", "### 8.5")), code(S8_BODIES)]
    return cells + [md(S8_END)]


def build(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        nb = json.load(fh)
    kind = KIND[name[:2]]
    particle = None if kind == "summary" else name[:-6].split("_")[-1]
    n_patch = 0
    for c in nb["cells"]:
        c.setdefault("id", uuid.uuid4().hex[:8])
        if c["cell_type"] == "code":
            c["outputs"], c["execution_count"] = [], None
            src = "".join(c["source"])
            if '"../../data/simulations/' in src:
                c["source"] = src.replace('"../../data/simulations/', f'"{DATA_ROOT}/').splitlines(True)
                n_patch += 1
    assert n_patch == 1, (name, n_patch)
    nb["cells"].insert(1, md(NOTE.format(name=name, what=WHAT[kind])))
    nb["cells"] += section8(kind, name, particle)
    nb.setdefault("metadata", {})["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    return kind


os.makedirs(OUT, exist_ok=True)
shutil.copy2(os.path.join(SRC, "00_common.ipynb"), os.path.join(OUT, "00_common.ipynb"))
shutil.copytree(os.path.join(SRC, "results"), os.path.join(OUT, "results"), dirs_exist_ok=True)   # the report's saved results
for name in sorted(f for f in os.listdir(SRC) if f.endswith(".ipynb") and f[:2] in KIND):
    print("built", name, build(name))
