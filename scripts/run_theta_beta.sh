#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p logs
export MPLBACKEND=Agg
for p in electron muon proton pion; do
  ( [ -f results/particles/$p/theta_entrance_beta.json ] || ${PYTHON:-python3} scripts/theta_entrance.py $p beta > logs/theta_beta_$p.log 2>&1 ) &
done
wait
echo THETAB_DONE >> logs/theta_beta_done.log
