**English** | [Magyar](formula.hu.md)

# The final formula – muon

Mass m = 0.105658 GeV; variant `full_att+all+all4`; the parameters are polynomials in the variable x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m. Fitted to the hits of the training set with a per-event likelihood (`shapelab.fit_fast`); the degree and the terms were selected on the validation set.

## In brief

- **What it is:** Minimum-ionising passage: most of the energy is in the axial term (the primary's own ionisation and the nearby delta electrons). The axial term widens with depth as multiple scattering predicts; for the LFHCal layers with the 40 mm steel front plate, the Highland formula gives ≈ 62–63 mm and an exponent of 1.35–1.41. At the end there is a Bragg rise (Bragg–Kleeman: q ≈ 0.43); the range is nearly linear in T.
- **Accuracy (test NLL, report metric, lower = better):** new formula 16.0120, the baseline × Ā fitted the same way 16.0846, the fine-tuned network 16.0034. The new formula closes 89 % of the gap between the baseline and the network (3D metric: 83 %; independent s2 sample: 90 % / 84 %).
- **Split of the energy deposited in the detector, 1 GeV → 20 GeV** (3D metric): shower 2 % → 1 %; track 91 % → 93 %; entry spike 6 % → 6 %; end-of-range blob 0.24 % → < 0.01 %; far halo 0.085 % → 0.094 %.
- **Axial term:** range R ≈ 864 mm at 1 GeV (exponent k_R ≈ 1.02); attenuation length λ_att ≈ 1211 mm; widening c ≈ 74 mm, k ≈ 1.41; Bragg exponent q ≈ 0.42.
- **Cross-section at z' = 100 mm, 1 → 20 GeV:** Gaussian narrow component σ ≈ 11 → 16 mm, Cauchy body R ≈ 10 → 295 mm, halo λ ≈ 52 mm; fractions (core / body / halo) 0.93 / 0.04 / 0.03 → 0.16 / 0.00 / 0.84.
- **98 % envelope bodies** (the smallest body that, in 98 % of the showers, contains ≥ 95 % of the energy; average of 20 bins): super-egg 37.7 L (35.8 L in the detector, coverage 0.98); drop 46.5 L (43.5 L in the detector, coverage 0.98); capsule 38.7 L (36.8 L in the detector, coverage 0.98); calibrated iso-density body 48.9 L (44.9 L in the detector, coverage 0.98).
- **Mean profiles** (independent s2 sample, separation power × 10⁻³, depth / radius, lower = better): new formula 4.19 / 1.88, network 0.31 / 2.09, old formula 5.28 / 15.92; statistical floor 0.07 / 0.08.
- **Energy of the region before the entrance (z' < 0) versus the angle of incidence** (θ ≈ 0.25 → 0.57 rad, p ≥ 2 GeV): data 1.0 → 4.2 %, new formula 2.1 → 2.3 %, network 2.1 → 2.4 %.
- **Simulation truth** (s2, in four momentum ranges of 0–20 GeV): deposition by the incoming particle itself 79–91 %, by the daughters of neutrons 0–1 %; energy arriving after 100 ns (left out of the fit) 0.0–1.7 %. The region r ≥ 300 mm holds 0.05–0.09 % of the energy (0.06–0.07 % in the model); of this, 2–20 % comes from neutrons, 11–36 % is electromagnetic and 72–96 % is prompt (< 5 ns); in the model, the far halo term carries 89–91 % of it.
- **Angle-dependent extension – not a model prediction.** The angle of incidence is given per event as an input, and 7 entrance parameters (entry spike, shower and axial-term start) may vary linearly with the angle: P + β·(1/cosθ − 1.1). The β values were fitted to the data (an empirical correction, not predicted by the physics of the formula); all other numbers on this card come from the angle-free formula. 3D test NLL: 16.0144 → 15.9690 (s2: -0.0454 ± 0.0005 nat/event). Energy before the entrance (θ ≈ 0.25 → 0.57 rad): data 1.0 → 4.2 %, final formula 2.1 → 2.3 %, angle-dependent 1.0 → 2.5 %. For the muon, the fit rearranges the terms, which then have no physical interpretation.
- **Shower-to-shower fluctuation** (PCA on the per-event profiles): the first 3 principal components explain 73–78 % of the variance. Separation power of the per-event quantities (× 10⁻³, floor from two half-samples: 3–15): any mean model 923 (binning constant), 3 principal components with Gaussian coefficients 137–196, 10 principal components with coefficients drawn from the training set 52–76.

## The formula

ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H — each term is normalised separately on the (z', r) grid (σ(·) = logistic function; terms not switched on for this particle are omitted; the subscripts are the Hungarian term names: zápor = shower, tengelytag = axial term (formerly “track”), csúcs = entry spike, folt = end-of-range blob, távoli = far halo):

- **Shower** S = L(z')·T(r | z'). Plateau depth profile: L ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ z'/1 m); gamma: L ∝ s^(α−1)·e^(−(α−1) s/t_max), s ≈ z' − z0. Cross-section: T = f1·e^(−r²/2σ²)/(2πσ²) + f2·R²/(π(r² + R²)²) + f3·e^(−r/λ)/(2πλ(r + 1 mm)); ln σ, ln R, ln λ and the mixing logits are linear in depth (σ and the logits also with a quadratic term when “curvature” is switched on); at every depth normalised on the disc r < 700 mm.
- **Axial term** U ∝ σ((z' − z_t0)/4 mm)·σ((R(T) − z')/w_R)·e^(−κ_t z'/R)·e^(−z'/λ_att)·(1 − z'/R + 0.03)^(−q) × [(1 − f)·Gauss(r; σ(z')) + f·e^(−r/l)/(2πl(r + 1 mm))], where R(T) = R1·T^(k_R) − R0 (range), w_R = w·R + 3 mm, σ(z')² = σ0² + (c·(z'/1 m)^k / βp)² (multiple scattering), βp = (T² + 2Tm)/(T + m).
- **Entry spike**: D ∝ e^(−(z' − z_sp)²/2σ_z²)·e^(−r²/2σ_r²); **end-of-range blob**: E ∝ e^(−(z' − R(T))²/2σ_ez²)·e^(−r²/2σ_er²); **far halo**: H ∝ σ(z'/10 mm)·e^(−z'/L)·e^(−r/R)/(r + 10 mm).
- **Weights**: w_távoli = σ(a_far), w_folt = σ(a_end)·(1 − w_távoli); the shower, the axial term and the entry spike share the remainder (the entry spike is tied to the axial term: f1 = d1/(d1 + L_t), where L_t is the length of the axial term).
- Every raw parameter is P(x) = Σ c_k x^k, x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m; “log_” = logarithm of the quantity, “logit_” = logit of a fraction.

