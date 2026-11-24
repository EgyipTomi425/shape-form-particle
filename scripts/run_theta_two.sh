#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p logs
export MPLBACKEND=Agg
for p in electron muon proton pion; do
  ( [ -f results/particles/$p/theta_entrance_two.json ] || ${PYTHON:-python3} scripts/theta_entrance.py $p two > logs/theta_two_$p.log 2>&1 ) &
done
wait
echo THETA2_DONE >> logs/theta_two_done.log
