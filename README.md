**English** | [Magyar](README.hu.md)

# Shower shape – a better 3D shape (electron, pion, proton, muon)

A continuation of the team report [`report_hu.pdf`](https://github.com/EgyipTomi425/models-particle/blob/master/lib/report_hu.pdf) (Sofiya's `shape-form` notebooks): the same data, split (70/15/15%, `SEED = 1`), grid and
per-event NLL; the common code (`00_common.ipynb`) is unchanged. The data are a standalone DD4hep simulation of the ePIC LFHCal
(60 layers × [4 mm scintillator + 15.2 mm steel + 1.3 mm Kapton/air], preceded by 40.4 mm of steel; for the layer structure
X₀ = 23.5 mm, λ_I = 212 mm, λ_π = 260 mm, R_M = 21.9 mm; source: eic/epic `compact/hcal/lfhcal.xml`).

## In brief

- **The formula.** A sum of physically distinct terms (shower + track + entry spike + end-of-range blob + far halo), 75–143 parameters,
  fitted directly to the simulated hits. It closes **70–90%** of the gap between the old formula and the network; the same result is
  obtained on an independent second sample (s2).
- **How well it describes the shower.** Radially, the mean profile is close to the network for the electron and the proton, and better
  than it for the muon; in depth the network is better, but for hadrons (p ≥ 2 GeV) the deviation of the formula in the bulk of the
  profile is only ~1.5–2%.
- **Physics.** The physically meaningful parameters mostly lie close to the values expected from the detector material (muon multiple
  scattering, ranges, attenuation lengths). According to the simulation truth, the far halo of the electron is prompt electromagnetic
  energy, while one half to three quarters of the far energy of hadrons comes from neutrons.
- **Shapes.** The best 98% envelope body is the super-egg (proton: 3.5% smaller than the refitted drop, 4.4% smaller than the report's
  drop); the calibrated iso-density body is not meaningfully smaller (proton: 0.2% below the refitted drop).
- **Angle-dependent extension (not a model prediction, see 6.).** If the angle of incidence is given as an input and a few entrance
  parameters are fitted together with the angle, the 3D likelihood improves further (−0.045 nat for the muon).
- **What is missing.** The shower-to-shower fluctuation (the formula is a mean), the exact angle dependence at the entrance, and the
  energy arriving after 100 ns (at least 3–5% for hadrons).

## Per particle – what came out, what follows from it

(The terms are explained in chapter 1; the numbers come from chapters 2–7.)

**Electron** – shower + entry spike + far halo, no track (64 parameters).
- At low energy the first layer receives a lot of energy: the entry spike is 17% of the energy at 1 GeV, and only 0.35% at 20 GeV;
  the rest is the shower.
- The shower core is σ ≈ 16–19 mm, about 0.8 Molière radii: the cross-section is that of the expected electromagnetic shower.
- The shower maximum is at 35 → 76 mm (1 → 20 GeV), the PDG estimate is 23 → 94 mm: the trend is right, but the energy dependence of
  the formula is weaker than expected.
- According to the simulation, the far halo (~1% of the energy, length in depth ~0.77 m) is prompt e±/γ energy, not neutrons; the
  formula underestimates it by ~30% at 5–20 GeV.
- The most is left here relative to the network (gap closed 70%): the deep tail (6–11% less at 0.35–0.44 m) and the core, which is
  narrower than a cell.
- The angle hardly matters (−0.002 nat); 3 principal components describe ~73% of the fluctuation; the best envelope body is about as
  large as the drop (26 L).
- **Conclusion:** the classical EM shape describes the electron shower well; what is missing lies in the details (position of the
  maximum, deep tail).

**Muon** – small shower + track, with all extensions (129 parameters); 87–93% of the energy is in the track.
- The gain is largest here (−0.073 nat relative to the old formula, gap closed 89%): the old formula had no track.
- The widening of the track comes from multiple scattering: k ≈ 1.41 agrees with the Highland estimate (1.35–1.41), c ≈ 74 mm is 17%
  larger than expected.
- The exponent of the Bragg rise is 0.42 (theory 0.43), the range ≈ 1.06 m/GeV · T, in agreement with the CSDA table; above
  T ≳ 1.3 GeV the muon passes through the detector.
- A stopping μ⁻ is captured in the iron (neutrons, gammas), so at low momentum up to 20% of the far energy comes from neutrons.
- Radially it is better than the network, in depth worse: in the deepest ~13 cm the data fall off (some of the tracks leave through
  the edge), the formula does not.
- The angle-dependent extension gives the most here (−0.045 nat), but only through the terms swapping roles, so it cannot be
  interpreted physically.
- Best envelope body: super-egg or capsule (~38 L), 19% smaller than the drop.
- **Conclusion:** the muon “shape” is in fact a track that physics describes well; the fitted parameters reproduce textbook values.

**Proton** – shower + track, with all extensions (143 parameters).
- Two regimes: at 1 GeV the proton mostly stops (track 61%, entry spike 24%, shower 15%), at 5–20 GeV it creates a shower (shower
  74–81%).
- Most of the gain (−0.039 nat, gap closed 90%) comes from the stopping protons; ~60% of what remains relative to the network is also
  at p < 2 GeV.
- The range at T = 0.5 / 1 GeV is 185 / 722 mm (CSDA: 219 / 694 mm); the attenuation length is 266 mm ≈ 1.26 λ_I.
- Above 2 GeV the “track” is already effective: it carries more energy (17–27%) than the proton's own ionisation (5–12%), because it
  also describes part of the hadronic core.
- One half to three quarters of the far energy comes from neutrons; it is carried by the exponential halo of the shower. The cells
  first hit later (≥ 5 ns) give at least 8–11% of the energy and lie 2.5–3 times wider: two (fast + slow) halo terms would be the
  next step.
- In the bulk of the profile the deviation is 2.1%; radially it is close to the network.
- Best envelope body: super-egg, 1544 L, 3.5% smaller than the drop.
- **Conclusion:** the physics of the stopping proton (range, attenuation) is captured well by the formula, and so is the mean of the
  high-energy hadronic shower; its event-to-event fluctuation, however, is not (3 principal components give only 40–66% of the
  variance).

**Pion** – like the proton (101 parameters); the track is 26–53%.
- Gap closed 88%; the extension terms add hardly anything here (~0.001 nat), what matters is shower + track.
- The attenuation length is 339 mm ≈ 1.31 λ_π; the pion/proton ratio is 1.28 (expected 1.23): the pion penetrates deeper than the
  proton, as it should.
- The deviation in the bulk of the profile is smallest here (1.5%).
- 45–60% of the far energy comes from neutrons; the cells hit later give at least 6–8% of the energy.
- Best envelope body: super-egg, 1423 L, 3.8% smaller than the drop.
- The pion 3D network is degenerate, so for the pion the 3D comparison with the network is not reliable (the report-metric one is).
- **Conclusion:** the pion behaves like the proton, with a longer attenuation length; the mean shape is good, the fluctuation is
  high-dimensional.

## Physical interpretation

What do these mean physically? The points marked with ✓ have been checked by calculation; the rest is interpretation: consistent with
the data, but no separate measurement was made for it.

- **The Bragg exponent follows from the range law (✓).** If the range is R ∝ T^a, then the specific energy loss as a function of the
  distance from the end of the path is dE/dx ∝ (R − z')^(−(1 − 1/a)). With the Bragg–Kleeman a = 1.77 this gives 0.43; the value fitted
  for the muon is q = 0.42. For the stopping muon the formula has thus learned the real Bragg rise.
- **The muon range is linear in T (✓),** because in the interval studied (T ≈ 0.15–1.3 GeV, βγ ≈ 2.2–13) the muon is close to the
  minimum-ionising region, where dE/dx is nearly constant. Hence R ≈ T / (dE/dx) – the fitted 1.06 m/GeV agrees with the CSDA table.
- **The multiple-scattering exponent is smaller than 1.5 because of the front plate (✓).** In thin material the lateral displacement
  of the track is ∝ z'^1.5 (Highland). The 40 mm steel front plate already produces angular scattering before the detector, and this
  adds in quadrature: the effective exponent becomes 1.35–1.41. c is 17% larger than expected; this is probably the energy loss along
  the path (the muon slows down, and the scattering, ∝ 1/p, grows), which the estimate does not include.
- **At low energy the fitted proton range is shorter than the CSDA range (−16%, T = 0.5 GeV).** The CSDA assumes that the proton
  slows down without interacting. The 219 mm path, however, is comparable to the nuclear interaction length (212 mm): about 55–65% of
  the protons undergo a nuclear interaction before the end of the path, so the mean “track” ends earlier.
- **The attenuation length is ~1.3 times the nuclear interaction length.** λ_att does not measure when the primary ceases to exist,
  but when the track-like energy along the axis runs out. After elastic and quasi-elastic collisions, or when a leading particle
  carries on most of the energy, the deposition along the axis continues. It is therefore natural that λ_att > λ_I. The pion/proton
  ratio (1.28, expected 1.23) follows the smaller pion–nucleus cross-section.
- **Two regimes for the proton.** At p = 1 GeV/c (T = 0.43 GeV) the CSDA range behind the front plate is 165 mm (≈ 8 layers;
  the fitted range is 135 mm ≈ 6–7 layers). The proton therefore stops in the first few layers, which is why the entry spike and the track carry the energy. Above 5 GeV
  nuclear interactions dominate, and a hadronic shower develops.
- **Neutrons and the slow, wide halo.** Neutrons are uncharged: they travel far and deposit energy only indirectly (recoil protons in
  the hydrogen-rich scintillator, capture gammas). The slowing-down and capture of MeV neutrons is a ns–µs process. This explains why
  the energy of the cells hit later is wider and deeper, and why a fast and a slow halo term are needed.
- **The proton produces more neutrons than the pion** (far energy 51–75% vs. 45–60%; delayed 8–11% vs. 6–8%). This is consistent
  with the known baryon-number effect: in the proton shower fewer π⁰ are produced because of the leading baryon, so the
  electromagnetic part is smaller and the hadronic/neutron part larger.
- **Why is the fluctuation of the hadronic shower high-dimensional?** From event to event an EM shower differs mainly in its starting
  point and its length (1–2 degrees of freedom, 3 principal components ~3/4). For a hadronic shower, the following vary from event
  to event:
  - the position of the first interaction;
  - the fraction and position of the π⁰s (i.e. of the EM part);
  - the number of neutrons;
  - the nuclear binding energy, which is lost invisibly.

  These are largely independent of each other, so 3 principal components describe only 40–50% of the variance.
- **Electron: the entry spike and the shower maximum.** The front plate is 2.3 X₀ thick, so the shower already starts before the
  detector. At low energy the maximum is close to the entrance, and most of this early part is carried by the entry-spike term (17% at
  1 GeV). This is probably why the fitted maximum shifts later at low energy, and why its energy dependence is weaker (35 → 76 mm
  instead of the expected 23 → 94 mm). The 20.5 mm layer pitch also limits how sharply the maximum can be seen.
- **Electron: the far halo** is prompt e±/γ energy. These are probably photons of a few MeV: they are the least absorbed photons
  (near the absorption minimum in the Compton region), which is why they travel far.

Contents: Per particle · Physical interpretation · 1. Terms · 2. The formula · 3. Accuracy · 4. Shapes · 5. Cross-checks · 6. Angle-dependent extension · 7. Further results
(time separation, fluctuation) · 8. Conclusions · 9. Limitations · 10. Files.

## 1. Terms – what the numbers mean

| term | meaning |
|---|---|
| z', r | depth along the direction of incidence from the start of the shower (from the first hit layer), and distance from the axis [mm] |
| p, T | momentum [GeV/c] and kinetic energy T = √(p² + m²) − m [GeV] of the incoming particle |
| NLL [nat] | per event, the mean negative log-likelihood of the deposits under the model; **lower = better**. Only the NLLs of models trained with the same metric can be compared; the differences matter, not the absolute value |
| Δ (paired) | difference between the NLLs of two models on the same events, ± its standard error; negative = the first one is better |
| gap closed | (old formula − new formula) / (old formula − network): the percentage of the distance between the old formula and the network that the formula recovers |
| report metric, × Ā | the likelihood of the report; the model multiplied by an angle-averaged detector-acceptance template (Ā) |
| 3D metric | the likelihood normalised per event to the actual detector slab (between the tilted entrance face and the back face) |
| test, s2 | the test set (15%), and an independent second simulation sample (~100,000 events) that played no part in any decision |
| n / parameters | the degree of the polynomials and the number of free parameters of the formula |
| S (separation power) | difference between two normalised histograms (CaloChallenge): S = ½ Σ (h − g)² / (h + g); 0 = identical, 1 = no overlap. For small differences √(4S) ≈ the energy-weighted RMS relative deviation; in the tables in × 10⁻³ units |
| floor | S between two random halves of the data: a deviation this large occurs even for a perfect model, because of the finite sample |
| “in-detector” share | a term's share of the energy falling inside the detector (behind the entrance face) |

## 2. The formula

**What it is fitted to.** The parameters are fitted directly to the hits of the training set (energy-weighted, maximum likelihood), not
to network output. The terms and the degree were selected on the validation set. The network is only a benchmark.

`ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H`

Each term is a distribution normalised to 1 on its own; the weights w are the energy shares of the terms (they sum to 1; the subscripts
are the Hungarian names of the terms: zápor = shower, nyom = track, csúcs = entry spike, folt = end-of-range blob, távoli = far halo).
σ(·) is the logistic “step”.

| term | formula | meaning |
|---|---|---|
| shower S | `L(z')·T(r│z')` | the hadronic or EM shower |
| – depth profile | plateau: `σ((z'−z_s)/w1)·σ((ℓ−z')/w2)·e^(κz')`; muon: gamma `s^(α−1)e^(−(α−1)s/t_max)` | z_s: start, w1: rise, ℓ: end, w2: fall-off, κ: slow slope |
| – cross-section | `f1·Gauss(r;σ) + f2·R²/(π(r²+R²)²) + f3·e^(−r/λ)/(2πλ(r+1 mm))` | narrow core (σ), Cauchy body (R), exponential halo (λ); f1–f3 fractions; all vary with depth |
| track U | `σ((z'−z_t0)/4 mm)·σ((R(T)−z')/w_R)·e^(−z'/λ_att)·e^(−κ_t·z'/R)·(1−z'/R+0.03)^(−q)` × cross-section | the track of the primary particle: R(T) = R1·T^k_R − R0 is the range (smoothly floored at ~1 mm), w_R = w·R + 3 mm the width of its end, λ_att the attenuation (first nuclear interaction), κ_t a gradual fading along the range, q the Bragg rise |
| – track width | `σ(z')² = σ0² + (c·(z'/1 m)^k / βp)²`, plus an `f·e^(−r/l)/(2πl(r+1 mm))` halo | widening due to multiple scattering (c, k), delta-electron halo (f, l) |
| entry spike D | Gaussian at the entrance | the energy of the first layer |
| end-of-range blob E | Gaussian at z' = R(T) | end of a stopping particle (Bragg peak, capture) |
| far halo H | `σ(z'/10 mm)·e^(−z'/L)/(r+1 cm)` | diffuse energy that travels far |

Every parameter is a polynomial in `x = (ln T − v0)/vs`: the weights and the main shape parameters of degree n, the depth slopes and
the entry-spike parameters of degree 2, and the track, halo and blob parameters constant (21 of them for the muon and the hadrons). The full description per particle, with all
fitted values and coefficients: `results/particles/<particle>/formula.md`.

**Fitted values** (3D metric):

| particle | terms | n / param. | energy inside the detector | key parameters (in parentheses the value expected from the detector material) |
|---|---|---|---|---|
| electron | plateau shower + entry spike + far halo | 3 / 64 | shower 82% (1 GeV) → 99% (20 GeV); entry spike 17% → 0.35%; far halo 0.7–1.0% | core σ ≈ 16–19 mm (R_M = 21.9 mm); shower maximum 35 → 76 mm (PDG: 23 → 94 mm) |
| muon | gamma shower + track + all extensions | 6 / 129 | track 87–93% | widening c ≈ 74 mm, k ≈ 1.41 (Highland: 62–63 mm, 1.35–1.41); q ≈ 0.42 (0.43); range ≈ 1.06 m/GeV · T (CSDA ≈ 1.06–1.07) |
| proton | plateau shower + track + all extensions | 6 / 143 | 1 GeV: track 61%, entry spike 24%, shower 15%; 5–20 GeV: shower 74–81%, track 17–21% | range at T = 0.5 / 1 GeV: 185 / 722 mm (CSDA: 219 / 694 mm); λ_att ≈ 266 mm (λ_I = 212 mm) |
| pion | as for the proton | 3 / 101 | track 26–53% | λ_att ≈ 339 mm (λ_π = 260 mm) |

For hadrons the widening, the delta halo and the Bragg exponent of the track are effective: they also describe part of the hadronic
core.

<!-- KEPLETEK:START (scripts/readme_particle_formulas.py generates this block) -->

### Per-particle formulas (3D metric; the numbers are the fitted values)

The general formula above, per particle: the terms it contains, the constant parameters substituted, and the momentum-dependent ones at 1, 5 and 20 GeV/c. The “energy share” is the split of the energy deposited in the detector (behind the tilted entrance face). Polynomial coefficients: `results/particles/<particle>/formula_coefficients_slab.csv`; all momenta and the report metric: `formula.md`. If the range exceeds the depth of the detector (~1.3 m), the particle passes through it.

**Electron** (m = 0.511 MeV; polynomial degree and number of parameters: n = 3, 64)

`ρ(z', r | p) = w_zápor·S + w_csúcs·D + w_távoli·H`

- Shower depth profile, plateau: `L(z') ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ·z'/1 m)` (values below).
- Shower cross-section: `T(r│z') = f_core·Gauss(r; σ) + f_body·Cauchy(r; R) + f_halo·e^(−r/λ)/(2πλ(r + 1 mm))`; σ, R, λ and the fractions vary with depth (below at z' = 100 mm).
- Entry spike: Gaussian (position and widths below). Far halo: `H ∝ σ(z'/10 mm)·e^(−z'/767 mm)/(r + 1 cm)`.

| | p = 1 GeV/c | p = 5 GeV/c | p = 20 GeV/c |
|---|---:|---:|---:|
| T (kinetic energy) | 0.999 GeV | 5 GeV | 20 GeV |
| energy share: shower | 82.4% | 94.7% | 98.7% |
| energy share: spike | 17% | 4.38% | 0.351% |
| energy share: far halo | 0.666% | 0.899% | 0.951% |
| shower start z_s / rise w1 | 5.51 / 19.9 mm | 15.1 / 24 mm | 25.2 / 26.3 mm |
| shower end ℓ / fall-off w2 | 42.8 / 60.2 mm | 82.3 / 65.5 mm | 154 / 66.2 mm |
| slow slope κ | −1.44 /m | −1.16 /m | −1.33 /m |
| core σ / Cauchy R / halo λ (z' = 100 mm) | 19 / 34.8 / 39.5 mm | 16.5 / 26.7 / 39.5 mm | 15.8 / 20.7 / 39.5 mm |
| fractions core / body / halo (z' = 100 mm) | 0.74 / 0.13 / 0.13 | 0.82 / 0.04 / 0.13 | 0.85 / 0.02 / 0.13 |
| spike position / σ_z / σ_r | −8.84 / 21.9 / 8.88 mm | −10.6 / 24.6 / 9.15 mm | −12.6 / 18.3 / 9.74 mm |

**Muon** (m = 105.7 MeV; polynomial degree and number of parameters: n = 6, 129)

`ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H`

- Shower depth profile, gamma: `L(z') ∝ s^(α−1)·e^(−(α−1)s/t_max)`, s = z' − z0 (values below).
- Shower cross-section: `T(r│z') = f_core·Gauss(r; σ) + f_body·Cauchy(r; R) + f_halo·e^(−r/λ)/(2πλ(r + 1 mm))`; σ, R, λ and the fractions vary with depth (below at z' = 100 mm).
- Track: range `R(T) = 1057 mm · (T/GeV)^1.02 − 85 mm` (smoothly floored at ~1 mm); start `σ((z' − 24.2 mm)/4 mm)`, end `σ((R − z')/w_R)` with w_R = 0.0232·R + 3 mm; attenuation `e^(−z'/1211 mm)·e^(−0.735·z'/R)`; Bragg rise `(1 − z'/R + 0.03)^(−0.42)`; width `σ(z')² = (15 mm)² + (74.4 mm · (z'/1 m)^1.41 / βp)²`; delta-electron halo `e^(−r/51.4 mm)/(2π·51.4 mm·(r + 1 mm))` (its share below).
- End-of-range blob: Gaussian, σ_z = 73.1 mm, σ_r = 85.6 mm.
- Entry spike: Gaussian (position and widths below). Far halo: `H ∝ σ(z'/10 mm)·e^(−z'/1309 mm)/(r + 1 cm)`.

| | p = 1 GeV/c | p = 5 GeV/c | p = 20 GeV/c |
|---|---:|---:|---:|
| T (kinetic energy) | 0.9 GeV | 4.9 GeV | 19.9 GeV |
| energy share: shower | 2.42% | 6.11% | 1.39% |
| energy share: track | 90.9% | 88% | 92.5% |
| energy share: spike | 6.38% | 5.79% | 5.97% |
| energy share: blob | 0.239% | < 0.01% | < 0.01% |
| energy share: far halo | 0.0852% | 0.093% | 0.0942% |
| shower start z0 | −48.6 mm | −57.1 mm | −71 mm |
| shower maximum t_max | 5.36 mm | 90.9 mm | 240 mm |
| shape α − 1 | 0.0747 | 0.00916 | 0.0508 |
| core σ / Cauchy R / halo λ (z' = 100 mm) | 11.2 / 9.51 / 52.3 mm | 11.7 / 16.6 / 51.4 mm | 16 / 295 / 50 mm |
| fractions core / body / halo (z' = 100 mm) | 0.93 / 0.04 / 0.03 | 0.81 / 0.03 / 0.17 | 0.16 / 0.00 / 0.84 |
| track range R(T) | 864 mm | 5287 mm | 22483 mm |
| delta-halo share | 0.899% | 0.79% | 1.3% |
| spike position / σ_z / σ_r | −9.95 / 23 / 9.2 mm | −15.2 / 27.8 / 9.1 mm | −21.1 / 28.7 / 9.21 mm |

**Proton** (m = 938.3 MeV; polynomial degree and number of parameters: n = 6, 143)

`ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H`

- Shower depth profile, plateau: `L(z') ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ·z'/1 m)` (values below).
- Shower cross-section: `T(r│z') = f_core·Gauss(r; σ) + f_body·Cauchy(r; R) + f_halo·e^(−r/λ)/(2πλ(r + 1 mm))`; σ, R, λ and the fractions vary with depth (below at z' = 100 mm).
- Track: range `R(T) = 757 mm · (T/GeV)^1.78 − 36.5 mm` (smoothly floored at ~1 mm); start `σ((z' − 24.1 mm)/4 mm)`, end `σ((R − z')/w_R)` with w_R = 0.0579·R + 3 mm; attenuation `e^(−z'/266 mm)·e^(−2.46·z'/R)`; Bragg rise `(1 − z'/R + 0.03)^(−0.804)`; width `σ(z')² = (18.5 mm)² + (285 mm · (z'/1 m)^2.37 / βp)²`; delta-electron halo `e^(−r/81.5 mm)/(2π·81.5 mm·(r + 1 mm))` (its share below).
- End-of-range blob: Gaussian, σ_z = 76.3 mm, σ_r = 81.1 mm.
- Entry spike: Gaussian (position and widths below). Far halo: `H ∝ σ(z'/10 mm)·e^(−z'/962 mm)/(r + 1 cm)`.

| | p = 1 GeV/c | p = 5 GeV/c | p = 20 GeV/c |
|---|---:|---:|---:|
| T (kinetic energy) | 0.433 GeV | 4.15 GeV | 19.1 GeV |
| energy share: shower | 14.9% | 73.6% | 81.1% |
| energy share: track | 60.5% | 21.1% | 16.8% |
| energy share: spike | 23.6% | 4.87% | 2.12% |
| energy share: blob | 0.671% | < 0.01% | < 0.01% |
| energy share: far halo | 0.383% | 0.408% | < 0.01% |
| shower start z_s / rise w1 | −7.12 / 123 mm | 22.3 / 86.3 mm | 80.7 / 80.2 mm |
| shower end ℓ / fall-off w2 | 132 / 198 mm | 863 / 378 mm | 1330 / 76.2 mm |
| slow slope κ | −3.02 /m | −2.72 /m | −2.65 /m |
| core σ / Cauchy R / halo λ (z' = 100 mm) | 84.4 / 121 / 227 mm | 58.8 / 71 / 207 mm | 38.9 / 77.6 / 203 mm |
| fractions core / body / halo (z' = 100 mm) | 0.08 / 0.87 / 0.05 | 0.08 / 0.80 / 0.13 | 0.13 / 0.76 / 0.10 |
| track range R(T) | 135 mm | 9485 mm | 143749 mm |
| delta-halo share | 3.94% | 33.4% | 20.4% |
| spike position / σ_z / σ_r | −3.17 / 13.7 / 10.1 mm | −7.75 / 22.1 / 11.5 mm | −18.5 / 23.8 / 11.6 mm |

**Pion** (m = 139.6 MeV; polynomial degree and number of parameters: n = 3, 101)

`ρ(z', r | p) = w_zápor·S + w_nyom·U + w_csúcs·D + w_folt·E + w_távoli·H`

- Shower depth profile, plateau: `L(z') ∝ σ((z' − z_s)/w1)·σ((ℓ − z')/w2)·e^(κ·z'/1 m)` (values below).
- Shower cross-section: `T(r│z') = f_core·Gauss(r; σ) + f_body·Cauchy(r; R) + f_halo·e^(−r/λ)/(2πλ(r + 1 mm))`; σ, R, λ and the fractions vary with depth (below at z' = 100 mm).
- Track: range `R(T) = 952 mm · (T/GeV)^1.26 − 26.9 mm` (smoothly floored at ~1 mm); start `σ((z' − 28.4 mm)/4 mm)`, end `σ((R − z')/w_R)` with w_R = 0.0861·R + 3 mm; attenuation `e^(−z'/339 mm)·e^(−2.25·z'/R)`; Bragg rise `(1 − z'/R + 0.03)^(−0.526)`; width `σ(z')² = (20.1 mm)² + (135 mm · (z'/1 m)^1.72 / βp)²`; delta-electron halo `e^(−r/69.4 mm)/(2π·69.4 mm·(r + 1 mm))` (its share below).
- End-of-range blob: Gaussian, σ_z = 103 mm, σ_r = 130 mm.
- Entry spike: Gaussian (position and widths below). Far halo: `H ∝ σ(z'/10 mm)·e^(−z'/701 mm)/(r + 1 cm)`.

| | p = 1 GeV/c | p = 5 GeV/c | p = 20 GeV/c |
|---|---:|---:|---:|
| T (kinetic energy) | 0.87 GeV | 4.86 GeV | 19.9 GeV |
| energy share: shower | 43% | 68.1% | 68.5% |
| energy share: track | 43% | 26.7% | 28.9% |
| energy share: spike | 13.4% | 4.93% | 2.64% |
| energy share: blob | 0.0701% | < 0.01% | < 0.01% |
| energy share: far halo | 0.52% | 0.176% | 0.0112% |
| shower start z_s / rise w1 | 12.8 / 111 mm | 44.8 / 80.8 mm | 84.7 / 66.6 mm |
| shower end ℓ / fall-off w2 | 56.9 / 167 mm | 224 / 423 mm | 1207 / 596 mm |
| slow slope κ | −1.99 /m | −2 /m | −2.03 /m |
| core σ / Cauchy R / halo λ (z' = 100 mm) | 68 / 96.3 / 216 mm | 71.9 / 67.5 / 206 mm | 59.1 / 67.8 / 196 mm |
| fractions core / body / halo (z' = 100 mm) | 0.27 / 0.66 / 0.07 | 0.13 / 0.77 / 0.11 | 0.12 / 0.72 / 0.16 |
| track range R(T) | 772 mm | 6980 mm | 41375 mm |
| delta-halo share | 16.3% | 19.3% | 14.9% |
| spike position / σ_z / σ_r | −5.3 / 20.8 / 11.1 mm | −7.04 / 23.9 / 11.6 mm | −9.26 / 23.5 / 11.4 mm |

<!-- KEPLETEK:END -->

### Where the terms came from, and how the symbolic regression was done

The terms were written down from physical considerations, and each of them was fitted directly to the data; the network only showed
where something was still missing. We proceeded in three rounds; in each round the candidate terms were compared on the validation
set, and only what improved there was kept:

1. **Base** (`scripts/run_all.sh`): we started from the report's formula (GFlash shower, cylinder for the muon) and added what physics
   obviously provides: the **track** of the primary particle up to its range (range law, attenuation due to nuclear interactions), the
   **entry spike** and the plateau or gamma depth profile; the cross-section forms tried in the report (Gaussian, Cauchy,
   exponential) were summed.
2. **Where it still loses** (`scripts/diag_residual.py`): the NLL difference between the network and the formula was split into
   (z', r) regions, separately for p < 2 and p ≥ 2 GeV. This showed where the deficit lies: for the proton, the stopping protons near
   the axis in the first ~20 cm; for the electron, the region around the entrance and large radii; for the muon, the radial structure
   around the track.
3. **Symbolic regression** (`scripts/sr_residual.py`): PySR searched for an expression g(z', r, x) for the difference
   ln P_háló − ln P_formula, where P_háló and P_formula are the network and formula densities and x is the momentum variable of the
   formula. Operators: + − × /, exp, square; at most 18 nodes; 6000 points sampled according to the network density, at 16 momenta.
   The expression found was added as a correction (ln P' = ln P_formula + a·g) and fitted to the data together with the formula. To
   ensure that the gain did not come from the mere extra training, a control was trained for the same amount without the correction
   (`scripts/sr_control.py`).
4. **The suggestions as physical terms** (`scripts/variants_v2.py`, `variants_v3.py`): the expressions were not taken over; instead,
   we looked for their physical meaning and fitted the physical form of the corresponding term. This is how **multiple scattering**
   (the track widens as z'^k, Highland) and the **far halo** entered. The physics of stopping particles gave the **end-of-range
   blob** and the **Bragg rise**, the ionisation around the track the **delta-electron halo**.
   The Bock double-gamma depth profile and the GFlash EM lateral profile were also considered, but they were worse (chapter 8).
5. **Refit and decision:** after adding a new term, not only the new term was fitted, but the whole formula was refitted to the data by
   maximum likelihood, because a new term also rearranges the roles of the other terms. The new term was kept if it improved the
   result on the validation set. At the end, a complete, final round was run with the selected terms (`scripts/run_round3.sh`): degree
   selection, test, the independent second sample s2, and the cross-checks.

**The chain of reasoning, term by term** (the diagnosis is qualitative; for the gain of the terms that were included, see chapter 8):

- **Track:** the report's formula contained only a shower, whereas the muon and low-momentum hadrons deposit energy mainly in a long,
  narrow track. Compared with the old formula, the network was much better along the axis; together with the physical expectation, this
  pointed to a separate track term: straight up to the range, with attenuation due to nuclear interactions.
- **Entry spike:** in the first layers the network was better (it put more energy there than a smoothly rising shower). This pointed
  to a short term sitting at the entrance; physically, this is the energy of the shower that already started in the front plate and of
  the slow particles that stop early.
- **Multiple scattering:** for the muon the network was better in the radial region around the track; PySR also found structure at
  the edge of the track (r ≈ 12.5 mm). That is, the track widens with depth, as expected from multiple scattering; therefore the track
  width was written in the Highland form (σ² = σ0² + (c·z'^k / βp)²). This became the largest single improvement.
- **Far halo:** for the electron the network was better at large radius (far from the shower), and PySR also found a
  radius-dependent correction. This pointed to a low-weight, slowly decaying, diffuse term; the simulation truth later confirmed that
  it is real, prompt electromagnetic energy (chapter 5).
- **End-of-range blob, Bragg rise:** at low momentum (p < 2 GeV) the network remained better for the proton near the axis in the
  first ~20 cm, where the protons stop. For a stopping particle the energy deposition increases at the end of the path (Bragg), and
  there capture or decay adds further energy; these two terms were suggested by this location and this physics.
- **Delta-electron halo:** around the track, in addition to the narrow Gaussian width, a more slowly decaying halo was also needed;
  physically, these are the electrons knocked out by the primary.

**What does “symbolic regression on the difference” mean?** The network and the formula are fitted to the same data; where the
network finds the data more probable, something is missing from the formula. PySR tries to describe this difference
(ln P_háló − ln P_formula, at every point of the (z', r, p) space) with a short closed-form expression. The expression found is
therefore not the formula of the shower, but a description of *where and in what form* the formula still deviates; from it we read
off which physical term is missing.

- **Two separate steps.** Measuring the difference is a simple subtraction and summation per region (step 2). Symbolic regression
  then searches for an expression that describes this difference: not the coefficients of a fixed form, but the form itself (which
  variable, with which operations).
- **Evolutionary search.** PySR works by genetic programming: it treats expressions as trees, varies them (mutation) and crosses them
  over in populations, and keeps those that fit well while remaining short. It does not learn by gradients; it “breeds” the
  expression.
- **Why the difference between the network and the formula, and not that of the data?** The data are discrete and noisy (a few hundred
  deposits per event, few hits at large radius and in the tails), so the data − formula difference would be mostly noise there. The
  network is fitted to the same data and gives a smooth, continuous density everywhere: it serves as a noise filter and interpolator,
  and its difference from the formula is a smooth function for which a short expression can be searched. The price is that errors of
  the network can also enter; therefore the expression found was not accepted directly, but checked as a correction on the data, with
  the likelihood and a control run, and the final terms were also fitted to the data. (It could also be run directly on the
  data − formula difference, on binned histograms, only noisier and slower.)
- **Independent auxiliary expression.** The result of the symbolic regression is a separate expression, not the formula of the
  shower, and it did not enter the final formula; it is meaningful only relative to our formula, because it describes what that
  formula lacks.

**Summary: where each term came from** (old formula = the report's GFlash formula, the cylinder for the muon):

| new term | where it came from | what it means |
|---|---|---|
| track (range, attenuation) | physics missing from the old formula: the muon and slow hadrons deposit energy along a straight path; the network was better along the axis | the incoming particle's own ionisation path until it stops or until the first nuclear interaction |
| entry spike | the network was better in the first layers | the energy of the shower already started in the front plate and of the particles that stop early |
| multiple scattering | **symbolic regression** (muon: structure at the edge of the track) + the network was better around the track | the track widens with depth because the particle scatters through many small angles |
| far halo | **symbolic regression** (electron: radius-dependent correction) + the network was better at large radius | small, diffuse energy that travels far (photons for the electron) |
| end-of-range blob, Bragg rise | physics of the stopping particle; the network was better where the protons stop | the energy deposition increasing at the end of the path, and the energy of capture or decay, respectively |
| delta-electron halo | physics of the track (more slowly decaying energy was needed around the narrow Gaussian track) | electrons knocked out by the incoming particle |

Result of the symbolic regression (validation, nat; negative = better):

| particle | character of the best expression found | gain with the correction | the same relative to the control | what it suggested |
|---|---|---:|---:|---|
| muon | ~ c / (r − 12.5 mm): structure at the edge of the track | −0.0030 | −0.0025 | the track widens → multiple-scattering term |
| electron | polynomial in r near the axis and at large radius | −0.0010 | −0.0017 | the shape of the core and large radius → far halo |
| proton | ~ c / (r + z' + …): weak, near the axis | −0.0005 | – | essentially no residual |
| pion | ~ c / (r − 17 mm), decreasing with depth | −0.0003 | – | essentially no residual |

PySR was thus a compass, not the source of the formula: on its own it gave at most 0.0025 nat, whereas the physical terms read off
from it gave more (the muon multiple scattering alone −0.0044 nat on the validation set). No expression entered the final formula.
This differs from the report's distillation in that there the symbolic regression approximated the network's map from an 8-element
expression library, whereas here it searched for an arbitrary expression, and only for what is still missing from the physical
formula.

## 3. Accuracy

Test NLL, report metric (number of parameters in parentheses). “Old formula × Ā” is the report's formula, refitted in the same way with the template – this is the basis of the comparison.

| particle | old formula (report) | old formula × Ā | new formula | Δ test | Δ s2 | network (report / fine-tuned) | gap closed |
|---|---:|---:|---:|---:|---:|---:|---:|
| electron | 14.8479 (33) | 14.8406 (27) | **14.8167** (75) | −0.0239 ± 0.0009 | −0.0236 ± 0.0003 | 14.8068 / 14.8067 | 70% |
| pion | 18.1563 (27) | 18.1420 (39) | **18.1235** (101) | −0.0186 ± 0.0007 | −0.0212 ± 0.0004 | 18.1221 / 18.1208 | 88% |
| proton | 18.2536 (45) | 18.2331 (45) | **18.1940** (143) | −0.0391 ± 0.0016 | −0.0409 ± 0.0007 | 18.1922 / 18.1898 | 90% |
| muon | 16.0899 (59) | 16.0846 (59) | **16.0120** (129) | −0.0726 ± 0.0011 | −0.0739 ± 0.0007 | 16.0046 / 16.0034 | 89% |

Reading: the new formula for the proton is better than the old formula by 0.039 nat per event and recovers 90% of the distance between
the old formula and the network, while the network has 881–3841 parameters. On the 3D metric the gap closed is: electron 68%, proton
88%, muon 83% (for the pion the 3D network is degenerate, see 9.). The smaller degree-2 variant is worse by at most 0.0012 nat.

**Comparison with all models of the report** (Table 1 of the report and the new formula; same test set and metric, number of
parameters in parentheses). The report's distilled formula (“MLP formula”) is a symbolic formula fitted to the network's map; the new
formula consists of physical terms and is fitted directly to the data:

| particle | report baseline | report distilled (MLP formula) | **new formula** | report MLP | new − baseline | new − distilled | new − MLP |
|---|---:|---:|---:|---:|---:|---:|---:|
| electron | 14.848 (33) | 14.852 (19) | **14.817** (75) | 14.807 (2785) | −0.031 | −0.035 | +0.010 |
| pion | 18.156 (27) | 18.163 (21) | **18.123** (101) | 18.122 (3841) | −0.033 | −0.040 | +0.001 |
| proton | 18.254 (45) | 18.268 (21) | **18.194** (143) | 18.192 (881) | −0.060 | −0.074 | +0.002 |
| muon | 16.090 (59) | 16.071 (27) | **16.012** (129) | 16.005 (2785) | −0.078 | −0.059 | +0.007 |

According to the report, the network is better than the baseline by 0.03–0.09 nat; the distilled formula recovered none of this for
the electron, the pion and the proton (it is worse than the baseline) and ~22% for the muon;
the new formula recovers ~76% of this difference for the electron, 96–97% for the pion and the proton, and ~91% for the muon. Part of
the gain (0.005–0.021 nat) comes from the parameter-free × Ā template; measured against the old formula refitted with it, the table
above applies (gap closed 70–90%).

**How close it comes to the network, and how many times smaller it is.** The reference is the fine-tuned network (100%). The
percentage shows how much of the network's probability the formula reaches, i.e. how probable it finds the actually simulated
deposits relative to the network (on average per deposit, e^(−(NLL_képlet − NLL_háló)), where képlet = formula and háló = network;
test NLL).

| particle | parameters of the formula | parameters of the network (MLP) | the formula is smaller by | old formula relative to the network | new formula relative to the network |
|---|---:|---:|---:|---:|---:|
| electron | 75 | 2785 | 37× | 96.0% | 99.0% |
| pion | 101 | 3841 | 38× | 96.5% | 99.7% |
| proton | 143 | 881 | 6× | 93.8% | 99.6% |
| muon | 129 | 2785 | 22× | 91.7% | 99.1% |

Reading (proton): the old formula reached 93.8% of the network, the new formula 99.6%. The number of parameters of the formula is the
total number of polynomial coefficients, for all momenta together (chapter 2).

For comparison, the report's distilled formula (the symbolic formula fitted to the network) in the same way, from Table 1 of the
report:

| particle | report distilled formula | new formula | PCA (3 components) |
|---|---:|---:|---:|
| Electron | 95.6% | 99.0% | 72–74% |
| Pion | 95.8% | 99.7% | 42–54% |
| Proton | 92.5% | 99.6% | 40–66% |
| Muon | 93.4% | 99.1% | 73–78% |

The variance measures how much the individual showers differ from each other (where they start, how long and how wide they are); the
last column shows what percentage of this fluctuation is described by 3 main directions (principal components; per momentum
interval, chapter 7). This is a property of the simulated showers, not of the formulas: every model, the network included, gives only
the mean shape, so none of them describes the fluctuation of individual showers. For the electron and the muon the fluctuation is
simple (3 directions give ~3/4 of it), for hadrons it is high-dimensional (only ~40–60%), so an event generator would need a more
complex fluctuation model there.

## 4. Shapes (envelope bodies)

In a cell, “V (V_szelet) / c”: V is the volume of the body in litres within the data region (−200 < z' < 1450 mm, r < 700 mm),
V_szelet the part of it inside the detector slab, and c the fraction of test showers in which ≥ 95% of the energy is inside the body.
Average over all 20 momentum bins. E.g. “1423 (1302) / 0.98”: 1423 L, of which 1302 L is in the detector; in 98% of the showers at
least 95% of the energy is inside.

| shape | electron | pion | proton | muon |
|---|---:|---:|---:|---:|
| 98% – drop (report) | 26.1 (24.6) / 0.98 | 1486 (1362) / 0.98 | 1616 (1469) / 0.98 | – |
| 98% – drop, refitted | 25.9 (24.4) / 0.98 | 1478 (1335) / 0.98 | 1600 (1428) / 0.98 | 46.5 (43.5) / 0.98 |
| 98% – **super-egg** | 25.9 (24.2) / 0.98 | **1423** (1302) / 0.98 | **1544** (1395) / 0.98 | **37.7** (35.8) / 0.98 |
| 98% – calibrated iso-density body (new formula) | 31.7 (30.7) / 0.98 | 1491 (1368) / 0.98 | 1596 (1449) / 0.98 | 48.9 (44.9) / 0.98 |
| r95 – network (report) | 5.7 (5.6) / 0.46, E_in 0.93 | 403 (384) / 0.77, E_in 0.95 | 466 (441) / 0.75, E_in 0.95 | 8.8 (8.5) / 0.03, E_in 0.72 |
| r95 – new formula (E_in = mean fraction of the energy inside) | 5.6 (5.6) / 0.43, E_in 0.93 | 389 (370) / 0.76, E_in 0.95 | 494 (467) / 0.77, E_in 0.95 | 9.3 (8.8) / 0.05, E_in 0.75 |

**Super-egg:** `r(z') = A·(1 − |τ|^n)^(1/m)`, where `τ = (z_c − z')/a1` in front of the widest point (z_c) and `(z' − z_c)/a2` behind
it; A is the largest radius, a1 / a2 the front / rear half-length, n, m the “squareness” of the shape. Per bin 6 parameters, fitted
directly to the showers (the smallest body in which ≥ 95% of the energy is inside in 98% of the showers). Example (proton, 4–5 GeV):
z_c ≈ 175 mm, a1 ≈ 338 mm, a2 ≈ 1231 mm, n ≈ 2.8, m ≈ 1.7, A ≈ 719 mm. The report's drop: `r = A·t^(1/2)(1 − t)^(3/2)/g_max`.
The report's own numbers are reproduced exactly.

## 5. Cross-checks

**Mean profile** (s2; S × 10⁻³, depth / radius; every model trained on the 3D metric):

| particle | floor | old formula | new formula | network |
|---|---:|---:|---:|---:|
| electron | 0.16 / 0.11 | 0.76 / 6.51 | 0.88 / 4.97 | 0.56 / 4.55 |
| muon | 0.07 / 0.08 | 5.28 / 15.9 | 4.19 / **1.88** | 0.31 / 2.09 |
| proton | 0.18 / 0.07 | 3.03 / 2.82 | 0.53 / 2.64 | 0.25 / 2.48 |
| pion | 0.17 / 0.05 | 2.25 / 1.06 | 0.77 / 0.98 | (degenerate) |

Radially the formula is close to the network (better for the muon), in depth the network is better. In the bulk of the profile
(p ≥ 2 GeV, 0 < z' < 1300 mm) the energy-weighted RMS relative deviation of the formula is: proton 2.1%, pion 1.5%, electron 4.2%
(2.9% for z' < 0.46 m), muon 5.8%. It reproduces the energy before the entrance (z' < 0) overall (e.g. proton 4.1% vs. 3.9% in the data), but its angle
dependence is too weak (6.). Further deviations: the deepest ~13 cm of the muon and its depth slope, and the deep tail of the
electron.

**What deposits the energy** (s2, per-hit information from the simulation; value ranges over 0–20 GeV):

| particle | own energy of the incoming particle | daughters of neutrons | r ≥ 300 mm: data (model) | of which from neutrons / prompt (< 5 ns) |
|---|---:|---:|---:|---:|
| electron | 1–4% | ≈ 0.1% | 0.56–0.91% (0.56–0.65%) | 1–2% / 99% |
| muon | 79–91% | 0–1% | 0.05–0.09% (0.06–0.07%) | 2–20% / 72–96% |
| proton | 5–50% | 18–25% | 3.5–7.9% (3.7–8.5%) | 51–75% / 41–60% |
| pion | 5–26% | 11–16% | 4.1–6.4% (4.4–6.5%) | 45–60% / 55–62% |

The far halo of the electron is thus prompt electromagnetic energy (the model underestimates it by ~30%); for hadrons the far energy
is carried by the exponential halo of the shower. The muon track is its own ionisation and the nearby delta electrons.

**Values expected from the detector material** (`scripts/lfhcal_expectations.py`; Highland formula, CSDA range, PDG): the exponent
of the muon widening (1.41) agrees, because the 40 mm steel front plate brings it below 1.5; c is 17% larger (explained by the energy
loss along the track); the proton range at T = 0.5–1 GeV is within 4–16%; the attenuation lengths are ~1.3 times the nuclear
interaction lengths; the energy dependence of the electron shower maximum is weaker than expected.

## 6. Angle-dependent extension – not a model prediction

**What it is.** The final formula does not know at what angle the particle arrived. In this extension the angle of incidence (θ) is
**given as an input** for each event – it is known from the simulation – and a few entrance parameters (the weight, position and
width of the entry spike, the start of the shower and of the track) may vary linearly with the angle: `P(x, u) = P(x) + β·u`,
u = 1/cosθ − 1.1; 6–8 new parameters (β) per particle.

**Why it is not a model prediction.** The physics of the formula does not predict the angle dependence: the β coefficients were
fitted to the data; this is an empirical correction. The formula itself and every number in sections 2–5 are angle-free. The network
was not trained with the angle either, so the comparison with it below is not made under the same conditions.

| particle | 3D test NLL: final formula → angle-dependent | Δ relative to the final formula (s2) | network (without angle) |
|---|---:|---:|---:|
| electron | 14.8072 → 14.8047 | −0.002 | 14.7976 |
| muon | 16.0144 → 15.9690 | −0.045 | 16.0000 |
| proton | 18.1660 → 18.1576 | −0.008 | 18.1614 |
| pion | 18.1014 → 18.0928 | −0.009 | (degenerate) |

For hadrons the gain comes from the first ~2 layers: the weight of the entry spike grows 2–6-fold at large angles. It halves the
error of the angular trend of the energy before the entrance (e.g. proton, θ ≈ 0.25 → 0.57 rad: data 1.8 → 4.7%, final formula
2.8 → 3.8%, angle-dependent 2.2 → 4.0%). For the muon the fit rearranges the terms; there the physical interpretation of the terms
does not hold. Therefore the angle-dependent variant is not part of the final formula.

## 7. Further results

**Time separation** (proton, pion; s1 test). The data store only the time of the first hit per cell; a cell is “delayed” if it was
first hit by something more than 5 ns after the first hit of the event. The energy of the delayed cells is on average 8–11% (proton)
and 6–8% (pion) per event – this is a lower bound – and it is ~2.5–3 times wider (mean radius ~240–250 mm vs. ~85–97 mm for the fast
cells), ~115–150 mm deeper. The single exponential halo of the formula (λ ≈ 200–215 mm) falls between the fast (≈ 135–160 mm) and the
delayed (≈ 410–600 mm) fit. Next step: two halo terms (fast and delayed).

**Shower-to-shower fluctuation** (s1; principal component analysis of the per-event profiles). The first 3 principal components
describe ~3/4 of the shower-to-shower variance for the electron and the muon, but only ~40–50% for hadrons above 2 GeV. A simple
generator built from principal components is a multiple of the floor even with 10 components. The formula is a mean; an event
generator needs a separate, non-Gaussian fluctuation model.

## 8. Conclusions

1. The detector acceptance (× Ā) gives an improvement without any parameter; the networks had learned part of it as a “cone”.
2. The new formula is better than the old formula for all four particles (−0.019 … −0.073 nat) and closes 70–90% of the gap to the
   network.
3. Among the extension terms, the muon multiple scattering and the electron far halo gave the most; the further terms and the
   corrections found by symbolic regression (PySR) give ≤ 0.0025 nat – the formula saturates here.
4. Literature: the Bock double-gamma depth profile and the GFlash EM lateral profile are worse; we found no new closed-form
   parametrisation of calorimeter showers from 2025–26 (the field has moved towards generative networks: CaloHadronic, AllShowers,
   CaloDiT-2; the benchmark is the CaloChallenge separation power, arXiv:2410.21611).
5. The report's drop is a near-optimal envelope body; the super-egg is 3.5–3.8% smaller than the refitted drop (4.3–4.4% smaller than
   the report's), the calibrated iso-density body is not meaningfully smaller (the 98% criterion is decided by the extreme showers).

## 9. Limitations

- Neither metric is normalised exactly to the instrumented cells (~0.2 nat); therefore only models trained in the same way are
  compared.
- Diagnostics performed on the test set also played a role in selecting the terms; therefore the clean check is the independent
  second sample s2.
- The pion 3D network is degenerate (its probability mass lies practically outside the detector slab), so the numbers of the pion 3D
  network are not reliable.
- The angle dependence of the energy before the entrance is too weak; the energy arriving after 100 ns is left out; the formula gives
  no shower-to-shower fluctuation.
- The model treats the cells as uniform 48.6 × 48.6 × 20.5 mm boxes (at the module boundaries the real pitch is larger).
- For hadrons the parameters of the track extensions are effective.

## 10. Files, running

- Model: `particle_shape.py`; loading: `shapelab.build_final`. Final results: `results/particles/<particle>/test_v3.json`,
  `s2_v3.json`, `shapes.json`; per-particle description: `results/particles/<particle>/formula.md`.
- Running: `scripts/run_all.sh` → `scripts/variants_v2.py`, `variants_v3.py` → `scripts/run_round3.sh` (final formula, test, s2,
  shapes, cross-checks); verification: `scripts/verify_results.py`; then the formula cards and formula blocks (`scripts/formula_card.py`, `scripts/readme_particle_formulas.py`) and the figure `scripts/formula_maps.py`. Logs go to `logs/`.
- Inputs: the simulation CSVs (`results/data.sha256`) and the report's saved models (baseline degree ladders, MLPs, distilled formulas,
  exports), whose copies are in `report_notebooks/results/<particle>/` (`REPORT_RESULTS` in `protonlab.py`). The CNN row of the
  08 notebook also needs the CNN class of the report's `06_cnn_proton.ipynb` (path in `shapelab.py`).
- `results/particles/<particle>/` also keeps the earlier rounds (`new_*`, `new2_*`, `variant*.pt` and their JSON summaries): the later
  rounds, the variant selection and the symbolic-regression diagnostics (`scripts/sr_residual.py`, `sr_control.py`, run on the
  round-2 formula) start from them.
- Measurements: `scripts/profile_metrics.py`, `truth_decomposition.py`, `front_region.py`, `lfhcal_expectations.py`; angle-dependent
  extension (chapter 6): `scripts/theta_entrance.py <particle> two` (`scripts/run_theta_two.sh`); time separation and fluctuation: `scripts/time_split.py`, `fluctuations_pca.py`.
- Proton analysis with figures: `08_shape3d_proton.ipynb`. The data cache (`cache/`) is rebuilt from the CSVs on the first run.
- Archived, not runnable from this repository (their inputs belong to the earlier proton-only stage): `review/` (independent review of
  the likelihood and of the numbers) and `results/isobody/` (iso-density bodies used for the 90%/90% comparison in the 08 notebook).
- `results/detektor_es_alakok/`, `results/detektor_*.png` and `Protonmodell-Tamas.pdf` are presentation figures (in Hungarian) made from
  the saved fits; no plotting script is included for them.
- The report's `05_mlp_<particle>` notebooks extended with the new formula: `report_notebooks/` (section 8 evaluates the formula on the same test set as the network and the distilled formula; built by `scripts/build_report_notebooks.py`).
- Reproducibility: package versions in `requirements.txt` (Python 3.10); SHA-256 of the input simulation files in `results/data.sha256` (check a local copy with `cd <simulations folder> && sha256sum -c <repo>/results/data.sha256`); the split uses `SEED = 1`.
- Hungarian version of this description: [README.hu.md](README.hu.md); all formulas in one place: [ALL-README.md](ALL-README.md).
