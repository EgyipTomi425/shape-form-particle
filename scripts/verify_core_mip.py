"""Independent cross-check of the issue #1 numbers: a second implementation written from the definitions (it does not import
src/core_mip*.py). Part A: simulation truth, finder start tile and truth interaction length from the raw CSVs on a random subset of
20 000 events (pion, proton, muon); part B: headline numbers recomputed from the parquet files.
    python scripts/verify_core_mip.py      -> results/core_mip/verification.csv (one line per check)"""
import json, os
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.csv as pc, pyarrow.compute as pcc
from sklearn.metrics import roc_auc_score

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.environ.get("LFHCAL_DATA", "/home/user/data/simulations")
ZF, Z1, PITCH = 3620.0, 3662.4, 20.5
HAD = {"proton", "neutron", "pi+", "pi-", "pi0", "deuteron", "triton", "He3", "alpha", "kaon+", "kaon-", "K0L", "K0S"}
cal = json.load(open(f"{REPO}/results/features/mip_calibration.json"))
fin = json.load(open(f"{REPO}/results/features/mip_finder.json"))["versions"]["strict"]
ans = json.load(open(f"{REPO}/results/core_mip/answers.json"))
MPV = np.array(cal["mpv"])
rep = []


def say(item, ours, indep, ok, note=""):
    rep.append((item, ours, indep, "AGREES" if ok else "DIFFERS", note))
    print(f"[{'AGREES' if ok else 'DIFFERS'}] {item}: ours {ours} | independent {indep} {note}", flush=True)


def read_subset(particle, n=20000, seed=7):
    feat = pd.read_parquet(f"{REPO}/results/features/{particle}.parquet")
    ev = feat.event_number.values
    pick = np.random.default_rng(seed).choice(ev, size=min(n, len(ev)), replace=False)
    cols = ["event_number", "x", "y", "z", "energy", "earliest_contribution_time", "incoming_momentum", "incoming_theta", "incoming_phi",
            "particle_type", "is_secondary", "daughter_type"]
    r = pc.open_csv(f"{DATA}/regression-{particle}/{particle}_standalone_N100000_M0_20GeV_reg_balanced_s1_v3.csv",
                    read_options=pc.ReadOptions(block_size=512 << 20), convert_options=pc.ConvertOptions(include_columns=cols))
    s = pa.array(np.sort(pick))
    parts = []
    for b in r:
        b = b.filter(pcc.and_(pcc.is_in(b.column("event_number"), value_set=s), pcc.less(b.column("earliest_contribution_time"), 100.0)))
        parts.append(b.to_pandas())
    return pd.concat(parts, ignore_index=True), feat.set_index("event_number").loc[np.sort(pick)]


def tiles(h):
    return np.clip(np.rint((h.z.values - Z1) / PITCH).astype(int), 0, 59)


def core_fraction(h):
    th, ph = h.incoming_theta.values, h.incoming_phi.values
    n = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], 1)
    g = (np.arange(8) + 0.5) / 8 * 48.6 - 24.3
    gx, gy = np.meshgrid(g, g)
    frac = np.zeros(len(h))
    for a in range(0, len(h), 500000):
        sl = slice(a, a + 500000)
        P = np.stack([h.x.values[sl, None] + gx.ravel(), h.y.values[sl, None] + gy.ravel(), np.repeat(h.z.values[sl, None], 64, 1)], -1)
        d = (P * n[sl, None, :]).sum(-1, keepdims=True)
        r2 = ((P - d * n[sl, None, :]) ** 2).sum(-1)
        frac[sl] = (r2 <= 2500.0).mean(1)
    return frac


