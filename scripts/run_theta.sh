#!/bin/bash
# szögfüggő belépés mind a négy részecskére (háttérben, folytatható: kész részecskét kihagy)
cd "$(dirname "$0")/.."
mkdir -p logs
export MPLBACKEND=Agg
for p in electron muon proton pion; do
  ( [ -f results/particles/$p/theta_entrance.json ] || ${PYTHON:-python3} scripts/theta_entrance.py $p > logs/theta_$p.log 2>&1 ) &
done
wait
echo THETA_DONE >> logs/theta_done.log
