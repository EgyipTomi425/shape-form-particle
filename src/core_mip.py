"""Core, MIP segment and halo of the shower (particle issue #1): per-event features from the simulated hits.

Definitions (issue #1):
  axis         straight line of the incoming direction (theta, phi) from the vertex (0, 0, 0); it enters the calorimeter at the front
               face Z_FRONT = 3620.0 mm (ePIC LFHCAL_zmin: 25.4 mm mounting plate + 15 mm front wall, both steel, then the layers; each
               layer is 4 mm scintillator, 0.8 mm Kapton (0.5 mm air offset) and 15.2 mm steel, so a tile sits IN FRONT of its absorber)
  core         visible energy within R = 5 cm of the axis, excluding the MIP segment
  MIP segment  minimum-ionising deposit along the axis from the entry point until the shower starts
  halo         visible energy farther than R from the axis
  E_vis = E_MIP + E_core + E_halo,   f_core = E_core / E_vis,   f_MIP = E_MIP / E_vis   (a partition into regions: E_MIP within R in
  the tiles of the MIP segment, E_core within R in the tiles from the shower start on, E_halo outside R)
Only prompt deposits (t < 100 ns) count, as in the report; the events and the train/val/test split are the report's (SEED = 1).

Cell sharing ("folding"): the energy of a cell is shared by the part of its 48.6 x 48.6 mm face inside R (8 x 8 points); the
cell-centre rule is kept for comparison.

MIP calibration on muons (p >= 2 GeV/c, layers crossed by the axis): per layer, the most probable value (1 MIP) and the half widths at
half maximum of the core energy times cos(theta) (path-length correction).

MIP-segment finder: walk the layers from the entry point. A layer is MIP-like if its core energy is at most core_up MIP, its energy
outside R at most halo_up MIP and at most cells_up cells fire (> 0.3 MIP); "narrow" drops the core limit (slow hadrons). Layers without
a deposit on the axis (gaps, cell edges) do not interrupt the segment. The shower starts at the first of n_consec consecutive non-MIP
layers whose summed core energy exceeds core_sum MIP. L_MIP is the depth (from the entry point, along the axis) of the last tile with
a deposit on the axis before the start (0 if there is none); without a shower start the segment ends at the last deposit on the axis
(a stopping particle) or at the back. E_MIP is the core energy of the segment's tiles (single spikes such as delta rays or a Bragg
peak belong to the passage); f_MIP_like keeps only its MIP-like tiles. Since a tile precedes its absorber, an interaction in the steel behind tile k is first seen in tile k + 1:
L_MIP <= true interaction depth < z_start. The parameters are chosen against the simulation truth on the train split
(scripts/core_mip_tune.py -> results/features/mip_finder.json).

Readout: the ePIC LFHCal sums the SiPM signals of 5, 5, 10, 10, 10, 10, 10 consecutive tiles (rlayerz of the ePIC geometry), so the
per-layer finder is a simulation-level quantity; seg1_* / seg2_* give the same quantities for the first two readout segments
(layers 1-5 and 6-10).

Simulation truth (validation only; the CSV gives each cell's EARLIEST contributor with its full list of direct daughters): the primary's
track ends with an inelastic interaction if its daughters contain hadronic products (n, pi, d, alpha, ...); k_last is the deepest layer
whose cell has the primary as earliest contributor (about 13 % of crossed layers miss that cell: gaps and delta electrons arriving first,
so k_last can be one layer short); no primary cell at all means an interaction before the first layer. The primary's cells are its prompt passage (99.9 % within 33 mm of the axis
and within 0.06 ns of straight-line flight), so k_last is not shifted by soft products attributed to the primary.

    python src/core_mip.py build <particle> [s1|s2]      CSV -> cache/core_mip/<particle>_<sample>.npz (muon first: calibration)
    python src/core_mip.py features <particle> [s1|s2]   cache + mip_finder.json -> results/features/<particle>.parquet"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pcc
import pyarrow.csv as pc
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import CACHE, DATA_ROOT, RESULTS  # noqa: E402

FEAT = os.path.join(RESULTS, "features")
CACHE_DIR = os.path.join(CACHE, "core_mip")
PITCH, N_LAYERS, Z_L1 = 20.5, 60, 3662.4          # layer pitch, number of layers, z of the first scintillator layer centre [mm]
Z_FRONT = Z_L1 - 2.0 - 40.4                       # front face (= LFHCAL_zmin 3620.0 mm): half tile, 40.4 mm of front steel
HALF_CELL = 24.3                                   # half width of a cell [mm]
GAP_TOL = 35.0                                     # the axis is in the instrumented area if a cell centre is within 35 mm (Chebyshev)
MARGIN = 100.0                                     # fiducial: the area also holds 100 mm around the axis (4 directions)
SEGMENTS = (5, 5, 10, 10, 10, 10, 10)               # tiles per readout segment (ePIC rlayerz)
R_LIST = (25.0, 50.0, 75.0, 100.0)                 # radii of the scan [mm]
R_CORE = 50.0
TIME_CUT = 100.0                                   # ns, as in the report
CELL_THR = 0.3                                     # MIP units: a cell fires above 0.3 MIP
ACTIVE = 0.3                                       # MIP units: a layer has a deposit on the axis if its core energy exceeds this
SEED = 1
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
COLS = ["event_number", "x", "y", "z", "x_local", "y_local", "z_local", "energy", "earliest_contribution_time", "incoming_momentum",
        "incoming_momentum_bin", "incoming_theta", "incoming_phi", "is_secondary"]
SPLITS = {"train": 0, "val": 1, "test": 2, "none": -1}
# products of an inelastic hadronic interaction (Geant4 ends the primary's track there); e-, gamma and recoil nuclei also come from delta
# rays and elastic scattering, mu+ from the pi+ decay. A proton daughter marks knock-out reactions such as 56Fe(p,2p)55Mn, which emit no
# neutron or pion; elastic scattering on hydrogen (scintillator, Kapton) also gives one, for well below 1 % of the primaries
INELASTIC = {"proton", "neutron", "pi+", "pi-", "pi0", "deuteron", "triton", "He3", "alpha", "kaon+", "kaon-", "K0L", "K0S", "PDG_221",
             "PDG_331", "Lambda", "Sigma+", "Sigma-", "Sigma0", "anti_proton", "anti_neutron"}
CHARGED_HADRONS = ["proton", "pi+", "pi-", "kaon+", "kaon-", "deuteron", "triton", "He3", "alpha"]


def csv_path(particle, sample="s1"):
    return os.path.join(DATA_ROOT, f"regression-{particle}", f"{particle}_standalone_N100000_M0_20GeV_reg_balanced_{sample}_v3.csv")


def load(particle, sample="s1"):
    """Prompt hits, and the event table (p, bin, theta, phi, split)."""
    df = pc.read_csv(csv_path(particle, sample), convert_options=pc.ConvertOptions(include_columns=COLS)).to_pandas()
    df.sort_values("event_number", kind="stable", inplace=True)
    ev = df.groupby("event_number")[["incoming_momentum", "incoming_momentum_bin", "incoming_theta", "incoming_phi"]].first()
    ev.columns = ["p", "bin", "theta", "phi"]
    # the report's split (load_data of 00_common: same cuts, stratified per momentum bin, SEED = 1)
    d = df[df.earliest_contribution_time < TIME_CUT]
    d = d[(d.z_local >= -200.0) & (d.z_local <= 1450.0) & (np.hypot(d.x_local, d.y_local) < 700.0)]
    first = d.groupby("event_number").first()
    evn, bins = first.index.values, first.incoming_momentum_bin.values.astype(np.int64)
    rng, split = np.random.default_rng(SEED), {}
    for b in np.unique(bins):
        idx = rng.permutation(np.where(bins == b)[0])
        n1, n2 = round(0.70 * len(idx)), round(0.85 * len(idx))
        split.update({evn[i]: "train" for i in idx[:n1]})
        split.update({evn[i]: "val" for i in idx[n1:n2]})
        split.update({evn[i]: "test" for i in idx[n2:]})
    ev["split"] = [split.get(e, "none") for e in ev.index]
    return df[df.earliest_contribution_time < TIME_CUT], ev


def primary_truth(particle, sample, ev):
    """Per event: the primary's first and last layer, its number of layers, how its track ended (from its daughters), and the first
    layer with a charged hadron whose parent has the primary's type (prompt cells only)."""
    cols = ["event_number", "z", "earliest_contribution_time", "particle_type", "is_secondary", "parent_type", "daughter_type"]
    r = pc.open_csv(csv_path(particle, sample), read_options=pc.ReadOptions(block_size=512 << 20),
                    convert_options=pc.ConvertOptions(include_columns=cols, strings_can_be_null=True))
    prim, prod = [], []
    for b in r:
        b = b.filter(pcc.less(b.column("earliest_contribution_time"), TIME_CUT))
        is0 = pcc.equal(b.column("is_secondary"), 0)
        prim.append(b.filter(is0).select(["event_number", "z", "particle_type", "daughter_type"]).to_pandas())
        ch = pcc.and_(pcc.invert(is0), pcc.is_in(b.column("particle_type"), value_set=pa.array(CHARGED_HADRONS)))
        prod.append(b.filter(ch).select(["event_number", "z", "parent_type"]).to_pandas())
    prim, prod = pd.concat(prim, ignore_index=True), pd.concat(prod, ignore_index=True)
    layer = lambda z: np.clip(np.rint((z - Z_L1) / PITCH).astype(np.int64), 0, N_LAYERS - 1)
    prim["layer"], prod["layer"] = layer(prim.z.values), layer(prod.z.values)
    ptype = prim.particle_type.mode().iat[0] if len(prim) else ""
    g = prim.groupby("event_number")
    t = pd.DataFrame({"k_first": g.layer.min(), "k_last": g.layer.max(), "n_prim_layers": g.layer.nunique()})
    d = g.daughter_type.first().fillna("").str.split(";")
    t["inelastic"] = d.map(lambda s: bool(INELASTIC.intersection(s)))
    t["mu_daughter"] = d.map(lambda s: "mu+" in s or "mu-" in s)
    t["k_first_product"] = prod[prod.parent_type == ptype].groupby("event_number").layer.min()
    t = t.reindex(ev.index)
    out = {"has_prim": t.k_last.notna().values}
    for c in ("k_first", "k_last", "n_prim_layers", "k_first_product"):
        out[c] = t[c].fillna(-1).values.astype(np.int16)
    for c in ("inelastic", "mu_daughter"):
        out[c] = t[c].fillna(False).values.astype(bool)
    return out


