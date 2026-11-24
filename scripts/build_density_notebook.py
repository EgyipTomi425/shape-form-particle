"""Builds and runs notebooks/11_density.ipynb: Sofiya Kolesnyk's energy-density notebook of particle issue #2 (Q4, Q5), as attached to
the issue (notebooks/sofiya/energy_density.ipynb), integrated into the repository. Her cells are kept; only the data folder, the work
folder, the figure format and the DuckDB memory limit are adapted (each replacement must apply exactly once). Section 5 is added:
reproduction of her numbers, the two samples separately, per-event features, and the comparison with the core fraction of issue #1.
    python scripts/build_density_notebook.py [--no-run]        -> notebooks/11_density.ipynb, results/density/"""
import json
import os
import sys

import nbformat
from nbclient import NotebookClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC = os.path.join(ROOT, "notebooks", "sofiya", "energy_density.ipynb")
OUT = os.path.join(ROOT, "notebooks", "11_density.ipynb")

PATCHES = {
    1: [("from pathlib import Path\n",
         "import os\nif os.path.basename(os.getcwd()) == \"notebooks\":     # integration: run from the repository root\n"
         "    os.chdir(\"..\")\nfrom pathlib import Path\n"),
        ('DATA_DIR = Path(r"C:/Users/Sofia/Desktop/High energy physics thesis/data/extracted_v3/publ-balanced")',
         'DATA_DIR = Path(os.environ.get("LFHCAL_DATA", "/home/user/data/simulations"))   # integration: the group server\'s data folder'),
        ('"electron": "electron_standalone_*_v3.csv",', '"electron": "regression-electron/electron_standalone_N100000_M0_20GeV_reg_balanced_s*_v3.csv",'),
        ('"muon":     "muon_standalone_*_v3.csv",', '"muon":     "regression-muon/muon_standalone_N100000_M0_20GeV_reg_balanced_s*_v3.csv",'),
        ('"pion":     "pion_standalone_*_v3.csv",', '"pion":     "regression-pion/pion_standalone_N100000_M0_20GeV_reg_balanced_s*_v3.csv",'),
        ('"proton":   "proton_standalone_*_v3.csv",', '"proton":   "regression-proton/proton_standalone_N100000_M0_20GeV_reg_balanced_s*_v3.csv",'),
        ('WORK_DIR = Path("density_work"); WORK_DIR.mkdir(exist_ok=True)',
         'WORK_DIR = Path("cache/density"); WORK_DIR.mkdir(parents=True, exist_ok=True)       # integration: work tables (not in git)\n'
         'FIG_DIR = Path("results/density"); FIG_DIR.mkdir(parents=True, exist_ok=True)      # integration: figures (PNG) and tables'),
        ('DUCKDB_MEMORY = "3GB"', 'DUCKDB_MEMORY = os.environ.get("DUCKDB_MEMORY", "64GB")   # integration: server memory')],
    5: [('GLOBAL.to_csv(WORK_DIR / "global_density_table.csv", index=False)', 'GLOBAL.to_csv(FIG_DIR / "global_density_table.csv", index=False)')],
    6: [('fig.savefig(WORK_DIR / "global_density.pdf")', 'fig.savefig(FIG_DIR / "global_density.png", dpi=130)')],
    10: [('fig.savefig(WORK_DIR / f"density_profile_{lo}_{hi}GeV.pdf")', 'fig.savefig(FIG_DIR / f"density_profile_{lo}_{hi}GeV.png", dpi=130)')],
    11: [('fig.savefig(WORK_DIR / "axis_density_overlay_9_10GeV.pdf")', 'fig.savefig(FIG_DIR / "axis_density_overlay_9_10GeV.png", dpi=130)')],
    13: [('fig.savefig(WORK_DIR / f"local_density_{lo}_{hi}GeV.pdf")', 'fig.savefig(FIG_DIR / f"local_density_{lo}_{hi}GeV.png", dpi=130)')],
}

