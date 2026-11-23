**English** | [Magyar](formula.hu.md)

# The final formula – proton

Mass m = 0.938272 GeV; variant `plateau_track+all+all4`; the parameters are polynomials in the variable x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m. Fitted to the hits of the training set with a per-event likelihood (`shapelab.fit_fast`); the degree and the terms were selected on the validation set.

## In brief

- **What it is:** At low momentum a stopping proton (track + entry spike + end-of-range blob), at higher momentum a hadronic shower. At T = 0.5–1 GeV the range agrees with the CSDA range to within 4–16 % (after the front plate); the exponent k_R is global, the local CSDA exponent here is 1.3–1.6. The attenuation length is ≈ 1.26 λ_I. The widening, the delta halo and the Bragg exponent of the track are effective here: they also describe part of the core of the hadronic shower.
- **Accuracy (test NLL, report metric, lower = better):** new formula 18.1940, the baseline × Ā fitted the same way 18.2331, the fine-tuned network 18.1898. The new formula closes 90 % of the gap between the baseline and the network (3D metric: 88 %; independent s2 sample: 91 % / 89 %).
- **Split of the energy deposited in the detector, 1 GeV → 20 GeV** (3D metric): shower 15 % → 81 %; track 61 % → 17 %; entry spike 24 % → 2 %; end-of-range blob 0.67 % → < 0.01 %; far halo 0.38 % → < 0.01 %.
- **Track:** range R ≈ 135 mm at 1 GeV (exponent k_R ≈ 1.78); attenuation length λ_att ≈ 266 mm; widening c ≈ 285 mm, k ≈ 2.37; Bragg exponent q ≈ 0.80.
- **Cross-section at z' = 100 mm, 1 → 20 GeV:** Gaussian core σ ≈ 84 → 39 mm, Cauchy body R ≈ 121 → 78 mm, halo λ ≈ 227 mm; fractions (core / body / halo) 0.08 / 0.87 / 0.05 → 0.13 / 0.76 / 0.10.
- **98 % envelope bodies** (the smallest body that, in 98 % of the showers, contains ≥ 95 % of the energy; average of 20 bins): super-egg 1544 L (1395 L in the detector, coverage 0.98); drop 1600 L (1428 L in the detector, coverage 0.98); calibrated iso-density body 1596 L (1449 L in the detector, coverage 0.98).
- **Mean profiles** (independent s2 sample, separation power × 10⁻³, depth / radius, lower = better): new formula 0.53 / 2.64, network 0.25 / 2.48, old formula 3.03 / 2.82; statistical floor 0.18 / 0.07.
- **Energy of the region before the entrance (z' < 0) versus the angle of incidence** (θ ≈ 0.25 → 0.57 rad, p ≥ 2 GeV): data 1.8 → 4.7 %, new formula 2.8 → 3.8 %, network 2.7 → 3.6 %.
- **Simulation truth** (s2, in four momentum ranges of 0–20 GeV): deposition by the incoming particle itself 5–50 %, by the daughters of neutrons 18–25 %; energy arriving after 100 ns (left out of the fit) 3.3–4.3 %. The region r ≥ 300 mm holds 3.47–7.86 % of the energy (3.69–8.50 % in the model); of this, 51–75 % comes from neutrons, 18–29 % is electromagnetic and 41–60 % is prompt (< 5 ns); in the model, the far halo term carries 0–8 % of it.
- **Angle-dependent extension – not a model prediction.** The angle of incidence is given per event as an input, and 8 entrance parameters (entry spike, shower and track start) may vary linearly with the angle: P + β·(1/cosθ − 1.1). The β values were fitted to the data (an empirical correction, not predicted by the physics of the formula); all other numbers on this card come from the angle-free formula. 3D test NLL: 18.1660 → 18.1576 (s2: -0.0076 ± 0.0002 nat/event). Energy before the entrance (θ ≈ 0.25 → 0.57 rad): data 1.8 → 4.7 %, final formula 2.8 → 3.8 %, angle-dependent 2.2 → 4.0 %.
- **Separated in time** (per cell: a cell is prompt if it is first hit within < 5 ns of the event's first hit, delayed if it is first hit later; the delayed fraction is therefore a lower bound): the delayed cells carry on average 8.4–10.9 % of the energy per event. At 5–20 GeV, mean radius / r90 (model): prompt 96–97 / 205–227 mm, delayed 238–253 / 476–508 mm; halo length at z' = 100 mm: prompt 135–138 mm, delayed 410–414 mm.
- **Shower-to-shower fluctuation** (PCA on the per-event profiles): the first 3 principal components explain 40–66 % of the variance. Separation power of the per-event quantities (× 10⁻³, floor from two half-samples: 3–15): any mean model 923 (binning constant), 3 principal components with Gaussian coefficients 143–282, 10 principal components with coefficients drawn from the training set 31–127.

## The formula

ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H — each term is normalised separately on the (z', r) grid (σ(·) = logistic function; terms not switched on for this particle are omitted; the subscripts are the Hungarian term names: zápor = shower, nyom = track, csúcs = entry spike, folt = end-of-range blob, távoli = far halo):

- **Shower** S = L(z')·T(r | z'). Plateau depth profile: L ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ z'/1 m); gamma: L ∝ s^(α−1)·e^(−(α−1) s/t_max), s ≈ z' − z0. Cross-section: T = f1·e^(−r²/2σ²)/(2πσ²) + f2·R²/(π(r² + R²)²) + f3·e^(−r/λ)/(2πλ(r + 1 mm)); ln σ, ln R, ln λ and the mixing logits are linear in depth (σ and the logits also with a quadratic term when “curvature” is switched on); at every depth normalised on the disc r < 700 mm.
- **Track** U ∝ σ((z' − z_t0)/4 mm)·σ((R(T) − z')/w_R)·e^(−κ_t z'/R)·e^(−z'/λ_att)·(1 − z'/R + 0.03)^(−q) × [(1 − f)·Gauss(r; σ(z')) + f·e^(−r/l)/(2πl(r + 1 mm))], where R(T) = R1·T^(k_R) − R0 (range), w_R = w·R + 3 mm, σ(z')² = σ0² + (c·(z'/1 m)^k / βp)² (multiple scattering), βp = (T² + 2Tm)/(T + m).
- **Entry spike**: D ∝ e^(−(z' − z_sp)²/2σ_z²)·e^(−r²/2σ_r²); **end-of-range blob**: E ∝ e^(−(z' − R(T))²/2σ_ez²)·e^(−r²/2σ_er²); **far halo**: H ∝ σ(z'/10 mm)·e^(−z'/L)·e^(−r/R)/(r + 10 mm).
- **Weights**: w_távoli = σ(a_far), w_folt = σ(a_end)·(1 − w_távoli); the shower, the track and the entry spike share the remainder (the entry spike is tied to the track: f1 = d1/(d1 + L_t), where L_t is the length of the track).
- Every raw parameter is P(x) = Σ c_k x^k, x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m; “log_” = logarithm of the quantity, “logit_” = logit of a fraction.

