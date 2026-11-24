**English** | [Magyar](formula.hu.md)

# The final formula – pion

Mass m = 0.13957 GeV; variant `plateau_track+all+all4`; the parameters are polynomials in the variable x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m. Fitted to the hits of the training set with a per-event likelihood (`shapelab.fit_fast`); the degree and the terms were selected on the validation set.

## In brief

- **What it is:** Like the proton: an axial term up to the first nuclear interaction, then a hadronic shower. The attenuation length is ≈ 1.31 λ_π, longer than that of the proton, as is the interaction length of the pion. The parameters of the axial term's extra terms are effective.
- **Accuracy (test NLL, report metric, lower = better):** new formula 18.1235, the baseline × Ā fitted the same way 18.1420, the fine-tuned network 18.1208. The new formula closes 88 % of the gap between the baseline and the network (3D metric: 63 %; independent s2 sample: 90 % / 69 %).
- **Split of the energy deposited in the detector, 1 GeV → 20 GeV** (3D metric): shower 43 % → 68 %; track 43 % → 29 %; entry spike 13 % → 3 %; end-of-range blob 0.07 % → < 0.01 %; far halo 0.52 % → 0.011 %.
- **Axial term:** range R ≈ 772 mm at 1 GeV (exponent k_R ≈ 1.26); attenuation length λ_att ≈ 339 mm; widening c ≈ 135 mm, k ≈ 1.72; Bragg exponent q ≈ 0.53.
- **Cross-section at z' = 100 mm, 1 → 20 GeV:** Gaussian narrow component σ ≈ 68 → 59 mm, Cauchy body R ≈ 96 → 68 mm, halo λ ≈ 216 mm; fractions (core / body / halo) 0.27 / 0.66 / 0.07 → 0.12 / 0.72 / 0.16.
- **98 % envelope bodies** (the smallest body that, in 98 % of the showers, contains ≥ 95 % of the energy; average of 20 bins): super-egg 1423 L (1302 L in the detector, coverage 0.98); drop 1478 L (1335 L in the detector, coverage 0.98); calibrated iso-density body 1491 L (1368 L in the detector, coverage 0.98).
- **Mean profiles** (independent s2 sample, separation power × 10⁻³, depth / radius, lower = better): new formula 0.77 / 0.98, network 1.79 / 0.75, old formula 2.25 / 1.06; statistical floor 0.17 / 0.05. The 3D network of the pion is degenerate (its mass lies practically outside the detector slab); its values are not reliable.
- **Energy of the region before the entrance (z' < 0) versus the angle of incidence** (θ ≈ 0.25 → 0.57 rad, p ≥ 2 GeV): data 1.4 → 4.1 %, new formula 2.3 → 3.0 %, network 2.2 → 7.2 %.
- **Simulation truth** (s2, in four momentum ranges of 0–20 GeV): deposition by the incoming particle itself 5–26 %, by the daughters of neutrons 11–16 %; energy arriving after 100 ns (left out of the fit) 2.7–5.1 %. The region r ≥ 300 mm holds 4.11–6.41 % of the energy (4.36–6.51 % in the model); of this, 45–60 % comes from neutrons, 22–34 % is electromagnetic and 55–62 % is prompt (< 5 ns); in the model, the far halo term carries 0–7 % of it.
- **Angle-dependent extension – not a model prediction.** The angle of incidence is given per event as an input, and 8 entrance parameters (entry spike, shower and axial-term start) may vary linearly with the angle: P + β·(1/cosθ − 1.1). The β values were fitted to the data (an empirical correction, not predicted by the physics of the formula); all other numbers on this card come from the angle-free formula. 3D test NLL: 18.1014 → 18.0928 (s2: -0.0090 ± 0.0002 nat/event). Energy before the entrance (θ ≈ 0.25 → 0.57 rad): data 1.4 → 4.1 %, final formula 2.3 → 3.0 %, angle-dependent 1.7 → 3.6 %.
- **Separated in time** (per cell: a cell is prompt if it is first hit within < 5 ns of the event's first hit, delayed if it is first hit later; the delayed fraction is therefore a lower bound): the delayed cells carry on average 6.3–8.3 % of the energy per event. At 5–20 GeV, mean radius / r90 (model): prompt 85–87 / 183–205 mm, delayed 231–252 / 476–508 mm; halo length at z' = 100 mm: prompt 155–156 mm, delayed 577–598 mm.
- **Shower-to-shower fluctuation** (PCA on the per-event profiles): the first 3 principal components explain 42–54 % of the variance. Separation power of the per-event quantities (× 10⁻³, floor from two half-samples: 3–14): any mean model 923 (binning constant), 3 principal components with Gaussian coefficients 154–278, 10 principal components with coefficients drawn from the training set 39–97.

## The formula

ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H — each term is normalised separately on the (z', r) grid (σ(·) = logistic function; terms not switched on for this particle are omitted; the subscripts are the Hungarian term names: zápor = shower, tengelytag = axial term (formerly “track”), csúcs = entry spike, folt = end-of-range blob, távoli = far halo):

- **Shower** S = L(z')·T(r | z'). Plateau depth profile: L ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ z'/1 m); gamma: L ∝ s^(α−1)·e^(−(α−1) s/t_max), s ≈ z' − z0. Cross-section: T = f1·e^(−r²/2σ²)/(2πσ²) + f2·R²/(π(r² + R²)²) + f3·e^(−r/λ)/(2πλ(r + 1 mm)); ln σ, ln R, ln λ and the mixing logits are linear in depth (σ and the logits also with a quadratic term when “curvature” is switched on); at every depth normalised on the disc r < 700 mm.
- **Axial term** U ∝ σ((z' − z_t0)/4 mm)·σ((R(T) − z')/w_R)·e^(−κ_t z'/R)·e^(−z'/λ_att)·(1 − z'/R + 0.03)^(−q) × [(1 − f)·Gauss(r; σ(z')) + f·e^(−r/l)/(2πl(r + 1 mm))], where R(T) = R1·T^(k_R) − R0 (range), w_R = w·R + 3 mm, σ(z')² = σ0² + (c·(z'/1 m)^k / βp)² (multiple scattering), βp = (T² + 2Tm)/(T + m).
- **Entry spike**: D ∝ e^(−(z' − z_sp)²/2σ_z²)·e^(−r²/2σ_r²); **end-of-range blob**: E ∝ e^(−(z' − R(T))²/2σ_ez²)·e^(−r²/2σ_er²); **far halo**: H ∝ σ(z'/10 mm)·e^(−z'/L)·e^(−r/R)/(r + 10 mm).
- **Weights**: w_távoli = σ(a_far), w_folt = σ(a_end)·(1 − w_távoli); the shower, the axial term and the entry spike share the remainder (the entry spike is tied to the axial term: f1 = d1/(d1 + L_t), where L_t is the length of the axial term).
- Every raw parameter is P(x) = Σ c_k x^k, x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m; “log_” = logarithm of the quantity, “logit_” = logit of a fraction.