def cell_grid():
    """(x, y) centres of all cells that ever fired in the proton sample (the instrumented area), cached."""
    path = os.path.join(FEAT, "cells_xy.csv")
    if not os.path.exists(path):
        t = pc.read_csv(csv_path("proton"), convert_options=pc.ConvertOptions(include_columns=["x", "y"])).to_pandas()
        xy = np.unique(np.round(t[["x", "y"]].values, 1), axis=0)
        os.makedirs(FEAT, exist_ok=True)
        pd.DataFrame(xy, columns=["x", "y"]).to_csv(path, index=False)
    return pd.read_csv(path).values


def axis_inside(theta, phi, margin=0.0):
    """(n_events, 60) bool: the axis crosses the instrumented area in layer k (not the beam hole, not beyond the outer edge); with a
    margin, the points margin mm away in +-x and +-y must be inside too."""
    from scipy.spatial import cKDTree
    tree = cKDTree(cell_grid())
    zk = Z_L1 + PITCH * np.arange(N_LAYERS)
    t = np.tan(theta)[:, None] * zk[None, :]
    pts = np.stack([t * np.cos(phi)[:, None], t * np.sin(phi)[:, None]], -1).reshape(-1, 2)
    ok = np.ones(len(pts), bool)
    offs = [(0.0, 0.0)] + ([(margin, 0.0), (-margin, 0.0), (0.0, margin), (0.0, -margin)] if margin > 0 else [])
    for dx, dy in offs:
        dist, _ = tree.query(pts + np.array([dx, dy]), p=np.inf)
        ok &= dist <= GAP_TOL
    return ok.reshape(len(theta), N_LAYERS)