NOTE = """> **Integrated into shape-form-particle.** Notebook by **Sofiya Kolesnyk** (particle issue #2, Q4 and Q5), as attached to the
> issue (original: `notebooks/sofiya/energy_density.ipynb`). Changes for the integration only (built by `scripts/build_density_notebook.py`):
> the data folder (`$LFHCAL_DATA`; the balanced s1 and s2 files, the same as in her data folder), the work tables in `cache/density/`,
> figures as PNG and the table in `results/density/`, and the DuckDB memory limit. The analysis is unchanged. Section 5 was added:
> the reproduction of her numbers, the two samples separately, per-event features, and the comparison with the core fraction of issue #1."""

S5_MD = """## 5. Checks and the connection to issue #1 (added in the repository)

1. **Reproduction:** the numbers of this run against the outputs of her original notebook.
2. **Two samples:** her events combine s1 and s2 (event id = file number × 10⁷ + `event_number`, files sorted: 1 = s1, 2 = s2); the
   median density per momentum bin and the share of electron-like boxes, per sample, with their statistical errors.
3. **Per-event features** for further use: `results/density/<particle>.parquet` (sample, `event_number`, p, E_tot, V95_L, `rho95`,
   `rho_max`), joinable with `results/features/<particle>.parquet` (s1) on `event_number`.
4. **ρ̄95 as a feature** (her issue asks for the AUC per bin): AUC on the test split of the s1 events in the fiducial selection of
   issue #1, compared with the core fraction `f_core` and with both together (logistic regression on log ρ̄95 and f_core, trained on the
   train split). For pion vs. proton the AUC is the probability that the proton has the larger value: below 0.5 means that protons
   are less dense (have less core); the combination is oriented and lies above 0.5. Note: ρ̄95 uses all deposits and her shower frame;
   f_core uses prompt deposits (t < 100 ns) and the issue #1 axis."""

S5_REPRO = r'''import json, re, sys
sys.path.insert(0, os.path.abspath("src"))
from core_mip_analysis import auc as auc_hm
orig = json.load(open("notebooks/sofiya/energy_density.ipynb"))
def out_text(i):
    t = ""
    for o in orig["cells"][i].get("outputs", []):
        t += "".join(o.get("text", [])) if o.get("output_type") == "stream" else "".join(o.get("data", {}).get("text/plain", []))
    return t
# her table of median rho95 (cell 5) against this run
rows = [l.split() for l in out_text(5).splitlines()[2:] if re.match(r"^\d+-\d+", l)]
hers = pd.DataFrame([[float(x) for x in r[1:]] for r in rows], index=[r[0] for r in rows], columns=["electron", "muon", "pion", "proton"])
mine = GLOBAL.pivot(index="bin", columns="particle", values="rho95_median").reindex(hers.index)[hers.columns]
dev = (mine.round(2) - hers).abs()
print(f"median rho95: {dev.size} values, max |this run - hers| = {dev.values.max():.3f} MeV/L")
# her shares of events with an electron-like box (cell 13) against this run
SHARES = {}
for lo, hi in [(4, 5), (9, 10), (19, 20)]:
    thr, F = local_features(lo, hi)
    for n, f in F.items():
        SHARES[(lo, n)] = float(np.mean(f.rho_max >= thr))
hs = {(int(m.group(1)), m.group(3)): float(m.group(4)) / 100 for m in re.finditer(r"p=(\d+)-(\d+): (\w+)\s+share of events with an electron-like box:\s+([\d.]+)%", out_text(13))}
d = max(abs(SHARES[k] - v) for k, v in hs.items())
print(f"electron-like box shares: {len(hs)} values, max |this run - hers| = {100 * d:.2f} percentage points")
REPRO = {"rho95_max_abs_diff": float(dev.values.max()), "shares_max_abs_diff": float(d), "n_rho95": int(dev.size), "n_shares": len(hs)}'''

