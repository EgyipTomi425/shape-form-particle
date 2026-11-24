"""Rough cross-checks quoted on the Q2 and Q3 pages, from first principles and PDG constants (not fitted to the simulation):

1. the CSDA range of a 1 GeV/c proton in iron (Bethe formula, without shell and density corrections, which change the range at this
   energy by about a per cent), compared with the nuclear interaction length of iron: if the two are about equal, roughly e^-1 of the
   protons come to rest before an inelastic interaction;
2. the Molière radius of the layer stack (15.2 mm steel taken as iron + 4 mm polystyrene of 1.032 g/cm3 per 20.5 mm pitch; the
   remaining 1.3 mm taken as air and neglected), 1/R_M = sum_j w_j / R_M,j with the mass fractions w_j;
3. the share of hadrons that interact in the 40.4 mm of steel in front of the first tile, 1 - <exp(-40.4 mm / (lambda cos theta))>, with
   the interaction lengths of iron and the simulated angles (fiducial s1 events, 1-20 GeV/c);

each next to the simulation truth it is compared with. Constants: PDG, Atomic and nuclear properties of materials, iron (Fe):
density 7.874 g/cm3, mean excitation energy 286.0 eV, nuclear interaction length 132.1 g/cm2 = 16.77 cm, pion interaction length
160.7 g/cm2 = 20.41 cm, Molière radius 13.53 g/cm2 (https://pdg.lbl.gov/2024/AtomicNuclearProperties/HTML/iron_Fe.html); polystyrene:
Molière radius 9.97 g/cm2 (https://pdg.lbl.gov/2024/AtomicNuclearProperties/HTML/polystyrene.html).
    python scripts/core_mip_estimates.py      -> results/core_mip/estimates.json"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import core_mip as cm  # noqa: E402
from core_mip_analysis import ANS  # noqa: E402

RHO_FE, I_FE, ZA_FE = 7.874, 286.0e-6, 26.0 / 55.845            # g/cm3, MeV, Z/A
LAMBDA_FE = {"proton": 16.77, "pion": 20.41}                     # cm
ME, MP, K = 0.51099895, 938.272, 0.307075                        # MeV, MeV, MeV cm2/mol
FRONT_STEEL = 4.04                                                # cm of steel in front of the first tile
BINS = [1.0, 2.0, 3.0, 5.0, 10.0, 20.0]
RM_FE, RM_PS, RHO_PS = 13.53, 9.97, 1.032                       # g/cm2, g/cm2, g/cm3
STEEL, TILE, PITCH = 1.52, 0.40, 2.05                           # cm per layer


def moliere_radius_mm():
    m_fe, m_ps = STEEL * RHO_FE, TILE * RHO_PS                    # g/cm2 per layer
    w_fe, w_ps = m_fe / (m_fe + m_ps), m_ps / (m_fe + m_ps)
    rm = 1.0 / (w_fe / RM_FE + w_ps / RM_PS)                       # g/cm2
    return float(10.0 * rm / ((m_fe + m_ps) / PITCH))


def dedx(t):
    """Bethe stopping power of iron for protons of kinetic energy t [MeV], MeV cm2/g (no shell or density correction)."""
    g = 1.0 + t / MP
    b2 = 1.0 - 1.0 / g ** 2
    bg2 = b2 * g * g
    tmax = 2.0 * ME * bg2 / (1.0 + 2.0 * g * ME / MP + (ME / MP) ** 2)
    return K * ZA_FE / b2 * (0.5 * np.log(2.0 * ME * bg2 * tmax / I_FE ** 2) - b2)


def proton_range(p_mev=1000.0):
    t0 = np.hypot(p_mev, MP) - MP
    t = np.linspace(1.0, t0, 200001)                             # below 1 MeV the range adds about 0.003 g/cm2
    y = 1.0 / dedx(t)
    r = float(np.sum((y[1:] + y[:-1]) * np.diff(t)) / 2.0)        # g/cm2
    return t0, r


def main():
    t0, r = proton_range()
    out = {"proton_1gev": {"kinetic_energy_mev": t0, "range_g_cm2": r, "range_cm_iron": r / RHO_FE,
                           "lambda_I_cm_iron": LAMBDA_FE["proton"],
                           "survival_estimate": float(np.exp(-r / RHO_FE / LAMBDA_FE["proton"]))}}
    f = pd.read_parquet(os.path.join(cm.FEAT, "proton.parquet"), columns=["p", "fiducial", "true_end", "L_true"])
    s = f[f.fiducial & (f.p >= 0.9) & (f.p < 1.1)]
    st = s[s.true_end == "stops"]
    out["proton_1gev"].update({"n_events": int(len(s)), "truth_shares": s.true_end.value_counts(normalize=True).round(4).to_dict(),
                               "truth_stop_depth_median_cm": float(st.L_true.median()),
                               "truth_stop_depth_quartiles_cm": [float(st.L_true.quantile(.25)), float(st.L_true.quantile(.75))]})
    out["moliere_radius_stack_mm"] = moliere_radius_mm()
    out["front_steel"] = {}
    for part, lam in LAMBDA_FE.items():
        g = pd.read_parquet(os.path.join(cm.FEAT, f"{part}.parquet"), columns=["p", "fiducial", "theta", "k_last_true"])
        g = g[g.fiducial & (g.p >= BINS[0]) & (g.p < BINS[-1])]
        est = float(1.0 - np.exp(-FRONT_STEEL / (lam * np.cos(g.theta.values))).mean())
        b = pd.cut(g.p, BINS, right=False)
        truth = (g.k_last_true < 0).groupby(b, observed=True).mean()
        out["front_steel"][part] = {"lambda_cm_iron": lam, "estimate": est,
                                    "truth_no_primary_cell": {f"{iv.left:g}-{iv.right:g}": float(v) for iv, v in truth.items()}}
    path = os.path.join(ANS, "estimates.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    p = out["proton_1gev"]
    print(f"1 GeV/c proton: T = {p['kinetic_energy_mev']:.0f} MeV, range in iron {p['range_cm_iron']:.1f} cm, lambda_I {p['lambda_I_cm_iron']} cm,"
          f" e^(-R/lambda) = {p['survival_estimate']:.2f}; simulation: {p['truth_shares']}")
    for part, d in out["front_steel"].items():
        print(f"front steel, {part}: estimate {d['estimate']:.3f}; simulation {d['truth_no_primary_cell']}")
    print(f"Molière radius of the layer stack: {out['moliere_radius_stack_mm']:.1f} mm")
    print("written", path)


if __name__ == "__main__":
    main()