def per_hit(hits, ev):
    """Per hit: event index, layer, energy, folded fractions inside R_LIST, centre-rule flag (R_CORE), primary flag."""
    eidx = np.searchsorted(ev.index.values, hits.event_number.values)
    th, ph = ev.theta.values[eidx], ev.phi.values[eidx]
    n = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], 1)
    g = (np.arange(8) + 0.5) / 8 * 2 * HALF_CELL - HALF_CELL
    dx, dy = [torch.tensor(a.reshape(-1), device=DEV, dtype=torch.float64) for a in np.meshgrid(g, g, indexing="ij")]
    X, Y, Z = (torch.tensor(hits[c].values, device=DEV, dtype=torch.float64) for c in ("x", "y", "z"))
    N = torch.tensor(n, device=DEV, dtype=torch.float64)
    frac = torch.empty(len(hits), len(R_LIST), dtype=torch.float32, device=DEV)
    centre = torch.empty(len(hits), dtype=torch.bool, device=DEV)
    for a in range(0, len(hits), 2_000_000):
        b = slice(a, a + 2_000_000)
        px, py, pz = X[b, None] + dx, Y[b, None] + dy, Z[b, None].expand(-1, len(dx))
        dot = px * N[b, 0:1] + py * N[b, 1:2] + pz * N[b, 2:3]
        r2 = (px - dot * N[b, 0:1]) ** 2 + (py - dot * N[b, 1:2]) ** 2 + (pz - dot * N[b, 2:3]) ** 2
        frac[b] = torch.stack([(r2 <= R * R).float().mean(1) for R in R_LIST], 1)
        dc = X[b] * N[b, 0] + Y[b] * N[b, 1] + Z[b] * N[b, 2]
        centre[b] = ((X[b] - dc * N[b, 0]) ** 2 + (Y[b] - dc * N[b, 1]) ** 2 + (Z[b] - dc * N[b, 2]) ** 2) <= R_CORE ** 2
    layer = np.clip(np.rint((hits.z.values - Z_L1) / PITCH).astype(np.int64), 0, N_LAYERS - 1)
    return {"eidx": torch.tensor(eidx, device=DEV), "layer": torch.tensor(layer, device=DEV),
            "e": torch.tensor(hits.energy.values, device=DEV, dtype=torch.float64), "frac": frac, "centre": centre,
            "prim": torch.tensor(hits.is_secondary.values == 0, device=DEV)}