S5_SAMPLES = r'''rng = np.random.default_rng(12345)
def med_se(x, n_boot=200):
    x = np.asarray(x)
    return float(np.median(x)), float(np.std([np.median(rng.choice(x, len(x))) for _ in range(n_boot)], ddof=1))
rows = []
for n, ev in EV.items():
    smp = (ev.index.values // 10_000_000).astype(int)
    for pb in (0, 1, 4, 9, 14, 19):
        r = {"particle": n, "bin": f"{pb}-{pb + 1}"}
        for s in (1, 2):
            v = ev.rho95.values[(smp == s) & (ev.pbin.values == pb)]
            r[f"s{s}"], r[f"s{s}_se"] = med_se(v)
        r["z"] = (r["s1"] - r["s2"]) / np.hypot(r["s1_se"], r["s2_se"])
        rows.append(r)
TWO = pd.DataFrame(rows)
display(TWO.round(3))
rows = []
for lo, hi in [(4, 5), (9, 10), (19, 20)]:
    thr, F = local_features(lo, hi)
    for n in ("pion", "proton"):
        f = F[n]; smp = (f.index.values // 10_000_000).astype(int)
        r = {"particle": n, "p": f"{lo}-{hi}"}
        for s in (1, 2):
            k = (f.rho_max.values[smp == s] >= thr)
            r[f"s{s}"], r[f"s{s}_se"] = float(k.mean()), float(np.sqrt(k.mean() * (1 - k.mean()) / len(k)))
        r["z"] = (r["s1"] - r["s2"]) / np.hypot(r["s1_se"], r["s2_se"])
        rows.append(r)
TWO_SHARES = pd.DataFrame(rows)
display(TWO_SHARES.round(4))
print(f"largest |z| between the samples: rho95 medians {TWO.z.abs().max():.2f}, electron-like shares {TWO_SHARES.z.abs().max():.2f}")'''

S5_FEATURES = r'''for n, ev in EV.items():
    smp = (ev.index.values // 10_000_000).astype(int)
    out = pd.DataFrame({"sample": np.where(smp == 1, "s1", "s2"), "event_number": (ev.index.values % 10_000_000).astype(np.int64),
                        "p": ev.p.values, "E_tot": ev.E_tot.values.astype(np.float32), "V95_L": ev.V95_L.values.astype(np.float32),
                        "rho95": ev.rho95.values.astype(np.float32), "rho_max": ev.rho_max.values.astype(np.float32)})
    out.to_parquet(FIG_DIR / f"{n}.parquet", index=False, compression="zstd")
    print(n, len(out), "events ->", FIG_DIR / f"{n}.parquet")'''