Terms: shower (gamma depth profile × [Gaussian narrow component + Cauchy body + e^(−r/λ)/r halo]) + axial term (range, attenuation) + entry spike + far halo + end-of-range blob + multiple scattering (widening of the axial term) + delta-electron halo around the axial term + Bragg rise + quadratic depth terms in the cross-section.

## How to read the tables

- Columns: the momentum p [GeV]; each row is the value of one fitted quantity at that momentum.
- **w …**: weight of the component in the uncut body of revolution. **in-detector: …**: share of the component in the energy deposited in the detector (behind the tilted entrance face) – this is the physically meaningful energy share.
- **z_s, w1, ℓ, w2, κ** (plateau) or **z0, t_max, α−1** (gamma): depth profile of the shower. **σ core, R Cauchy, λ halo** and **f core / body / halo**: widths and fractions of the three cross-section terms at the given depth.
- **R(T)**: length of the axial term (range); **σ0**: its width at the entrance; **c_ms, k_ms**: widening due to multiple scattering; **λ_att**: attenuation length; **f, l delta halo**: fraction and length of the halo around the axial term; **q Bragg**: exponent of the Bragg rise; **entry spike …, end-of-range blob …**: position and width of the two Gaussians; **far halo L, R**: depth and radial length (R → ∞: no radial cut-off).
- There are two fits: the **3D metric** (normalised per event to the detector slab; it describes the body of revolution) and the **report metric** (× Ā; the r95 and iso-density shapes are computed from it). Their values differ slightly.

## 3D metric (normalised per event to the detector slab) – this is the body of revolution