def layer_sums(H, n_ev, weight):
    """(n_events, 60) sum of weight per event and layer (weight: per hit)."""
    out = torch.zeros(n_ev * N_LAYERS, dtype=torch.float64, device=DEV)
    out.index_add_(0, H["eidx"] * N_LAYERS + H["layer"], weight.double())
    return out.view(n_ev, N_LAYERS).cpu().numpy()


def depth_cm(theta):
    """(n_events, 60) depth of each layer's scintillator centre along the axis from the entry point [cm]."""
    zk = Z_L1 + PITCH * np.arange(N_LAYERS)
    return (zk[None, :] - Z_FRONT) / np.cos(theta)[:, None] / 10.0


def calibrate(core, inside, p, theta):
    """MIP calibration on muons with p >= 2 GeV/c: per layer the most probable value and the half widths at half maximum of the core
    energy * cos(theta), and the quantiles of the core energy in MIP units."""
    c = np.cos(theta)[:, None]
    v = core * c
    sel = (p >= 2.0)[:, None] & inside & (v > 0)
    res = {"layer": [], "mpv": [], "w_left": [], "w_right": [], "n": [], "zero_frac": []}
    for k in range(N_LAYERS):
        x = v[sel[:, k], k]
        h, e = np.histogram(x, bins=240, range=(0, np.quantile(x, 0.99)))
        hs = np.convolve(h, np.ones(5) / 5, mode="same")
        i = int(np.argmax(hs))
        cen = 0.5 * (e[1:] + e[:-1])
        half = hs[i] / 2
        lft = i - np.argmax(hs[:i + 1][::-1] < half) if (hs[:i + 1] < half).any() else 0
        rgt = i + np.argmax(hs[i:] < half) if (hs[i:] < half).any() else len(hs) - 1
        base = (p >= 2.0) & inside[:, k]
        res["layer"].append(k + 1); res["mpv"].append(float(cen[i])); res["w_left"].append(float(cen[i] - cen[lft]))
        res["w_right"].append(float(cen[rgt] - cen[i])); res["n"].append(int(len(x)))
        res["zero_frac"].append(float((core[base, k] <= 0).mean()))
    u = (core * c / np.array(res["mpv"])[None, :])[(p >= 2.0)[:, None] & inside]
    res["core_quantiles_mip"] = {str(q): float(np.quantile(u, q)) for q in (0.5, 0.9, 0.95, 0.98, 0.99, 0.995)}
    return res


