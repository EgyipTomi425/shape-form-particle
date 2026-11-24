"""A végleges formula „kártyája” részecskénként: a képlet, a bekapcsolt tagok, az illesztett paraméterek néhány impulzusnál
és a teljes együttható-táblázat (a polinomok az x = (ln(T/GeV) − v0)/vs változóban, T = √(p² + m²) − m).
Adat nem kell hozzá: a checkpointokból és a rács-állandókból dolgozik. Két nyelven: a szövegek nyelvenként az S táblában; a táblázat
sorai a formula_values.json (magyar) kulcsai, az angol kártyán a ROW_EN szerinti címkével (csak megjelenítés, a kulcsok nem változnak).
    python formula_card.py            kimenet: results/particles/<p>/formula.md (angol), formula.hu.md (magyar),
                                      formula_coefficients_<mérce>.csv, formula_values.json"""
import json
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # repository root
sys.path.insert(0, os.path.join(ROOT, "src"))
import numpy as np
import torch
import torch.nn.functional as F

import protonlab
import shapelab
from particle_shape import MASS

P_SHOW = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
TERMS = ("far", "endblob", "ms", "track_halo", "bragg", "curv")            # kiegészítő tagok; a nevük: S[nyelv]["terms"]


def fmt(v):
    a = abs(v)
    return f"{v:.3g}" if (a >= 1e4 or (0 < a < 1e-2)) else (f"{v:.0f}" if a >= 100 else f"{v:.3g}")


def evaluate(core, p, abar=None):
    """Fizikai paraméterek a p [GeV] impulzusoknál (lista). abar: a szögekre átlagolt detektor-elfogadás (Ā) – ezzel súlyozva a
    komponensek részaránya a detektorba (a belépési sík mögé) eső energiában."""
    lnp = torch.log(torch.tensor(p, device=core.coef.device))
    with torch.no_grad():
        lw, comp, th = core.components(lnp)
    g = {k: v.flatten().cpu().numpy() for k, v in th.items()}
    ex = lambda k: np.exp(g[k])
    names = ["zápor", "nyom", "csúcs"] + (["folt"] if core.endblob else []) + (["távoli udvar"] if core.far else [])
    out = {"p [GeV]": list(p), "T [GeV]": list(np.exp(g["lnT"]))}
    for nm, w in zip(names, lw):
        if w is not None:
            out[f"w {nm}"] = list(torch.exp(w).flatten().cpu().numpy())
    if abar is not None:
        with torch.no_grad():
            e = {nm: (torch.exp(w).flatten() * (torch.exp(c) * abar).sum((1, 2))) for nm, w, c in zip(names, lw, comp) if w is not None}
            tot = sum(e.values())
        for nm, v in e.items():
            out[f"a detektorban: {nm}"] = list((v / tot).cpu().numpy())
    if core.long == "plateau":
        out.update({"z_s [mm]": g["zs"], "w1 [mm]": ex("log_w1"), "ℓ [mm]": ex("log_ell"), "w2 [mm]": ex("log_w2"), "κ [1/m]": g["kappa"]})
    elif core.long == "gamma":
        out.update({"z0 [mm]": g["z0"], "t_max [mm]": ex("log_tmax"), "α−1": ex("log_am1")})
    for zz in (100.0, 600.0):
        zk = zz / 1000
        q = lambda k: g[k] * zk * zk if k in g else 0.0
        l1 = g["logit_1"] + g["s_1"] * zk + q("q_1")
        l2 = g["logit_2"] + g["s_2"] * zk + q("q_2")
        s1, s2 = 1 / (1 + np.exp(-l1)), 1 / (1 + np.exp(-l2))
        out.update({f"σ mag, z'={zz:.0f} [mm]": np.exp(g["log_sig"] + g["s_sig"] * zk + q("q_sig")),
                    f"R Cauchy, z'={zz:.0f} [mm]": np.exp(g["log_R"] + g["s_R"] * zk),
                    f"λ udvar, z'={zz:.0f} [mm]": np.exp(g["log_lam"] + g["s_lam"] * zk),
                    f"f mag / test / udvar, z'={zz:.0f}": [f"{a:.2f} / {b:.2f} / {c:.2f}" for a, b, c in zip(s1, (1 - s1) * s2, (1 - s1) * (1 - s2))]})
    if core.use_track:
        out["R(T) hatótáv [mm]"] = core.range_mm(th).flatten().cpu().numpy()
        out["σ0 tengelytag [mm]"] = ex("log_st")
        if core.att:
            out["λ_att [mm]"] = ex("log_latt")
        if core.ms:
            out["c_ms [mm]"], out["k_ms"] = ex("log_cms"), g["ms_pow"]
        if core.track_halo:
            out["f delta-udvar"], out["l delta-udvar [mm]"] = 1 / (1 + np.exp(-g["logit_th"])), ex("log_lh")
        if core.bragg:
            out["q Bragg"] = g["q_bk"]
    if core.use_spike:
        out.update({"csúcs z [mm]": g["sp_z"], "csúcs σ_z [mm]": ex("log_sp_sz"), "csúcs σ_r [mm]": ex("log_sp_sr")})
    if core.endblob:
        out.update({"folt σ_z [mm]": ex("log_sez"), "folt σ_r [mm]": ex("log_ser")})
    if core.far:
        out.update({"távoli udvar L [mm]": ex("log_Lf"), "távoli udvar R [mm]": ex("log_Rf")})
    return {k: [x if isinstance(x, str) else float(x) for x in (v if hasattr(v, "__len__") else [v] * len(p))] for k, v in out.items()}


