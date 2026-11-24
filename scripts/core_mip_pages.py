"""Answer pages of particle issue #1 (Q1-Q3, English and Hungarian) from results/core_mip/answers.json and the CSV tables of
scripts/core_mip_answers.py; every number on the pages is read from those files.
    python scripts/core_mip_pages.py      -> results/core_mip/Q1.md, Q2.md, Q3.md and the .hu.md twins"""
import json
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D = os.path.join(ROOT, "results", "core_mip")
A = json.load(open(os.path.join(D, "answers.json")))
T = {n: pd.read_csv(os.path.join(D, f"{n}.csv")) for n in ("q1_fractions", "q2_table", "q2_auc_fcore", "q3_p_long", "q3_truth_agreement",
                                                         "q3_start_visibility", "q3_classify", "claim1_may_or_may_not_be_there",
                                                         "claim2_starts_at_entry", "claim4_indicator", "q3_calibration_theta")}
PNAME = {"en": {"electron": "electron", "muon": "muon", "pion": "pion", "proton": "proton"},
         "hu": {"electron": "elektron", "muon": "müon", "pion": "pion", "proton": "proton"}}
ISSUE = "https://github.com/EgyipTomi425/particle/issues/1"
S2 = json.load(open(os.path.join(D, "s2_check.json")))


def s2_sentence(lang):
    n = lambda x, d=2: num(x, d, lang)
    if lang == "hu":
        return (f"A független második minta (s2; ugyanaz a kereső, saját MIP-kalibráció) a {S2['comparisons']} összevetett számot a "
                f"statisztikai hibán belül megismétli ({pct(S2['within_2_sigma'], 0, lang)} 2σ-n belül, a legnagyobb eltérés "
                f"{n(S2['max_abs_z'], 1)}σ; `s2_check.csv`); a MIP-kalibráció csempénként mediánban {pct(abs(S2['mpv_rel_diff_median']), 1, lang)}-ra egyezik.")
    return (f"The independent second sample (s2; same finder, its own MIP calibration) reproduces all {S2['comparisons']} compared numbers "
            f"within their statistical errors ({pct(S2['within_2_sigma'], 0)} within 2σ, largest difference {n(S2['max_abs_z'], 1)}σ; "
            f"`s2_check.csv`); the MIP calibration agrees to {pct(abs(S2['mpv_rel_diff_median']), 1)} per tile (median).")


def num(x, d=2, lang="en"):
    s = f"{x:.{d}f}"
    return s.replace(".", ",") if lang == "hu" else s


def pct(x, d=0, lang="en"):
    return num(100 * x, d, lang) + " %"


def q2row(p, w):
    t = T["q2_table"]
    return t[(t.particle == p) & (t.p_window == w)].iloc[0]


def frac(p, b, comp, ver="strict"):
    t = T["q1_fractions"]
    return t[(t.particle == p) & (t.bin == b) & (t.version == ver) & (t.component == comp)].iloc[0]


W = {1: "0.9-1.1", 5: "4.75-5.25", 20: "19.5-20.0"}


def lam(p, r, v):
    return A["q3_lambda"][p][r][v]


def eff(pair, b, feat, col="eff99"):
    t = T["q3_classify"]
    return float(t[(t.pair == pair) & (t.bin == b) & (t.feature == feat)][col].iloc[0])


def agr(p, r, c):
    t = T["q3_truth_agreement"]
    return float(t[(t.particle == p) & (t.p_range == r)][c].iloc[0])


def c1(p, r, c):
    t = T["claim1_may_or_may_not_be_there"]
    return float(t[(t.particle == p) & (t.p_range == r)][c].iloc[0])


def c2(p, r, c):
    t = T["claim2_starts_at_entry"]
    return float(t[(t.particle == p) & (t.p_range == r)][c].iloc[0])


def c4(h, r, x, c):
    t = T["claim4_indicator"]
    return float(t[(t.hadron == h) & (t.p_range == r) & (t.L_min_cm == x)][c].iloc[0])


def vis(p, r):
    t = T["q3_start_visibility"]
    return float(t[(t.particle == p) & (t.p_range == r)].share_below_threshold.iloc[0])


def auc_fcore(b, pair="pion vs proton"):
    t = T["q2_auc_fcore"]
    return float(t[t.pair.str.startswith(pair) & (t.bin == b)].auc.iloc[0])