Degree n = 6, 129 parameters; v0 = -0.6642, vs = 3.6546. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.405 | 0.9 | 1.9 | 4.9 | 9.89 | 19.9 |
| w shower | 0.0449 | 0.0681 | 0.08 | 0.0659 | 0.0383 | 0.0142 |
| w track | 0.791 | 0.819 | 0.814 | 0.818 | 0.833 | 0.844 |
| w entry spike | 0.156 | 0.11 | 0.104 | 0.115 | 0.128 | 0.141 |
| w end-of-range blob | 0.00761 | 0.00217 | 0.000515 | 4.27e-05 | 3.14e-06 | 8.6e-08 |
| w far halo | 0.000983 | 0.000859 | 0.000843 | 0.000928 | 0.000999 | 0.000922 |
| in-detector: shower | 0.000801 | 0.0242 | 0.0698 | 0.0611 | 0.0359 | 0.0139 |
| in-detector: track | 0.891 | 0.909 | 0.872 | 0.88 | 0.903 | 0.925 |
| in-detector: entry spike | 0.0984 | 0.0638 | 0.0574 | 0.0579 | 0.0596 | 0.0597 |
| in-detector: end-of-range blob | 0.00857 | 0.00239 | 0.000114 | 8.84e-06 | 6.56e-07 | 1.81e-08 |
| in-detector: far halo | 0.00099 | 0.000852 | 0.000844 | 0.00093 | 0.00101 | 0.000942 |
| z0 [mm] | -44.8 | -48.6 | -52 | -57.1 | -62.5 | -71 |
| t_max [mm] | 2.23 | 5.36 | 17 | 90.9 | 234 | 240 |
| α−1 | 0.248 | 0.0747 | 0.0243 | 0.00916 | 0.0107 | 0.0508 |
| σ core, z'=100 [mm] | 10.5 | 11.2 | 11.5 | 11.7 | 12.6 | 16 |
| R Cauchy, z'=100 [mm] | 9.75 | 9.51 | 10.3 | 16.6 | 42.7 | 295 |
| λ halo, z'=100 [mm] | 52.4 | 52.3 | 52 | 51.4 | 50.7 | 50 |
| f core / body / halo, z'=100 | 0.94 / 0.03 / 0.02 | 0.93 / 0.04 / 0.03 | 0.91 / 0.04 / 0.05 | 0.81 / 0.03 / 0.17 | 0.57 / 0.01 / 0.43 | 0.16 / 0.00 / 0.84 |
| σ core, z'=600 [mm] | 13.3 | 14 | 14.3 | 14.4 | 15.4 | 19.5 |
| R Cauchy, z'=600 [mm] | 9.33 | 7.18 | 5.39 | 4.41 | 5.92 | 18.9 |
| λ halo, z'=600 [mm] | 61.5 | 60.5 | 58.4 | 54.3 | 50.5 | 46.2 |
| f core / body / halo, z'=600 | 0.97 / 0.01 / 0.02 | 0.96 / 0.01 / 0.03 | 0.94 / 0.00 / 0.06 | 0.83 / 0.00 / 0.17 | 0.54 / 0.00 / 0.46 | 0.12 / 0.00 / 0.88 |
| R(T) range [mm] | 335 | 864 | 1951 | 5287 | 1.1e+04 | 2.25e+04 |
| σ0 tengelytag [mm] | 15 | 15 | 15 | 15 | 15 | 15 |
| λ_att [mm] | 1211 | 1211 | 1211 | 1211 | 1211 | 1211 |
| c_ms [mm] | 74.4 | 74.4 | 74.4 | 74.4 | 74.4 | 74.4 |
| k_ms | 1.41 | 1.41 | 1.41 | 1.41 | 1.41 | 1.41 |
| f delta halo | 0.0109 | 0.00899 | 0.00806 | 0.0079 | 0.00902 | 0.013 |
| l delta halo [mm] | 51.4 | 51.4 | 51.4 | 51.4 | 51.4 | 51.4 |
| q Bragg | 0.42 | 0.42 | 0.42 | 0.42 | 0.42 | 0.42 |
| entry spike z [mm] | -8.21 | -9.95 | -12 | -15.2 | -18 | -21.1 |
| entry spike σ_z [mm] | 19.8 | 23 | 25.5 | 27.8 | 28.7 | 28.7 |
| entry spike σ_r [mm] | 9.34 | 9.2 | 9.13 | 9.1 | 9.13 | 9.21 |
| end-of-range blob σ_z [mm] | 73.1 | 73.1 | 73.1 | 73.1 | 73.1 | 73.1 |
| end-of-range blob σ_r [mm] | 85.6 | 85.6 | 85.6 | 85.6 | 85.6 | 85.6 |
| far halo L [mm] | 1309 | 1309 | 1309 | 1309 | 1309 | 1309 |
| far halo R [mm] | 2.93e+08 | 2.93e+08 | 2.93e+08 | 2.93e+08 | 2.93e+08 | 2.93e+08 |