Terms: shower (plateau depth profile × [Gaussian core + Cauchy body + e^(−r/λ)/r halo]) + track (range, attenuation) + entry spike + far halo + end-of-range blob + multiple scattering (track widening) + delta-electron halo around the track + Bragg rise + quadratic depth terms in the cross-section.

## How to read the tables

- Columns: the momentum p [GeV]; each row is the value of one fitted quantity at that momentum.
- **w …**: weight of the component in the uncut body of revolution. **in-detector: …**: share of the component in the energy deposited in the detector (behind the tilted entrance face) – this is the physically meaningful energy share.
- **z_s, w1, ℓ, w2, κ** (plateau) or **z0, t_max, α−1** (gamma): depth profile of the shower. **σ core, R Cauchy, λ halo** and **f core / body / halo**: widths and fractions of the three cross-section terms at the given depth.
- **R(T)**: length of the track (range); **σ0**: width of the track at the entrance; **c_ms, k_ms**: widening due to multiple scattering; **λ_att**: attenuation length; **f, l delta halo**: fraction and length of the halo around the track; **q Bragg**: exponent of the Bragg rise; **entry spike …, end-of-range blob …**: position and width of the two Gaussians; **far halo L, R**: depth and radial length (R → ∞: no radial cut-off).
- There are two fits: the **3D metric** (normalised per event to the detector slab; it describes the body of revolution) and the **report metric** (× Ā; the r95 and iso-density shapes are computed from it). Their values differ slightly.

## 3D metric (normalised per event to the detector slab) – this is the body of revolution