def build(particle, sample="s1"):
    """One pass over the CSV: per-layer arrays, event sums and the primary truth -> cache/core_mip/<particle>_<sample>.npz."""
    t0 = time.time()
    hits, ev = load(particle, sample)
    n = len(ev)
    H = per_hit(hits, ev)
    inside = axis_inside(ev.theta.values, ev.phi.values)
    inside_margin = axis_inside(ev.theta.values, ev.phi.values, MARGIN)
    j = R_LIST.index(R_CORE)
    core = layer_sums(H, n, H["e"] * H["frac"][:, j])
    calib_path = os.path.join(FEAT, "mip_calibration.json" if sample == "s1" else f"mip_calibration_{sample}.json")
    if particle == "muon":
        calib = calibrate(core, inside, ev.p.values, ev.theta.values)
        calib.update({"definition": "core energy (R = 5 cm, folded) * cos(theta), muons p >= 2 GeV/c, layers crossed by the axis",
                      "unit": "GeV (mpv, w_left, w_right); MIP for the quantiles", "sample": sample})
        os.makedirs(FEAT, exist_ok=True)
        json.dump(calib, open(calib_path, "w"), indent=1)
    calib = json.load(open(calib_path))
    mip = np.array(calib["mpv"])[None, :] / np.cos(ev.theta.values)[:, None]        # one MIP in this event and layer [GeV]
    thr = torch.tensor(mip, device=DEV)[H["eidx"], H["layer"]] * CELL_THR
    fired = H["e"] > thr
    arr = {"core": core, "all": layer_sums(H, n, H["e"]), "prim_core": layer_sums(H, n, H["e"] * H["frac"][:, j] * H["prim"]),
           "ncell": layer_sums(H, n, fired.double()), "ncell_out": layer_sums(H, n, (fired & ~H["centre"]).double())}
    tot = lambda w: torch.zeros(n, dtype=torch.float64, device=DEV).index_add_(0, H["eidx"], w.double()).cpu().numpy()
    evs = {"E_vis": tot(H["e"]), "E_prim": tot(H["e"] * H["prim"]), "E_prim_near_R50": tot(H["e"] * H["prim"] * H["frac"][:, j]),
           "near_centre_R50": tot(H["e"] * H["centre"])}
    for jj, R in enumerate(R_LIST):
        evs[f"near_R{int(R)}"] = tot(H["e"] * H["frac"][:, jj])
    del H, hits
    truth = primary_truth(particle, sample, ev)
    os.makedirs(CACHE_DIR, exist_ok=True)
    np.savez_compressed(os.path.join(CACHE_DIR, f"{particle}_{sample}.npz"),
                        event_number=ev.index.values, split=ev.split.map(SPLITS).values.astype(np.int8), p=ev.p.values,
                        bin=ev.bin.values.astype(np.int16), theta=ev.theta.values, phi=ev.phi.values, inside=inside,
                        inside_margin=inside_margin,
                        **{k: v.astype(np.float32) for k, v in arr.items() if k not in ("ncell", "ncell_out")},
                        ncell=arr["ncell"].astype(np.uint8), ncell_out=arr["ncell_out"].astype(np.uint8), mip=mip.astype(np.float32),
                        **{f"ev_{k}": v for k, v in evs.items()}, **{f"truth_{k}": v for k, v in truth.items()})
    print(f"{particle} {sample}: {n} events, cache written in {time.time() - t0:.0f} s", flush=True)


def load_cache(particle, sample="s1"):
    return dict(np.load(os.path.join(CACHE_DIR, f"{particle}_{sample}.npz")))


