import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # repository root
import sys, time
sys.path.insert(0, os.path.join(ROOT, "src"))
import protonlab
t0 = time.time()
C = protonlab.load_common()
geo, data = protonlab.load_proton(C)
print("geo", geo)
for k, s in data.items():
    print(k, len(s), "events", len(s.w), "hits")
print(f"done in {time.time() - t0:.0f}s")
