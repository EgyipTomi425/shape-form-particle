#!/bin/bash
# Mind a négy részecske elemzése a háttérben, a modellkvótától függetlenül; minden lépés folytatható (újraindításkor kihagyja a kész lépéseket).
cd /home/user/tamas/shape-form-proton
mkdir -p logs
export MPLBACKEND=Agg
PY=/home/user/.venv/bin/python
# the data caches (cache/) are built from the CSVs on first use
for p in electron muon proton pion; do
  nohup $PY scripts/particle_pipeline.py $p > logs/pipeline_$p.log 2>&1 &
done
for p in electron proton pion; do
  for bb in "0,1,2,3,4,5,6,7,8,9" "10,11,12,13,14,15,16,17,18,19"; do
    nohup $PY scripts/particle_bodies.py $p $bb > logs/bodies_${p}_${bb%%,*}.log 2>&1 &
  done
done
# muon: the report has no drop for the muon; cylinder and capsule are fitted as well
for bb in "0,1,2,3,4,5,6,7,8,9" "10,11,12,13,14,15,16,17,18,19"; do
  nohup $PY scripts/particle_bodies.py muon $bb 0.95 0.98 drop,egg,superegg,cylinder,capsule > logs/bodies_muon_${bb%%,*}.log 2>&1 &
done
echo launched