Terms: shower (plateau depth profile × [Gaussian narrow component + Cauchy body + e^(−r/λ)/r halo]) + axial term (range, attenuation) + entry spike + far halo + end-of-range blob + multiple scattering (widening of the axial term) + delta-electron halo around the axial term + Bragg rise + quadratic depth terms in the cross-section.

## How to read the tables

- Columns: the momentum p [GeV]; each row is the value of one fitted quantity at that momentum.
- **w …**: weight of the component in the uncut body of revolution. **in-detector: …**: share of the component in the energy deposited in the detector (behind the tilted entrance face) – this is the physically meaningful energy share.
- **z_s, w1, ℓ, w2, κ** (plateau) or **z0, t_max, α−1** (gamma): depth profile of the shower. **σ core, R Cauchy, λ halo** and **f core / body / halo**: widths and fractions of the three cross-section terms at the given depth.
- **R(T)**: length of the axial term (range); **σ0**: its width at the entrance; **c_ms, k_ms**: widening due to multiple scattering; **λ_att**: attenuation length; **f, l delta halo**: fraction and length of the halo around the axial term; **q Bragg**: exponent of the Bragg rise; **entry spike …, end-of-range blob …**: position and width of the two Gaussians; **far halo L, R**: depth and radial length (R → ∞: no radial cut-off).
- There are two fits: the **3D metric** (normalised per event to the detector slab; it describes the body of revolution) and the **report metric** (× Ā; the r95 and iso-density shapes are computed from it). Their values differ slightly.

## 3D metric (normalised per event to the detector slab) – this is the body of revolution