def find_segment(C, core_up, halo_up, cells_up, n_consec, core_sum=0.0, core_sum_per_gev=0.0):
    """The MIP-segment finder on cached per-layer arrays. Returns per event: start layer k (60 if none), last MIP-like layer with a
    deposit on the axis before the start (-1 if none), end code (0 shower start, 1 the axis leaves the instrumented area first,
    2 stops inside without a shower start, 3 reaches the back without a shower start), the mask of the MIP-like segment layers (for
    E_MIP) and the per-layer MIP-like flags."""
    u, h = C["core"] / C["mip"], (C["all"] - C["core"]) / C["mip"]
    inside = C["inside"]
    mip_like = (u <= core_up) & (h <= halo_up) & (C["ncell"] <= cells_up)
    bad = ~mip_like & inside
    run = bad[:, :N_LAYERS - n_consec + 1].copy()
    usum = u[:, :N_LAYERS - n_consec + 1].copy()
    for j in range(1, n_consec):
        run &= bad[:, j:N_LAYERS - n_consec + 1 + j]
        usum += u[:, j:N_LAYERS - n_consec + 1 + j]
    thr = core_sum + core_sum_per_gev * C["p"]                           # the start threshold may grow with the momentum
    run &= usum > np.asarray(thr)[:, None] if np.ndim(thr) else usum > thr
    has = run.any(1)
    k = np.where(has, run.argmax(1), N_LAYERS)
    first_out = np.where((~inside).any(1), (~inside).argmax(1), N_LAYERS)
    stop = np.minimum(k, first_out)
    lay = np.arange(N_LAYERS)[None, :]
    act = inside & (u > ACTIVE) & (lay < stop[:, None])                # tiles with a deposit on the axis before the start
    last = np.where(act.any(1), N_LAYERS - 1 - act[:, ::-1].argmax(1), -1)
    end = np.where(has & (k < first_out), 0, np.where(first_out < N_LAYERS, 1, np.where(last >= N_LAYERS - 2, 3, 2)))
    # the segment (a region of the axis): the tiles before the start; without a start, up to the last deposit on the axis
    seg_end = np.where(end == 0, k, last + 1)
    return k, last, end, lay < seg_end[:, None], mip_like


def longest_run(a):
    """Per row of a (n, L) bool array: length and first index of the longest run of True (length 0, start -1 if none)."""
    cnt = np.zeros(a.shape, np.int16)
    c = np.zeros(a.shape[0], np.int16)
    for j in range(a.shape[1]):
        c = np.where(a[:, j], c + 1, 0).astype(np.int16)
        cnt[:, j] = c
    length = cnt.max(1)
    return length, np.where(length > 0, cnt.argmax(1) - length + 1, -1)