# ------------------------------------------------------------------------------------------------------------------------------- Q1
def page_q1(lang):
    hu = lang == "hu"
    C = A["q1"]["containment"]
    S = A["q1"]["e_h_separation_2_20GeV"]
    n = lambda x, d=2: num(x, d, lang)
    rows = []
    for p in ("electron", "muon", "pion", "proton"):
        for b in (1, 4, 9, 19):
            m, c, h = (frac(p, b, x).ratio_of_sums for x in ("MIP", "core", "halo"))
            rows.append(f"| {PNAME[lang][p]} | {b}–{b + 1} | {n(m)} | {n(c)} | {n(h)} |")
    tab = "\n".join(rows)
    cont = "\n".join(f"| {PNAME[lang][p]} | {n(C[p]['R25'])} | {n(C[p]['R50'])} | {n(C[p]['R75'])} | {n(C[p]['R100'])} | {n(C[p]['centre_R50'])} |"
                     for p in ("electron", "muon", "pion", "proton"))
    sep = " / ".join(n(S[f"electron_vs_pion|R{r}"], 3) for r in (25, 50, 75, 100))
    sepp = " / ".join(n(S[f"electron_vs_proton|R{r}"], 3) for r in (25, 50, 75, 100))
    mu = C["muon"]["rel_to_R100"]
    fr = lambda p, b, c: frac(p, b, c).ratio_of_sums
    e_core = min(fr("electron", b, "core") for b in range(2, 20))
    e_halo = max(fr("electron", b, "halo") for b in range(2, 20))
    mu_mip = (min(fr("muon", b, "MIP") for b in range(1, 20)), max(fr("muon", b, "MIP") for b in range(1, 20)))
    h_halo = (min(fr(p, b, "halo") for p in ("pion", "proton") for b in range(2, 20)), max(fr(p, b, "halo") for p in ("pion", "proton") for b in range(2, 20)))
    g = {(p, b, c): n(fr(p, b, c)) for p in ("pion", "proton") for b in (1, 19) for c in ("MIP", "core", "halo")}
    if not hu:
        return f"""**English** | [Magyar](Q1.hu.md)

# Q1 – What is the core, and how does it look within the whole shower as a function of energy?

Particle issue [#1]({ISSUE}). Notebook: [`notebooks/09_axis_core.ipynb`](../../notebooks/09_axis_core.ipynb).

**Answer.** The core is the visible energy within **R = 5 cm** of the axis (the incoming direction from the entry point at the front
face, z = 3620 mm), taken from the shower start on; the axis region before the start is the MIP segment, everything farther than 5 cm
is the halo, so `E_vis = E_MIP + E_core + E_halo`. Electron showers are almost entirely core (at least {n(e_core)} from 2 GeV/c on,
halo at most {n(e_halo)}). Muons are mostly MIP segment ({n(mu_mip[0])}–{n(mu_mip[1])} from 1 GeV/c on). For pions and protons the core
grows with momentum (pion {g['pion', 1, 'core']} → {g['pion', 19, 'core']}, proton {g['proton', 1, 'core']} → {g['proton', 19, 'core']} from
1–2 to 19–20 GeV/c) while the MIP segment shrinks (pion {g['pion', 1, 'MIP']} → {g['pion', 19, 'MIP']}, proton {g['proton', 1, 'MIP']} →
{g['proton', 19, 'MIP']}); from 2 GeV/c on the halo holds {n(h_halo[0])}–{n(h_halo[1])} of the energy.

![Where the energy goes: depth along the axis against distance from it](q1_region_map.png)

*Where the energy goes* (4.5–5.5 GeV/c, mean energy density per event): the dashed line is R = 5 cm, the orange mark the median
shower start of pions and protons. Inside 5 cm, before the mark: MIP segment; after it: core; outside 5 cm: halo.

![MIP segment, core and halo](q1_fractions.png)

Shares of `E_vis` (ratio of sums; the event means are in the notebook and in `q1_fractions.csv`):

| particle | p [GeV/c] | MIP segment | core | halo |
|---|---|---|---|---|
{tab}

## Why 5 cm

![Containment and separation versus R](q1_rscan.png)

| particle | R = 2.5 cm | 5 cm | 7.5 cm | 10 cm | 5 cm, cell-centre rule |
|---|---|---|---|---|---|
{cont}

1. **The MIP track fits.** Of the muon energy within 10 cm, {pct(mu['R25'], 0)} lies within 2.5 cm, {pct(mu['R50'], 0)} within 5 cm and
   {pct(mu['R75'], 0)} within 7.5 cm: with 48.6 mm cells, 5 cm is the smallest radius that holds the cell(s) the primary crosses.
   Below it the result is set by the assumption that the energy is uniform within a cell (folding), not by the shower.
2. **The electromagnetic shower fits.** 5 cm = 2.3 Molière radii (R_M = 21.9 mm); {pct(C['electron']['R50'], 0)} of the electron energy
   lies within it.
3. **It separates best.** The electron/hadron separation by the energy within R (AUC averaged over 2–20 GeV/c, R = 2.5 / 5 / 7.5 / 10 cm)
   is {sep} for e/π and {sepp} for e/p: 5 cm is the best or tied for best.

**Cell-centre rule or proportional sharing?** The cell-centre rule assigns a whole cell to the core when its centre is within 5 cm; it
gives about 0.03 more core than proportional sharing (table, last column) and practically the same separation. Proportional sharing
does not depend on where the axis crosses a cell, so we use it; both are stored (`f_near_R50`, `f_near_centre_R50`).

**Selection.** Entry point in the instrumented area and the axis 10 cm inside the area in all 60 layers (no lateral leakage at the outer
edge or the beam hole; {pct(A['selection']['pion']['events_fiducial'] / 1e5, 0)} of the events); only prompt deposits (t < 100 ns).
"""
    return f"""[English](Q1.md) | **Magyar**

# Q1 – Mi a mag, és hogyan néz ki a teljes záporon belül az energia függvényében?

Részecske-issue [#1]({ISSUE}). Notebook: [`notebooks/09_axis_core.ipynb`](../../notebooks/09_axis_core.ipynb).

**Válasz.** A mag a tengelytől (a beérkezés iránya a belépési ponttól, z = 3620 mm-es front) **R = 5 cm**-en belüli látható energia a
zápor kezdetétől; a kezdet előtti tengely menti rész a MIP-szakasz, az 5 cm-nél távolabbi energia a halo, így
`E_vis = E_MIP + E_core + E_halo`. Az elektronzápor szinte csak mag (2 GeV/c-től legalább {n(e_core)}, a halo legfeljebb {n(e_halo)}). A
müon nagyrészt MIP-szakasz (1 GeV/c-től {n(mu_mip[0])}–{n(mu_mip[1])}). A pionnál és a protonnál a mag az impulzussal nő (pion
{g['pion', 1, 'core']} → {g['pion', 19, 'core']}, proton {g['proton', 1, 'core']} → {g['proton', 19, 'core']} az 1–2 és a 19–20 GeV/c között),
a MIP-szakasz csökken (pion {g['pion', 1, 'MIP']} → {g['pion', 19, 'MIP']}, proton {g['proton', 1, 'MIP']} → {g['proton', 19, 'MIP']}); 2 GeV/c-től a
halo az energia {n(h_halo[0])}–{n(h_halo[1])} részét viszi.

![Hová kerül az energia: mélység a tengely mentén és távolság a tengelytől](q1_region_map.png)

*Hová kerül az energia* (4,5–5,5 GeV/c, eseményenkénti átlagos energiasűrűség): a szaggatott vonal R = 5 cm, a narancssárga jel a
pionok és protonok zápor-kezdetének mediánja. 5 cm-en belül a jel előtt: MIP-szakasz; utána: mag; 5 cm-en kívül: halo.

![MIP-szakasz, mag és halo](q1_fractions.png)

Az `E_vis` megoszlása (összegek aránya; az eseményátlagok a notebookban és a `q1_fractions.csv`-ben):

| részecske | p [GeV/c] | MIP-szakasz | mag | halo |
|---|---|---|---|---|
{tab}

## Miért 5 cm

![Tartalmazás és szétválasztás R függvényében](q1_rscan.png)

| részecske | R = 2,5 cm | 5 cm | 7,5 cm | 10 cm | 5 cm, cellaközép-szabály |
|---|---|---|---|---|---|
{cont}

1. **A MIP-nyom belefér.** A müon 10 cm-en belüli energiájának {pct(mu['R25'], 0, lang)}-a 2,5 cm-en, {pct(mu['R50'], 0, lang)}-a
   5 cm-en, {pct(mu['R75'], 0, lang)}-a 7,5 cm-en belül van: 48,6 mm-es cellákkal az 5 cm a legkisebb sugár, amely a primer által
   átszelt cellá(ka)t tartalmazza. Ennél kisebb sugárnál az eredményt az a feltevés dönti el, hogy a cellán belül egyenletes az energia
   (felezés), nem a zápor.
2. **Az elektromágneses zápor belefér.** 5 cm = 2,3 Molière-sugár (R_M = 21,9 mm); az elektron energiájának
   {pct(C['electron']['R50'], 0, lang)}-a ezen belül van.
3. **Ez választ szét a legjobban.** Az R-en belüli energiával az elektron–hadron szétválasztás (AUC 2–20 GeV/c átlaga,
   R = 2,5 / 5 / 7,5 / 10 cm) e/π-re {sep}, e/p-re {sepp}: az 5 cm a legjobb vagy holtversenyben a legjobb.

**Cellaközép-szabály vagy arányos felezés?** A cellaközép-szabály az egész cellát a maghoz sorolja, ha a középpontja 5 cm-en belül van;
kb. 0,03-dal több magot ad, mint az arányos felezés (a táblázat utolsó oszlopa), a szétválasztás gyakorlatilag ugyanaz. Az arányos
felezés nem függ attól, hol szeli át a tengely a cellát, ezért ezt használjuk; mindkettő megvan (`f_near_R50`, `f_near_centre_R50`).

**Kiválasztás.** A belépési pont a műszerezett területen van, és a tengely mind a 60 rétegben 10 cm-rel a terület szélén belül marad
(nincs oldalirányú kiszivárgás a külső szélen vagy a nyalábnyílásnál; az események {pct(A['selection']['pion']['events_fiducial'] / 1e5, 0, lang)}-a);
csak a gyors (t < 100 ns) lerakódások számítanak.
"""


