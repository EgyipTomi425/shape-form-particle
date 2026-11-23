"""The per-particle formula section of the READMEs, from the final (3D-metric) fit, in English and in Hungarian.

Source: results/particles/<p>/formula_values.json and formula_coefficients_slab.csv (written by scripts/formula_card.py).
Output: the part between the two markers (<!-- KEPLETEK:START/END -->) of README.md and ALL-README.md (English) and of
README.hu.md and ALL-README.hu.md (Hungarian).
    python readme_particle_formulas.py"""
import csv
import json
import math
import os
import re

ROOT = "/home/user/tamas/shape-form-proton"
NPAR = {"electron": "n = 3, 64", "muon": "n = 6, 129", "proton": "n = 6, 143", "pion": "n = 3, 101"}
MASS = {"electron": 0.511, "muon": 105.7, "proton": 938.3, "pion": 139.6}          # MeV
P_COLS = [1.0, 5.0, 20.0]
COMP = ("zápor", "nyom", "csúcs", "folt", "távoli udvar")                             # keys of formula_values.json

T = {
    "en": dict(
        files=("README.md", "ALL-README.md"), dec=".", pct="%",
        name={"electron": "Electron", "muon": "Muon", "proton": "Proton", "pion": "Pion"},
        comp=dict(zip(COMP, ("shower", "track", "spike", "blob", "far halo"))),
        head="### Per-particle formulas (3D metric; the numbers are the fitted values)",
        intro="The general formula above, per particle: the terms it contains, the constant parameters substituted, and the "
              "momentum-dependent ones at 1, 5 and 20 GeV/c. The “energy share” is the split of the energy deposited in the detector "
              "(behind the tilted entrance face). Polynomial coefficients: `results/particles/<particle>/formula_coefficients_slab.csv`; "
              "all momenta and the report metric: `formula.md`. If the range exceeds the depth of the detector (~1.3 m), the particle "
              "passes through it.",
        title="**{name}** (m = {mass}; polynomial degree and number of parameters: {npar})",
        gamma="- Shower depth profile, gamma: `L(z') ∝ s^(α−1)·e^(−(α−1)s/t_max)`, s = z' − z0 (values below).",
        plateau="- Shower depth profile, plateau: `L(z') ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ·z'/1 m)` (values below).",
        lateral="- Shower cross-section: `T(r│z') = f_core·Gauss(r; σ) + f_body·Cauchy(r; R) + f_halo·e^(−r/λ)/(2πλ(r + 1 mm))`; "
                "σ, R, λ and the fractions vary with depth (below at z' = 100 mm).",
        track="- Track: range `R(T) = {R1} mm · (T/GeV)^{kR} − {R0} mm` (smoothly floored at ~1 mm); start `σ((z' − {zt0} mm)/4 mm)`, "
              "end `σ((R − z')/w_R)` with w_R = {w}·R + 3 mm; attenuation `e^(−z'/{lat} mm)·e^(−{kap}·z'/R)`; Bragg rise "
              "`(1 − z'/R + {eps})^(−{q})`; width `σ(z')² = ({s0} mm)² + ({c} mm · (z'/1 m)^{k} / βp)²`; delta-electron halo "
              "`e^(−r/{l} mm)/(2π·{l} mm·(r + 1 mm))` (its share below).",
        blob="- End-of-range blob: Gaussian, σ_z = {sz} mm, σ_r = {sr} mm.",
        spike="- Entry spike: Gaussian (position and widths below). Far halo: `H ∝ σ(z'/10 mm)·e^(−z'/{L} mm)/(r + 1 cm)`.",
        rows=dict(T="T (kinetic energy)", share="energy share: {c}", z0="shower start z0", tmax="shower maximum t_max",
                  am1="shape α − 1", zs="shower start z_s / rise w1", ell="shower end ℓ / fall-off w2", kappa="slow slope κ",
                  lat="core σ / Cauchy R / halo λ (z' = 100 mm)", frac="fractions core / body / halo (z' = 100 mm)",
                  range="track range R(T)", dhalo="delta-halo share", spike="spike position / σ_z / σ_r"),
        gen="(scripts/readme_particle_formulas.py generates this block)"),
    "hu": dict(
        files=("README.hu.md", "ALL-README.hu.md"), dec=",", pct=" %",
        name={"electron": "Elektron", "muon": "Müon", "proton": "Proton", "pion": "Pion"},
        comp=dict(zip(COMP, COMP)),
        head="### Részecskénkénti képletek (3D-mérce, a beírt számok az illesztett értékek)",
        intro="A fenti általános képlet részecskénként: melyik tag van benne, az állandó paraméterek behelyettesítve, a p-függő "
              "paraméterek 1, 5 és 20 GeV/c-nél. Az „energiarész” a detektorba (a ferde belépési sík mögé) eső energia megoszlása. "
              "A polinom-együtthatók: `results/particles/<részecske>/formula_coefficients_slab.csv`; minden impulzus és a "
              "report-mérce: `formula.hu.md`. Ha a hatótáv nagyobb a detektornál (~1,3 m), a részecske átmegy rajta.",
        title="**{name}** (m = {mass}; polinomfok és paraméterszám: {npar})",
        gamma="- Zápor mélységprofilja gamma: `L(z') ∝ s^(α−1)·e^(−(α−1)s/t_max)`, s = z' − z0 (értékek lent).",
        plateau="- Zápor mélységprofilja plató: `L(z') ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ·z'/1 m)` (értékek lent).",
        lateral="- Zápor keresztmetszete: `T(r│z') = f_mag·Gauss(r; σ) + f_test·Cauchy(r; R) + f_udvar·e^(−r/λ)/(2πλ(r + 1 mm))`; "
                "σ, R, λ és az arányok a mélységgel változnak (lent z' = 100 mm-en).",
        track="- Nyom: hatótáv `R(T) = {R1} mm · (T/GeV)^{kR} − {R0} mm` (~1 mm-nél simán levágva); kezdet `σ((z' − {zt0} mm)/4 mm)`, "
              "vég `σ((R − z')/w_R)`, w_R = {w}·R + 3 mm; csillapítás `e^(−z'/{lat} mm)·e^(−{kap}·z'/R)`; Bragg-felfutás "
              "`(1 − z'/R + {eps})^(−{q})`; szélesség `σ(z')² = ({s0} mm)² + ({c} mm · (z'/1 m)^{k} / βp)²`; delta-elektron-udvar "
              "`e^(−r/{l} mm)/(2π·{l} mm·(r + 1 mm))` (aránya lent).",
        blob="- Folt a hatótáv végén: Gauss, σ_z = {sz} mm, σ_r = {sr} mm.",
        spike="- Csúcs a belépésnél: Gauss (hely és szélességek lent). Távoli udvar: `H ∝ σ(z'/10 mm)·e^(−z'/{L} mm)/(r + 1 cm)`.",
        rows=dict(T="T (mozgási energia)", share="energiarész: {c}", z0="zápor kezdete z0", tmax="zápor maximuma t_max",
                  am1="alak α − 1", zs="zápor kezdete z_s / felfutás w1", ell="zápor vége ℓ / lecsengés w2", kappa="lassú meredekség κ",
                  lat="mag σ / Cauchy R / udvar λ (z' = 100 mm)", frac="arány mag / test / udvar (z' = 100 mm)",
                  range="nyom hatótáva R(T)", dhalo="delta-udvar aránya", spike="csúcs helye / σ_z / σ_r"),
        gen="(scripts/readme_particle_formulas.py generálja)"),
}


