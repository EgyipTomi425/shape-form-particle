**English** | [Magyar](formula.hu.md)

# The final formula – electron

Mass m = 0.000511 GeV; variant `plateau+all+curv`; the parameters are polynomials in the variable x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m. Fitted to the hits of the training set with a per-event likelihood (`shapelab.fit_fast`); the degree and the terms were selected on the validation set.

## In brief

- **What it is:** Electromagnetic shower, no track. At low momentum the entry spike is significant, at higher momentum the shower dominates. Of the additional terms, the ~1 % far halo gave the largest improvement; according to the simulation truth it is prompt electromagnetic (e±/γ) energy, not neutrons, and at 5–20 GeV the model underestimates it by ~30 %.
- **Accuracy (test NLL, report metric, lower = better):** new formula 14.8167, the baseline × Ā fitted the same way 14.8406, the fine-tuned network 14.8067. The new formula closes 70 % of the gap between the baseline and the network (3D metric: 68 %; independent s2 sample: 73 % / 71 %).
- **Split of the energy deposited in the detector, 1 GeV → 20 GeV** (3D metric): shower 82 % → 99 %; entry spike 17 % → 0.35 %; far halo 0.67 % → 0.95 %.
- **Cross-section at z' = 100 mm, 1 → 20 GeV:** Gaussian core σ ≈ 19 → 16 mm, Cauchy body R ≈ 35 → 21 mm, halo λ ≈ 40 mm; fractions (core / body / halo) 0.74 / 0.13 / 0.13 → 0.85 / 0.02 / 0.13.
- **98 % envelope bodies** (the smallest body that, in 98 % of the showers, contains ≥ 95 % of the energy; average of 20 bins): super-egg 25.9 L (24.2 L in the detector, coverage 0.98); drop 25.9 L (24.4 L in the detector, coverage 0.98); calibrated iso-density body 31.7 L (30.7 L in the detector, coverage 0.98).
- **Mean profiles** (independent s2 sample, separation power × 10⁻³, depth / radius, lower = better): new formula 0.88 / 4.97, network 0.56 / 4.55, old formula 0.76 / 6.51; statistical floor 0.16 / 0.11.
- **Energy of the region before the entrance (z' < 0) versus the angle of incidence** (θ ≈ 0.25 → 0.57 rad, p ≥ 2 GeV): data 3.0 → 6.2 %, new formula 3.9 → 4.7 %, network 4.1 → 5.3 %.
- **Simulation truth** (s2, in four momentum ranges of 0–20 GeV): deposition by the incoming particle itself 1–4 %, by the daughters of neutrons 0 %; energy arriving after 100 ns (left out of the fit) 0.0–0.1 %. The region r ≥ 300 mm holds 0.56–0.91 % of the energy (0.56–0.65 % in the model); of this, 1–2 % comes from neutrons, 96–98 % is electromagnetic and 99 % is prompt (< 5 ns); in the model, the far halo term carries 67–86 % of it.
- **Angle-dependent extension – not a model prediction.** The angle of incidence is given per event as an input, and 6 entrance parameters (entry spike, shower and track start) may vary linearly with the angle: P + β·(1/cosθ − 1.1). The β values were fitted to the data (an empirical correction, not predicted by the physics of the formula); all other numbers on this card come from the angle-free formula. 3D test NLL: 14.8072 → 14.8047 (s2: -0.0024 ± 0.0001 nat/event). Energy before the entrance (θ ≈ 0.25 → 0.57 rad): data 3.0 → 6.2 %, final formula 3.9 → 4.7 %, angle-dependent 3.4 → 5.7 %.
- **Shower-to-shower fluctuation** (PCA on the per-event profiles): the first 3 principal components explain 72–74 % of the variance. Separation power of the per-event quantities (× 10⁻³, floor from two half-samples: 3–13): any mean model 923 (binning constant), 3 principal components with Gaussian coefficients 106–176, 10 principal components with coefficients drawn from the training set 16–56.

## The formula

ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H — each term is normalised separately on the (z', r) grid (σ(·) = logistic function; terms not switched on for this particle are omitted; the subscripts are the Hungarian term names: zápor = shower, nyom = track, csúcs = entry spike, folt = end-of-range blob, távoli = far halo):

- **Shower** S = L(z')·T(r | z'). Plateau depth profile: L ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ z'/1 m); gamma: L ∝ s^(α−1)·e^(−(α−1) s/t_max), s ≈ z' − z0. Cross-section: T = f1·e^(−r²/2σ²)/(2πσ²) + f2·R²/(π(r² + R²)²) + f3·e^(−r/λ)/(2πλ(r + 1 mm)); ln σ, ln R, ln λ and the mixing logits are linear in depth (σ and the logits also with a quadratic term when “curvature” is switched on); at every depth normalised on the disc r < 700 mm.
- **Track** U ∝ σ((z' − z_t0)/4 mm)·σ((R(T) − z')/w_R)·e^(−κ_t z'/R)·e^(−z'/λ_att)·(1 − z'/R + 0.03)^(−q) × [(1 − f)·Gauss(r; σ(z')) + f·e^(−r/l)/(2πl(r + 1 mm))], where R(T) = R1·T^(k_R) − R0 (range), w_R = w·R + 3 mm, σ(z')² = σ0² + (c·(z'/1 m)^k / βp)² (multiple scattering), βp = (T² + 2Tm)/(T + m).
- **Entry spike**: D ∝ e^(−(z' − z_sp)²/2σ_z²)·e^(−r²/2σ_r²); **end-of-range blob**: E ∝ e^(−(z' − R(T))²/2σ_ez²)·e^(−r²/2σ_er²); **far halo**: H ∝ σ(z'/10 mm)·e^(−z'/L)·e^(−r/R)/(r + 10 mm).
- **Weights**: w_távoli = σ(a_far), w_folt = σ(a_end)·(1 − w_távoli); the shower, the track and the entry spike share the remainder (the entry spike is tied to the track: f1 = d1/(d1 + L_t), where L_t is the length of the track).
- Every raw parameter is P(x) = Σ c_k x^k, x = (ln(T/GeV) − v0)/vs, T = √(p² + m²) − m; “log_” = logarithm of the quantity, “logit_” = logit of a fraction.