Coefficients: `formula_coefficients_slab.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).

## Report metric (× Ā; the r95 and iso-density shapes are computed from it)

Degree n = 6, 129 parameters; v0 = -0.6642, vs = 3.6546. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.405 | 0.9 | 1.9 | 4.9 | 9.89 | 19.9 |
| w shower | 0.029 | 0.0555 | 0.0836 | 0.0979 | 0.0757 | 0.0328 |
| w track | 0.872 | 0.884 | 0.867 | 0.856 | 0.878 | 0.92 |
| w entry spike | 0.0876 | 0.0555 | 0.0473 | 0.0445 | 0.0454 | 0.0465 |
| w end-of-range blob | 0.0101 | 0.00338 | 0.00112 | 0.000182 | 2.66e-05 | 1.65e-06 |
| w far halo | 0.00138 | 0.00108 | 0.000972 | 0.001 | 0.00107 | 0.00103 |
| in-detector: shower | 0.000132 | 0.0132 | 0.0734 | 0.0867 | 0.0675 | 0.0301 |
| in-detector: track | 0.899 | 0.925 | 0.876 | 0.866 | 0.884 | 0.921 |
| in-detector: entry spike | 0.0891 | 0.0574 | 0.0494 | 0.0464 | 0.0472 | 0.0481 |
| in-detector: end-of-range blob | 0.0104 | 0.00352 | 0.000224 | 3.47e-05 | 5.05e-06 | 3.12e-07 |
| in-detector: far halo | 0.00127 | 0.00101 | 0.000919 | 0.000943 | 0.00101 | 0.000964 |
| z0 [mm] | -39.8 | -43.1 | -46.7 | -53.1 | -61 | -73.9 |
| t_max [mm] | 0.765 | 3.55 | 45 | 1.27e+04 | 1.73e+07 | 2.17e+12 |
| α−1 | 0.249 | 0.0693 | 0.0292 | 0.0198 | 0.0311 | 0.108 |
| σ core, z'=100 [mm] | 11 | 11.4 | 11.5 | 11.6 | 12.4 | 15.1 |
| R Cauchy, z'=100 [mm] | 23.9 | 9.49 | 5.49 | 5.77 | 16.3 | 209 |
| λ halo, z'=100 [mm] | 50.8 | 50.6 | 50.3 | 49.7 | 49.2 | 48.5 |
| f core / body / halo, z'=100 | 0.87 / 0.11 / 0.02 | 0.88 / 0.09 / 0.03 | 0.88 / 0.06 / 0.06 | 0.84 / 0.02 / 0.14 | 0.75 / 0.00 / 0.25 | 0.47 / 0.00 / 0.53 |
| σ core, z'=600 [mm] | 14.7 | 15.1 | 15.1 | 15.1 | 15.9 | 19.1 |
| R Cauchy, z'=600 [mm] | 4.59 | 1.42 | 0.537 | 0.251 | 0.318 | 1.56 |
| λ halo, z'=600 [mm] | 59.9 | 58.4 | 56.2 | 52.4 | 49 | 45.2 |
| f core / body / halo, z'=600 | 0.94 / 0.00 / 0.06 | 0.93 / 0.00 / 0.06 | 0.92 / 0.00 / 0.08 | 0.86 / 0.00 / 0.14 | 0.71 / 0.00 / 0.29 | 0.35 / 0.00 / 0.65 |
| R(T) range [mm] | 329 | 852 | 1930 | 5253 | 1.09e+04 | 2.25e+04 |
| σ0 tengelytag [mm] | 14.9 | 14.9 | 14.9 | 14.9 | 14.9 | 14.9 |
| λ_att [mm] | 1353 | 1353 | 1353 | 1353 | 1353 | 1353 |
| c_ms [mm] | 75.2 | 75.2 | 75.2 | 75.2 | 75.2 | 75.2 |
| k_ms | 1.42 | 1.42 | 1.42 | 1.42 | 1.42 | 1.42 |
| f delta halo | 0.0084 | 0.00762 | 0.00721 | 0.00701 | 0.00721 | 0.0083 |
| l delta halo [mm] | 52.9 | 52.9 | 52.9 | 52.9 | 52.9 | 52.9 |
| q Bragg | 0.546 | 0.546 | 0.546 | 0.546 | 0.546 | 0.546 |
| entry spike z [mm] | 5.94 | 6.05 | 6.1 | 6.11 | 6.07 | 6 |
| entry spike σ_z [mm] | 4.19 | 5.13 | 5.65 | 5.61 | 5.08 | 4.26 |
| entry spike σ_r [mm] | 9.66 | 9.54 | 9.47 | 9.44 | 9.46 | 9.51 |
| end-of-range blob σ_z [mm] | 63.4 | 63.4 | 63.4 | 63.4 | 63.4 | 63.4 |
| end-of-range blob σ_r [mm] | 70.8 | 70.8 | 70.8 | 70.8 | 70.8 | 70.8 |
| far halo L [mm] | 1456 | 1456 | 1456 | 1456 | 1456 | 1456 |
| far halo R [mm] | 2.8e+08 | 2.8e+08 | 2.8e+08 | 2.8e+08 | 2.8e+08 | 2.8e+08 |

Coefficients: `formula_coefficients_std.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).