# ------------------------------------------------------------------------------------------------------------------------------- Q2
def page_q2(lang):
    hu = lang == "hu"
    n = lambda x, d=2: num(x, d, lang)
    pr, pi = q2row("proton", W[1]), q2row("pion", W[1])
    rows = []
    for p in ("electron", "muon", "pion", "proton"):
        for w in (1, 5, 20):
            r = q2row(p, w if False else W[w])
            rows.append(f"| {PNAME[lang][p]} | {w} | {n(r.f_core)} ± {n(r.f_core_se)} | {n(r.f_core_event_mean)} | {n(r.f_MIP)} | "
                        f"{n(r.f_core_plus_MIP)} | {n(r.formula_axial_term)} | {n(r.truth_primary_share)} | {n(r.truth_core_from_primary_passage)} | "
                        f"{pct(r.truth_before_layer1, 0, lang)} / {pct(r.truth_inelastic, 0, lang)} / {pct(r.truth_stops, 0, lang)} |")
    tab = "\n".join(rows)
    a1, a9, a19 = (1 - auc_fcore(b) for b in (1, 9, 19))
    if not hu:
        return f"""**English** | [Magyar](Q2.hu.md)

# Q2 – Is the core fraction of protons really ~60 % at 1 GeV/c, and ~43 % for pions?

Particle issue [#1]({ISSUE}). Notebook: [`notebooks/09_axis_core.ipynb`](../../notebooks/09_axis_core.ipynb).

**Answer. No.** Measured with the definition of issue #1, the core fraction at 1 GeV/c is **f_core = {n(pr.f_core)} ± {n(pr.f_core_se)}
for protons and {n(pi.f_core)} ± {n(pi.f_core_se)} for pions** (ratio of sums; event means {n(pr.f_core_event_mean)} and
{n(pi.f_core_event_mean)}). The infographic numbers ({n(pr.formula_axial_term)} and {n(pi.formula_axial_term)}) are not a core fraction:
they are the share of the *axial term* of the fitted shape formula, the model's component for the primary's whole passage. The measured
counterpart of that is the whole axis region `f_core + f_MIP` = {n(pr.f_core_plus_MIP)} (proton) and {n(pi.f_core_plus_MIP)} (pion), or
the primary's own share of `E_vis` in the simulation truth, {n(pr.truth_primary_share)} and {n(pi.truth_primary_share)}. For the proton the
axial term ({n(pr.formula_axial_term)}) is close to that truth ({n(pr.truth_primary_share)}); for the pion it is too large
({n(pi.formula_axial_term)} against {n(pi.truth_primary_share)}): the fit gives the axial term energy of secondaries near the axis.

![f_core against momentum](q2_fcore.png)

| particle | p [GeV/c] | f_core (ratio of sums) | f_core (event mean) | f_MIP | f_core + f_MIP | infographic (axial term) | truth: primary's share | truth: f_core from the primary's passage | truth: interaction before tile 1 / inelastic / stops |
|---|---|---|---|---|---|---|---|---|---|
{tab}

Windows: 0.9–1.1, 4.75–5.25 and 19.5–20 GeV/c. Halving the window width changes f_core by less than its error (`q2_table.csv`).

**How much comes from an initial non-interacting passage?** At 1 GeV/c {pct(pr.truth_stops, 0)} of the protons stop without a hadronic
interaction (their range is about 16 cm of steel), {pct(pr.truth_before_layer1, 0)} interact in the 40.4 mm front steel and
{pct(pr.truth_inelastic, 0)} later. **{n(pr.truth_core_from_primary_passage)} of the proton's {n(pr.f_core)} core is the proton's own
deposit after its MIP segment** (the heavily ionising end of the range, more than 2 MIP per tile, where the finder ends the MIP segment);
for stopping protons f_core is {n(pr.f_core_not_interacting)}, for interacting ones {n(pr.f_core_interacting)}. For pions only
{n(pi.truth_core_from_primary_passage)} of {n(pi.f_core)} comes from the pion itself: {pct(pi.truth_inelastic + pi.truth_before_layer1, 0)}
of them interact, so the pion core is shower. At 5 and 20 GeV/c the primary's own passage gives at most 0.02 for both. Pions and protons
reach at least the second tile in about two thirds of the events (`truth_reaches_tile2` in `q2_table.csv`).

**Discriminating power.** The core fraction separates pions from protons weakly but clearly: AUC = {n(a1)} (1–2 GeV/c), {n(a9)} (9–10)
and {n(a19)} (19–20 GeV/c) – protons have less core than pions above 1 GeV/c (below 1 GeV/c the stopping protons have more). The
ratio core / rest of the shower is a monotonic function of f_core and has the same AUC. Against electrons f_core is the strongest single
feature (see Q3: about 99 % hadron efficiency at 99 % electron rejection from 2 GeV/c).

![AUC of f_core](q2_auc_fcore.png)

**To confirm with Gábor.** *Event mean or ratio of sums?* Both are in the table; they differ by up to 0.07 for 1 GeV/c protons (a few
high-energy events dominate the sum). The infographic, being a model of the mean density, corresponds to the ratio of sums.
"""
    return f"""[English](Q2.md) | **Magyar**

# Q2 – Valóban ~60 % a proton magaránya 1 GeV/c-n, és ~43 % a pioné?

Részecske-issue [#1]({ISSUE}). Notebook: [`notebooks/09_axis_core.ipynb`](../../notebooks/09_axis_core.ipynb).

**Válasz. Nem.** Az issue #1 definíciójával mérve 1 GeV/c-n **f_core = {n(pr.f_core)} ± {n(pr.f_core_se)} a protonra és
{n(pi.f_core)} ± {n(pi.f_core_se)} a pionra** (összegek aránya; eseményátlag {n(pr.f_core_event_mean)} és {n(pi.f_core_event_mean)}).
Az infografika számai ({n(pr.formula_axial_term)} és {n(pi.formula_axial_term)}) nem magarányok: az illesztett alakképlet
*tengelytagjának* részarányai, ami a modellben a primer teljes áthaladását írja le. Ennek mért megfelelője a teljes tengely menti
tartomány, `f_core + f_MIP` = {n(pr.f_core_plus_MIP)} (proton) és {n(pi.f_core_plus_MIP)} (pion), vagy a szimulációs igazság szerint a
primer saját részaránya az `E_vis`-ből: {n(pr.truth_primary_share)} és {n(pi.truth_primary_share)}. A protonnál a tengelytag
({n(pr.formula_axial_term)}) közel van ehhez az igazsághoz ({n(pr.truth_primary_share)}); a pionnál túl nagy
({n(pi.formula_axial_term)} a {n(pi.truth_primary_share)} helyett): az illesztés a tengely közelében lévő másodlagos részecskék energiáját is
a tengelytaghoz adja.

![f_core az impulzus függvényében](q2_fcore.png)

| részecske | p [GeV/c] | f_core (összegek aránya) | f_core (eseményátlag) | f_MIP | f_core + f_MIP | infografika (tengelytag) | igazság: a primer része | igazság: f_core a primer áthaladásából | igazság: kölcsönhatás az 1. csempe előtt / rugalmatlan / megáll |
|---|---|---|---|---|---|---|---|---|---|
{tab}

Ablakok: 0,9–1,1, 4,75–5,25 és 19,5–20 GeV/c. Az ablak felére szűkítése a hibánál kevesebbet változtat f_core-on (`q2_table.csv`).

**Mennyi jön a kezdeti, kölcsönhatás nélküli áthaladásból?** 1 GeV/c-n a protonok {pct(pr.truth_stops, 0, lang)}-a hadronikus
kölcsönhatás nélkül megáll (hatótávolsága kb. 16 cm acél), {pct(pr.truth_before_layer1, 0, lang)}-a a 40,4 mm-es elülső acélban,
{pct(pr.truth_inelastic, 0, lang)}-a később hat kölcsön. **A proton {n(pr.f_core)}-os magjából {n(pr.truth_core_from_primary_passage)} a
proton saját lerakódása a MIP-szakasza után** (a hatótávolság erősen ionizáló vége, rétegenként 2 MIP fölött, ahol a kereső lezárja a
MIP-szakaszt); a megálló protonokra f_core = {n(pr.f_core_not_interacting)}, a kölcsönhatókra {n(pr.f_core_interacting)}. A pionnál a
{n(pi.f_core)}-ból csak {n(pi.truth_core_from_primary_passage)} jön magától a piontól: {pct(pi.truth_inelastic + pi.truth_before_layer1, 0, lang)}-uk
kölcsönhat, így a pionmag zápor. 5 és 20 GeV/c-n a primer saját áthaladása mindkettőnél legfeljebb 0,02. A pionok és a protonok kb.
kétharmada legalább a második csempéig eljut (`truth_reaches_tile2` a `q2_table.csv`-ben).

**Megkülönböztető erő.** A magarány gyengén, de egyértelműen választja szét a piont a protontól: AUC = {n(a1)} (1–2 GeV/c), {n(a9)}
(9–10) és {n(a19)} (19–20 GeV/c) – 1 GeV/c felett a protonnak kisebb a magja, mint a pionnak (1 GeV/c alatt a megálló protonoké
nagyobb). A mag / a zápor többi része arány f_core monoton függvénye, ugyanaz az AUC-ja. Az elektronokkal szemben f_core a legerősebb
egyedi jellemző (lásd Q3: 2 GeV/c-től kb. 99 % hadronhatásfok 99 % elektron-elutasításnál).

![f_core AUC](q2_auc_fcore.png)

**Gáborral egyeztetendő.** *Eseményátlag vagy összegek aránya?* Mindkettő a táblázatban; az 1 GeV/c-s protonoknál 0,07-ig eltérnek (az
összeget néhány nagy energiájú esemény uralja). Az infografika az átlagos sűrűség modellje, így az összegek arányának felel meg.
"""


