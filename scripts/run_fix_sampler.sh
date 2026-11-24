#!/bin/bash
# a javított mintavétellel: profil-egyezés, belépés előtti arány, és a szögfüggő modellek belépés előtti aránya
cd "$(dirname "$0")/.."
mkdir -p logs
export MPLBACKEND=Agg
PY=${PYTHON:-python3}
for p in electron muon proton pion; do
  ( $PY scripts/front_region.py $p > logs/front_$p.log 2>&1
    $PY scripts/theta_entrance.py $p front > logs/theta_front_$p.log 2>&1
    $PY scripts/profile_metrics.py $p > logs/profile_$p.log 2>&1 ) &
done
wait
echo FIX_DONE >> logs/fix_sampler_done.log