Degree n = 3, 101 parameters; v0 = -0.3259, vs = 3.3146. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.38 | 0.87 | 1.87 | 4.86 | 9.86 | 19.9 |
| w shower | 0.339 | 0.506 | 0.615 | 0.688 | 0.702 | 0.682 |
| w track | 0.383 | 0.324 | 0.267 | 0.235 | 0.24 | 0.272 |
| w entry spike | 0.27 | 0.165 | 0.115 | 0.0755 | 0.0576 | 0.0462 |
| w end-of-range blob | 0.00422 | 0.000528 | 8e-05 | 9.1e-06 | 2.34e-06 | 8.22e-07 |
| w far halo | 0.00434 | 0.00435 | 0.00359 | 0.00171 | 0.000589 | 0.000117 |
| in-detector: shower | 0.219 | 0.43 | 0.583 | 0.681 | 0.702 | 0.685 |
| in-detector: track | 0.533 | 0.43 | 0.329 | 0.267 | 0.263 | 0.289 |
| in-detector: entry spike | 0.237 | 0.134 | 0.084 | 0.0493 | 0.0351 | 0.0264 |
| in-detector: end-of-range blob | 0.0058 | 0.000701 | 2.28e-05 | 2.13e-06 | 5.27e-07 | 1.8e-07 |
| in-detector: far halo | 0.00544 | 0.0052 | 0.004 | 0.00176 | 0.000583 | 0.000112 |
| z_s [mm] | 2.12 | 12.8 | 25.1 | 44.8 | 63.1 | 84.7 |
| w1 [mm] | 132 | 111 | 95.7 | 80.8 | 72.6 | 66.6 |
| ℓ [mm] | 37 | 56.9 | 96 | 224 | 488 | 1207 |
| w2 [mm] | 94.6 | 167 | 266 | 423 | 533 | 596 |
| κ [1/m] | -2 | -1.99 | -1.99 | -2 | -2.01 | -2.03 |
| σ core, z'=100 [mm] | 61.4 | 68 | 71.9 | 71.9 | 67.4 | 59.1 |
| R Cauchy, z'=100 [mm] | 118 | 96.3 | 80.1 | 67.5 | 64.5 | 67.8 |
| λ halo, z'=100 [mm] | 220 | 216 | 211 | 206 | 201 | 196 |
| f core / body / halo, z'=100 | 0.43 / 0.52 / 0.05 | 0.27 / 0.66 / 0.07 | 0.18 / 0.74 / 0.09 | 0.13 / 0.77 / 0.11 | 0.11 / 0.76 / 0.13 | 0.12 / 0.72 / 0.16 |
| σ core, z'=600 [mm] | 139 | 168 | 188 | 194 | 180 | 152 |
| R Cauchy, z'=600 [mm] | 403 | 259 | 174 | 113 | 89.1 | 77.7 |
| λ halo, z'=600 [mm] | 596 | 532 | 472 | 400 | 349 | 302 |
| f core / body / halo, z'=600 | 0.06 / 0.85 / 0.09 | 0.04 / 0.87 / 0.09 | 0.03 / 0.87 / 0.10 | 0.04 / 0.85 / 0.12 | 0.06 / 0.80 / 0.14 | 0.12 / 0.71 / 0.18 |
| R(T) range [mm] | 254 | 772 | 2064 | 6980 | 1.71e+04 | 4.14e+04 |
| σ0 tengelytag [mm] | 20.1 | 20.1 | 20.1 | 20.1 | 20.1 | 20.1 |
| λ_att [mm] | 339 | 339 | 339 | 339 | 339 | 339 |
| c_ms [mm] | 135 | 135 | 135 | 135 | 135 | 135 |
| k_ms | 1.72 | 1.72 | 1.72 | 1.72 | 1.72 | 1.72 |
| f delta halo | 0.125 | 0.163 | 0.187 | 0.193 | 0.178 | 0.149 |
| l delta halo [mm] | 69.4 | 69.4 | 69.4 | 69.4 | 69.4 | 69.4 |
| q Bragg | 0.526 | 0.526 | 0.526 | 0.526 | 0.526 | 0.526 |
| entry spike z [mm] | -4.85 | -5.3 | -5.94 | -7.04 | -8.07 | -9.26 |
| entry spike σ_z [mm] | 18.4 | 20.8 | 22.6 | 23.9 | 24 | 23.5 |
| entry spike σ_r [mm] | 10.6 | 11.1 | 11.4 | 11.6 | 11.6 | 11.4 |
| end-of-range blob σ_z [mm] | 103 | 103 | 103 | 103 | 103 | 103 |
| end-of-range blob σ_r [mm] | 130 | 130 | 130 | 130 | 130 | 130 |
| far halo L [mm] | 701 | 701 | 701 | 701 | 701 | 701 |
| far halo R [mm] | 8.7e+05 | 8.7e+05 | 8.7e+05 | 8.7e+05 | 8.7e+05 | 8.7e+05 |