def coef_table(core):
    rows = []
    cm = (core.coef * core.mask).detach().cpu().numpy()
    for i, n in enumerate(core.names):
        d = int(core.mask[i].sum().item()) - 1
        rows.append([n, d] + [float(v) for v in cm[i, :d + 1]])
    return rows


# A kártya szövegei nyelvenként (a {…} helyekre a számok kerülnek; a magyar szöveg tizedesvesszőit a loc() teszi be).
S = {
    "en": dict(
        file="formula.md", nav="**English** | [Magyar](formula.hu.md)", hu=False,
        name={"electron": "electron", "muon": "muon", "proton": "proton", "pion": "pion"},
        title="# The final formula – {name}",
        head="Mass m = {mass} GeV; variant `{variant}`; the parameters are polynomials in the variable x = (ln(T/GeV) − v0)/vs, "
             "T = √(p² + m²) − m. Fitted to the hits of the training set with a per-event likelihood (`shapelab.fit_fast`); the degree "
             "and the terms were selected on the validation set.",
        formula=["## The formula", "",
                 "ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H — each term is normalised separately on the "
                 "(z', r) grid (σ(·) = logistic function; terms not switched on for this particle are omitted; the subscripts are the "
                 "Hungarian term names: zápor = shower, tengelytag = axial term (formerly “track”), csúcs = entry spike, folt = end-of-range blob, távoli = far halo):",
                 "",
                 "- **Shower** S = L(z')·T(r | z'). Plateau depth profile: L ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ z'/1 m); "
                 "gamma: L ∝ s^(α−1)·e^(−(α−1) s/t_max), s ≈ z' − z0. Cross-section: "
                 "T = f1·e^(−r²/2σ²)/(2πσ²) + f2·R²/(π(r² + R²)²) + f3·e^(−r/λ)/(2πλ(r + 1 mm)); ln σ, ln R, ln λ and the mixing "
                 "logits are linear in depth (σ and the logits also with a quadratic term when “curvature” is switched on); at every "
                 "depth normalised on the disc r < 700 mm.",
                 "- **Axial term** U ∝ σ((z' − z_t0)/4 mm)·σ((R(T) − z')/w_R)·e^(−κ_t z'/R)·e^(−z'/λ_att)·(1 − z'/R + 0.03)^(−q) "
                 "× [(1 − f)·Gauss(r; σ(z')) + f·e^(−r/l)/(2πl(r + 1 mm))], where R(T) = R1·T^(k_R) − R0 (range), w_R = w·R + 3 mm, "
                 "σ(z')² = σ0² + (c·(z'/1 m)^k / βp)² (multiple scattering), βp = (T² + 2Tm)/(T + m).",
                 "- **Entry spike**: D ∝ e^(−(z' − z_sp)²/2σ_z²)·e^(−r²/2σ_r²); **end-of-range blob**: "
                 "E ∝ e^(−(z' − R(T))²/2σ_ez²)·e^(−r²/2σ_er²); **far halo**: H ∝ σ(z'/10 mm)·e^(−z'/L)·e^(−r/R)/(r + 10 mm).",
                 "- **Weights**: w_távoli = σ(a_far), w_folt = σ(a_end)·(1 − w_távoli); the shower, the axial term and the entry spike "
                 "share the remainder (the entry spike is tied to the axial term: f1 = d1/(d1 + L_t), where L_t is the length of the axial term).",
                 "- Every raw parameter is P(x) = Σ c_k x^k, x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m; “log_” = logarithm of the "
                 "quantity, “logit_” = logit of a fraction.", ""],
        terms_line="Terms: shower ({long} depth profile × [Gaussian narrow component + Cauchy body + e^(−r/λ)/r halo])", plateau="plateau",
        track_term=" + axial term (range, attenuation)", spike_term=" + entry spike",
        terms={"far": "far halo", "endblob": "end-of-range blob", "ms": "multiple scattering (widening of the axial term)",
               "track_halo": "delta-electron halo around the axial term", "bragg": "Bragg rise",
               "curv": "quadratic depth terms in the cross-section"},
        metric={"slab": "3D metric (normalised per event to the detector slab) – this is the body of revolution",
                "std": "Report metric (× Ā; the r95 and iso-density shapes are computed from it)"},
        block="Degree n = {n}, {npar} parameters; v0 = {v0}, vs = {vs}. The “w” rows are the shares in the uncut body of revolution, "
              "the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the "
              "angle-averaged acceptance Ā).",
        param="parameter",
        coef="Coefficients: `{file}` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).",
        glossary=["## How to read the tables", "",
                  "- Columns: the momentum p [GeV]; each row is the value of one fitted quantity at that momentum.",
                  "- **w …**: weight of the component in the uncut body of revolution. **in-detector: …**: share of the component in "
                  "the energy deposited in the detector (behind the tilted entrance face) – this is the physically meaningful energy share.",
                  "- **z_s, w1, ℓ, w2, κ** (plateau) or **z0, t_max, α−1** (gamma): depth profile of the shower. **σ core, R Cauchy, "
                  "λ halo** and **f core / body / halo**: widths and fractions of the three cross-section terms at the given depth.",
                  "- **R(T)**: length of the axial term (range); **σ0**: its width at the entrance; **c_ms, k_ms**: widening due "
                  "to multiple scattering; **λ_att**: attenuation length; **f, l delta halo**: fraction and length of the halo around "
                  "the axial term; **q Bragg**: exponent of the Bragg rise; **entry spike …, end-of-range blob …**: position and width of the "
                  "two Gaussians; **far halo L, R**: depth and radial length (R → ∞: no radial cut-off).",
                  "- There are two fits: the **3D metric** (normalised per event to the detector slab; it describes the body of "
                  "revolution) and the **report metric** (× Ā; the r95 and iso-density shapes are computed from it). Their values "
                  "differ slightly.", ""],
        brief="## In brief", what="- **What it is:** {note}",
        note={"electron": "Electromagnetic shower, no axial term. At low momentum the entry spike is significant, at higher momentum the "
                          "shower dominates. Of the additional terms, the ~1 % far halo gave the largest improvement; according to the "
                          "simulation truth it is prompt electromagnetic (e±/γ) energy, not neutrons, and at 5–20 GeV the model "
                          "underestimates it by ~30 %.",
              "muon": "Minimum-ionising passage: most of the energy is in the axial term (the primary's own ionisation and the nearby delta "
                      "electrons). The axial term widens with depth as multiple scattering predicts; for the LFHCal layers with the 40 mm "
                      "steel front plate, the Highland formula gives ≈ 62–63 mm and an exponent of 1.35–1.41. At the end there is a "
                      "Bragg rise (Bragg–Kleeman: q ≈ 0.43); the range is nearly linear in T.",
              "proton": "At low momentum a stopping proton (axial term + entry spike + end-of-range blob), at higher momentum a hadronic "
                        "shower. At T = 0.5–1 GeV the range agrees with the CSDA range to within 4–16 % (after the front plate); the "
                        "exponent k_R is global, the local CSDA exponent here is 1.3–1.6. The attenuation length is ≈ 1.26 λ_I. The "
                        "widening, the delta halo and the Bragg exponent of the axial term are effective here: they also describe part of "
                        "the core of the hadronic shower.",
              "pion": "Like the proton: an axial term up to the first nuclear interaction, then a hadronic shower. The attenuation length "
                      "is ≈ 1.31 λ_π, longer than that of the proton, as is the interaction length of the pion. The parameters of the "
                      "axial term's extra terms are effective."},
        acc="- **Accuracy (test NLL, report metric, lower = better):** new formula {new}, the baseline × Ā fitted the same way {base}, "
            "the fine-tuned network {mlp}. The new formula closes {gap} % of the gap between the baseline and the network (3D metric: "
            "{gap3} %; independent s2 sample: {s2} % / {s23} %).",
        shares="- **Split of the energy deposited in the detector, 1 GeV → 20 GeV** (3D metric): {shares}.",
        track="- **Axial term:** range R ≈ {R} mm at 1 GeV (exponent k_R ≈ {kR}); attenuation length λ_att ≈ {latt} mm; widening "
              "c ≈ {c} mm, k ≈ {k}; Bragg exponent q ≈ {q}.",
        lat="- **Cross-section at z' = 100 mm, 1 → 20 GeV:** Gaussian narrow component σ ≈ {s1} → {s20} mm, Cauchy body R ≈ {R1} → {R20} mm, "
            "halo λ ≈ {lam} mm; fractions (core / body / halo) {f1} → {f20}.",
        env="- **98 % envelope bodies** (the smallest body that, in 98 % of the showers, contains ≥ 95 % of the energy; average of "
            "20 bins): {parts}.",
        env_part="{lab} {V} L ({Vs} L in the detector, coverage {cov})",
        shapes=("super-egg", "drop", "capsule", "calibrated iso-density body"),
        prof="- **Mean profiles** (independent s2 sample, separation power × 10⁻³, depth / radius, lower = better): new formula "
             "{nz} / {nr}, network {mz} / {mr}, old formula {bz} / {br}; statistical floor {fz} / {fr}.",
        prof_pion=" The 3D network of the pion is degenerate (its mass lies practically outside the detector slab); its values are "
                  "not reliable.",
        front="- **Energy of the region before the entrance (z' < 0) versus the angle of incidence** (θ ≈ {t0} → {t1} rad, "
              "p ≥ 2 GeV): data {data}, new formula {new}, network {mlp}.",
        truth="- **Simulation truth** (s2, in four momentum ranges of 0–20 GeV): deposition by the incoming particle itself {prim} %, "
              "by the daughters of neutrons {neu} %; energy arriving after 100 ns (left out of the fit) {late} %. The region "
              "r ≥ 300 mm holds {fr} % of the energy ({mfar} % in the model); of this, {neut} % comes from neutrons, {em} % is "
              "electromagnetic and {prompt} % is prompt (< 5 ns); in the model, the far halo term carries {mhalo} % of it.",
        theta="- **Angle-dependent extension – not a model prediction.** The angle of incidence is given per event as an input, and "
              "{nb} entrance parameters (entry spike, shower and axial-term start) may vary linearly with the angle: "
              "P + β·(1/cosθ − 1.1). The β values were fitted to the data (an empirical correction, not predicted by the physics of "
              "the formula); all other numbers on this card come from the angle-free formula. 3D test NLL: {c} → {th} (s2: {d0} ± "
              "{d1} nat/event).",
        theta_front=" Energy before the entrance (θ ≈ 0.25 → 0.57 rad): data {data}, final formula {final}, angle-dependent {theta}.",
        theta_muon=" For the muon, the fit rearranges the terms, which then have no physical interpretation.",
        time="- **Separated in time** (per cell: a cell is prompt if it is first hit within < 5 ns of the event's first hit, delayed "
             "if it is first hit later; the delayed fraction is therefore a lower bound): the delayed cells carry on average {fd} % "
             "of the energy per event. At 5–20 GeV, mean radius / r90 (model): prompt {pr} / {pr90} mm, delayed {de} / {de90} mm; "
             "halo length at z' = 100 mm: prompt {ph} mm, delayed {dh} mm.",
        pca="- **Shower-to-shower fluctuation** (PCA on the per-event profiles): the first 3 principal components explain {ev3} % of "
            "the variance. Separation power of the per-event quantities (× 10⁻³, floor from two half-samples: {fl}): any mean "
            "model {s0} (binning constant), 3 principal components with Gaussian coefficients {s3}, 10 principal components with "
            "coefficients drawn from the training set {s10}."),
    "hu": dict(
        file="formula.hu.md", nav="[English](formula.md) | **Magyar**", hu=True,
        name={"electron": "elektron", "muon": "müon", "proton": "proton", "pion": "pion"},
        title="# A végleges formula – {name}",
        head="Tömeg m = {mass} GeV; változat `{variant}`; a paraméterek az x = (ln(T/GeV) − v0)/vs változó polinomjai, "
             "T = √(p² + m²) − m. Illesztés: a tanítóhalmaz találataira, eseményenkénti likelihooddal (`shapelab.fit_fast`), a fokszám "
             "és a tagok a validáción választva.",
        formula=["## A képlet", "",
                 "ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H — minden tag külön a (z', r) rácsra normálva "
                 "(σ(·) = logisztikus függvény; ami ennél a részecskénél nincs bekapcsolva, az kimarad):", "",
                 "- **Zápor** S = L(z')·T(r | z'). Plató-mélységprofil: L ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ z'/1 m); "
                 "gamma: L ∝ s^(α−1)·e^(−(α−1) s/t_max), s ≈ z' − z0. Keresztmetszet: "
                 "T = f1·e^(−r²/2σ²)/(2πσ²) + f2·R²/(π(r² + R²)²) + f3·e^(−r/λ)/(2πλ(r + 1 mm)); ln σ, ln R, ln λ és a keverési logitok "
                 "lineárisak a mélységben (σ-nál és a logitoknál négyzetes taggal is, ha „görbület” be van kapcsolva); minden mélységben "
                 "az r < 700 mm korongra normálva.",
                 "- **Tengelytag** U ∝ σ((z' − z_t0)/4 mm)·σ((R(T) − z')/w_R)·e^(−κ_t z'/R)·e^(−z'/λ_att)·(1 − z'/R + 0,03)^(−q) "
                 "× [(1 − f)·Gauss(r; σ(z')) + f·e^(−r/l)/(2πl(r + 1 mm))], ahol R(T) = R1·T^(k_R) − R0 (hatótáv), w_R = w·R + 3 mm, "
                 "σ(z')² = σ0² + (c·(z'/1 m)^k / βp)² (többszörös szórás), βp = (T² + 2Tm)/(T + m).",
                 "- **Csúcs** a belépésnél: D ∝ e^(−(z' − z_sp)²/2σ_z²)·e^(−r²/2σ_r²); **folt** a hatótáv végén: "
                 "E ∝ e^(−(z' − R(T))²/2σ_ez²)·e^(−r²/2σ_er²); **távoli udvar**: H ∝ σ(z'/10 mm)·e^(−z'/L)·e^(−r/R)/(r + 10 mm).",
                 "- **Súlyok**: w_távoli = σ(a_far), w_folt = σ(a_end)·(1 − w_távoli); a zápor, a tengelytag és a csúcs a maradékon osztozik "
                 "(a csúcs a tengelytaghoz kötve: f1 = d1/(d1 + L_t), L_t a tengelytag hossza).",
                 "- Minden nyers paraméter P(x) = Σ c_k x^k, x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m; „log_” = a mennyiség "
                 "logaritmusa, „logit_” = arány logitja.", ""],
        terms_line="Tagok: zápor ({long}-mélységprofil × [Gauss-féle keskeny komponens + Cauchy-test + e^(−r/λ)/r udvar])", plateau="plató",
        track_term=" + tengelytag (hatótáv, csillapítás)", spike_term=" + csúcs a belépésnél",
        terms={"far": "távoli udvar", "endblob": "folt a hatótáv végén", "ms": "többszörös szórás (a tengelytag szélesedése)",
               "track_halo": "delta-elektron-udvar a tengelytag körül", "bragg": "Bragg-felfutás",
               "curv": "négyzetes mélységtagok a keresztmetszetben"},
        metric={"slab": "3D-mérce (eseményenként a detektor-szeletre normálva) – ez a forgástest",
                "std": "report-mérce (× Ā; ebből számolódik az r95- és az izoszint-alak)"},
        block="Fokszám n = {n}, {npar} paraméter; v0 = {v0}, vs = {vs}. A „w” sorok a vágatlan forgástest részarányai, az „a detektorban” "
              "sorok a detektorba (a ferde belépési sík mögé) eső energiáé (a szögekre átlagolt elfogadással, Ā-val súlyozva).",
        param="paraméter",
        coef="Együtthatók: `{file}` (nyers paraméter = Σ c_k x^k; log_* = a mennyiség logaritmusa, logit_* = arány logitja).",
        glossary=["## Hogyan olvasd a táblázatokat", "",
                  "- Oszlopok: az impulzus p [GeV]; minden sor egy illesztett mennyiség értéke ennél az impulzusnál.",
                  "- **w …**: a komponens súlya a vágatlan forgástestben. **a detektorban: …**: a komponens aránya a detektorba (a ferde "
                  "belépési sík mögé) eső energiában – ez a fizikailag értelmezhető energiaarány.",
                  "- **z_s, w1, ℓ, w2, κ** (plató) ill. **z0, t_max, α−1** (gamma): a zápor mélységprofilja. **σ mag, R Cauchy, λ udvar** és "
                  "**f mag / test / udvar**: a keresztmetszet három tagjának szélessége és aránya az adott mélységben.",
                  "- **R(T)**: a tengelytag hossza (hatótáv); **σ0**: a tengelytag szélessége a belépésnél; **c_ms, k_ms**: a többszörös szórás miatti "
                  "szélesedés; **λ_att**: csillapítási hossz; **f, l delta-udvar**: a tengelytag körüli udvar aránya és hossza; **q Bragg**: a "
                  "Bragg-felfutás kitevője; **csúcs …, folt …**: a két Gauss-folt helye és szélessége; **távoli udvar L, R**: mélységi és "
                  "sugárirányú hossz (R → ∞: sugárirányban nincs levágás).",
                  "- Két illesztés van: a **3D-mérce** (eseményenként a detektor-szeletre normálva; ez írja le a forgástestet) és a "
                  "**report-mérce** (× Ā; ebből számolódik az r95- és az izoszint-alak). A kettő értékei kissé eltérnek.", ""],
        brief="## Röviden", what="- **Mi ez:** {note}",
        note={"electron": "Elektromágneses zápor, tengelytag nincs. Kis impulzuson a belépés körüli csúcs jelentős, nagyobb impulzuson a zápor "
                          "dominál. A ~1 %-os távoli udvar hozta a legnagyobb javulást a kiegészítő tagok közül; a szimulációs igazság "
                          "szerint ez azonnali elektromágneses (e±/γ) energia, nem neutron, és a modell 5–20 GeV-en ~30 %-kal alulbecsli.",
              "muon": "Minimálisan ionizáló áthaladás: az energia nagy része a tengelytagban van (a primer saját ionizációja és a közeli "
                      "delta-elektronok). A tengelytag a mélységgel a többszörös szórás szerint szélesedik; a Highland-képlet az LFHCal "
                      "rétegeire a 40 mm-es acél előlappal ≈ 62–63 mm-t és 1,35–1,41-es kitevőt ad. A végén Bragg-felfutás "
                      "(Bragg–Kleeman: q ≈ 0,43); a hatótáv közel lineáris T-ben.",
              "proton": "Kis impulzuson megálló proton (tengelytag + csúcs + folt), nagyobb impulzuson hadronzápor. A hatótáv T = 0,5–1 GeV-en "
                        "4–16 %-on belül egyezik a CSDA-hatótávval (az előlap után); a k_R kitevő globális, a CSDA helyi kitevője itt "
                        "1,3–1,6. A csillapítási hossz ≈ 1,26 λ_I. A tengelytag szélesedése, delta-udvara és Bragg-kitevője itt effektív: a "
                        "hadronmag egy részét is ezek írják le.",
              "pion": "Mint a proton: tengelytag az első magkölcsönhatásig, utána hadronzápor. A csillapítási hossz ≈ 1,31 λ_π, a protonénál "
                      "hosszabb, ahogy a pion kölcsönhatási hossza is. A tengelytag kiegészítőinek paraméterei effektívek."},
        acc="- **Pontosság (teszt-NLL, report-mérce, kisebb = jobb):** új formula {new}, az ugyanígy illesztett baseline × Ā {base}, "
            "a finomhangolt háló {mlp}. A baseline és a háló közti rés {gap} %-át zárja be (3D-mérce: {gap3} %; független s2 minta: "
            "{s2} % / {s23} %).",
        shares="- **A detektorba eső energia megoszlása, 1 GeV → 20 GeV** (3D-mérce): {shares}.",
        track="- **Tengelytag:** hatótáv R ≈ {R} mm 1 GeV-en (kitevő k_R ≈ {kR}); csillapítási hossz λ_att ≈ {latt} mm; szélesedés "
              "c ≈ {c} mm, k ≈ {k}; Bragg-kitevő q ≈ {q}.",
        lat="- **Keresztmetszet z' = 100 mm-en, 1 → 20 GeV:** Gauss-féle keskeny komponens σ ≈ {s1} → {s20} mm, Cauchy-test R ≈ {R1} → {R20} mm, "
            "udvar λ ≈ {lam} mm; arányok (mag / test / udvar) {f1} → {f20}.",
        env="- **98 %-os burkok** (a legkisebb test, amelyben a záporok 98 %-ában az energia ≥ 95 %-a bent van; 20 bin átlaga): {parts}.",
        env_part="{lab} {V} L ({Vs} L a detektorban, lefedés {cov})",
        shapes=("szuper-tojás", "csepp", "kapszula", "kalibrált izoszint"),
        prof="- **Átlagos profilok** (független s2 minta, szeparációs erő × 10⁻³, mélység / sugár, kisebb = jobb): új formula "
             "{nz} / {nr}, háló {mz} / {mr}, régi képlet {bz} / {br}; statisztikai padló {fz} / {fr}.",
        prof_pion=" A pion 3D-hálója degenerált (tömege gyakorlatilag a detektor-szeleten kívül van), az értékei nem megbízhatók.",
        front="- **A belépés előtti tartomány (z' < 0) energiája a beesési szöggel** (θ ≈ {t0} → {t1} rad, p ≥ 2 GeV): adat {data}, "
              "új formula {new}, háló {mlp}.",
        truth="- **Szimulációs igazság** (s2, 0–20 GeV négy impulzus-tartományában): a beeső részecske saját lerakódása {prim} %, a "
              "neutronok leányaié {neu} %; a 100 ns után érkező (a fitből kihagyott) energia {late} %. Az r ≥ 300 mm-es tartomány az "
              "energia {fr} %-a (a modellben {mfar} %), ennek {neut} %-a neutronból, {em} %-a elektromágneses és {prompt} %-a "
              "azonnali (< 5 ns); a modellben ennek {mhalo} %-át viszi a távoli udvar tag.",
        theta="- **Szögfüggő kiegészítés – nem modellpredikció.** A beesési szöget eseményenként bemenetként megadjuk, és {nb} "
              "belépési paraméter (csúcs, zápor- és tengelytag-kezdet) a szöggel lineárisan változhat: P + β·(1/cosθ − 1,1). A β-kat az "
              "adatra illesztettük (empirikus korrekció, a formula fizikája nem jósolja); a többi szám ezen a kártyán szög nélküli. "
              "3D teszt-NLL: {c} → {th} (s2: {d0} ± {d1} nat/esemény).",
        theta_front=" A belépés előtti energia (θ ≈ 0,25 → 0,57 rad): adat {data}, végleges formula {final}, szögfüggő {theta}.",
        theta_muon=" Müonnál az illesztés átrendezi a tagokat, ott a tagok fizikailag nem értelmezhetők.",
        time="- **Időben szétválasztva** (cellánként: gyors az a cella, amelyet az első találat után < 5 ns-on belül, késleltetett, "
             "amelyet később talált el először valami; a késleltetett hányad így alsó becslés): a késleltetett cellák energiája "
             "eseményenként átlagosan {fd} %. Az 5–20 GeV-es átlagos sugár / r90 (modell): gyors {pr} / {pr90} mm, késleltetett "
             "{de} / {de90} mm; az udvar hossza z' = 100 mm-en: gyors {ph} mm, késleltetett {dh} mm.",
        pca="- **Záporonkénti ingadozás** (PCA az eseményenkénti profilokon): az első 3 főkomponens a variancia {ev3} %-a. Az "
            "eseményenkénti mennyiségek szeparációs ereje (× 10⁻³, a két félminta padlója {fl}): bármely átlag-modell {s0} "
            "(binelési állandó), 3 főkomponens Gauss-együtthatókkal {s3}, 10 főkomponens a tanító együtthatóiból {s10}."),
}
COMP = ("zápor", "nyom", "csúcs", "folt", "távoli udvar")
Z100 = {k: f"{k}, z'=100 [mm]" for k in ("σ mag", "R Cauchy", "λ udvar")}
SHAPES = ("98% superegg (refit)", "98% drop (refit)", "98% capsule (refit)", "98% iso-density (new formula)")
# Az angol kártya sorcímkéi: csak megjelenítés; a formula_values.json kulcsai magyarok maradnak (más szkriptek olvassák).
ROW_EN = {"a detektorban: ": "in-detector: ", "távoli udvar": "far halo", "delta-udvar": "delta halo", "zápor": "shower",
          "nyom": "track", "csúcs": "entry spike", "folt": "end-of-range blob", "hatótáv": "range", "mag": "core", "test": "body",
          "udvar": "halo"}
