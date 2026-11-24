#!/bin/bash
# a Bock-féle irodalmi mélységprofil újratesztelése (proton, pion) a névütközés javítása után; az adat-gyorsítótár első futáskor újraépül
cd "$(dirname "$0")/.."
mkdir -p logs
export MPLBACKEND=Agg
for p in proton pion; do
  ( ${PYTHON:-python3} scripts/test_literature_variants.py $p > logs/bock_$p.log 2>&1 ) &
done
wait
echo BOCK_DONE >> logs/bock_done.log
