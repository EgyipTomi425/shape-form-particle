"""Részecske-gyorsítótár építése: python build_cache_particle.py <particle> <s1|s2>"""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # repository root
import sys, time
sys.path.insert(0, os.path.join(ROOT, "src"))
import protonlab
particle, sample = sys.argv[1], sys.argv[2]
t0 = time.time()
C = protonlab.load_common_for(particle, sample, OUT_DIR=os.path.join(ROOT, "results"))
geo, sets = protonlab.load_particle(C, particle, sample)
print(particle, sample, "geo", geo, {k: len(v) for k, v in sets.items()}, f"done in {time.time() - t0:.0f}s", flush=True)