def part_a(particle):
    h, f = read_subset(particle)
    t = tiles(h)
    h = h.assign(tile=t)
    # truth
    prim = h[h.is_secondary == 0]
    kl = prim.groupby("event_number").tile.max()
    dau = prim.groupby("event_number").daughter_type.first().fillna("").str.split(";").map(lambda s: bool(HAD.intersection(s)))
    k_last = kl.reindex(f.index).fillna(-1).astype(int)
    inel = dau.reindex(f.index).fillna(False).astype(bool)
    agree_k = float((k_last.values == f.k_last_true.values).mean())
    mine_end = np.where(k_last.values < 0, "before_layer1", np.where(inel.values, "inelastic", "other"))
    ours_end = np.where(f.true_end.isin(["before_layer1", "inelastic"]), f.true_end.values, "other")
    agree_end = float((mine_end == ours_end).mean())
    say(f"{particle}: k_last_true (event by event, {len(f)} events)", "parquet", f"{agree_k:.4f} equal", agree_k > 0.999)
    say(f"{particle}: true_end class", "parquet", f"{agree_end:.4f} equal", agree_end > 0.999)
    # finder on fiducial events
    fid = f[f.fiducial & f.entry_inside]
    hh = h[h.event_number.isin(fid.index)].copy()
    hh["frac"] = core_fraction(hh)
    cos = np.cos(hh.incoming_theta.values)
    mip = MPV[hh.tile.values] / cos
    hh["core_mip"] = hh.energy.values * hh.frac.values / mip
    hh["fired"] = (hh.energy.values > 0.3 * mip).astype(int)
    idx = {e: i for i, e in enumerate(fid.index)}
    ei = hh.event_number.map(idx).values
    U = np.zeros((len(fid), 60)); NC = np.zeros((len(fid), 60))
    np.add.at(U, (ei, hh.tile.values), hh.core_mip.values)
    np.add.at(NC, (ei, hh.tile.values), hh.fired.values)
    nonmip = ~((U <= fin["core_up"]) & (NC <= fin["cells_up"]))
    m = fin["n_consec"]
    thr = fin["core_sum"] + fin["core_sum_per_gev"] * fid.p.values
    run = np.ones((len(fid), 61 - m), bool); usum = np.zeros((len(fid), 61 - m))
    for j in range(m):
        run &= nonmip[:, j:61 - m + j]; usum += U[:, j:61 - m + j]
    run &= usum > thr[:, None]
    k = np.where(run.any(1), run.argmax(1), -1)
    agree = float((k == fid.k_start_strict.values).mean())
    say(f"{particle}: finder start tile (fiducial, {len(fid)} events)", "k_start_strict", f"{agree:.4f} equal", agree > 0.995)
    return f, k_last, inel, fid, k


def lam_fit(x, obs, lo=8.0, hi=80.0):
    grid = np.arange(lo, hi + 0.01, 1.0)
    xx = np.where(obs, x, np.inf)
    S = np.array([np.mean(xx > g) for g in grid])
    return -1.0 / np.polyfit(grid, np.log(S), 1)[0]