ROW_RE = re.compile("|".join(map(re.escape, ROW_EN)))


def pct(v):
    if v < 1e-4:
        return "< 0.01 %"
    return f"{100 * v:.2g} %" if v < 0.01 else f"{100 * v:.0f} %"


def vol(v):
    return f"{v:.0f}" if v >= 100 else f"{v:.1f}"


def loc(lines, L):
    """Magyarul tizedesvessző a felsorolások szövegében (a táblázatokban marad a pont)."""
    return [re.sub(r"(\d)\.(\d)", r"\1,\2", x) for x in lines] if L["hu"] else lines


def label(key, L):
    """Egy formula_values.json-kulcs megjelenített neve (angolul a ROW_EN szerint)."""
    return key if L["hu"] else ROW_RE.sub(lambda m: ROW_EN[m[0]], key)


def summary(particle, D, models, vals, L):
    """Rövid, a számokból generált összefoglaló a táblázatok elé."""
    t = json.load(open(os.path.join(D, "test_v3.json")))
    s2 = json.load(open(os.path.join(D, "s2_v3.json")))
    n, g = t["nll"], t["gap_closed"]
    ev = vals["slab"]
    i1, i20 = P_SHOW.index(1.0), P_SHOW.index(20.0)
    shares = "; ".join(f"{label(c, L)} {pct(ev['a detektorban: ' + c][i1])} → {pct(ev['a detektorban: ' + c][i20])}"
                       for c in COMP if ("a detektorban: " + c) in ev)
    pc = lambda v: f"{100 * v:.0f}"
    out = [L["brief"], "", L["what"].format(note=L["note"][particle]),
           L["acc"].format(new=f"{n['std:new']:.4f}", base=f"{n['std:base_acc']:.4f}", mlp=f"{n['std:mlp_ft']:.4f}", gap=pc(g["std:new"]),
                           gap3=pc(g["slab:new"]), s2=pc(s2["gap_closed"]["std:new"]), s23=pc(s2["gap_closed"]["slab:new"])),
           L["shares"].format(shares=shares)]
    core = models["slab"][1]
    if core.use_track:
        with torch.no_grad():
            kR = float(core.theta(torch.log(torch.tensor([1.0], device=core.coef.device)))["k_R"].flatten()[0])
        out.append(L["track"].format(R=f"{ev['R(T) hatótáv [mm]'][i1]:.0f}", kR=f"{kR:.2f}", latt=f"{ev['λ_att [mm]'][0]:.0f}",
                                     c=f"{ev['c_ms [mm]'][0]:.0f}", k=f"{ev['k_ms'][0]:.2f}", q=f"{ev['q Bragg'][0]:.2f}"))
    f100, z = ev["f mag / test / udvar, z'=100"], lambda k, i: f"{ev[Z100[k]][i]:.0f}"
    out.append(L["lat"].format(s1=z("σ mag", i1), s20=z("σ mag", i20), R1=z("R Cauchy", i1), R20=z("R Cauchy", i20),
                               lam=z("λ udvar", i1), f1=f100[i1], f20=f100[i20]))
    sh = {r["shape"]: r for r in json.load(open(os.path.join(D, "shapes.json")))["shapes"]}
    parts = [L["env_part"].format(lab=lab, V=vol(sh[k]["V_in"]), Vs=vol(sh[k]["V_slab"]), cov=f"{sh[k]['cov']:.2f}")
             for lab, k in zip(L["shapes"], SHAPES) if k in sh]
    out.append(L["env"].format(parts="; ".join(parts)))
    out += measurement_bullets(D, L)
    return loc(out, L) + [""]


