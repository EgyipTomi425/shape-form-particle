"""README block of particle issue #2 (energy density, Sofiya Kolesnyk's notebook) from results/density/summary.json and
global_density_table.csv, written by notebooks/11_density.ipynb (scripts/build_density_notebook.py).
    python scripts/density_pages.py      -> the block between <!-- ISSUE2 BEGIN --> and <!-- ISSUE2 END --> of README.md / README.hu.md"""
import json
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D = os.path.join(ROOT, "results", "density")
S = json.load(open(os.path.join(D, "summary.json")))
G = pd.read_csv(os.path.join(D, "global_density_table.csv"))
ISSUE = "https://github.com/EgyipTomi425/particle/issues/2"


def num(x, d=1, lang="en"):
    s = f"{x:.{d}f}"
    return s.replace(".", ",") if lang == "hu" else s


def block(lang):
    hu = lang == "hu"
    n = lambda x, d=1: num(x, d, lang)
    pc = lambda x, d=0: num(100 * x, d, lang) + " %"
    m = S["rho95_median_9_10"]
    ratio = G.pivot(index="bin", columns="particle", values="rho95_median")
    hb = [f"{b}-{b + 1}" for b in range(4, 20)]
    r = (ratio.loc[hb, "electron"] / ratio.loc[hb, ["pion", "proton"]].max(axis=1)).min(), (ratio.loc[hb, "electron"] / ratio.loc[hb, ["pion", "proton"]].min(axis=1)).max()
    sh = S["electron_like_share"]
    A = S["auc_2_20"]
    rng = lambda pair, c: f"{n(A[pair][c][0], 2)}–{n(A[pair][c][1], 2)}"
    sep = lambda pair, c: f"{n(1 - A[pair][c][1], 2)}–{n(1 - A[pair][c][0], 2)}"     # single features: protons score lower
    rep, two = S["reproduction"], S["two_samples_max_abs_z"]
    if not hu:
        return f"""## Particle issue #2 – energy density of the showers

[Issue #2]({ISSUE}) (Sofiya Kolesnyk) asks how dense the showers are and what the density can be used for. Her notebook is part of
the repository as `notebooks/11_density.ipynb` (her original: `notebooks/sofiya/energy_density.ipynb`); figures and tables are in
`results/density/`, per-event density features in `results/density/<particle>.parquet`. The numbers below are written by
`scripts/density_pages.py` from `results/density/`.

- **Global density (Q4).** ρ̄95 = E95 / V95 with 5 × 5 × 10 cm boxes (visible energy): median at 9–10 GeV/c {n(m['electron'])} MeV/L
  for electrons, {n(m['pion'])} for pions, {n(m['proton'])} for protons and {n(m['muon'])} for muons (flat, one MIP). From 4 GeV/c electron
  showers are {n(r[0])}–{n(r[1])} times denser than hadron showers.
- **Electron-like dense boxes (Q5).** A box denser than the 10th percentile of the electrons' densest box (same momentum) occurs in
  {pc(sh['pion|4'], 1)} / {pc(sh['pion|9'], 1)} / {pc(sh['pion|19'], 1)} of the pion and {pc(sh['proton|4'], 1)} / {pc(sh['proton|9'], 1)} /
  {pc(sh['proton|19'], 1)} of the proton events (4–5 / 9–10 / 19–20 GeV/c): more candidate EM sub-showers (π⁰) in pion showers.
- **Checks.** The run in this repository reproduces her numbers ({rep['n_rho95']} medians within {n(rep['rho95_max_abs_diff'], 2)} MeV/L,
  {rep['n_shares']} shares within {n(100 * rep['shares_max_abs_diff'], 2)} percentage points); the samples s1 and s2 agree (largest
  difference {n(two['rho95'], 1)}σ for the medians, {n(two['shares'], 1)}σ for the shares).
- **ρ̄95 as a feature** (test split, 2–20 GeV/c, AUC): electron vs. pion {rng('electron vs pion', 'auc_rho95')} (f_core of issue #1:
  {rng('electron vs pion', 'auc_fcore')}, both: {rng('electron vs pion', 'auc_both')}); pion vs. proton {sep('pion vs proton', 'auc_rho95')} – protons
  are less dense; this separates them better than f_core ({sep('pion vs proton', 'auc_fcore')}), both together {rng('pion vs proton', 'auc_both')};
  muon vs. the rest {rng('muon vs rest', 'auc_rho95')}.
"""
    return f"""## Részecske-issue #2 – a záporok energiasűrűsége

A [2-es issue]({ISSUE}) (Kolesnyk Szófia) azt kérdezi, mennyire sűrűek a záporok, és mire használható a sűrűség. A notebookja a repó
része `notebooks/11_density.ipynb` néven (az eredetije: `notebooks/sofiya/energy_density.ipynb`); az ábrák és táblázatok a
`results/density/` mappában, az eseményenkénti sűrűségjellemzők a `results/density/<particle>.parquet` fájlokban vannak. Az alábbi
számokat a `scripts/density_pages.py` írja a `results/density/` alapján.

- **Globális sűrűség (Q4).** ρ̄95 = E95 / V95 5 × 5 × 10 cm-es dobozokkal (látható energia): mediánja 9–10 GeV/c-n {n(m['electron'])} MeV/L
  az elektronra, {n(m['pion'])} a pionra, {n(m['proton'])} a protonra és {n(m['muon'])} a müonra (állandó, egy MIP). 4 GeV/c-től az
  elektronzápor {n(r[0])}–{n(r[1])}-szor sűrűbb a hadronzápornál.
- **Elektronszerű sűrű dobozok (Q5).** Az elektronok legsűrűbb dobozának 10. percentilisénél (azonos impulzusnál) sűrűbb doboz a pion-
  események {pc(sh['pion|4'], 1)} / {pc(sh['pion|9'], 1)} / {pc(sh['pion|19'], 1)}-ában, a protonesemények {pc(sh['proton|4'], 1)} /
  {pc(sh['proton|9'], 1)} / {pc(sh['proton|19'], 1)}-ában fordul elő (4–5 / 9–10 / 19–20 GeV/c): a pionzáporban több az EM-alzápor-jelölt (π⁰).
- **Ellenőrzések.** A repóbeli futás megismétli a számait ({rep['n_rho95']} medián {n(rep['rho95_max_abs_diff'], 2)} MeV/L-en, {rep['n_shares']}
  arány {n(100 * rep['shares_max_abs_diff'], 2)} százalékponton belül); az s1 és s2 minta egyezik (a legnagyobb eltérés a mediánoknál
  {n(two['rho95'], 1)}σ, az arányoknál {n(two['shares'], 1)}σ).
- **ρ̄95 mint jellemző** (tesztminta, 2–20 GeV/c, AUC): elektron–pion {rng('electron vs pion', 'auc_rho95')} (az 1-es issue f_core-ja:
  {rng('electron vs pion', 'auc_fcore')}, együtt: {rng('electron vs pion', 'auc_both')}); pion–proton {sep('pion vs proton', 'auc_rho95')} – a proton
  ritkább; ez jobban szétválasztja őket, mint az f_core ({sep('pion vs proton', 'auc_fcore')}), a kettő együtt {rng('pion vs proton', 'auc_both')};
  müon a többiekkel szemben {rng('muon vs rest', 'auc_rho95')}.
"""


def put_block(path, text):
    s = open(path, encoding="utf-8").read()
    a, b = "<!-- ISSUE2 BEGIN -->", "<!-- ISSUE2 END -->"
    i, j = s.index(a) + len(a), s.index(b)
    open(path, "w", encoding="utf-8").write(s[:i] + "\n" + text + s[j:])


if __name__ == "__main__":
    put_block(os.path.join(ROOT, "README.md"), block("en"))
    put_block(os.path.join(ROOT, "README.hu.md"), block("hu"))
    print("README issue #2 blocks written")