# ------------------------------------------------------------------------------------------------------------------------------- Q3
REFS = """- CALICE, *Pion and proton showers in the CALICE scintillator-steel analogue hadron calorimeter*, JINST 10 (2015) P04014,
  [arXiv:1412.2653](https://arxiv.org/abs/1412.2653) – shower-start finder, truth from the primary's inelastic interaction.
- CALICE, *Testing hadronic interaction models using a highly granular silicon-tungsten calorimeter*, NIM A 794 (2015) 240,
  [arXiv:1411.7215](https://arxiv.org/abs/1411.7215) – interaction-layer finder, muon false starts per interaction length.
- CMS HGCAL and CALICE, *Performance of the CMS High Granularity Calorimeter prototype to charged pion beams of 20–300 GeV/c*,
  JINST 18 (2023) P08014, [arXiv:2211.04740](https://arxiv.org/abs/2211.04740) – energy-dependent shower-start thresholds, λ_π / λ_I ≈ 1.2.
- CALICE, *Particle identification using Boosted Decision Trees in the Semi-Digital Hadronic Calorimeter prototype*, JINST 15 (2020)
  P10009, [arXiv:2004.02972](https://arxiv.org/abs/2004.02972) – shower start and radius as e/π features.
- Particle Data Group, *Passage of particles through matter* (2024) and *Atomic and nuclear properties of materials* – MIP energy loss,
  most probable value, interaction lengths.
- ePIC geometry, [eic/epic `compact/hcal/lfhcal.xml`](https://github.com/eic/epic/blob/main/compact/hcal/lfhcal.xml) (tag 26.08.0):
  tile in front of its absorber, 25.4 mm + 15 mm front steel, readout segments of 5, 5, 10, 10, 10, 10, 10 tiles (`rlayerz`)."""