Terms: shower (plateau depth profile × [Gaussian core + Cauchy body + e^(−r/λ)/r halo]) + entry spike + far halo + quadratic depth terms in the cross-section.

## How to read the tables

- Columns: the momentum p [GeV]; each row is the value of one fitted quantity at that momentum.
- **w …**: weight of the component in the uncut body of revolution. **in-detector: …**: share of the component in the energy deposited in the detector (behind the tilted entrance face) – this is the physically meaningful energy share.
- **z_s, w1, ℓ, w2, κ** (plateau) or **z0, t_max, α−1** (gamma): depth profile of the shower. **σ core, R Cauchy, λ halo** and **f core / body / halo**: widths and fractions of the three cross-section terms at the given depth.
- **R(T)**: length of the track (range); **σ0**: width of the track at the entrance; **c_ms, k_ms**: widening due to multiple scattering; **λ_att**: attenuation length; **f, l delta halo**: fraction and length of the halo around the track; **q Bragg**: exponent of the Bragg rise; **entry spike …, end-of-range blob …**: position and width of the two Gaussians; **far halo L, R**: depth and radial length (R → ∞: no radial cut-off).
- There are two fits: the **3D metric** (normalised per event to the detector slab; it describes the body of revolution) and the **report metric** (× Ā; the r95 and iso-density shapes are computed from it). Their values differ slightly.

## 3D metric (normalised per event to the detector slab) – this is the body of revolution

Degree n = 3, 64 parameters; v0 = -0.7756, vs = 3.7713. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.499 | 0.999 | 2 | 5 | 10 | 20 |
| w shower | 0.664 | 0.742 | 0.82 | 0.915 | 0.962 | 0.983 |
| w entry spike | 0.332 | 0.252 | 0.173 | 0.0762 | 0.0284 | 0.00701 |
| w far halo | 0.00473 | 0.00599 | 0.00731 | 0.0089 | 0.00972 | 0.01 |
| in-detector: shower | 0.754 | 0.824 | 0.884 | 0.947 | 0.975 | 0.987 |
| in-detector: entry spike | 0.24 | 0.17 | 0.108 | 0.0438 | 0.0153 | 0.00351 |
| in-detector: far halo | 0.00545 | 0.00666 | 0.00781 | 0.00899 | 0.00948 | 0.00951 |
| z_s [mm] | 1.96 | 5.51 | 9.4 | 15.1 | 19.9 | 25.2 |
| w1 [mm] | 18.1 | 19.9 | 21.7 | 24 | 25.4 | 26.3 |
| ℓ [mm] | 33.3 | 42.8 | 56.1 | 82.3 | 112 | 154 |
| w2 [mm] | 57.2 | 60.2 | 62.9 | 65.5 | 66.4 | 66.2 |
| κ [1/m] | -1.68 | -1.44 | -1.26 | -1.16 | -1.19 | -1.33 |
| σ core, z'=100 [mm] | 20.8 | 19 | 17.6 | 16.5 | 16 | 15.8 |
| R Cauchy, z'=100 [mm] | 39.5 | 34.8 | 31 | 26.7 | 23.7 | 20.7 |
| λ halo, z'=100 [mm] | 39.5 | 39.5 | 39.5 | 39.5 | 39.5 | 39.5 |
| f core / body / halo, z'=100 | 0.69 / 0.19 / 0.12 | 0.74 / 0.13 / 0.13 | 0.78 / 0.08 / 0.14 | 0.82 / 0.04 / 0.13 | 0.84 / 0.03 / 0.13 | 0.85 / 0.02 / 0.13 |
| σ core, z'=600 [mm] | 2.11 | 1.92 | 1.79 | 1.67 | 1.62 | 1.6 |
| R Cauchy, z'=600 [mm] | 110 | 97.3 | 86.7 | 74.7 | 66.3 | 57.9 |
| λ halo, z'=600 [mm] | 22.7 | 22.7 | 22.7 | 22.7 | 22.7 | 22.7 |
| f core / body / halo, z'=600 | 0.00 / 1.00 / 0.00 | 0.00 / 1.00 / 0.00 | 0.00 / 1.00 / 0.00 | 0.00 / 1.00 / 0.00 | 0.00 / 1.00 / 0.00 | 0.00 / 1.00 / 0.00 |
| entry spike z [mm] | -8.25 | -8.84 | -9.54 | -10.6 | -11.6 | -12.6 |
| entry spike σ_z [mm] | 17.9 | 21.9 | 24.5 | 24.6 | 22.2 | 18.3 |
| entry spike σ_r [mm] | 8.9 | 8.88 | 8.94 | 9.15 | 9.4 | 9.74 |
| far halo L [mm] | 767 | 767 | 767 | 767 | 767 | 767 |
| far halo R [mm] | 9.8e+08 | 9.8e+08 | 9.8e+08 | 9.8e+08 | 9.8e+08 | 9.8e+08 |