def rng(vals, scale=100, fmt_="{:.0f}"):
    lo, hi = min(vals) * scale, max(vals) * scale
    a, b = fmt_.format(lo), fmt_.format(hi)
    return a if a == b else f"{a}–{b}"


def measurement_bullets(D, L):
    """Az új mérések (független s2 minta) részecskénkénti eredményei, ha megvannak."""
    out = []
    arrow = lambda b, k: f"{100 * b[0][k]:.1f} → {100 * b[-1][k]:.1f} %"
    f = os.path.join(D, "profile_metrics.json")
    if os.path.exists(f):
        s = json.load(open(f))["summary"]["all"]
        g = lambda m, q: f"{1e3 * s[f'{m}:{q}']:.2f}"
        out.append(L["prof"].format(nz=g("new formula", "S_z"), nr=g("new formula", "S_r"), mz=g("MLP", "S_z"), mr=g("MLP", "S_r"),
                                    bz=g("baseline", "S_z"), br=g("baseline", "S_r"), fz=f"{1e3 * s['floor_S_z']:.2f}",
                                    fr=f"{1e3 * s['floor_S_r']:.2f}") + (L["prof_pion"] if "pion" in D else ""))
    f = os.path.join(D, "front_region.json")
    if os.path.exists(f):
        b = json.load(open(f))["bins"]
        out.append(L["front"].format(t0=f"{b[0]['theta_mean']:.2f}", t1=f"{b[-1]['theta_mean']:.2f}", data=arrow(b, "data"),
                                     new=arrow(b, "new formula"), mlp=arrow(b, "MLP")))
    f = os.path.join(D, "truth_decomposition.json")
    if os.path.exists(f):
        G = json.load(open(f))["groups"]
        far = "távoli (r≥300)"
        fr = [g["region"][far] for g in G.values()]
        neut = [g["region_cat"][far]["neutronból"] / max(g["region"][far], 1e-12) for g in G.values()]
        em = [g["region_cat"][far]["EM"] / max(g["region"][far], 1e-12) for g in G.values()]
        prompt = [g["region_time"][far]["<5 ns"] / max(g["region"][far], 1e-12) for g in G.values()]
        mfar = [g["model"]["region"][far] for g in G.values()]
        mhalo = [g["model"]["region_comp"][far].get("távoli udvar", 0.0) / max(g["model"]["region"][far], 1e-12) for g in G.values()]
        prim = [g["cat"]["primer"] for g in G.values()]
        late = [g["late_frac_of_all"] for g in G.values()]
        out.append(L["truth"].format(prim=rng(prim), neu=rng([g["cat"]["neutronból"] for g in G.values()]), late=rng(late, fmt_="{:.1f}"),
                                     fr=rng(fr, fmt_="{:.2f}"), mfar=rng(mfar, fmt_="{:.2f}"), neut=rng(neut), em=rng(em),
                                     prompt=rng(prompt), mhalo=rng(mhalo)))
    f = os.path.join(D, "theta_entrance_two.json")
    if os.path.exists(f):
        t = json.load(open(f))
        d, fr = t["s2"]["theta_minus_final"], t.get("front") or []
        out.append(L["theta"].format(nb=len(t["beta"]), c=f"{t['test']['final']:.4f}", th=f"{t['test']['theta']:.4f}",
                                     d0=f"{d[0]:+.4f}", d1=f"{d[1]:.4f}")
                   + (L["theta_front"].format(data=arrow(fr, "data"), final=arrow(fr, "final"), theta=arrow(fr, "theta")) if fr else "")
                   + (L["theta_muon"] if "muon" in D else ""))
    f = os.path.join(D, "time_split.json")
    if os.path.exists(f):
        t = json.load(open(f))
        fd = [v["mean"] for v in t["delayed_fraction_test"].values()]
        pr, de = t["prompt"]["describe"], t["delayed"]["describe"]
        out.append(L["time"].format(fd=rng(fd, fmt_="{:.1f}"), pr=rng(pr["mean_r_mm"][2:], scale=1), pr90=rng(pr["r90_mm"][2:], scale=1),
                                    de=rng(de["mean_r_mm"][2:], scale=1), de90=rng(de["r90_mm"][2:], scale=1),
                                    ph=rng(t["prompt"]["halo_lambda_z100_mm"][1:], scale=1), dh=rng(t["delayed"]["halo_lambda_z100_mm"][1:], scale=1)))
    f = os.path.join(D, "fluctuations_pca.json")
    if os.path.exists(f):
        t = json.load(open(f))["groups"]
        ev3 = [sum(g["explained_variance"][:3]) for g in t.values()]
        mean_S = lambda key: [1e3 * np.nanmean(list(g["S"][key].values())) for g in t.values()]
        fl = [1e3 * np.nanmean(list(g["floor"].values())) for g in t.values()]
        out.append(L["pca"].format(ev3=rng(ev3), fl=rng(fl, scale=1, fmt_="{:.0f}"), s0=rng(mean_S("gauss, k=0"), scale=1),
                                   s3=rng(mean_S("gauss, k=3"), scale=1), s10=rng(mean_S("empirical, k=10"), scale=1)))
    return loc(out, L)