Coefficients: `formula_coefficients_slab.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).

## Report metric (× Ā; the r95 and iso-density shapes are computed from it)

Degree n = 3, 101 parameters; v0 = -0.3259, vs = 3.3146. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.38 | 0.87 | 1.87 | 4.86 | 9.86 | 19.9 |
| w shower | 0.325 | 0.484 | 0.594 | 0.683 | 0.722 | 0.748 |
| w track | 0.485 | 0.411 | 0.333 | 0.267 | 0.238 | 0.22 |
| w entry spike | 0.178 | 0.097 | 0.0632 | 0.0388 | 0.0277 | 0.0204 |
| w end-of-range blob | 0.00558 | 0.000763 | 0.000133 | 1.9e-05 | 5.87e-06 | 2.44e-06 |
| w far halo | 0.00527 | 0.0073 | 0.00925 | 0.0113 | 0.012 | 0.0118 |
| in-detector: shower | 0.184 | 0.374 | 0.53 | 0.654 | 0.707 | 0.739 |
| in-detector: track | 0.591 | 0.501 | 0.388 | 0.293 | 0.253 | 0.229 |
| in-detector: entry spike | 0.213 | 0.116 | 0.0723 | 0.0418 | 0.0289 | 0.0209 |
| in-detector: end-of-range blob | 0.00671 | 0.000934 | 3.55e-05 | 4.25e-06 | 1.27e-06 | 5.16e-07 |
| in-detector: far halo | 0.00577 | 0.00801 | 0.00972 | 0.0111 | 0.0115 | 0.011 |
| z_s [mm] | 6.15 | 17.4 | 30.3 | 50.7 | 69.2 | 90.8 |
| w1 [mm] | 140 | 117 | 98.4 | 80.2 | 70 | 62.5 |
| ℓ [mm] | 25.9 | 36.2 | 59.3 | 154 | 421 | 1529 |
| w2 [mm] | 103 | 175 | 285 | 524 | 815 | 1257 |
| κ [1/m] | -1.97 | -2.04 | -2.11 | -2.19 | -2.22 | -2.22 |
| σ core, z'=100 [mm] | 63.8 | 60.3 | 57 | 50.5 | 43.2 | 34.1 |
| R Cauchy, z'=100 [mm] | 130 | 107 | 91.3 | 79.2 | 76.3 | 79.3 |
| λ halo, z'=100 [mm] | 90.7 | 89.3 | 87.5 | 84.7 | 82.3 | 79.5 |
| f core / body / halo, z'=100 | 0.39 / 0.57 / 0.04 | 0.22 / 0.73 / 0.05 | 0.12 / 0.81 / 0.07 | 0.07 / 0.84 / 0.09 | 0.06 / 0.81 / 0.13 | 0.06 / 0.76 / 0.19 |
| σ core, z'=600 [mm] | 108 | 139 | 191 | 303 | 431 | 603 |
| R Cauchy, z'=600 [mm] | 398 | 256 | 173 | 111 | 85.6 | 70.9 |
| λ halo, z'=600 [mm] | 329 | 299 | 266 | 218 | 183 | 150 |
| f core / body / halo, z'=600 | 0.12 / 0.83 / 0.05 | 0.06 / 0.88 / 0.06 | 0.03 / 0.88 / 0.09 | 0.02 / 0.82 / 0.16 | 0.02 / 0.70 / 0.28 | 0.02 / 0.51 / 0.47 |
| R(T) range [mm] | 245 | 755 | 2046 | 7035 | 1.74e+04 | 4.27e+04 |
| σ0 tengelytag [mm] | 20.1 | 20.1 | 20.1 | 20.1 | 20.1 | 20.1 |
| λ_att [mm] | 297 | 297 | 297 | 297 | 297 | 297 |
| c_ms [mm] | 117 | 117 | 117 | 117 | 117 | 117 |
| k_ms | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 |
| f delta halo | 0.144 | 0.288 | 0.363 | 0.233 | 0.0626 | 0.00488 |
| l delta halo [mm] | 78.4 | 78.4 | 78.4 | 78.4 | 78.4 | 78.4 |
| q Bragg | 0.52 | 0.52 | 0.52 | 0.52 | 0.52 | 0.52 |
| entry spike z [mm] | 5.3 | 5.43 | 5.57 | 5.75 | 5.89 | 6.04 |
| entry spike σ_z [mm] | 4.77 | 5.05 | 4.99 | 4.48 | 3.88 | 3.19 |
| entry spike σ_r [mm] | 10.6 | 11.2 | 11.5 | 11.6 | 11.5 | 11.1 |
| end-of-range blob σ_z [mm] | 99 | 99 | 99 | 99 | 99 | 99 |
| end-of-range blob σ_r [mm] | 125 | 125 | 125 | 125 | 125 | 125 |
| far halo L [mm] | 1236 | 1236 | 1236 | 1236 | 1236 | 1236 |
| far halo R [mm] | 2.55e+05 | 2.55e+05 | 2.55e+05 | 2.55e+05 | 2.55e+05 | 2.55e+05 |

Coefficients: `formula_coefficients_std.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).
