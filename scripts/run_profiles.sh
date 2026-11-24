#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p logs
export MPLBACKEND=Agg
for p in electron muon proton pion; do
  ( ${PYTHON:-python3} scripts/profile_metrics.py $p > logs/profile_$p.log 2>&1 ) &
done
wait
echo PROF_DONE >> logs/profiles_done.log