S5_AUC = r'''from sklearn.linear_model import LogisticRegression
J = {}
for n, ev in EV.items():
    smp = (ev.index.values // 10_000_000).astype(int)
    d = pd.DataFrame({"event_number": (ev.index.values % 10_000_000).astype(np.int64), "rho95": ev.rho95.values})[smp == 1]
    f = pd.read_parquet(f"results/features/{n}.parquet", columns=["event_number", "split", "bin", "entry_inside", "fiducial", "E_vis", "f_core_strict"])
    f = f[f.entry_inside & f.fiducial & (f.E_vis > 0)]
    J[n] = f.merge(d, on="event_number", how="inner")
print({n: len(j) for n, j in J.items()}, "events (s1, fiducial, joined)")
PAIRS = [("electron", "pion", -1), ("electron", "proton", -1), ("pion", "proton", +1), ("muon", "rest", +1)]   # sign: the second scores high
rows = []
for a, b, sgn in PAIRS:
    for k in range(20):
        A = J[a][(J[a].bin == k)]
        B = (pd.concat([J[x] for x in ("electron", "pion", "proton")]) if b == "rest" else J[b])
        B = B[B.bin == k]
        tr = pd.concat([A[A.split == "train"].assign(y=0), B[B.split == "train"].assign(y=1)])
        te_a, te_b = A[A.split == "test"], B[B.split == "test"]
        X = lambda t: np.c_[np.log(np.maximum(t.rho95.values, 1e-3)), t.f_core_strict.values]
        lr = LogisticRegression(max_iter=1000).fit(X(tr), tr.y.values)
        r = {"pair": f"{a} vs {b}", "bin": k}
        r["auc_rho95"], r["se_rho95"] = auc_hm(sgn * te_a.rho95.values, sgn * te_b.rho95.values)
        r["auc_fcore"], r["se_fcore"] = auc_hm(sgn * te_a.f_core_strict.values, sgn * te_b.f_core_strict.values)
        r["auc_both"], r["se_both"] = auc_hm(lr.decision_function(X(te_a)), lr.decision_function(X(te_b)))
        rows.append(r)
AUC = pd.DataFrame(rows)
AUC.round(4).to_csv(FIG_DIR / "auc_rho95_fcore.csv", index=False)
display(AUC[AUC.bin.isin([1, 2, 4, 9, 14, 19])].round(3))
fig, ax = plt.subplots(1, 4, figsize=(18, 3.6), sharey=False)
for a_, (pair, g) in zip(ax, AUC.groupby("pair", sort=False)):
    for c, lab, col in (("auc_rho95", "rho95 (density)", "#0072B2"), ("auc_fcore", "f_core (issue #1)", "#D55E00"), ("auc_both", "both", "0.2")):
        a_.errorbar(g.bin + 0.5, g[c], yerr=g[c.replace("auc", "se")], fmt="o-", ms=4, capsize=2, color=col, label=lab)
    a_.axhline(0.5, color="0.5", lw=1); a_.set(title=pair, xlabel="p [GeV/c]", xlim=(0, 20)); a_.grid(alpha=.3)
ax[0].set_ylabel("AUC (test split)"); ax[0].legend(fontsize=8)
fig.tight_layout(); fig.savefig(FIG_DIR / "auc_rho95_fcore.png", dpi=130); plt.show()
hi = AUC[AUC.bin >= 2]
SUMMARY = {"reproduction": REPRO,
           "rho95_median_9_10": {n: float(GLOBAL[(GLOBAL.particle == n) & (GLOBAL.bin == "9-10")].rho95_median.iloc[0]) for n in NAMES},
           "electron_like_share": {f"{n}|{lo}": SHARES[(lo, n)] for lo in (4, 9, 19) for n in ("pion", "proton")},
           "two_samples_max_abs_z": {"rho95": float(TWO.z.abs().max()), "shares": float(TWO_SHARES.z.abs().max())},
           "auc_2_20": {p: {c: [float(hi[hi.pair == p][c].min()), float(hi[hi.pair == p][c].max())] for c in ("auc_rho95", "auc_fcore", "auc_both")}
                        for p in AUC.pair.unique()}}
json.dump(SUMMARY, open(FIG_DIR / "summary.json", "w"), indent=1)
print(json.dumps(SUMMARY, indent=1))'''


def build(run=True):
    nb = nbformat.read(SRC, as_version=4)
    for c in nb.cells:
        if c.cell_type == "code":
            c.outputs, c.execution_count = [], None
    for i, reps in PATCHES.items():
        src = nb.cells[i].source
        for a, b in reps:
            assert src.count(a) == 1, (i, a[:60])
            src = src.replace(a, b)
        nb.cells[i].source = src
    nb.cells.insert(1, nbformat.v4.new_markdown_cell(NOTE))
    nb.cells += [nbformat.v4.new_markdown_cell(S5_MD), nbformat.v4.new_code_cell(S5_REPRO), nbformat.v4.new_code_cell(S5_SAMPLES),
                 nbformat.v4.new_code_cell(S5_FEATURES), nbformat.v4.new_code_cell(S5_AUC)]
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    if run:
        NotebookClient(nb, timeout=14400, kernel_name="python3", resources={"metadata": {"path": os.path.dirname(OUT)}}).execute()
    nbformat.write(nb, OUT)
    print("written", OUT)


if __name__ == "__main__":
    build("--no-run" not in sys.argv)