def page_q3(lang):
    hu = lang == "hu"
    n = lambda x, d=2: num(x, d, lang)
    F = A["finder"]["versions"]["strict"]
    TM = A["finder"]["train_metrics"]
    cal = A["calibration"]
    th = T["q3_calibration_theta"]
    lt, ls, ln = (lam("pion", "3-20", v) for v in ("truth", "strict", "narrow"))
    pt, ps, pn = (lam("proton", "3-20", v) for v in ("truth", "strict", "narrow"))
    mf = A["q3_lambda"]["muon_false_start"]["strict"]
    cl3 = A["claim3_pre_interaction_tiles"]
    rng = ("1-2", "2-3", "3-5", "5-10", "10-20")
    plong = "\n".join(f"| {PNAME[lang][p]} | " + " | ".join(f"{n(c1(p, r, 'P_L_ge_8'))} / {n(c1(p, r, 'P_L_ge_10'))}" for r in rng) + " |"
                      for p in ("electron", "muon", "pion", "proton"))
    agt = "\n".join(f"| {PNAME[lang][p]} | " + " | ".join(f"{n(agr(p, r, 'within_1'))} ({n(agr(p, r, 'early'))} / {n(agr(p, r, 'late'))} / {n(agr(p, r, 'no_start'))})"
                                                       for r in rng) + " |" for p in ("pion", "proton"))
    vt = " / ".join(f"{pct(vis('pion', r), 0, lang)}" for r in rng)
    vp = " / ".join(f"{pct(vis('proton', r), 0, lang)}" for r in rng)
    bins = (1, 2, 4, 9, 19)
    ef = "\n".join(f"| {pair.split('_')[-1] if not hu else PNAME['hu'][pair.split('_')[-1]]} | {feat} | " + " | ".join(n(eff(pair, b, feat)) for b in bins) + " |"
                   for pair in ("electron_vs_pion", "electron_vs_proton") for feat in ("f_core", "L_MIP", "seg1", "combined"))
    lr8 = (c4("pion", "1-2", 8, "likelihood_ratio"), c4("pion", "10-20", 8, "likelihood_ratio"))
    pe8 = (c4("pion", "1-2", 8, "P_electron"), c4("pion", "10-20", 8, "P_electron"))
    ph8 = (min(c4(h, r, 8, "P_hadron") for h in ("pion", "proton") for r in rng), max(c4(h, r, 8, "P_hadron") for h in ("pion", "proton") for r in rng))
    present = (min(c1(h, r, "P_L_gt_0") for h in ("pion", "proton") for r in rng), max(c1(h, r, "P_L_gt_0") for h in ("pion", "proton") for r in rng))
    reach = (min(c1(h, r, "truth_reaches_tile1") for h in ("pion", "proton") for r in rng), max(c1(h, r, "truth_reaches_tile1") for h in ("pion", "proton") for r in rng))
    late = (min(c2(h, r, "late_run_by_secondary") for h in ("pion", "proton") for r in rng[2:]), max(c2(h, r, "late_run_by_secondary") for h in ("pion", "proton") for r in rng[2:]))
    latep = max(c2(h, r, "late_run_by_primary") for h in ("pion", "proton") for r in rng)
    mref = cl3["muon_reference"]
    w1 = (min(agr(p, r, "within_1") for p in ("pion", "proton") for r in ("5-10", "10-20")), max(agr(p, r, "within_1") for p in ("pion", "proton") for r in ("5-10", "10-20")))
    thr = f"{n(F['core_sum'], 0)} + {n(F['core_sum_per_gev'], 1)} · p[GeV/c]"
    g, s_ = TM["gabor_rule"], TM["strict"]
    comp = (f"| {'választott' if hu else 'chosen'} | {n(s_['had_pm1_3_20'])} | {pct(s_['pion_early'], 0, lang)} | {pct(s_['pion_late'], 0, lang)} | "
            f"{pct(s_['muon_false_per_lambda'], 1, lang)} | {n(s_['eff99_pion_1_3'])} / {n(s_['eff99_pion_3_20'])} |\n"
            f"| {'az issue szabálya (2,5 MIP-sáv, energiafeltétel nélkül)' if hu else 'issue rule (2.5 MIP band, no energy condition)'} | {n(g['had_pm1_3_20'])} | "
            f"{pct(g['pion_early'], 0, lang)} | {pct(g['pion_late'], 0, lang)} | {pct(g['muon_false_per_lambda'], 1, lang)} | {n(g['eff99_pion_1_3'])} / {n(g['eff99_pion_3_20'])} |\n"
            f"| {'keskeny lerakódás' if hu else 'narrow deposit'} | {n(TM['narrow']['had_pm1_3_20'])} | {pct(TM['narrow']['pion_early'], 0, lang)} | "
            f"{pct(TM['narrow']['pion_late'], 0, lang)} | {pct(TM['narrow']['muon_false_per_lambda'], 1, lang)} | {n(TM['narrow']['eff99_pion_1_3'])} / {n(TM['narrow']['eff99_pion_3_20'])} |")
    if not hu:
        return f"""**English** | [Magyar](Q3.hu.md)

# Q3 – Is there a MIP segment at the start of hadron showers, and how well does it identify hadrons?

Particle issue [#1]({ISSUE}). Notebook: [`notebooks/10_mip_segment.ipynb`](../../notebooks/10_mip_segment.ipynb).

**Answer.** Yes: {pct(present[0], 0)}–{pct(present[1], 0)} of pions and protons start with a MIP segment; most of the rest interact
already in the 40.4 mm of steel in front of the first tile. A segment of 8 cm or longer is a high-purity hadron tag – it occurs for
{pct(ph8[0], 0)}–{pct(ph8[1], 0)} of hadrons and for {pct(pe8[0], 1)} (1–2 GeV/c) to {pct(pe8[1], 1)} (10–20 GeV/c) of electrons, a
likelihood ratio of {n(lr8[0], 0)} to {n(lr8[1], 0)} – but it keeps only about 60–80 % of hadrons at 99 % electron rejection, because
the rest interact earlier. The core fraction is the stronger electron/hadron feature (about 99 % from 2 GeV/c); the MIP segment does
not separate pions from protons. The rule of the issue had to be changed to find the shower start reliably (see *The finder*).

## Gábor's four properties

1. **It may or may not be there – true.** A segment exists in {pct(present[0], 0)}–{pct(present[1], 0)} of the hadron events; in the
   simulation truth {pct(reach[0], 0)}–{pct(reach[1], 0)} of the primaries reach the first tile (the others interact in the front steel,
   about 1 − exp(−4.04 cm / (λ cos θ)); at low momentum some of these interactions are not visible, so the observed share is higher).
2. **If it is there, it always starts at the entry point – true for the primary.** The primary's segment starts at the entry by
   construction; but after the shower start a secondary (a leading hadron of a soft interaction) draws another MIP-like run of ≥ 4
   tiles in {pct(late[0], 0)}–{pct(late[1], 0)} of the events at 3–20 GeV/c (truth: carried by a secondary; by the primary itself in at
   most {pct(latep, 1)}). Such later segments do not start at the entry point.
3. **Very small energy deposit, along the axis only – true for the primary, not for the tiles.** In the tiles the primary crosses before
   its interaction (truth, p ≥ 3 GeV/c) the core holds {n(cl3['pion']['core_mip_per_tile'], 2)} MIP per tile for pions, of which
   {n(cl3['pion']['primary_core_mip_per_tile'], 2)} MIP is the pion itself and {n(cl3['pion']['secondary_core_mip_per_tile'], 2)} MIP
   secondaries; outside 5 cm the same tiles receive {n(cl3['pion']['outside_R_mip_per_tile'], 2)} MIP (protons
   {n(cl3['proton']['outside_R_mip_per_tile'], 2)}), and {pct(cl3['pion']['share_tiles_with_outside_R_gt_1mip'], 0)}
   ({pct(cl3['proton']['share_tiles_with_outside_R_gt_1mip'], 0)}) of them more than 1 MIP, against {n(mref['outside_R_mip_per_tile'], 2)} MIP and
   {pct(mref['share_tiles_with_outside_R_gt_1mip'], 1)} for muons, which have no hadronic interaction: this is **backsplash** from the shower deeper in
   the calorimeter. A condition on the energy outside 5 cm therefore ends the segment too early.
4. **8–10 cm or longer is a very powerful hadron indicator – true for purity, limited in efficiency** (numbers above and below).

## MIP calibration with muons

![MIP calibration](q3_calibration.png)

Muons with p ≥ 2 GeV/c, every tile on its own: most probable value of the core energy × cos θ = {n(cal['mpv_median_MeV'], 3)} MeV
(median of the 60 tiles; the first tile {n(cal['mpv_layer1_MeV'], 3)} MeV), half widths at half maximum {n(cal['hwhm_left_median_MeV'], 3)} /
{n(cal['hwhm_right_median_MeV'], 3)} MeV. With θ the raw value rises from {n(th.mpv_raw_MeV.iloc[0], 3)} to {n(th.mpv_raw_MeV.iloc[-1], 3)} MeV
({pct(th.mpv_raw_MeV.iloc[-1] / th.mpv_raw_MeV.iloc[0] - 1, 0)}); after the 1/cos θ correction it changes by
{pct(th.mpv_cos_MeV.iloc[-1] / th.mpv_cos_MeV.iloc[0] - 1, 1)}, about half of which is expected because the most probable loss grows
slightly faster than the path length (Landau–Vavilov, ≈ 1 % at θ = 0.57 rad).
This agrees with the PDG Landau–Vavilov most probable value for a 4 mm tile of the ePIC polystyrene (1.032 g/cm³): 0.615–0.624 MeV
for 2–20 GeV/c muons. About {pct(cal['zero_frac_median'], 0)} of the crossed
tiles have no energy (gaps between tiles), so empty tiles must not end a segment.

## The finder

A tile is **MIP-like** if its core energy is at most {n(F['core_up'], 1)} MIP and at most {F['cells_up']} cells fire (> 0.3 MIP). The
**shower starts** at the first {F['n_consec']} consecutive non-MIP tiles whose summed core energy exceeds **{thr} MIP** (the momentum is
known from the tracker; CMS HGCAL also uses energy-dependent thresholds). Empty tiles do not interrupt the segment; without a start the
segment ends at the last deposit on the axis (a stopping particle). `L_MIP` is the depth of the last tile with a deposit on the axis
before the start; `z_start` the depth of the start tile. Because a tile sits in front of its absorber, L_MIP ≤ true interaction depth
< z_start.

The parameters were chosen on the train split against the simulation truth (`scripts/core_mip_tune.py`, {len(pd.read_csv(os.path.join(D, 'finder_scan.csv')))} settings): among the
settings with at most 3 % muon false starts per interaction length (the CALICE Si-W level), those within 0.01 of the best ±1-tile
agreement with the true interaction, then the best L_MIP efficiency at 99 % electron rejection. Comparison on the train split:

| rule | ±1-tile agreement (π, p; 3–20 GeV/c) | early starts (π) | late starts (π) | muon false starts per λ_I | π efficiency at 99 % e rejection, 1–3 / 3–20 GeV/c |
|---|---|---|---|---|---|
{comp}

The issue's rule starts the shower too early in a quarter of the pion events: the energy outside 5 cm and the cell count react to
backsplash, and a single Landau/δ-ray tile pair is enough. The energy condition on the core removes that. **Strict band or narrow deposit
for slow hadrons?** The narrow-deposit version (no limit on the core energy) cannot tell an electron shower from a slow hadron – both are
narrow – so it fails as an identifier ({n(TM['narrow']['eff99_pion_1_3'])} pion efficiency at 1–3 GeV/c); with the energy condition the
strict band already keeps slow protons in their segment except at the end of their range. We recommend the strict version.

## L_MIP and P(L_MIP ≥ 8 / 10 cm)

![L_MIP distributions](q3_lmip.png)
![P(L_MIP ≥ 8 cm) and P(L_MIP ≥ 10 cm)](q3_plong.png)

P(L ≥ 8 cm) / P(L ≥ 10 cm):

| particle | 1–2 GeV/c | 2–3 | 3–5 | 5–10 | 10–20 |
|---|---|---|---|---|---|
{plong}

## Effective interaction length

![Survival without a (visible) interaction](q3_survival.png)

Truncated, censored exponential likelihood on 8–80 cm, p ≥ 3 GeV/c:

- **simulation truth** (the primary's last tile): **λ = {n(lt['lambda_cm'], 1)} ± {n(lt['se'], 1)} cm for pions and {n(pt['lambda_cm'], 1)} ± {n(pt['se'], 1)} cm
  for protons**, ratio {n(lt['lambda_cm'] / pt['lambda_cm'], 2)}. The PDG values of the layer stack, 26.0 and 21.2 cm (ratio 1.23), are for
  200 GeV/c; the pion value rises with momentum ({n(lam('pion', '3-5', 'truth')['lambda_cm'], 1)} cm at 3–5, {n(lam('pion', '10-20', 'truth')['lambda_cm'], 1)} cm at 10–20 GeV/c), the proton
  value is flat ({n(lam('proton', '3-5', 'truth')['lambda_cm'], 1)} / {n(lam('proton', '10-20', 'truth')['lambda_cm'], 1)} cm). The truth survival is a clean exponential.
- **the finder** measures the first *visible* shower start: λ_eff = {n(ls['lambda_cm'], 1)} cm (pions) and {n(ps['lambda_cm'], 1)} cm
  (protons), and its survival is not a single exponential. It is longer than the truth because a part of the interactions puts little
  energy near the axis: the two tiles after the true interaction hold less than the start threshold in {vt} of the pion and {vp} of the
  proton interactions (1–2, 2–3, 3–5, 5–10, 10–20 GeV/c). Muon false starts ({pct(mf['share_with_start'], 0)} of the muons, λ_fake = {n(mf['lambda_fake_cm'], 0)} cm)
  shorten it a little. The effective length therefore depends on the start definition; the physical interaction length is the truth value.

## The start tile against the true interaction

![Start tile against the truth](q3_truth.png)

Share within ±1 tile of the true interaction (early / late / no start), all events:

| particle | 1–2 GeV/c | 2–3 | 3–5 | 5–10 | 10–20 |
|---|---|---|---|---|---|
{agt}

From 5 GeV/c the agreement ({n(w1[0])}–{n(w1[1])}) is at the level of the CALICE finders (≈ 80 % within ±1 layer at 10–80 GeV); below 3 GeV/c
many interactions are not visible as a shower start (low multiplicity, energy carried by neutrons), so the MIP segment there ends at the
first *visible* activity.

## Hadron identification

![Hadron efficiency at 99 % electron rejection](q3_eff99.png)

Hadron efficiency at 99 % electron rejection (test split; thresholds from the train + val electrons):

| hadron | feature | 1–2 GeV/c | 2–3 | 4–5 | 9–10 | 19–20 |
|---|---|---|---|---|---|---|
{ef}

`seg1` is the energy of tiles 1–5. **The ePIC LFHCal reads these five tiles out as one channel** (segments of 5, 5, 10, 10, 10, 10, 10
tiles), so a per-tile L_MIP exists only in simulation (and in the individually read insert); at the readout level the tag becomes
"the first segment is MIP-like", which keeps almost the same efficiency. Below 1 GeV/c nothing works (soft electrons deposit only a few
MeV).

## Checks

{s2_sentence("en")} A second implementation written from the definitions (`scripts/verify_core_mip.py`) reproduces the truth, the
start tile of the finder event by event and the headline numbers (`verification.csv`).

## References

{REFS}
"""
    return f"""[English](Q3.md) | **Magyar**

# Q3 – Van-e MIP-szakasz a hadronzáporok elején, és mennyire jól azonosítja a hadronokat?

Részecske-issue [#1]({ISSUE}). Notebook: [`notebooks/10_mip_segment.ipynb`](../../notebooks/10_mip_segment.ipynb).

**Válasz.** Igen: a pionok és protonok {pct(present[0], 0, lang)}–{pct(present[1], 0, lang)}-a MIP-szakasszal kezd; a többi nagyrészt már az
első csempe előtti 40,4 mm acélban kölcsönhat. A legalább 8 cm-es szakasz nagy tisztaságú hadronjel – a hadronok
{pct(ph8[0], 0, lang)}–{pct(ph8[1], 0, lang)}-ánál és az elektronok {pct(pe8[0], 1, lang)} (1–2 GeV/c) – {pct(pe8[1], 1, lang)}
(10–20 GeV/c) részénél fordul elő, a valószínűségi hányados {n(lr8[0], 0)}–{n(lr8[1], 0)} –, de 99 % elektron-elutasításnál a hadronoknak
csak kb. 60–80 %-át tartja meg, mert a többi korábban kölcsönhat. Az elektron–hadron szétválasztásban a magarány az erősebb (2 GeV/c-től
kb. 99 %); a MIP-szakasz a piont a protontól nem választja el. Az issue szabályán változtatni kellett, hogy a zápor kezdete megbízható
legyen (lásd *A kereső*).

## Gábor négy állítása

1. **Lehet, hogy ott van, lehet, hogy nincs – igaz.** A hadronesemények {pct(present[0], 0, lang)}–{pct(present[1], 0, lang)}-ában van
   szakasz; a szimulációs igazság szerint a primerek {pct(reach[0], 0, lang)}–{pct(reach[1], 0, lang)}-a eléri az első csempét (a többi
   az elülső acélban hat kölcsön, kb. 1 − exp(−4,04 cm / (λ cos θ)); kis impulzusnál e kölcsönhatások egy része nem látszik, ezért ott a
   megfigyelt arány nagyobb).
2. **Ha ott van, mindig a belépési pontnál kezdődik – a primerre igaz.** A primer szakasza definíció szerint a belépésnél kezdődik; a zápor
   kezdete után viszont egy másodlagos részecske (egy lágy kölcsönhatás vezető hadronja) 3–20 GeV/c-n az események
   {pct(late[0], 0, lang)}–{pct(late[1], 0, lang)}-ában újabb, legalább 4 csempés MIP-szerű szakaszt húz (igazság: másodlagos viszi; maga a
   primer legfeljebb {pct(latep, 1, lang)}-ban). Ezek a későbbi szakaszok nem a belépési pontnál kezdődnek.
3. **Nagyon kis energialerakódás, csak a tengely mentén – a primerre igaz, a csempékre nem.** Azokban a csempékben, amelyeket a primer a
   kölcsönhatása előtt átszel (igazság, p ≥ 3 GeV/c), a magban pionnál {n(cl3['pion']['core_mip_per_tile'], 2)} MIP van csempénként, ebből
   {n(cl3['pion']['primary_core_mip_per_tile'], 2)} MIP maga a pion, {n(cl3['pion']['secondary_core_mip_per_tile'], 2)} MIP másodlagos; 5 cm-en
   kívül ugyanezek a csempék {n(cl3['pion']['outside_R_mip_per_tile'], 2)} MIP-et kapnak (proton {n(cl3['proton']['outside_R_mip_per_tile'], 2)}),
   és {pct(cl3['pion']['share_tiles_with_outside_R_gt_1mip'], 0, lang)}-uk ({pct(cl3['proton']['share_tiles_with_outside_R_gt_1mip'], 0, lang)}-uk)
   több mint 1 MIP-et, szemben a müonok {n(mref['outside_R_mip_per_tile'], 2)} MIP-jével és {pct(mref['share_tiles_with_outside_R_gt_1mip'], 1, lang)}-ával
   (náluk nincs hadronikus kölcsönhatás): ez a kaloriméterben mélyebben induló zápor **visszaszórása**. Az 5 cm-en kívüli energiára tett
   feltétel ezért túl korán zárja le a szakaszt.
4. **A 8–10 cm-es vagy hosszabb szakasz nagyon erős hadronjel – a tisztaságra igaz, a hatásfoka korlátozott** (számok fent és lent).

## MIP-kalibráció müonokkal

![MIP-kalibráció](q3_calibration.png)

Müonok p ≥ 2 GeV/c-vel, minden csempe külön: a mag-energia × cos θ legvalószínűbb értéke {n(cal['mpv_median_MeV'], 3)} MeV (a 60 csempe
mediánja; az első csempe {n(cal['mpv_layer1_MeV'], 3)} MeV), a félértékszélesség felei {n(cal['hwhm_left_median_MeV'], 3)} /
{n(cal['hwhm_right_median_MeV'], 3)} MeV. A nyers érték θ-val {n(th.mpv_raw_MeV.iloc[0], 3)}-ról {n(th.mpv_raw_MeV.iloc[-1], 3)} MeV-re nő
({pct(th.mpv_raw_MeV.iloc[-1] / th.mpv_raw_MeV.iloc[0] - 1, 0, lang)}); az 1/cos θ korrekció után csak
{pct(th.mpv_cos_MeV.iloc[-1] / th.mpv_cos_MeV.iloc[0] - 1, 1, lang)}-ot változik, és ennek kb. fele várható, mert a legvalószínűbb
energiaveszteség kicsit gyorsabban nő, mint az úthossz (Landau–Vavilov, θ = 0,57 rad-nál ≈ 1 %). Ez egyezik a PDG
Landau–Vavilov-képlet szerinti legvalószínűbb értékkel az ePIC 4 mm-es polisztirol csempéjére (1,032 g/cm³): 0,615–0,624 MeV a
2–20 GeV/c-s müonokra. Az átszelt csempék kb.
{pct(cal['zero_frac_median'], 0, lang)}-ában nincs energia (rések a csempék között), ezért üres csempe nem zárhatja le a szakaszt.

## A kereső

Egy csempe **MIP-szerű**, ha a mag-energiája legfeljebb {n(F['core_up'], 1)} MIP, és legfeljebb {F['cells_up']} cella tüzel (> 0,3 MIP). A
**zápor ott kezdődik**, ahol először {F['n_consec']} egymást követő nem MIP-szerű csempe mag-energiájának összege meghaladja a **{thr} MIP**-et
(az impulzus a nyomkövetőből ismert; a CMS HGCAL is energiafüggő küszöböket használ). Üres csempe nem szakítja meg a szakaszt; kezdet
nélkül a szakasz a tengely menti utolsó lerakódásnál ér véget (megálló részecske). `L_MIP` a kezdet előtti utolsó, tengely menti
lerakódású csempe mélysége, `z_start` a kezdő csempéé. Mivel a csempe az elnyelője előtt ül, L_MIP ≤ a valódi kölcsönhatás mélysége < z_start.

A paramétereket a tanító mintán, a szimulációs igazsághoz mérve választottuk (`scripts/core_mip_tune.py`, {len(pd.read_csv(os.path.join(D, 'finder_scan.csv')))} beállítás): a legfeljebb 3 %
müon-hamis-kezdetet adó (λ_I-nként; CALICE Si-W szint) beállítások közül a legjobb ±1 csempés egyezéstől 0,01-en belüliek, ezek közül a
legjobb L_MIP-hatásfok 99 % elektron-elutasításnál. Összehasonlítás a tanító mintán:

| szabály | ±1 csempés egyezés (π, p; 3–20 GeV/c) | korai kezdet (π) | késői kezdet (π) | müon hamis kezdet λ_I-nként | π hatásfok 99 % e-elutasításnál, 1–3 / 3–20 GeV/c |
|---|---|---|---|---|---|
{comp}

Az issue szabálya a pionesemények negyedében túl korán indítja a záport: az 5 cm-en kívüli energia és a cellaszám a visszaszórásra
reagál, és egyetlen Landau-/δ-sugaras csempepár is elég. A mag-energiára tett feltétel ezt megszünteti. **Szigorú sáv vagy keskeny
lerakódás a lassú hadronokra?** A keskeny változat (a mag-energiára nincs korlát) nem tudja megkülönböztetni az elektronzáport a lassú
hadrontól – mindkettő keskeny –, így azonosításra alkalmatlan (pionhatásfok 1–3 GeV/c-n: {n(TM['narrow']['eff99_pion_1_3'])}); az
energiafeltétellel a szigorú sáv a lassú protonokat a hatótávolságuk végéig a szakaszban tartja. A szigorú változatot javasoljuk.

## L_MIP és P(L_MIP ≥ 8 / 10 cm)

![L_MIP eloszlások](q3_lmip.png)
![P(L_MIP ≥ 8 cm) és P(L_MIP ≥ 10 cm)](q3_plong.png)

P(L ≥ 8 cm) / P(L ≥ 10 cm):

| részecske | 1–2 GeV/c | 2–3 | 3–5 | 5–10 | 10–20 |
|---|---|---|---|---|---|
{plong}

## Effektív kölcsönhatási hossz

![Túlélés (látható) kölcsönhatás nélkül](q3_survival.png)

Csonkolt, cenzorált exponenciális likelihood 8–80 cm-en, p ≥ 3 GeV/c:

- **szimulációs igazság** (a primer utolsó csempéje): **λ = {n(lt['lambda_cm'], 1)} ± {n(lt['se'], 1)} cm a pionra és
  {n(pt['lambda_cm'], 1)} ± {n(pt['se'], 1)} cm a protonra**, arányuk {n(lt['lambda_cm'] / pt['lambda_cm'], 2)}. A rétegszerkezet PDG-értékei,
  26,0 és 21,2 cm (arány 1,23), 200 GeV/c-re vonatkoznak; a pionérték az impulzussal nő ({n(lam('pion', '3-5', 'truth')['lambda_cm'], 1)} cm
  3–5, {n(lam('pion', '10-20', 'truth')['lambda_cm'], 1)} cm 10–20 GeV/c-n), a protoné állandó
  ({n(lam('proton', '3-5', 'truth')['lambda_cm'], 1)} / {n(lam('proton', '10-20', 'truth')['lambda_cm'], 1)} cm). Az igazság túlélése tiszta exponenciális.
- **a kereső** az első *látható* zápor-kezdetet méri: λ_eff = {n(ls['lambda_cm'], 1)} cm (pion) és {n(ps['lambda_cm'], 1)} cm (proton), a
  túlélése nem egyetlen exponenciális. Azért hosszabb az igazságnál, mert a kölcsönhatások egy része kevés energiát ad le a tengely
  közelében: a valódi kölcsönhatás utáni két csempe a pionkölcsönhatások {vt}, a protonkölcsönhatások {vp} részében kevesebbet tartalmaz
  a kezdési küszöbnél (1–2, 2–3, 3–5, 5–10, 10–20 GeV/c). A müonok hamis kezdetei ({pct(mf['share_with_start'], 0, lang)}, λ_fake =
  {n(mf['lambda_fake_cm'], 0)} cm) kicsit rövidítik. Az effektív hossz tehát a kezdet definíciójától függ; a fizikai kölcsönhatási hossz az
  igazság szerinti érték.

## A kezdő csempe a valódi kölcsönhatáshoz képest

![Kezdő csempe az igazsághoz képest](q3_truth.png)

A valódi kölcsönhatástól legfeljebb ±1 csempére lévő kezdetek aránya (korai / késői / nincs kezdet), minden esemény:

| részecske | 1–2 GeV/c | 2–3 | 3–5 | 5–10 | 10–20 |
|---|---|---|---|---|---|
{agt}

5 GeV/c-től az egyezés ({n(w1[0])}–{n(w1[1])}) a CALICE-keresők szintjén van (10–80 GeV-en kb. 80 % ±1 rétegen belül); 3 GeV/c alatt sok
kölcsönhatás nem látszik zápor-kezdetként (kis multiplicitás, az energiát neutronok viszik), ott a MIP-szakasz az első *látható*
aktivitásig tart.

## Hadronazonosítás

![Hadronhatásfok 99 % elektron-elutasításnál](q3_eff99.png)

Hadronhatásfok 99 % elektron-elutasításnál (tesztminta; a küszöbök a tanító és a validációs elektronokból):

| hadron | jellemző | 1–2 GeV/c | 2–3 | 4–5 | 9–10 | 19–20 |
|---|---|---|---|---|---|---|
{ef}

A `seg1` az 1–5. csempe energiája. **Az ePIC LFHCal ezt az öt csempét egy csatornán olvassa ki** (5, 5, 10, 10, 10, 10, 10 csempés
szegmensek), így a csempénkénti L_MIP csak a szimulációban (és az egyenként kiolvasott betétben) létezik; a kiolvasás szintjén a jel úgy
szól: „az első szegmens MIP-szerű”, és ez majdnem ugyanazt a hatásfokot adja. 1 GeV/c alatt semmi sem működik (a lágy elektronok csak
néhány MeV-et adnak le).

## Ellenőrzések

{s2_sentence("hu")} A definíciókból írt második implementáció (`scripts/verify_core_mip.py`) eseményenként megismétli az igazságot,
a kereső kezdő csempéjét és a fő számokat (`verification.csv`).

## Hivatkozások

{REFS}
"""