def features(particle, sample="s1", finder=None):
    C = load_cache(particle, sample)
    if finder is None:
        finder = json.load(open(os.path.join(FEAT, "mip_finder.json")))
    n = len(C["p"])
    rows = np.arange(n)
    lay = np.arange(N_LAYERS)[None, :]
    s = depth_cm(C["theta"])
    E = np.maximum(C["ev_E_vis"], 1e-30)
    inside = C["inside"]
    u, h = C["core"] / C["mip"], (C["all"] - C["core"]) / C["mip"]
    out = pd.DataFrame({"event_number": C["event_number"], "split": pd.Series(C["split"]).map({v: k for k, v in SPLITS.items()}).values,
                        "p": C["p"], "bin": C["bin"], "theta": C["theta"], "phi": C["phi"], "E_vis": C["ev_E_vis"],
                        "entry_inside": inside[:, 0] & inside[:, 1], "n_layers_inside": inside.sum(1),
                        "fiducial": C["inside_margin"].all(1)})
    for R in R_LIST:
        out[f"f_near_R{int(R)}"] = C[f"ev_near_R{int(R)}"] / E
    out["f_near_centre_R50"] = C["ev_near_centre_R50"] / E
    out["f_halo"] = 1.0 - out["f_near_R50"]
    valid = out.entry_inside.values
    # the first two readout segments of the ePIC LFHCal (tiles 1-5 and 6-10 summed): core and outside-R energy in MIP units
    for i, (a, b) in enumerate(((0, 5), (5, 10)), 1):
        out[f"seg{i}_core_mip"] = np.where(valid, u[:, a:b].sum(1), np.nan)
        out[f"seg{i}_halo_mip"] = np.where(valid, h[:, a:b].sum(1), np.nan)
    ends = np.array(["shower", "leaves", "stops", "exits"])
    for ver, prm in finder["versions"].items():
        k, last, end, seg, mip_like = find_segment(C, prm["core_up"], prm["halo_up"], prm["cells_up"], prm["n_consec"],
                                                   prm.get("core_sum", 0.0), prm.get("core_sum_per_gev", 0.0))
        L = np.where(last >= 0, s[rows, np.maximum(last, 0)], 0.0)
        zst = np.where(end == 0, s[rows, np.minimum(k, N_LAYERS - 1)], np.nan)
        e_mip = (C["core"] * seg).sum(1)
        e_mip_like = (C["core"] * (seg & mip_like)).sum(1)
        out[f"k_start_{ver}"] = np.where(valid & (end == 0), k, -1).astype(np.int16)
        out[f"L_MIP_{ver}"] = np.where(valid, L, np.nan)
        out[f"z_start_{ver}"] = np.where(valid, zst, np.nan)
        out[f"end_{ver}"] = np.where(valid, ends[end], "outside")
        out[f"f_MIP_{ver}"] = np.where(valid, e_mip / E, np.nan)
        out[f"f_MIP_like_{ver}"] = np.where(valid, e_mip_like / E, np.nan)
        out[f"f_core_{ver}"] = np.maximum(out["f_near_R50"] - out[f"f_MIP_{ver}"], 0.0)
        # core energy deposited by the primary itself outside the MIP segment (truth, validation only)
        out[f"f_core_primary_{ver}"] = np.where(valid, (C["prim_core"] * ~seg).sum(1) / E, np.nan)
        # Gabor's property 2: the longest run of consecutive MIP-like layers with a deposit on the axis AFTER the shower start, and the
        # share of its core energy that the primary deposited (truth)
        late = mip_like & inside & (u > ACTIVE) & (lay > k[:, None]) & (end == 0)[:, None]
        rl, rs = longest_run(late)
        in_run = (lay >= rs[:, None]) & (lay < (rs + rl)[:, None]) & (rl > 0)[:, None]
        out[f"late_run_layers_{ver}"] = np.where(valid, rl, 0).astype(np.int16)
        out[f"late_run_depth_{ver}"] = np.where(valid & (rl > 0), s[rows, np.maximum(rs, 0)], np.nan)
        out[f"late_run_primary_{ver}"] = np.where(valid & (rl > 0), (C["prim_core"] * in_run).sum(1) / np.maximum((C["core"] * in_run).sum(1), 1e-30), np.nan)
    # simulation truth (validation only)
    out["f_primary"] = C["ev_E_prim"] / E
    out["f_primary_near_R50"] = C["ev_E_prim_near_R50"] / E
    kl = C["truth_k_last"].astype(np.int64)
    has = C["truth_has_prim"]
    first_out = np.where((~inside).any(1), (~inside).argmax(1), N_LAYERS)
    out["true_end"] = np.select([~has, C["truth_inelastic"], C["truth_mu_daughter"], kl >= N_LAYERS - 1, first_out <= kl + 1],
                                ["before_layer1", "inelastic", "decay", "exits", "leaves"], "stops")
    out["L_true"] = np.where(has, s[rows, np.maximum(kl, 0)], 0.0)          # depth of the last tile the primary reached
    out["k_last_true"] = kl.astype(np.int16)
    out["k_first_product_true"] = C["truth_k_first_product"]
    return out


def tidy(out):
    """Columns named as in the issue (the strict version) and float32 storage (p, theta, phi stay float64)."""
    out = out.copy()
    for a in ("f_MIP", "L_MIP", "z_start", "f_core"):
        out[a] = out[f"{a}_strict"]
    for c in out.columns:
        if out[c].dtype == np.float64 and c not in ("p", "theta", "phi"):
            out[c] = out[c].astype(np.float32)
    return out


if __name__ == "__main__":
    cmd, particle = sys.argv[1], sys.argv[2]
    sample = sys.argv[3] if len(sys.argv) > 3 else "s1"
    if cmd == "build":
        build(particle, sample)
    else:
        os.makedirs(FEAT, exist_ok=True)
        name = f"{particle}.parquet" if sample == "s1" else f"{particle}_{sample}.parquet"
        tidy(features(particle, sample)).to_parquet(os.path.join(FEAT, name), index=False, compression="zstd")
        print(f"{particle} {sample}: features written", flush=True)