if __name__ == "__main__":
    for particle in ("pion", "proton"):
        f, k_last, inel, fid, k = part_a(particle)
        g = f[f.fiducial & f.entry_inside & (f.p >= 3)]
        c = np.cos(g.theta.values)
        kl = k_last.reindex(g.index).values
        x = np.where(kl < 0, 0.0, (Z1 + PITCH * kl + PITCH / 2 - ZF) / c / 10.0)
        obs = (kl < 0) | inel.reindex(g.index).values
        lam = lam_fit(x, obs)
        ours = ans["q3_lambda"][particle]["3-20"]["truth"]["lambda_cm"]
        say(f"{particle}: truth lambda, p >= 3 (log-survival fit, subset)", f"{ours:.2f} cm (censored MLE, all events)", f"{lam:.2f} cm",
            abs(lam - ours) / ours < 0.05)
    # muon false starts
    f, k_last, inel, fid, k = part_a("muon")
    sel = fid.p.values >= 2.0
    share = float((k[sel] >= 0).mean())
    ours = ans["q3_lambda"]["muon_false_start"]["strict"]["share_with_start"]
    say("muon: share with a (false) shower start, p >= 2, fiducial", f"{ours:.4f}", f"{share:.4f} (subset)", abs(share - ours) < 0.02)
    # part B: numbers from the parquet files
    F = {p: pd.read_parquet(f"{REPO}/results/features/{p}.parquet") for p in ("electron", "muon", "pion", "proton")}
    F = {p: d[d.entry_inside & d.fiducial & (d.E_vis > 0)] for p, d in F.items()}
    for p, d in F.items():
        say(f"{p}: selected events", ans["selection"][p]["events_fiducial"], len(d), ans["selection"][p]["events_fiducial"] == len(d))
        dev = np.nanmax(np.abs(d.f_MIP_strict + d.f_core_strict + d.f_halo - 1))
        say(f"{p}: partition f_MIP + f_core + f_halo = 1", "max |dev|", f"{dev:.2e}", dev < 1e-5)
    q2 = pd.read_csv(f"{REPO}/results/core_mip/q2_table.csv")
    for p, d in F.items():
        for lo, hi in ((0.9, 1.1), (4.75, 5.25), (19.5, 20.0)):
            w = d[(d.p >= lo) & (d.p < hi)]
            v = (w.f_core_strict * w.E_vis).sum() / w.E_vis.sum()
            o = q2[(q2.particle == p) & (q2.p_window == f"{lo}-{hi}")].f_core.iloc[0]
            say(f"{p}: f_core ratio of sums, p {lo}-{hi}", f"{o:.4f}", f"{v:.4f}", abs(v - o) < 1e-3)
    cl = pd.read_csv(f"{REPO}/results/core_mip/q3_classify.csv")
    for b in (2, 9, 19):
        e = F["electron"][F["electron"].bin == b]; h = F["pion"][F["pion"].bin == b]
        cale, th = e[e.split.isin(["train", "val"])], h[h.split == "test"]
        for feat, col, sgn in (("L_MIP", "L_MIP_strict", 1), ("f_core", "f_core_strict", -1)):
            t = np.quantile(sgn * cale[col].values, 0.99)
            eff = float(np.mean(sgn * th[col].values > t))
            o = cl[(cl.pair == "electron_vs_pion") & (cl.bin == b) & (cl.feature == feat)].eff99.iloc[0]
            say(f"e vs pi eff99 {feat}, bin {b}", f"{o:.4f}", f"{eff:.4f}", abs(eff - o) < 1e-3)
    au = pd.read_csv(f"{REPO}/results/core_mip/q2_auc_fcore.csv")
    for b in (1, 9, 19):
        a = F["pion"][(F["pion"].bin == b) & (F["pion"].split == "test")]; c = F["proton"][(F["proton"].bin == b) & (F["proton"].split == "test")]
        v = roc_auc_score(np.r_[np.zeros(len(a)), np.ones(len(c))], np.r_[a.f_core_strict, c.f_core_strict])
        o = au[au.pair.str.startswith("pion vs proton") & (au.bin == b)].auc.iloc[0]
        say(f"pi vs p AUC f_core, bin {b}", f"{o:.4f}", f"{v:.4f}", abs(v - o) < 1e-3)
    c4 = pd.read_csv(f"{REPO}/results/core_mip/claim4_indicator.csv")
    e = F["electron"][(F["electron"].p >= 3) & (F["electron"].p < 5)]; h = F["pion"][(F["pion"].p >= 3) & (F["pion"].p < 5)]
    o = c4[(c4.hadron == "pion") & (c4.p_range == "3-5") & (c4.L_min_cm == 8)].iloc[0]
    say("P(L >= 8 cm), 3-5 GeV/c, electron / pion", f"{o.P_electron:.4f} / {o.P_hadron:.4f}",
        f"{(e.L_MIP_strict >= 8).mean():.4f} / {(h.L_MIP_strict >= 8).mean():.4f}",
        abs((e.L_MIP_strict >= 8).mean() - o.P_electron) < 1e-3 and abs((h.L_MIP_strict >= 8).mean() - o.P_hadron) < 1e-3)
    bad = [r for r in rep if r[3] != "AGREES"]
    print(f"\n{len(rep)} checks, {len(bad)} differ")
    pd.DataFrame(rep, columns=["item", "ours", "independent", "verdict", "note"]).to_csv(os.path.join(REPO, "results", "core_mip", "verification.csv"), index=False)