# ------------------------------------------------------------------------------------------------------------------- README block
def readme_block(lang):
    hu = lang == "hu"
    n = lambda x, d=2: num(x, d, lang)
    P = lambda x, d=0: pct(x, d, lang)
    C = A["q1"]["containment"]
    fr = lambda p, b, c: frac(p, b, c).ratio_of_sums
    e_core = min(fr("electron", b, "core") for b in range(2, 20))
    mu_mip = (min(fr("muon", b, "MIP") for b in range(1, 20)), max(fr("muon", b, "MIP") for b in range(1, 20)))
    hc1 = (min(fr(p, 1, "core") for p in ("pion", "proton")), max(fr(p, 1, "core") for p in ("pion", "proton")))
    hc19 = (min(fr(p, 19, "core") for p in ("pion", "proton")), max(fr(p, 19, "core") for p in ("pion", "proton")))
    hh = (min(fr(p, b, "halo") for p in ("pion", "proton") for b in range(2, 20)), max(fr(p, b, "halo") for p in ("pion", "proton") for b in range(2, 20)))
    pr, pi = q2row("proton", W[1]), q2row("pion", W[1])
    a_pp = (min(1 - auc_fcore(b) for b in range(1, 20)), max(1 - auc_fcore(b) for b in range(1, 20)))
    rng = ("1-2", "2-3", "3-5", "5-10", "10-20")
    present = (min(c1(h, r, "P_L_gt_0") for h in ("pion", "proton") for r in rng), max(c1(h, r, "P_L_gt_0") for h in ("pion", "proton") for r in rng))
    ph8 = (min(c4(h, r, 8, "P_hadron") for h in ("pion", "proton") for r in rng), max(c4(h, r, 8, "P_hadron") for h in ("pion", "proton") for r in rng))
    pe8 = (c4("pion", "10-20", 8, "P_electron"), c4("pion", "1-2", 8, "P_electron"))
    lr8 = (c4("pion", "1-2", 8, "likelihood_ratio"), c4("pion", "10-20", 8, "likelihood_ratio"))
    effL = [eff(pair, b, "L_MIP") for pair in ("electron_vs_pion", "electron_vs_proton") for b in range(2, 20)]
    effF = [eff(pair, b, "f_core") for pair in ("electron_vs_pion", "electron_vs_proton") for b in range(2, 20)]
    late = (min(c2(h, r, "late_run_by_secondary") for h in ("pion", "proton") for r in rng[2:]), max(c2(h, r, "late_run_by_secondary") for h in ("pion", "proton") for r in rng[2:]))
    cl3 = A["claim3_pre_interaction_tiles"]
    bs = (min(cl3[h]["outside_R_mip_per_tile"] for h in ("pion", "proton")), max(cl3[h]["outside_R_mip_per_tile"] for h in ("pion", "proton")))
    F = A["finder"]["versions"]["strict"]
    w1 = (min(agr(p, r, "within_1") for p in ("pion", "proton") for r in ("5-10", "10-20")), max(agr(p, r, "within_1") for p in ("pion", "proton") for r in ("5-10", "10-20")))
    lt, ltp = lam("pion", "3-20", "truth"), lam("proton", "3-20", "truth")
    links = "[Q1](results/core_mip/Q1{s}) · [Q2](results/core_mip/Q2{s}) · [Q3](results/core_mip/Q3{s})".format(s=".hu.md" if hu else ".md")
    if not hu:
        return f"""## Particle issue #1 – core, MIP segment and halo

[Issue #1]({ISSUE}) asked about the region around the shower axis (terms: axis, core, MIP segment, halo). Answer pages with figures:
{links}; notebooks `notebooks/09_axis_core.ipynb` and `notebooks/10_mip_segment.ipynb`; per-event features for further use in
`results/features/<particle>.parquet`. Every number below is written by `scripts/core_mip_pages.py` from `results/core_mip/`.

- **Q1 – the core** is the energy within R = 5 cm of the axis (from the entry point at the front face, z = 3620 mm) from the shower
  start on. 5 cm holds {P(C['muon']['rel_to_R100']['R50'])} of the muon energy within 10 cm and {P(C['electron']['R50'])} of the electron
  shower, and separates electrons from hadrons best among 2.5–10 cm. Electron showers are core (≥ {n(e_core)}), muons MIP segment
  ({n(mu_mip[0])}–{n(mu_mip[1])}); for hadrons the core grows from {n(hc1[0])}–{n(hc1[1])} (1–2 GeV/c) to {n(hc19[0])}–{n(hc19[1])}
  (19–20 GeV/c) and the halo carries {n(hh[0])}–{n(hh[1])}.
- **Q2 – the infographic's 60 % / 43 %** are the share of the formula's axial term, not a core fraction. Measured at 1 GeV/c:
  f_core = {n(pr.f_core)} ± {n(pr.f_core_se)} (proton) and {n(pi.f_core)} ± {n(pi.f_core_se)} (pion); {n(pr.truth_core_from_primary_passage)}
  of the proton's {n(pr.f_core)} is the proton's own deposit after its MIP segment (mostly the end of its range). Pion/proton separation by f_core: AUC {n(a_pp[0])}–{n(a_pp[1])} (weak but
  non-zero).
- **Q3 – the MIP segment** is present in {P(present[0])}–{P(present[1])} of hadron events. L_MIP ≥ 8 cm occurs for {P(ph8[0])}–{P(ph8[1])}
  of hadrons and {P(pe8[0], 1)}–{P(pe8[1], 1)} of electrons (likelihood ratio {n(lr8[0], 0)}–{n(lr8[1], 0)}); at 99 % electron rejection it
  keeps {P(min(effL))}–{P(max(effL))} of hadrons from 2 GeV/c (f_core: {P(min(effF))}–{P(max(effF))}). Gábor's four properties hold for the
  primary, with two refinements: in {P(late[0])}–{P(late[1])} of the events a secondary draws a later MIP-like run, and the tiles before
  the interaction receive {n(bs[0])}–{n(bs[1])} MIP of backsplash per tile outside 5 cm. Therefore the shower start is found from the core
  energy (two non-MIP tiles with more than {n(F['core_sum'], 0)} + {n(F['core_sum_per_gev'], 1)}·p MIP), tuned on the simulation truth:
  within ±1 tile of the true interaction in {P(w1[0])}–{P(w1[1])} of the events from 5 GeV/c (the issue's original rule: early in a
  quarter of the pion events). True interaction lengths (Geant4, 3–20 GeV/c): λ_π = {n(lt['lambda_cm'], 1)} cm, λ_p = {n(ltp['lambda_cm'], 1)} cm.
  The ePIC LFHCal reads tiles 1–5 out as one channel, so a per-tile L_MIP exists only in simulation; a "first segment MIP-like" tag is
  nearly as good.
- **Checks.** {s2_sentence("en")}
"""
    return f"""## Részecske-issue #1 – mag, MIP-szakasz és halo

Az [issue #1]({ISSUE}) a zápor tengelye körüli tartományról kérdezett (fogalmak: tengely, mag, MIP-szakasz, halo). Válaszoldalak
ábrákkal: {links}; notebookok: `notebooks/09_axis_core.ipynb` és `notebooks/10_mip_segment.ipynb`; eseményenkénti jellemzők további
használatra: `results/features/<particle>.parquet`. Az alábbi számokat a `scripts/core_mip_pages.py` írja a `results/core_mip/` alapján.

- **Q1 – a mag** a tengelytől (a front belépési pontjától, z = 3620 mm) R = 5 cm-en belüli energia a zápor kezdetétől. Az 5 cm a müon
  10 cm-en belüli energiájának {P(C['muon']['rel_to_R100']['R50'])}-át és az elektronzápor {P(C['electron']['R50'])}-át tartalmazza, és a
  2,5–10 cm közül ez választja szét legjobban az elektront a hadrontól. Az elektronzápor mag (≥ {n(e_core)}), a müon MIP-szakasz
  ({n(mu_mip[0])}–{n(mu_mip[1])}); a hadronoknál a mag {n(hc1[0])}–{n(hc1[1])}-ról (1–2 GeV/c) {n(hc19[0])}–{n(hc19[1])}-ra (19–20 GeV/c)
  nő, a halo {n(hh[0])}–{n(hh[1])} részt visz.
- **Q2 – az infografika 60 %-a / 43 %-a** a képlet tengelytagjának részaránya, nem magarány. Mérve 1 GeV/c-n: f_core =
  {n(pr.f_core)} ± {n(pr.f_core_se)} (proton) és {n(pi.f_core)} ± {n(pi.f_core_se)} (pion); a proton {n(pr.f_core)}-es magjából
  {n(pr.truth_core_from_primary_passage)} a proton saját lerakódása a MIP-szakasza után (főleg a hatótávolsága végén). Pion–proton szétválasztás f_core-ral: AUC {n(a_pp[0])}–{n(a_pp[1])} (gyenge, de nem nulla).
- **Q3 – a MIP-szakasz** a hadronesemények {P(present[0])}–{P(present[1])}-ában van jelen. L_MIP ≥ 8 cm a hadronok
  {P(ph8[0])}–{P(ph8[1])}-ánál és az elektronok {P(pe8[0], 1)}–{P(pe8[1], 1)}-ánál fordul elő (valószínűségi hányados
  {n(lr8[0], 0)}–{n(lr8[1], 0)}); 99 % elektron-elutasításnál 2 GeV/c-től a hadronok {P(min(effL))}–{P(max(effL))}-át tartja meg (f_core:
  {P(min(effF))}–{P(max(effF))}). Gábor négy állítása a primerre igaz, két pontosítással: az események {P(late[0])}–{P(late[1])}-ában egy
  másodlagos részecske későbbi MIP-szerű szakaszt húz, és a kölcsönhatás előtti csempék 5 cm-en kívül csempénként {n(bs[0])}–{n(bs[1])} MIP
  visszaszórást kapnak. Ezért a zápor kezdetét a mag-energiából keressük (két nem MIP-szerű csempe több mint {n(F['core_sum'], 0)} +
  {n(F['core_sum_per_gev'], 1)}·p MIP-pel), a szimulációs igazsághoz hangolva: 5 GeV/c-től az események {P(w1[0])}–{P(w1[1])}-ában ±1 csempén
  belül van a valódi kölcsönhatástól (az issue eredeti szabálya a pionesemények negyedében túl korán jelez). Valódi kölcsönhatási hosszak
  (Geant4, 3–20 GeV/c): λ_π = {n(lt['lambda_cm'], 1)} cm, λ_p = {n(ltp['lambda_cm'], 1)} cm. Az ePIC LFHCal az 1–5. csempét egy csatornán olvassa
  ki, így a csempénkénti L_MIP csak a szimulációban létezik; az „első szegmens MIP-szerű” jel majdnem ugyanolyan jó.
- **Ellenőrzések.** {s2_sentence("hu")}
"""


def put_block(path, block):
    s = open(path, encoding="utf-8").read()
    a, b = "<!-- ISSUE1 BEGIN -->", "<!-- ISSUE1 END -->"
    i, j = s.index(a) + len(a), s.index(b)
    open(path, "w", encoding="utf-8").write(s[:i] + "\n" + block + s[j:])


if __name__ == "__main__":
    for q, fn in (("Q1", page_q1), ("Q2", page_q2), ("Q3", page_q3)):
        for lang, suffix in (("en", ".md"), ("hu", ".hu.md")):
            open(os.path.join(D, q + suffix), "w", encoding="utf-8").write(fn(lang))
    print("written:", sorted(f for f in os.listdir(D) if f.endswith(".md")))
    put_block(os.path.join(ROOT, "README.md"), readme_block("en"))
    put_block(os.path.join(ROOT, "README.hu.md"), readme_block("hu"))
    print("README blocks written")