def card(particle, D, models, vals, L):
    """A kártya sorai egy nyelven (L = S[nyelv])."""
    t, core = models["slab"][2], models["slab"][1]
    lines = [L["title"].format(name=L["name"][particle]), "", L["head"].format(mass=MASS[particle], variant=t["variant"]), ""]
    lines += summary(particle, D, models, vals, L) + L["formula"]
    lines += [L["terms_line"].format(long=L["plateau"] if core.long == "plateau" else "gamma") + (L["track_term"] if core.use_track else "")
              + L["spike_term"] + "".join(f" + {L['terms'][k]}" for k in TERMS if getattr(core, k, False)) + ".", ""] + L["glossary"]
    for metric, (m, core, t, K) in models.items():
        n = t["degrees"]["new_slab" if metric == "slab" else "new_std"]
        lines += [f"## {L['metric'][metric]}", "",
                  L["block"].format(n=n, npar=core.n_params(), v0=f"{float(core.v0):.4f}", vs=f"{float(core.vs):.4f}"), "",
                  f"| {L['param']} | " + " | ".join(f"p = {p:g}" for p in P_SHOW) + " |", "|---|" + "---:|" * len(P_SHOW)]
        lines += [f"| {label(k, L)} | " + " | ".join(x if isinstance(x, str) else fmt(x) for x in row) + " |"
                  for k, row in vals[metric].items() if k != "p [GeV]"]
        lines += ["", L["coef"].format(file=f"formula_coefficients_{metric}.csv"), ""]
    return lines


for particle in ("electron", "muon", "proton", "pion"):
    D = os.path.join(ROOT, "results", "particles", particle)
    C = protonlab.load_common_for(particle, "s1", OUT_DIR=D)
    models = {m: shapelab.build_final(C, particle, D, 0.0, 1.0, metric=m) for m in ("slab", "std")}   # v0, vs: from the checkpoint
    vals = {}
    for metric, (m, core, t, K) in models.items():
        vals[metric] = evaluate(core, P_SHOW, torch.load(os.path.join(D, "abar.pt"), map_location=core.coef.device))
        with open(os.path.join(D, f"formula_coefficients_{metric}.csv"), "w") as fh:
            fh.write("parameter,degree," + ",".join(f"c{k}" for k in range(core.degree + 1)) + "\n")
            for r in coef_table(core):
                fh.write(",".join([r[0], str(r[1])] + [f"{v:.8g}" for v in r[2:]]) + "\n")
    for L in S.values():
        open(os.path.join(D, L["file"]), "w").write("\n".join([L["nav"], ""] + card(particle, D, models, vals, L)))
    json.dump(vals, open(os.path.join(D, "formula_values.json"), "w"), indent=1)
    print(particle, "ok", flush=True)