Coefficients: `formula_coefficients_slab.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).

## Report metric (× Ā; the r95 and iso-density shapes are computed from it)

Degree n = 4, 75 parameters; v0 = -0.7756, vs = 3.7713. The “w” rows are the shares in the uncut body of revolution, the “in-detector” rows those of the energy deposited in the detector behind the tilted entrance face (weighted with the angle-averaged acceptance Ā).

| parameter | p = 0.5 | p = 1 | p = 2 | p = 5 | p = 10 | p = 20 |
|---|---:|---:|---:|---:|---:|---:|
| T [GeV] | 0.499 | 0.999 | 2 | 5 | 10 | 20 |
| w shower | 0.741 | 0.807 | 0.854 | 0.9 | 0.928 | 0.951 |
| w entry spike | 0.254 | 0.186 | 0.137 | 0.0887 | 0.0603 | 0.0382 |
| w far halo | 0.00498 | 0.00678 | 0.0088 | 0.0111 | 0.0117 | 0.0106 |
| in-detector: shower | 0.738 | 0.807 | 0.855 | 0.902 | 0.929 | 0.952 |
| in-detector: entry spike | 0.258 | 0.187 | 0.137 | 0.0882 | 0.06 | 0.0381 |
| in-detector: far halo | 0.00463 | 0.00624 | 0.00805 | 0.0101 | 0.0106 | 0.00963 |
| z_s [mm] | 7.35 | 10.2 | 13 | 16.6 | 19.3 | 22 |
| w1 [mm] | 11.2 | 10.4 | 10.5 | 11.5 | 13 | 15.2 |
| ℓ [mm] | 33.1 | 45.4 | 62.7 | 94.5 | 125 | 156 |
| w2 [mm] | 57.7 | 59.6 | 61.1 | 62.1 | 61.6 | 59.5 |
| κ [1/m] | -1.66 | -1.28 | -0.902 | -0.437 | -0.113 | 0.181 |
| σ core, z'=100 [mm] | 20.6 | 18.6 | 17.4 | 16.4 | 16 | 15.6 |
| R Cauchy, z'=100 [mm] | 39 | 34.1 | 30.3 | 26 | 22.8 | 19.6 |
| λ halo, z'=100 [mm] | 39.8 | 39.8 | 39.8 | 39.8 | 39.8 | 39.8 |
| f core / body / halo, z'=100 | 0.71 / 0.18 / 0.11 | 0.76 / 0.12 / 0.12 | 0.80 / 0.07 / 0.13 | 0.83 / 0.04 / 0.13 | 0.84 / 0.03 / 0.13 | 0.85 / 0.02 / 0.12 |
| σ core, z'=600 [mm] | 4.54 | 4.11 | 3.83 | 3.62 | 3.52 | 3.43 |
| R Cauchy, z'=600 [mm] | 104 | 90.7 | 80.5 | 69 | 60.7 | 52.2 |
| λ halo, z'=600 [mm] | 29.3 | 29.3 | 29.3 | 29.3 | 29.3 | 29.3 |
| f core / body / halo, z'=600 | 0.00 / 1.00 / 0.00 | 0.00 / 1.00 / 0.00 | 0.00 / 1.00 / 0.00 | 0.00 / 0.99 / 0.01 | 0.00 / 0.99 / 0.01 | 0.00 / 0.99 / 0.01 |
| entry spike z [mm] | 5.23 | 5.36 | 5.5 | 5.71 | 5.88 | 6.06 |
| entry spike σ_z [mm] | 4.03 | 4.35 | 4.53 | 4.51 | 4.32 | 3.98 |
| entry spike σ_r [mm] | 10.2 | 10.3 | 10.3 | 10.2 | 10.1 | 10 |
| far halo L [mm] | 906 | 906 | 906 | 906 | 906 | 906 |
| far halo R [mm] | 8.94e+09 | 8.94e+09 | 8.94e+09 | 8.94e+09 | 8.94e+09 | 8.94e+09 |

Coefficients: `formula_coefficients_std.csv` (raw parameter = Σ c_k x^k; log_* = logarithm of the quantity, logit_* = logit of a fraction).
