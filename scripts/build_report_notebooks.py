"""Copies of the report's 05_mlp_<particle> notebooks in report_notebooks/, extended with a section 8: the shape-form-particle formula
(fitted directly to the data) on the same test set, next to the report's network and distilled formula.

In the copies only the data path changes (absolute path). The report results needed to run them (the network candidates, the distilled
formula, the baseline export, the envelope bodies) and those read by the pipeline of this repository (the baseline degree ladders, the
proton CNN) are copied to report_notebooks/results/<particle>/ (protonlab.REPORT_RESULTS); the notebooks only load them.
    python build_report_notebooks.py
    cd ../report_notebooks && jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 05_mlp_<particle>.ipynb"""
import json
import os
import shutil
import uuid

SRC = "/home/user/sofiya/shape-form"                 # the report's notebooks and saved results (read-only)
ROOT = "/home/user/tamas/shape-form-proton"
OUT = os.path.join(ROOT, "report_notebooks")
DATA_ROOT = "/home/user/data/simulations"
NEEDED = ("mlp_", "export_gflash.pt", "export_cylinder.pt", "envelope.pt", "drop.pt",   # what the 05 notebook loads,
          "gflash_n", "cylinder_n")                                                 # + the baseline ladders the pipeline loads
NEEDED_PROTON = ("cnn.pt", "cnn_formula.pt")                                     # + the proton CNN (08 notebook)


def md(text):
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {}, "source": text.strip("\n").splitlines(True)}


