#!/bin/bash
# szimbolikus regresszió részecskénként, ha a 2. kör kész (audit_v2.json)
cd "$(dirname "$0")/.."
mkdir -p logs
export MPLBACKEND=Agg
for p in "$@"; do
  ( until [ -f results/particles/$p/audit_v2.json ]; do sleep 20; done
    ${PYTHON:-python3} scripts/sr_residual.py $p > logs/sr_$p.log 2>&1 ) &
done
wait
echo SR_DONE >> logs/sr_done.log