Degree n = 6, 143 parameters; v0 = -0.1055, vs = 3.0544. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.125 | 0.433 | 1.27 | 4.15 | 9.11 | 19.1 |
| w shower | 0.015 | 0.209 | 0.536 | 0.744 | 0.788 | 0.799 |
| w track | 0.000791 | 0.504 | 0.326 | 0.179 | 0.154 | 0.151 |
| w entry spike | 0.523 | 0.278 | 0.13 | 0.0729 | 0.0576 | 0.0492 |
| w end-of-range blob | 0.46 | 0.00584 | 7.88e-05 | 2.67e-06 | 6.07e-07 | 2.24e-07 |
| w far halo | 0.000635 | 0.00355 | 0.00787 | 0.00383 | 0.000411 | 4.75e-06 |
| in-detector: shower | 0.0116 | 0.149 | 0.489 | 0.736 | 0.79 | 0.811 |
| in-detector: track | 0.000979 | 0.605 | 0.398 | 0.211 | 0.177 | 0.168 |
| in-detector: entry spike | 0.568 | 0.236 | 0.104 | 0.0487 | 0.032 | 0.0212 |
| in-detector: end-of-range blob | 0.419 | 0.00671 | 9.46e-05 | 6.01e-07 | 1.33e-07 | 4.71e-08 |
| in-detector: far halo | 0.000925 | 0.00383 | 0.00866 | 0.00408 | 0.000426 | 4.75e-06 |
| z_s [mm] | -11.8 | -7.12 | 2.2 | 22.3 | 45.7 | 80.7 |
| w1 [mm] | 214 | 123 | 92.4 | 86.3 | 88 | 80.2 |
| ℓ [mm] | 51 | 132 | 331 | 863 | 1285 | 1330 |
| w2 [mm] | 205 | 198 | 298 | 378 | 249 | 76.2 |
| κ [1/m] | -3.16 | -3.02 | -2.86 | -2.72 | -2.67 | -2.65 |
| σ core, z'=100 [mm] | 190 | 84.4 | 63.7 | 58.8 | 52.8 | 38.9 |
| R Cauchy, z'=100 [mm] | 275 | 121 | 82.2 | 71 | 71.9 | 77.6 |
| λ halo, z'=100 [mm] | 246 | 227 | 215 | 207 | 204 | 203 |
| f core / body / halo, z'=100 | 0.08 / 0.89 / 0.04 | 0.08 / 0.87 / 0.05 | 0.08 / 0.84 / 0.08 | 0.08 / 0.80 / 0.13 | 0.09 / 0.78 / 0.14 | 0.13 / 0.76 / 0.10 |
| σ core, z'=600 [mm] | 651 | 360 | 320 | 342 | 333 | 262 |
| R Cauchy, z'=600 [mm] | 1340 | 424 | 213 | 131 | 104 | 89.3 |
| λ halo, z'=600 [mm] | 651 | 400 | 292 | 232 | 213 | 206 |
| f core / body / halo, z'=600 | 0.19 / 0.79 / 0.02 | 0.18 / 0.80 / 0.03 | 0.13 / 0.82 / 0.05 | 0.09 / 0.81 / 0.11 | 0.07 / 0.78 / 0.15 | 0.07 / 0.76 / 0.17 |
| R(T) range [mm] | 1.14 | 135 | 1125 | 9485 | 3.85e+04 | 1.44e+05 |
| σ0 track [mm] | 18.5 | 18.5 | 18.5 | 18.5 | 18.5 | 18.5 |
| λ_att [mm] | 266 | 266 | 266 | 266 | 266 | 266 |
| c_ms [mm] | 285 | 285 | 285 | 285 | 285 | 285 |
| k_ms | 2.37 | 2.37 | 2.37 | 2.37 | 2.37 | 2.37 |
| f delta halo | 0.000969 | 0.0394 | 0.226 | 0.334 | 0.248 | 0.204 |
| l delta halo [mm] | 81.5 | 81.5 | 81.5 | 81.5 | 81.5 | 81.5 |
| q Bragg | 0.804 | 0.804 | 0.804 | 0.804 | 0.804 | 0.804 |
| entry spike z [mm] | -6.44 | -3.17 | -3.67 | -7.75 | -12.5 | -18.5 |
| entry spike σ_z [mm] | 8.8 | 13.7 | 18.2 | 22.1 | 23.5 | 23.8 |
| entry spike σ_r [mm] | 8.93 | 10.1 | 10.9 | 11.5 | 11.6 | 11.6 |
| end-of-range blob σ_z [mm] | 76.3 | 76.3 | 76.3 | 76.3 | 76.3 | 76.3 |
| end-of-range blob σ_r [mm] | 81.1 | 81.1 | 81.1 | 81.1 | 81.1 | 81.1 |
| far halo L [mm] | 962 | 962 | 962 | 962 | 962 | 962 |
| far halo R [mm] | 5.55e+07 | 5.55e+07 | 5.55e+07 | 5.55e+07 | 5.55e+07 | 5.55e+07 |