def num(x, L, unit=""):
    """3 significant digits (integers above 1000), Unicode minus, the language's decimal separator."""
    if isinstance(x, str):
        return x.replace(".", L["dec"])
    s = f"{x:.3g}" if abs(x) < 1000 else f"{x:.0f}"
    if "e" in s:
        m, e = s.split("e")
        s = f"{m}·10^{int(e)}"
    return s.replace(".", L["dec"]).replace("-", "−") + unit


def pct(x, L):
    return f"< {num(0.01, L)}{L['pct']}" if x < 1e-4 else num(100 * x, L) + L["pct"]


def coef(D):
    return {r["parameter"]: float(r["c0"]) for r in csv.DictReader(open(os.path.join(D, "formula_coefficients_slab.csv")))}


def block(particle, L):
    D = os.path.join(ROOT, "results", "particles", particle)
    v = json.load(open(os.path.join(D, "formula_values.json")))["slab"]
    c = coef(D)
    idx = [v["p [GeV]"].index(p) for p in P_COLS]
    col = lambda k: [v[k][i] for i in idx]
    first = lambda k: col(k)[0]
    track, gamma, end = "w nyom" in v, "t_max [mm]" in v, "w folt" in v
    terms = ["w_zápor·S"] + (["w_nyom·U"] if track else []) + ["w_csúcs·D"] + (["w_folt·E"] if end else []) + ["w_távoli·H"]
    out = [L["title"].format(name=L["name"][particle], mass=f"{MASS[particle]:g} MeV".replace(".", L["dec"]), npar=NPAR[particle]), "",
           f"`ρ(z', r | p) = {' + '.join(terms)}`", "", L["gamma"] if gamma else L["plateau"], L["lateral"]]
    if track:
        out.append(L["track"].format(R1=num(math.exp(c["log_R1"]), L), kR=num(c["k_R"], L), R0=num(c["R0"], L),
                                     zt0=num(c["zt0"], L), w=num(math.exp(c["log_wR"]), L), kap=num(c["kap"], L),
                                     lat=num(first("λ_att [mm]"), L), eps=num(0.03, L), q=num(first("q Bragg"), L),
                                     s0=num(first("σ0 nyom [mm]"), L), c=num(first("c_ms [mm]"), L), k=num(first("k_ms"), L),
                                     l=num(first("l delta-udvar [mm]"), L)))
    if end:
        out.append(L["blob"].format(sz=num(first("folt σ_z [mm]"), L), sr=num(first("folt σ_r [mm]"), L)))
    out.append(L["spike"].format(L=num(first("távoli udvar L [mm]"), L)))
    out += ["", "| | " + " | ".join(f"p = {p:g} GeV/c" for p in P_COLS) + " |", "|---|" + "---:|" * len(P_COLS)]
    R = L["rows"]
    rows = [(R["T"], "T [GeV]", lambda x: num(x, L, " GeV"))]
    rows += [(R["share"].format(c=L["comp"][k]), f"a detektorban: {k}", lambda x: pct(x, L)) for k in COMP if f"a detektorban: {k}" in v]
    if gamma:
        rows += [(R["z0"], "z0 [mm]", lambda x: num(x, L, " mm")), (R["tmax"], "t_max [mm]", lambda x: num(x, L, " mm")),
                 (R["am1"], "α−1", lambda x: num(x, L))]
    else:
        rows += [(R["zs"], ("z_s [mm]", "w1 [mm]"), None), (R["ell"], ("ℓ [mm]", "w2 [mm]"), None),
                 (R["kappa"], "κ [1/m]", lambda x: num(x, L, " /m"))]
    rows += [(R["lat"], ("σ mag, z'=100 [mm]", "R Cauchy, z'=100 [mm]", "λ udvar, z'=100 [mm]"), None),
             (R["frac"], "f mag / test / udvar, z'=100", lambda x: num(x, L))]
    if track:
        rows += [(R["range"], "R(T) hatótáv [mm]", lambda x: num(x, L, " mm")), (R["dhalo"], "f delta-udvar", lambda x: pct(x, L))]
    rows += [(R["spike"], ("csúcs z [mm]", "csúcs σ_z [mm]", "csúcs σ_r [mm]"), None)]
    for lab, key, f in rows:
        cells = ([" / ".join(num(v[k][i], L) for k in key) + " mm" for i in idx] if isinstance(key, tuple)
                 else [f(x) for x in col(key)])
        out.append(f"| {lab} | " + " | ".join(cells) + " |")
    return out + [""]


for lang, L in T.items():
    out = [f"<!-- KEPLETEK:START {L['gen']} -->", "", L["head"], "", L["intro"], ""]
    for p in ("electron", "muon", "proton", "pion"):
        out += block(p, L)
    out.append("<!-- KEPLETEK:END -->")
    txt = "\n".join(out)
    for name in L["files"]:
        f = os.path.join(ROOT, name)
        if not os.path.exists(f):
            continue
        s = open(f, encoding="utf-8").read()
        if "<!-- KEPLETEK:START" not in s:
            raise SystemExit(f"{name}: the <!-- KEPLETEK:START/END --> markers are missing")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(re.sub(r"<!-- KEPLETEK:START.*?<!-- KEPLETEK:END -->", lambda m: txt, s, flags=re.S))
        print("updated", name)