def code(text):
    return {"cell_type": "code", "id": uuid.uuid4().hex[:8], "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(True)}


NOTE = """
> **Copy of the report notebook `05_mlp_{p}.ipynb`** (shape-form). Sections 1–7 are unchanged; only the data path is absolute, and the
> report's saved models are loaded from `results/{p}/`. **Section 8** adds the shower-shape formula of shape-form-particle, fitted
> directly to the data, and compares it with the network and the distilled formula on this notebook's own test set.
"""

S8_INTRO = """
## 8. The shape-form-particle formula, fitted directly to the data

Sections 5–7 distil the network: a few formula families are fitted to the network's maps. shape-form-particle builds the formula from
physically separate terms instead – shower + primary track (range, attenuation, multiple-scattering widening, Bragg rise) + entry spike
+ end-of-range blob + far halo, see `../ALL-README.md` – and fits every parameter (a polynomial in ln T) **directly to the simulated
hits** by maximum likelihood; the network serves only as a benchmark. Nothing is fitted here: the saved final models
(`../results/particles/<particle>/`) are loaded and evaluated on this notebook's test set.

Two metrics:
- **Report metric** (this notebook's `test_nll`). The formula is multiplied by the parameter-free template Ā(z', r), the detector
  acceptance averaged over the incidence angles (the tilted entrance face cuts the body of revolution). The fair reference is the
  report's baseline refitted with the same template ("old formula × Ā").
- **3D metric** of shape-form-particle: the likelihood normalised per event to its own detector slab (between the tilted entrance face
  and the back face). Only models trained in this metric are compared in it: the old formula, the new formula and the MLP, each refitted
  or fine-tuned in 3D.

The saved numbers of shape-form-particle (`test_v3.json`, quoted in its README) are printed next to the values recomputed here.
"""

S8_SETUP = r'''
import json
import sys

sys.path.insert(0, os.path.abspath(".."))                      # repository root: particle_shape.py, shapelab.py, protonlab.py
import protonlab
import shapelab

OUR = os.path.abspath(os.path.join("..", "results", "particles", particle))   # saved final models of shape-form-particle
PIPE = json.load(open(f"{OUR}/test_v3.json"))                   # its saved test-set numbers (both metrics)
c0, s0 = shapelab.lnp_center_scale(data)
base_name, base_long, _ = shapelab.REPORT_BASE[particle]       # the report's baseline: GFlash, or the cylinder for the muon
NET, FORM = NETS[particle], FORMULAS[particle]                 # the report's MLP and distilled formula (sections 4–5)


def ours(kind, metric, C):
    """A saved model of shape-form-particle: 'new' (the final formula), 'base' (the report's baseline refitted), 'mlp' (the report's
    MLP fine-tuned); metric 'std' = report metric (× Ā), 'slab' = 3D metric."""
    if kind == "new":
        return shapelab.build_final(C, particle, OUR, c0, s0, metric=metric)[0]
    n = PIPE["degrees"][f"base_{metric}"]
    st = torch.load(f"{OUR}/{kind}_{metric}" + (f"_n{n}" if kind == "base" else "") + ".pt", map_location=DEVICE,
                    weights_only=False)["state"]
    if kind == "mlp":
        m = FieldModel(NET.mlp[0].out_features, (len(NET.mlp) - 1) // 2)
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
'''

S8_STD_MD = """
### 8.1 Accuracy in the report metric

All models on the same test events; "saved" is the number of the report's export (baseline, distilled formula) or of
shape-form-particle (`test_v3.json`). Gap closed = (old formula × Ā − new formula) / (old formula × Ā − fine-tuned MLP).
"""

S8_STD = r'''
new_std, base_std, mlp_std = (ours(k, "std", globals()) for k in ("new", "base", "mlp"))
ex = {k: torch.load(f"{OUT_DIR}/{particle}/export_{k}.pt", weights_only=False) for k in (base_name, "mlp_formula")}
nll = {f"report baseline ({base_name})": ex[base_name]["test_nll"], "report MLP": nll_net, "report distilled formula": nll_f,
       "old formula × Ā (refit)": test_nll(base_std, data["test"]), "new formula × Ā": test_nll(new_std, data["test"]),
       "MLP fine-tuned": test_nll(mlp_std, data["test"])}
params = dict(zip(nll, [ex[base_name]["n_params"], sum(p.numel() for p in NET.parameters()), FORM.n_params(), base_std.n_params(),
                        new_std.n_params(), sum(p.numel() for p in mlp_std.parameters())]))
saved = dict(zip(nll, [PIPE["nll"]["std:report_baseline"], PIPE["nll"]["std:report_mlp"], float(np.mean(ex["mlp_formula"]["test_nll"])),
                       PIPE["nll"]["std:base_acc"], PIPE["nll"]["std:new"], PIPE["nll"]["std:mlp_ft"]]))
display(table(nll, params, saved, "new formula × Ā").round(4))
m_ = {k: float(np.mean(v)) for k, v in nll.items()}
gap = (m_["old formula × Ā (refit)"] - m_["new formula × Ā"]) / (m_["old formula × Ā (refit)"] - m_["MLP fine-tuned"])
print(f"gap closed: {100 * gap:.0f} % (saved: {100 * PIPE['gap_closed']['std:new']:.0f} %);  the new formula reaches "
      f"{100 * np.exp(m_['MLP fine-tuned'] - m_['new formula × Ā']):.1f} % of the fine-tuned network's likelihood per deposit, "
      f"with {params['new formula × Ā']} instead of {params['MLP fine-tuned']} parameters")
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

Same plots as in section 6, now with the new formula (report metric, × Ā) next to the network and the distilled formula.
"""

S8_PROFILES = r'''
COLORS["new formula"] = "tab:blue"
samples["new formula"] = sample_folded(new_std, data["test"])
profile_plot(hits, samples, "z", f"{particle}: depth profile – data, MLP, distilled formula, new formula")
profile_plot(hits, samples, "r", f"{particle}: lateral profile – data, MLP, distilled formula, new formula")
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

S8_END = """
**What to look for:** the recomputed test NLLs agree with the saved numbers; in both metrics the new formula lies between the old
formula and the network and closes most of the gap, while the distilled formula is fitted to the network's maps and is not; in the
profiles the new formula follows the data where a single shower term cannot (primary track, entrance, lateral tail); its r95 region is
close to the network's.
"""


def build(particle):
    with open(os.path.join(SRC, f"05_mlp_{particle}.ipynb"), encoding="utf-8") as fh:
        nb = json.load(fh)
    for c in nb["cells"]:
        c.setdefault("id", uuid.uuid4().hex[:8])
        if c["cell_type"] == "code":
            c["outputs"], c["execution_count"] = [], None
    setup = nb["cells"][3]
    src = "".join(setup["source"])
    old = f'DATA_DIR = "../../data/simulations/regression-{particle}/"'
    assert old in src, src
    setup["source"] = src.replace(old, f'DATA_DIR = "{DATA_ROOT}/regression-{particle}/"').splitlines(True)
    nb["cells"].insert(1, md(NOTE.format(p=particle)))
    nb["cells"] += [md(S8_INTRO), code(S8_SETUP), md(S8_STD_MD), code(S8_STD), md(S8_SLAB_MD), code(S8_SLAB), md(S8_FORMULA_MD),
                    code(S8_FORMULA), md(S8_PROFILES_MD), code(S8_PROFILES), md(S8_SHAPES_MD), code(S8_SHAPES), md(S8_END)]
    nb.setdefault("metadata", {})["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    with open(os.path.join(OUT, f"05_mlp_{particle}.ipynb"), "w", encoding="utf-8") as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    res = os.path.join(OUT, "results", particle)
    os.makedirs(res, exist_ok=True)
    for f in sorted(os.listdir(os.path.join(SRC, "results", particle))):
        if f.startswith(NEEDED) or (particle == "proton" and f in NEEDED_PROTON):
            shutil.copy2(os.path.join(SRC, "results", particle, f), os.path.join(res, f))


os.makedirs(OUT, exist_ok=True)
shutil.copy2(os.path.join(SRC, "00_common.ipynb"), os.path.join(OUT, "00_common.ipynb"))
for p in ("electron", "muon", "pion", "proton"):
    build(p)
    print("built", p)