Coefficients: `formula_coefficients_slab.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).

## Report metric (× Ā; the r95 and iso-density shapes are computed from it)

Degree n = 6, 143 parameters; v0 = -0.1055, vs = 3.0544. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.125 | 0.433 | 1.27 | 4.15 | 9.11 | 19.1 |
| w shower | 0.0175 | 0.228 | 0.545 | 0.75 | 0.795 | 0.799 |
| w track | 0.000989 | 0.541 | 0.362 | 0.206 | 0.177 | 0.181 |
| w entry spike | 0.432 | 0.221 | 0.084 | 0.0403 | 0.0278 | 0.0205 |
| w end-of-range blob | 0.55 | 0.00644 | 4.91e-05 | 5.13e-07 | 3.91e-08 | 4.45e-09 |
| w far halo | 0.000232 | 0.00368 | 0.00897 | 0.00397 | 0.000421 | 6.28e-06 |
| in-detector: shower | 0.0127 | 0.149 | 0.473 | 0.717 | 0.773 | 0.786 |
| in-detector: track | 0.00106 | 0.6 | 0.421 | 0.234 | 0.196 | 0.193 |
| in-detector: entry spike | 0.569 | 0.241 | 0.0962 | 0.0449 | 0.03 | 0.0212 |
| in-detector: end-of-range blob | 0.417 | 0.00689 | 5.61e-05 | 1.11e-07 | 8.23e-09 | 8.99e-10 |
| in-detector: far halo | 0.00028 | 0.00366 | 0.00938 | 0.00407 | 0.000421 | 6.03e-06 |
| z_s [mm] | -9.53 | 2.29 | 16.7 | 40.8 | 65.2 | 98.3 |
| w1 [mm] | 215 | 124 | 95.2 | 90.1 | 91 | 80.5 |
| ℓ [mm] | 18.6 | 48.4 | 132 | 542 | 2331 | 2.71e+04 |
| w2 [mm] | 253 | 192 | 330 | 729 | 1804 | 1.43e+04 |
| κ [1/m] | -2.6 | -2.64 | -2.69 | -2.75 | -2.73 | -2.59 |
| σ core, z'=100 [mm] | 24.8 | 34.8 | 47.1 | 56.5 | 52.4 | 42 |
| R Cauchy, z'=100 [mm] | 286 | 128 | 86.3 | 72.7 | 72.5 | 77.8 |
| λ halo, z'=100 [mm] | 264 | 244 | 232 | 222 | 218 | 216 |
| f core / body / halo, z'=100 | 0.04 / 0.95 / 0.01 | 0.07 / 0.90 / 0.03 | 0.09 / 0.85 / 0.07 | 0.09 / 0.79 / 0.12 | 0.09 / 0.78 / 0.13 | 0.12 / 0.78 / 0.10 |
| σ core, z'=600 [mm] | 119 | 200 | 298 | 370 | 339 | 261 |
| R Cauchy, z'=600 [mm] | 1587 | 466 | 221 | 129 | 102 | 88.3 |
| λ halo, z'=600 [mm] | 665 | 421 | 309 | 240 | 214 | 200 |
| f core / body / halo, z'=600 | 0.05 / 0.94 / 0.00 | 0.09 / 0.90 / 0.01 | 0.11 / 0.86 / 0.03 | 0.09 / 0.82 / 0.10 | 0.07 / 0.78 / 0.15 | 0.07 / 0.76 / 0.16 |
| R(T) range [mm] | 1.11 | 139 | 1127 | 9227 | 3.67e+04 | 1.34e+05 |
| σ0 track [mm] | 18.9 | 18.9 | 18.9 | 18.9 | 18.9 | 18.9 |
| λ_att [mm] | 249 | 249 | 249 | 249 | 249 | 249 |
| c_ms [mm] | 260 | 260 | 260 | 260 | 260 | 260 |
| k_ms | 2.3 | 2.3 | 2.3 | 2.3 | 2.3 | 2.3 |
| f delta halo | 0.00164 | 0.0497 | 0.245 | 0.362 | 0.303 | 0.292 |
| l delta halo [mm] | 77.3 | 77.3 | 77.3 | 77.3 | 77.3 | 77.3 |
| q Bragg | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 |
| entry spike z [mm] | 5.8 | 6.2 | 6.22 | 5.89 | 5.48 | 4.94 |
| entry spike σ_z [mm] | 0.753 | 2.39 | 4.5 | 6.12 | 5.98 | 4.96 |
| entry spike σ_r [mm] | 9.52 | 10.4 | 11 | 11.7 | 12 | 12.3 |
| end-of-range blob σ_z [mm] | 74.3 | 74.3 | 74.3 | 74.3 | 74.3 | 74.3 |
| end-of-range blob σ_r [mm] | 79.5 | 79.5 | 79.5 | 79.5 | 79.5 | 79.5 |
| far halo L [mm] | 1326 | 1326 | 1326 | 1326 | 1326 | 1326 |
| far halo R [mm] | 2.02e+08 | 2.02e+08 | 2.02e+08 | 2.02e+08 | 2.02e+08 | 2.02e+08 |

Coefficients: `formula_coefficients_std.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).
